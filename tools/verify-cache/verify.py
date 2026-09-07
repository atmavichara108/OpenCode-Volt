#!/usr/bin/env python3
"""Verify cache — детерминированные гейты волта с tree-hash кэшем (T-134/P6 #33).

Порт семантики verify-кэша M Code (tree-hash) в TUI-стек: повторный запуск на
неизменённом дереве не перезапускает проверки, а возвращает закэшированный
вердикт. Реализация — по методу [[02-Methods/tool-integration-pattern]] и
[[02-Methods/verifier-pattern]]: LLM думает, скрипт детерминированно проверяет.

Проверки (детерминированные, no network, no mutation входов):
  1. Пустые .md-файлы в контент-директориях волта.
  2. Битые [[wikilink]] — цель ссылки не разрешается в существующий файл
     (по той же логике, что pre-commit hook: суффиксы .md/.json/.jsonc/.js/.sh,
     поиск в контент-каталогах).

Кэш:
  - tree-hash = sha256 по отсортированным (path -> sha256_bytes) всех
    .md/.json/.jsonc/.js/.sh файлов контент-слоёв. Дерево неизменно -> вердикт
    берётся из кэша без повторного сканирования.
  - кэш хранится в tools/verify-cache/generated/verify-cache.json (gitignored).
  - --force: игнорировать кэш и пересчитать.
  - --json: вывод вердикта как JSON (для агента). По умолчанию — человекочитаемый.

Exit codes: 0 = ok (все проверки прошли); 1 = найдены проблемы; 2 = ошибка ввода.

Использование:
    python3 tools/verify-cache/verify.py
    python3 tools/verify-cache/verify.py --force
    python3 tools/verify-cache/verify.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_PATH = VAULT_ROOT / "tools" / "verify-cache" / "generated" / "verify-cache.json"

# Контент-слои волта (как в pre-commit hook, расширено до всех контент-директорий).
CONTENT_DIRS = [
    "00-INDEX.md",
    "01-Policies",
    "01-Reference",
    "02-Methods",
    "03-Projects",
    "04-Memory",
    "05-Templates",
    "06-Audits",
    "06-Specs",
    "07-Runbooks",
    "98-Temporary",
    "99-Inbox",
    "99-Inbox.md",
]

# Суффиксы, которые участвуют в tree-hash и разрешении викилинков.
LINK_SUFFIXES = [".md", ".json", ".jsonc", ".js", ".sh"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def collect_files() -> list[Path]:
    """Все (не-скрытые) файлы контент-слоёв с расширением из LINK_SUFFIXES."""
    files: list[Path] = []
    for rel in CONTENT_DIRS:
        p = VAULT_ROOT / rel
        if not p.exists():
            continue
        if p.is_file():
            if p.suffix in LINK_SUFFIXES:
                files.append(p)
            continue
        for sub in sorted(p.rglob("*")):
            if sub.is_file() and sub.suffix in LINK_SUFFIXES:
                # пропускаем generated/ и node_modules и скрытые
                parts = sub.parts
                if any(part.startswith(".") or part in ("node_modules", "generated", "__pycache__")
                       for part in parts[len(VAULT_ROOT.parts):]):
                    continue
                files.append(sub)
    return sorted(set(files))


def tree_hash() -> str:
    files = collect_files()
    entries = []
    for f in files:
        try:
            rel = f.relative_to(VAULT_ROOT)
            entries.append(f"{rel}:{sha256_file(f)}")
        except OSError:
            continue
    return hashlib.sha256("\n".join(sorted(entries)).encode("utf-8")).hexdigest()


def check_empty_files() -> list[str]:
    """Пустые .md-файлы в контент-слоях (0 байт)."""
    problems: list[str] = []
    for f in collect_files():
        if f.suffix != ".md":
            continue
        if f.stat().st_size == 0:
            problems.append(f"пустой файл: {f.relative_to(VAULT_ROOT)}")
    return sorted(problems)


def _resolve_wikilink(target: str) -> bool:
    """Разрешить цель [[target]] в существующий файл (логика как pre-commit)."""
    if target == "...":  # placeholder — пропустить, не битый
        return True
    if "#" in target:  # anchor-ссылка — пропустить
        return True
    target = target.rstrip("\\")

    # прямой файл "как набрано" (пустой суффикс) или с суффиксом
    for ext in [""] + LINK_SUFFIXES:
        p = VAULT_ROOT / f"{target}{ext}"
        if p.is_file():
            return True

    # поиск в контент-каталогах + .opencode (как pre-commit hook)
    search_dirs = [""] + [f"{c}/" for c in CONTENT_DIRS if not c.endswith(".md")]
    search_dirs += [".opencode/agent/", ".opencode/command/"]
    for d in search_dirs:
        for ext in [""] + LINK_SUFFIXES:
            p = VAULT_ROOT / f"{d}{target}{ext}"
            if p.is_file():
                return True
    return False


WIKILINK_RE = re.compile(r"\[\[([^\]|]+)")


def strip_code_spans(text: str) -> str:
    """Замаскировать содержимое инлайн-кода (``...``) и fenced-блоков (```...```),
    чтобы литеры вида `[[wikilinks]]` внутри кода не считались ссылками."""
    # fenced code blocks
    lines = text.split("\n")
    in_fence = False
    out: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        # inline code spans (``...``), сохраняем текст вне них
        out.append(re.sub(r"`[^`\n]*`", " ", line))
    return "\n".join(out)


def check_wikilinks() -> list[str]:
    """Битые [[wikilink]] по всем .md-файлам (литеры в code-span игнорируются)."""
    problems: list[str] = []
    seen: dict[str, bool] = {}
    for f in collect_files():
        if f.suffix != ".md":
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        text = strip_code_spans(text)
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip()
            if target in seen:
                good = seen[target]
            else:
                good = _resolve_wikilink(target)
                seen[target] = good
            if not good:
                problems.append(f"битый викилинк: [[{target}]] (в {f.relative_to(VAULT_ROOT)})")
    return sorted(set(problems))


def run_checks() -> dict:
    return {
        "empty_files": check_empty_files(),
        "broken_wikilinks": check_wikilinks(),
    }


def build_verdict(force: bool = False) -> dict:
    current_tree = tree_hash()

    # есть ли валидный кэш под этот tree-hash
    if not force and CACHE_PATH.exists():
        try:
            cached = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            if (cached.get("meta", {}).get("tree_hash") == current_tree
                    and "empty_files" in cached and "broken_wikilinks" in cached):
                return {
                    "meta": {
                        "schema": "verify-cache/1.0",
                        "tree_hash": current_tree,
                        "from_cache": True,
                        "deterministic": True,
                    },
                    "empty_files": cached["empty_files"],
                    "broken_wikilinks": cached["broken_wikilinks"],
                }
        except (OSError, json.JSONDecodeError):
            pass  # повреждённый кэш — пересчитываем

    problems = run_checks()
    verdict = {
        "meta": {
            "schema": "verify-cache/1.0",
            "tree_hash": current_tree,
            "from_cache": False,
            "deterministic": True,
        },
        "empty_files": problems["empty_files"],
        "broken_wikilinks": problems["broken_wikilinks"],
    }

    # сохранить кэш
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(verdict, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="Детерминированные гейты волта с tree-hash кэшем")
    parser.add_argument("--force", action="store_true", help="игнорировать кэш, пересчитать")
    parser.add_argument("--json", action="store_true", help="вывод вердикта как JSON")
    args = parser.parse_args()

    try:
        verdict = build_verdict(force=args.force)
    except OSError as e:
        print(f"verify: ошибка ввода: {e}", file=sys.stderr)
        return 2

    empty = verdict["empty_files"]
    broken = verdict["broken_wikilinks"]
    ok = not empty and not broken

    if args.json:
        verdict["meta"]["ok"] = ok
        print(json.dumps(verdict, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        src = "кэш" if verdict["meta"]["from_cache"] else "пересчёт"
        print(f"verify: tree {verdict['meta']['tree_hash'][:12]} ({src})")
        if ok:
            print("✅ все гейты прошли")
        else:
            for p in empty:
                print(f"❌ {p}")
            for p in broken:
                print(f"❌ {p}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())