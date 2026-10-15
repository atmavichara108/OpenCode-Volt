"""Идемпотентность: JSONL state обработанных писем + flock.

Формат строки: {"message_id": ..., "digest": sha256, "processed_at": iso}.
Append-only, эксклюзивный flock (по образцу tools/telegram-capture/inbox_queue.py),
поэтому параллельные запуски не портят файл. Проверка «обработано» — до выдачи
результата в capture.py, запись — только после успешной обработки.

Путь: config.STATE_PATH (env STATE_PATH), каталог gitignored (`.state/`).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable, Mapping

try:
    import fcntl
except ImportError:  # noqa: BLE001 — не-Linux (тесты/разработка)
    fcntl = None

import classifier
import config

# ключ записи state: message_id, а при его отсутствии — digest
_ID_PREFIX = "id:"
_DIGEST_PREFIX = "sha256:"


def default_path() -> Path:
    return Path(config.STATE_PATH)


def digest_of(message: Mapping) -> str:
    """sha256 от нормализованного текста письма (стабильный между запусками)."""
    payload = classifier.normalize(classifier.text_of(message)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _keys(message: Mapping) -> list[str]:
    """Ключи записи: message_id (если есть) и digest — оба помечаются."""
    keys = [_DIGEST_PREFIX + digest_of(message)]
    mid = classifier.message_id_of(message)
    if mid:
        keys.insert(0, _ID_PREFIX + mid)
    return keys


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # битая строка не валит весь state
    return rows


def processed_keys(path: Path | None = None) -> set[str]:
    """Множество ключей уже обработанных писем (id:... и sha256:...)."""
    p = path or default_path()
    keys: set[str] = set()
    for row in _load(p):
        mid = row.get("message_id")
        if mid:
            keys.add(_ID_PREFIX + str(mid))
        digest = row.get("digest")
        if digest:
            keys.add(_DIGEST_PREFIX + str(digest))
    return keys


def is_processed(message: Mapping, path: Path | None = None) -> bool:
    """True, если письмо уже обработано (по id или по digest текста)."""
    keys = processed_keys(path)
    return any(k in keys for k in _keys(message))


def filter_new(messages: Iterable[Mapping], path: Path | None = None) -> list[dict]:
    """Только ещё не обработанные письма (сохраняет порядок)."""
    keys = processed_keys(path)
    out: list[dict] = []
    for message in messages:
        record = dict(message)
        if any(k in keys for k in _keys(record)):
            continue
        out.append(record)
        keys.update(_keys(record))  # внутри одного батча дубли тоже глушим
    return out


def _keys_from_stream(f) -> set[str]:
    """Ключи из открытого JSONL-потока (чтение уже под flock)."""
    keys: set[str] = set()
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = row.get("message_id")
        if mid:
            keys.add(_ID_PREFIX + str(mid))
        digest = row.get("digest")
        if digest:
            keys.add(_DIGEST_PREFIX + str(digest))
    return keys


def mark(messages: Iterable[Mapping], path: Path | None = None) -> int:
    """Append обработанных в state под эксклюзивным flock.

    Чтение уже обработанных — ВНУТРИ лока (иначе два параллельных запуска
    дописали бы одни и те же id). Возвращает число новых записей;
    повторный вызов ничего не дублирует.
    """
    p = path or default_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    added = 0
    with p.open("a+", encoding="utf-8") as f:
        if fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            existing = _keys_from_stream(f)
            f.seek(0, os.SEEK_END)  # O_APPEND-запись в конец, позиция для чтения
            for message in messages:
                new_keys = [k for k in _keys(message) if k not in existing]
                if not new_keys:
                    continue
                row = {
                    "message_id": classifier.message_id_of(message) or None,
                    "digest": digest_of(message),
                    "processed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                existing.update(new_keys)
                added += 1
            f.flush()
        finally:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return added


if __name__ == "__main__":  # отладочный смоук: python state.py
    print(len(processed_keys()), file=sys.stderr)
    sys.exit(0)
