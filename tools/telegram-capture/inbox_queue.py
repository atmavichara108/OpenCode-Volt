"""inbox_queue.py — staging-очередь постов @inbox_tools (JSONL + flock).

Буфер между приёмом постов (userbot watch.py / таймер capture.py) и ингестом
(классификация → mark → signals). Чтобы группа не накапливалась, очередь живёт
ровно один цикл: пост попал → классифицирован → помечен реакцией → удалён.

Гарантии:
- дедуп по message_id (в рамках чата id уникален);
- flock — безопасность от конкурентного append (демон + таймер одновременно);
- операции только две: append (дописать новые) и remove (атомарная перезапись
  без обработанных). Никакой мутации записи на месте.

Формат строки JSONL: {message_id, topic, text, date, link, media_type,
sender_name, ingested_at}. topic обязателен — его знает приёмник (watch.py
мапит topic_id→имя, capture.py подставляет из --topic).

Использование:
    python inbox_queue.py count
    python inbox_queue.py ls [--limit N]
    cat posts.json | python inbox_queue.py append        # stdin: JSON array
    python inbox_queue.py remove --ids 1 2 3
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:  # noqa: BLE001 — не-Linux (тесты/разработка)
    fcntl = None

DEFAULT_PATH = Path(__file__).resolve().parent / "inbox-queue.jsonl"


def default_path() -> Path:
    """Путь очереди; переопределяется CAPTURE_QUEUE (для тестов/нескольких очередей)."""
    return Path(os.environ.get("CAPTURE_QUEUE", str(DEFAULT_PATH)))


def load(path: Path | None = None) -> list[dict]:
    """Прочитать очередь → list записей в порядке записи (пустой список если нет)."""
    p = path or default_path()
    if not p.exists():
        return []
    out: list[dict] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # битая строка игнорируется, не валит всю очередь
    return out


def to_flat(posts: list[dict]) -> list[dict]:
    """Записи очереди → плоский список в формате classify_batch (с 'topic').

    Запись JSONL уже несёт text/topic/etc. напрямую; здесь возвращаем её как
    есть (классификатору нужны только text и topic, остальное он игнорирует).
    """
    return posts


def ids(path: Path | None = None) -> set[int]:
    """Множество message_id уже в очереди."""
    return {r["message_id"] for r in load(path) if r.get("message_id") is not None}


def append(posts: list[dict], path: Path | None = None) -> tuple[int, int]:
    """Дописать новые посты (пропуская уже существующие message_id).

    Возвращает (added, total_after). flock эксклюзивный; безопасно при
    конкурентном вызове (демон + таймер). Посты без message_id игнорируются.
    """
    p = path or default_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    valid = [r for r in posts if r.get("message_id") is not None]

    added = 0
    with p.open("a+", encoding="utf-8") as f:
        if fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            existing = ids(p)
            for r in valid:
                if r["message_id"] in existing:
                    continue
                r.setdefault("ingested_at", time.time())
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                existing.add(r["message_id"])
                added += 1
            f.flush()
        finally:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    return added, len(load(p))


def remove(message_ids: list[int], path: Path | None = None) -> tuple[int, int]:
    """Удалить обработанные посты из очереди (атомарная перезапись).

    Возвращает (kept, removed). Порядок оставшихся сохраняется.
    """
    p = path or default_path()
    doomed = set(message_ids)
    kept = [r for r in load(p) if r.get("message_id") not in doomed]
    removed = len(doomed)  # сколько уникальных id просили удалить
    tmp = p.with_suffix(".jsonl.tmp")
    if kept:
        tmp.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept),
            encoding="utf-8",
        )
        os.replace(tmp, p)
    else:
        tmp.unlink(missing_ok=True)
        p.unlink(missing_ok=True)
    return len(kept), removed


# --- CLI -------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="staging-очередь постов @inbox_tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("count")
    ls = sub.add_parser("ls")
    ls.add_argument("--limit", type=int, default=0, help="0 = все")
    apd = sub.add_parser("append", help="читать JSON-array из stdin")
    apd.add_argument("--path")
    rm = sub.add_parser("remove")
    rm.add_argument("--ids", nargs="+", type=int, required=True)
    rm.add_argument("--path")
    args = ap.parse_args()

    if args.cmd == "count":
        print(len(load()))
        return 0
    if args.cmd == "ls":
        rows = load()
        if args.limit:
            rows = rows[: args.limit]
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
        return 0
    if args.cmd == "append":
        try:
            posts = json.loads(sys.stdin.read())
            if not isinstance(posts, list):
                raise ValueError("stdin должен быть JSON-array")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"queue: bad stdin: {e}", file=sys.stderr)
            return 2
        added, total = append(posts, Path(args.path) if args.path else None)
        print(f"queue: added={added} total={total}")
        return 0
    if args.cmd == "remove":
        kept, removed = remove(args.ids, Path(args.path) if args.path else None)
        print(f"queue: kept={kept} removed={removed}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())