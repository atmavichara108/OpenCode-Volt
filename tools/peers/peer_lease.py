#!/usr/bin/env python3
"""peer_lease — жёсткий flock-lease на hot-files волта (взаимное исключение записи).

Отличие от peer_role.py: то — advisory claim («я беру X», никого не блокирует),
это — ЖЁСТКИЙ лок. Два агента не могут одновременно писать один горячий файл;
второй ждёт LOCK_EX до timeout, не дождался — получает не-ноль exit и НЕ пишет.

Лок лежит на самом файле (flock на открытом fd, как inbox_queue.py): держится
ядром только пока жив процесс-держатель. Уронили сессию — лок освободился сам.

Почему `run`, а не acquire/release: hot-file правят атомарной командой (read→write
в одном shell-вызове), поэтому лок держится ровно пока выполняется эта команда.
Никаких зомби-процессов и «забыл release». Для edit-инструментов агентов правило:
мутировать hot-file ТОЛЬКО через `peer_lease run -- <cmd>`, а не через edit/write.

Hot-files (канон): TASKS.md, 04-Memory/active-context.md,
tools/ecosystem-map/registry.json, 00-INDEX.md. Лок-файл — найденный target
ломается через `flock <file>`; лишнего отдельного локирования не нужно.

Использование:
    # атомарная правка под локом (блокируемся до 10с):
    python3 tools/peers/peer_lease.py run --file TASKS.md --timeout 10 -- \
        python3 -c '...пишем TASKS.md...'

    # кто сейчас держит локи:
    python3 tools/peers/peer_lease.py holds

    # проверить, свободен ли файл (не блокируясь):
    python3 tools/peers/peer_lease.py check --file TASKS.md

JSON на stdout, exit codes: 0 ок · 1 лок не взят/timeout/команда-упала · 2 ошибка ввода.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent

# Горячие файлы, для которых lease обязателен (rel к корню волта).
HOT_FILES = {
    "TASKS.md": "task tracker",
    "04-Memory/active-context.md": "активный контекст",
    "tools/ecosystem-map/registry.json": "registry карточек",
    "00-INDEX.md": "дашборд-вход",
    "AGENTS.md": "правила агента",
}


def _resolve(rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else VAULT_ROOT / p


def _acquire(path: Path, timeout: float):
    """Блокирующе взять LOCK_EX на path. Вернуть открытый file-object (держит лок)
    или None по timeout. Возвращаем сам объект, а не fileno — иначе GC закроет fd
    и лок слетит раньше времени (Bad file descriptor)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open("a+", encoding="utf-8")
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except OSError:
            if time.monotonic() >= deadline:
                f.close()
                return None
            time.sleep(0.05)


def _release(f) -> None:
    if f is None:
        return
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    finally:
        f.close()


def _free(path: Path) -> bool:
    """Не блокируясь: свободен ли file (нет LOCK_EX)."""
    if not path.exists():
        return True
    f = path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return True
    finally:
        f.close()


def cmd_run(args) -> int:
    path = _resolve(args.file)
    timeout = float(args.timeout)

    f = _acquire(path, timeout)
    if f is None:
        print(json.dumps({
            "acquired": False,
            "file": args.file,
            "reason": "lock_timeout",
            "message": f"flock не взят за {args.timeout}s — другой агент пишет {args.file}. Не пиши этот файл.",
        }, ensure_ascii=False))
        return 1

    print(json.dumps({"acquired": True, "file": args.file, "pid": os.getpid()},
                     ensure_ascii=False), file=sys.stderr)
    cmd = list(args.cmd)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    try:
        proc = subprocess.run(cmd, cwd=VAULT_ROOT)
        return proc.returncode
    finally:
        _release(f)


def cmd_holds(args) -> int:
    rows = []
    for rel, why in sorted(HOT_FILES.items()):
        path = _resolve(rel)
        rows.append({"file": rel, "what": why, "locked": not _free(path)})
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_check(args) -> int:
    path = _resolve(args.file)
    free = _free(path)
    print(json.dumps({"file": args.file, "locked": not free}, ensure_ascii=False))
    return 0 if free else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="peer_lease — жёсткий flock-lease на hot-files")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="взять лок и выполнить команду (критическая секция)")
    r.add_argument("--file", required=True, help="hot-file (rel к корню волта)")
    r.add_argument("--timeout", default=10, help="секунды ждать лока (default 10)")
    r.add_argument("cmd", nargs=argparse.REMAINDER, help="команда записи (после --)")
    r.set_defaults(func=cmd_run)

    sub.add_parser("holds", help="кто сейчас держит локи горячих файлов").set_defaults(func=cmd_holds)

    c = sub.add_parser("check", help="свободен ли файл (не блокируясь)")
    c.add_argument("--file", required=True)
    c.set_defaults(func=cmd_check)

    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "run":
        cmd = [c for c in args.cmd if c != "--"]
        if not cmd:
            print("peer_lease run: нужна команда после '--'", file=sys.stderr)
            return 2
        args.cmd = cmd
    try:
        return args.func(args)
    except OSError as e:
        print(json.dumps({"error": "io", "message": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())