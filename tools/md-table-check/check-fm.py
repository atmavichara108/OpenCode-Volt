#!/usr/bin/env python3
"""Дешёвая валидация YAML-шапок (frontmatter) markdown: значения со
«: » или «#» без кавычек и строки без двоеточия ломают YAML — Obsidian
красит такое в свойствах. Выход 0/1. Использование: check-fm.py файл..."""
import sys

def extract(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    return None if end == -1 else text[4:end]

def check(path):
    text = open(path, encoding="utf-8").read()
    fm = extract(text)
    if fm is None:
        return 0
    bad = 0
    for i, line in enumerate(fm.splitlines(), 2):
        s = line.strip()
        if not s or s.startswith(("#", "- ", "  ")) or s == "---":
            continue
        if ":" not in s:
            print(f"{path}:{i}: строка frontmatter без двоеточия: {s[:50]}")
            bad += 1
            continue
        val = s.split(":", 1)[1].strip()
        if (": " in val or val.endswith(":")) and not val.startswith(('"', "'", "[", "{", "|", ">")):
            print(f"{path}:{i}: значение со «: » без кавычек: {val[:50]}")
            bad += 1
        elif "#" in val and not val.startswith(('"', "'")):
            print(f"{path}:{i}: «#» в значении без кавычек: {val[:50]}")
            bad += 1
    return bad

if __name__ == "__main__":
    total = sum(check(p) for p in sys.argv[1:])
    print(f"дефектов шапок: {total}")
    sys.exit(1 if total else 0)
