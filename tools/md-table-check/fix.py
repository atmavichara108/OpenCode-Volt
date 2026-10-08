#!/usr/bin/env python3
"""Чинит битые markdown-таблицы: после строки-заголовка вставляет
разделитель |---| с числом колонок по заголовку. Dry-run по умолчанию,
--apply для записи. Эвристика блоков зеркалит check.py."""
import sys

def is_row(s: str) -> bool:
    return s.startswith("|") and s.endswith("|") and "|" in s[1:]

def is_sep(s: str) -> bool:
    return bool(s) and all(c in "-: |" for c in s)

def sep_for(header: str) -> str:
    cells = header.strip().strip("|").split("|")
    return "|" + "|".join(" --- " for _ in cells) + "|"

def fix(path: str, apply: bool) -> int:
    lines = open(path, encoding="utf-8").readlines()
    out, fixed = [], 0
    in_block = False
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if not in_block:
            if is_row(s):
                in_block = True
                header = raw
            out.append(raw)
            continue
        # внутри блока: ждём разделитель второй строкой
        if is_sep(s):
            in_block = False
            out.append(raw)
            continue
        if is_row(s):
            out.append(sep_for(header) + "\n")
            fixed += 1
            print(f"{path}: разделитель вставлен после строки {n-1}")
            in_block = False
        else:
            in_block = False
        out.append(raw)
    if apply and fixed:
        open(path, "w", encoding="utf-8").writelines(out)
    return fixed

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    total = sum(fix(p, apply) for p in args)
    print(f"{'ПРИМЕНЕНО' if apply else 'DRY-RUN'}: таблиц починено = {total}")
