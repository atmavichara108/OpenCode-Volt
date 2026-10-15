#!/usr/bin/env python3
"""mem-index — центральный индекс памяти и спеков экосистемы (Vault).

Память проектов живёт локально (владение не трогаем), индекс — здесь:
для каждого файла — заголовки markdown с номерами строк + mtime/size,
для spec-home проектов — список спек (файл → title). Инвалидация — по mtime.

Пересборка: при flush/dream или вручную:
    python3 tools/mem-index/index.py build
Точечное чтение секции:
    python3 tools/mem-index/index.py get --path <файл> --header <подстрока>

Формат index.json — в духе tools/ecosystem-map/data.json (данные + запросы).
Только stdlib, без сети. Недостающие пути молча пропускаются (stderr).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
OUT = Path(__file__).resolve().parent / "index.json"

# project -> {memory: [...], spec_home: ...}. Пути абсолютные, проверяются.
SOURCES = {
    "dotfiles": {
        "memory": [
            "/home/rudra/dotfiles/.opencode/memory/decisions.md",
            "/home/rudra/dotfiles/.opencode/memory/user-profile.md",
            "/home/rudra/dotfiles/docs/decisions.md",
        ],
        "spec_home": "/home/rudra/dotfiles/docs/specs",
    },
    "vault": {
        "memory": [
            "/home/rudra/Projects/OpenCode-Vault/00-INDEX.md",
            "/home/rudra/Projects/OpenCode-Vault/TASKS.md",
        ],
        "spec_home": None,
    },
    "ChaT": {
        "memory": [
            "/home/rudra/Projects/ChaT/docs/active-context.md",
            "/home/rudra/Projects/ChaT/registers/decisions.md",
        ],
        "spec_home": "/home/rudra/Projects/ChaT/docs/specs",
    },
    "AndroidOS": {
        "memory": [],
        "spec_home": "/home/rudra/Projects/AndroidOS/docs/specs",
    },
    "SERPlux": {
        "memory": ["/home/rudra/Projects/serp/docs/decisions.md"],
        "spec_home": "/home/rudra/Projects/serp/docs/specs",
    },
    "dv-hub": {
        "memory": ["/home/rudra/Projects/dv-hub/docs/decisions.md"],
        "spec_home": "/home/rudra/Projects/dv-hub/docs/specs",
    },
}


def headers_of(path):
    """[(level, title, line)] для строк '# ...'."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                s = line.strip()
                if s.startswith("#"):
                    level = len(s) - len(s.lstrip("#"))
                    out.append({"level": level, "title": s.lstrip("#").strip(), "line": i})
    except OSError as e:
        print(f"skip {path}: {e}", file=sys.stderr)
    return out


def title_of(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if s.startswith("#"):
                    return s.lstrip("#").strip()
    except OSError:
        pass
    return Path(path).name


def build():
    memory, specs = [], {}
    for project, src in SOURCES.items():
        for path in src["memory"]:
            p = Path(path)
            if not p.is_file():
                print(f"skip missing: {path}", file=sys.stderr)
                continue
            st = p.stat()
            memory.append({
                "project": project, "path": path,
                "mtime": int(st.st_mtime), "size": st.st_size,
                "headers": headers_of(path),
            })
        home = src["spec_home"]
        if not home:
            continue
        items = []
        d = Path(home)
        if d.is_dir():
            for md in sorted(d.glob("*.md")):
                if md.name == "README.md":
                    continue
                st = md.stat()
                items.append({"file": md.name, "title": title_of(md),
                              "mtime": int(st.st_mtime)})
        else:
            print(f"skip missing dir: {home}", file=sys.stderr)
        specs[project] = items
    index = {"meta": {"built_at": datetime.now(timezone.utc).isoformat(),
                      "tool": "tools/mem-index/index.py"},
             "memory": memory, "specs": specs}
    OUT.write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")
    print(f"built {OUT}: {len(memory)} memory files, "
          f"{sum(len(v) for v in specs.values())} specs")


def get(path, header):
    """Печать секции файла от заголовка (подстрока, без учёта регистра)."""
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    start, level = None, None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#") and header.lower() in s.lower():
            start = i
            level = len(s) - len(s.lstrip("#"))
            break
    if start is None:
        print(f"Error: header '{header}' not found", file=sys.stderr)
        return 2
    print(lines[start])
    for line in lines[start + 1:]:
        s = line.strip()
        if s.startswith("#") and (len(s) - len(s.lstrip("#"))) <= level:
            break
        print(line)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Central memory/specs index")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    g = sub.add_parser("get")
    g.add_argument("--path", required=True)
    g.add_argument("--header", required=True)
    args = parser.parse_args()
    if args.cmd == "build":
        build()
    elif args.cmd == "get":
        sys.exit(get(args.path, args.header))


if __name__ == "__main__":
    main()
