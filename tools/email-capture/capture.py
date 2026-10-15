"""IMAP-клиент + CLI: письма Gmail → JSON с интентами (stdout) + idea-graph.

Поток:
    LIST папок → SELECT (read-only, BODY.PEEK[] — ящик не мутируется)
    → SEARCH (ALL / SINCE) → FETCH → email-парсинг (HTML→text)
    → дедуп + классификация (classifier) → фильтр по state (state)
    → dry-run: только JSON на stdout
    → обычный прогон: writer.append (idea-graph + валидатор) → state.mark

Конвенция вывода: письма/сводка — JSON в stdout, логи и ошибки — stderr.
Запуск ручной (никаких демонов и таймеров), см. README.md.
"""
from __future__ import annotations

import argparse
import imaplib
import json
import logging
import re
import sys
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from typing import Iterable, Mapping

import classifier
import config
import state
import writer

log = logging.getLogger("email-capture")

# LIST: (\Flags) "delimiter" "name"  /  (\Flags) NIL name
_LIST_RE = re.compile(r'^\((?P<attrs>[^)]*)\)\s+(?P<delim>"[^"]*"|NIL)\s+(?P<name>.+)$')


# --- IMAP ------------------------------------------------------------------

class ImapClient:
    """Тонкая обёртка imaplib.IMAP4_SSL: login, LIST, SELECT, SEARCH, FETCH."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host or config.IMAP_HOST
        self.port = port or config.IMAP_PORT
        self.user = user if user is not None else config.IMAP_USER
        self.password = password if password is not None else config.IMAP_PASS
        self._conn: imaplib.IMAP4_SSL | None = None

    # --- жизненный цикл ---
    def connect(self) -> None:
        if not self.user or not self.password:
            raise RuntimeError(
                "нет IMAP_USER/IMAP_PASS — заполни .env (см. .env.example); "
                "нужен app password при включённой 2FA"
            )
        log.info("connect %s:%s as %s", self.host, self.port, self.user)
        self._conn = imaplib.IMAP4_SSL(self.host, self.port)
        typ, data = self._conn.login(self.user, self.password)
        if typ != "OK":
            raise RuntimeError(f"login failed: {data!r}")

    def close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.logout()
        except Exception:  # noqa: BLE001 — закрытие не должно маскировать основную ошибку
            pass
        finally:
            self._conn = None

    def _require(self) -> imaplib.IMAP4_SSL:
        if self._conn is None:
            raise RuntimeError("IMAP не подключён — сначала connect()")
        return self._conn

    # --- операции ---
    def list_folders(self) -> list[str]:
        """Все папки из LIST (включая [Gmail]/...), без \\Noselect."""
        typ, data = self._require().list()
        if typ != "OK":
            raise RuntimeError(f"LIST failed: {data!r}")
        folders: list[str] = []
        for raw in data or []:
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
            m = _LIST_RE.match(line.strip())
            if not m:
                continue
            if "\\Noselect" in m.group("attrs"):
                continue
            name = m.group("name").strip()
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            folders.append(name)
        return folders

    def select(self, folder: str) -> int:
        """SELECT read-only (не мутирует ящик). Возвращает число писем."""
        typ, data = self._require().select(folder, readonly=True)
        if typ != "OK":
            raise RuntimeError(f"SELECT {folder!r} failed: {data!r}")
        try:
            return int((data or [b"0"])[0])
        except (TypeError, ValueError):
            return 0

    def search(self, since: str | None = None) -> list[str]:
        """SEARCH ALL либо SINCE (since в формате YYYY-MM-DD). → номера писем."""
        conn = self._require()
        if since:
            date_str = datetime.strptime(since, "%Y-%m-%d").strftime("%d-%b-%Y")
            typ, data = conn.search(None, "SINCE", date_str)
        else:
            typ, data = conn.search(None, "ALL")
        if typ != "OK":
            raise RuntimeError(f"SEARCH failed: {data!r}")
        if not data or not data[0]:
            return []
        return data[0].split()

    def fetch_raw(self, num: bytes | str) -> bytes:
        """RFC822-тело через BODY.PEEK[] — без установки флага \\Seen."""
        typ, data = self._require().fetch(num, "(BODY.PEEK[])")
        if typ != "OK":
            raise RuntimeError(f"FETCH {num!r} failed: {data!r}")
        for item in data or []:
            if isinstance(item, tuple) and len(item) > 1 and item[1]:
                return item[1]
        raise RuntimeError(f"FETCH {num!r}: пустое тело")


# --- парсинг ---------------------------------------------------------------

def parse_message(raw: bytes, folder: str = "") -> dict:
    """RFC822 → словарь: message_id, subject, from, date(+iso), body, folder."""
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    subject = str(msg.get("subject") or "")
    sender = str(msg.get("from") or "")
    date_raw = str(msg.get("date") or "")
    date_iso = ""
    if date_raw:
        try:
            date_iso = parsedate_to_datetime(date_raw).date().isoformat()
        except (TypeError, ValueError, IndexError):
            date_iso = ""

    body_text = ""
    body_html = ""
    try:
        part = msg.get_body(preferencelist=("plain", "html"))
    except Exception:  # noqa: BLE001 — не-mail объект (например, mbox)
        part = None
    if part is not None:
        if part.get_content_type() == "text/html":
            body_html = part.get_content() or ""
        else:
            body_text = part.get_content() or ""
    if not body_text and not body_html:
        for p in msg.walk():
            if p.get_content_maintype() != "text":
                continue
            payload = p.get_content() or ""
            if p.get_content_type() == "text/html" and not body_html:
                body_html = payload
            elif p.get_content_type() == "text/plain" and not body_text:
                body_text = payload

    if not body_text and body_html:
        body_text = classifier.html_to_text(body_html)

    return {
        "message_id": str(msg.get("message-id") or "").strip(),
        "subject": subject,
        "from": sender,
        "date": date_iso or date_raw,
        "folder": folder,
        "body": body_text,
        "body_html": body_html,
    }


# --- сбор ------------------------------------------------------------------

def list_folders_for(client: ImapClient, folder: str | None, all_folders: bool) -> list[str]:
    if all_folders:
        folders = client.list_folders()
        log.info("все папки: %s", folders)
        return folders
    if folder:
        return [folder]
    return list(config.FOLDERS)


def collect(
    client: ImapClient,
    folders: Iterable[str],
    limit: int = config.DEFAULT_LIMIT,
    since: str | None = None,
) -> list[dict]:
    """Обход папок → дедуплицированный список писем (лимит — общий бюджет)."""
    collected: list[dict] = []
    remaining = limit if limit and limit > 0 else 0
    for folder in folders:
        if remaining == 0:
            break
        try:
            count = client.select(folder)
        except RuntimeError as e:
            log.warning("пропускаю папку %r: %s", folder, e)
            continue
        nums = client.search(since)
        log.info("folder=%s писем=%d найдено=%d", folder, count, len(nums))
        for num in nums:
            if remaining == 0:
                break
            try:
                raw = client.fetch_raw(num)
            except RuntimeError as e:
                log.warning("fetch %s в %r: %s", num, folder, e)
                continue
            collected.append(parse_message(raw, folder))
            remaining -= 1
    # одно письмо может лежать в нескольких папках (All Mail) — дедуп сразу
    return classifier.dedup(collected)


# --- CLI -------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="capture.py",
        description="письма Gmail → интенты вайбкодинга (JSON stdout) + idea-graph",
    )
    ap.add_argument("--folder", help="одна папка (дефолт из FOLDERS в .env)")
    ap.add_argument("--all", action="store_true", help="обойти все папки ящика")
    ap.add_argument(
        "--limit",
        type=int,
        default=config.DEFAULT_LIMIT,
        help=f"максимум писем на прогон (дефолт {config.DEFAULT_LIMIT})",
    )
    ap.add_argument("--since", help="только писья с даты YYYY-MM-DD")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="JSON без записи в state и idea-graph",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    if args.since:
        try:
            datetime.strptime(args.since, "%Y-%m-%d")
        except ValueError:
            print(f"--since: ожидается YYYY-MM-DD, получено {args.since!r}", file=sys.stderr)
            return 2

    client = ImapClient()
    try:
        client.connect()
        folders = list_folders_for(client, args.folder, args.all)
        if not folders:
            print("не найдено ни одной папки (LIST пуст)", file=sys.stderr)
            return 1
        collected = collect(client, folders, args.limit, args.since)
    except (RuntimeError, OSError, imaplib.IMAP4.error) as e:
        print(f"capture: {e}", file=sys.stderr)
        return 1
    finally:
        client.close()

    try:
        new_messages = state.filter_new(collected)
    except OSError as e:
        print(f"capture: state недоступен: {e}", file=sys.stderr)
        return 1

    classified = classifier.classify_batch(new_messages)
    skipped = len(collected) - len(classified)

    if args.dry_run:
        # read-only: ни state, ни idea-graph не трогаем
        print(json.dumps(classified, ensure_ascii=False, indent=2))
        log.info("dry-run: новых=%d пропущено_обработанных=%d", len(classified), skipped)
        return 0

    intents = [m for m in classified if m["intent"] in config.INTENT_NAMES]
    summary: dict = {"written": False, "nodes": 0, "edges": 0, "validator": "skipped"}
    if intents:
        try:
            summary = writer.append(intents)
        except SystemExit as e:
            # валидатор FAIL: записи есть, state НЕ помечен — разбор вручную
            print(f"capture: {e}", file=sys.stderr)
            return 1
    try:
        marked = state.mark(new_messages)
    except OSError as e:
        print(f"capture: state не записан: {e}", file=sys.stderr)
        return 1

    print(json.dumps(classified, ensure_ascii=False, indent=2))
    log.info(
        "итог: новых=%d обработано=%d интентов_в_граф=%d state+=%d валидатор=%s",
        len(classified),
        marked,
        len(intents),
        marked,
        summary.get("validator"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
