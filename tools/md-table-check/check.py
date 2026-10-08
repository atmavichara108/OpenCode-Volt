#!/usr/bin/env python3
"""Валидатор markdown-таблиц (дешёвый, без LLM). Классы дефектов:
D1: блок строк |...| без строки-разделителя второй строкой;
D2: строка таблицы с числом колонок != заголовку таблицы;
D4: сырая вики-ссылка [[файл|псевдоним]] в строке таблицы — пайп рвёт
    ячейку (Obsidian); нужен экранированный вариант с обратным слэшем перед пайпом;
D3: осиротевшее продолжение — после конца таблицы идёт короткая
    вставка (менее 2 пустых строк) и снова | -строки с тем же числом
    колонок без своего заголовка и разделителя: Obsidian рендерит их текстом.
Выход 0 — чисто, 1 — есть дефекты. Использование: check.py файл..."""
import re
import sys

WIKILINK = re.compile(r"\[\[[^\]]+\]\]")

def raw_pipe_links(s):
    # вики-ссылки с пайпом, не экранированным обратным слэшем
    return [m.group(0) for m in WIKILINK.finditer(s)
            if re.search(r"(?<!\\)\|", m.group(0))]

def unesc(s):
    # экранированный \| внутри вики-ссылки — не разделитель колонок
    return s.replace("\\|", "")

def is_row(s):
    s = unesc(s)
    return s.startswith("|") and s.endswith("|") and "|" in s[1:]

def is_sep(s):
    return bool(s) and all(c in "-: |" for c in s)

def ncols(s):
    return unesc(s).strip().strip("|").count("|") + 1

def check(path):
    lines = [l.strip() for l in open(path, encoding="utf-8")]
    bad = 0
    tables = []
    i, n = 0, len(lines)
    for k, line in enumerate(lines):
        if line.startswith("|"):
            for link in raw_pipe_links(line):
                print(f"{path}:{k+1}: D4 сырая вики-ссылка в таблице: {link[:50]} — экранируй пайп")
                bad += 1
    while i < n:
        if is_row(lines[i]) and i + 1 < n and is_sep(lines[i + 1]):
            start, cols, j = i, ncols(lines[i]), i + 2
            while j < n and is_row(lines[j]):
                if ncols(lines[j]) != cols:
                    print(f"{path}:{j+1}: D2 колонки {ncols(lines[j])} != {cols} — {lines[j][:40]}")
                    bad += 1
                j += 1
            tables.append((start, cols, j - 1))
            i = j
        elif is_row(lines[i]):
            j = i
            while j < n and is_row(lines[j]):
                j += 1
            if j - i >= 2:
                print(f"{path}:{i+1}: D1 блок таблиц без разделителя ({j-i} строк)")
                bad += 1
            i = j
        else:
            i += 1
    for start, cols, end in tables:
        k, gap = end + 1, 0
        orphan_zone = True
        while k < n and not is_row(lines[k]):
            if lines[k]:
                gap += 1
                if lines[k].startswith("#"):
                    orphan_zone = False
                    break
            if gap >= 2:
                orphan_zone = False
                break
            k += 1
        if orphan_zone and k < n and is_row(lines[k]) and not (k + 1 < n and is_sep(lines[k + 1])) and ncols(lines[k]) == cols:
            print(f"{path}:{k+1}: D3 осиротевшее продолжение таблицы со строки {start+1} (колонок {cols})")
            bad += 1
    return bad

if __name__ == "__main__":
    total = sum(check(p) for p in sys.argv[1:])
    print(f"дефектов: {total}")
    sys.exit(1 if total else 0)
