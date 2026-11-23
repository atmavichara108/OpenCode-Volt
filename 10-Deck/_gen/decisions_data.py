#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deck v4 — решения как данные, а не как нарисованный холст.

Принцип (как у квестов): данные живут в реестре
`01-Policies/decisions-registry.md` (ведёт ЦУ), представление — Obsidian Bases
(живое, само обновляется). Canvas остаётся только скелетом навигации.

Что делает эта команда:
  1. Парсит `01-Policies/decisions-registry.md` — по одной строке на решение.
     Два формата:
       - со звёздами: `- **Р-NNN (дата)** — **Имя.** Текст... Статус: X.`
       - без звёзд:   `- **Р-NNN (дата)** — Имя. Текст... Статус: X.`
  2. Создаёт `10-Deck/decisions/R-NNN-<slug>.md` — по одному файлу на решение,
     с frontmatter (id, тип, имя, реестр, статус, ведомство, слово, проценанс,
     timestamp). Существующие файлы НЕ перезаписываются: тело и DoD ведёт
     исполнитель/ЦУ, а управляемые поля синхронизируются из реестра.
  3. Отчёт: создано/обновлено файлов.

Пересборка: python3 10-Deck/_gen/decisions_data.py  (из корня волта)
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "01-Policies" / "decisions-registry.md"
DEC_DIR = ROOT / "10-Deck" / "decisions"
DAY = "2026-11-23"

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

LINE_RE_STARS = re.compile(
    r"^\- \*\*(Р-\d+)\s*\(([^)]+)\)\*\*\s*—\s*\*\*(.*?)\*\*\.\s+(.*)$",
    re.DOTALL,
)
LINE_RE_PLAIN = re.compile(
    r"^\- \*\*(Р-\d+)\s*\(([^)]+)\)\*\*\s*—\s*(.*?)\.\s+(.*)$",
    re.DOTALL,
)


def make_slug(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    s = re.sub(r"-+", "-", "".join(out)).strip("-")
    return (s[:50].rstrip("-") or "reshenie")


def parse_registry():
    """Читает реестр решений — по одной строке на решение.

    Два формата строки:
      - с звёздами: `- **Р-NNN (дата)** — **Имя.** Текст... Статус: X.`
      - без звёзд:  `- **Р-NNN (дата)** — Имя. Текст... Статус: X.`
    """
    text = REGISTRY.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        m = LINE_RE_STARS.match(line.strip()) or LINE_RE_PLAIN.match(line.strip())
        if not m:
            continue
        rid, rdate, name, rest = m.groups()
        name = name.strip().strip("*").strip()
        prov_match = re.search(r"Провенанс:\s*(.*?)(?=\s+Статус:|\s*$)", rest)
        status_match = re.search(r"Статус:\s*(.+?)\.?\s*$", rest)
        out.append(
            dict(
                id=rid,
                date=rdate,
                name=name,
                rest=rest.strip(),
                provenance=prov_match.group(1).strip() if prov_match else "",
                status=status_match.group(1).strip() if status_match else "",
            )
        )
    return out


def frontmatter(d):
    return (
        "---\n"
        "type: decision\n"
        "тип: решение\n"
        f"id: {d['id']}\n"
        f'имя: "{d["name"]}"\n'
        f"реестр: 01-Policies/decisions-registry.md\n"
        f"статус: {d['status']}\n"
        f"отметка_слова: {d['date']}\n"
        f"ведомство: ЦУ\n"
        f"проценанс: {d['provenance']}\n"
        f"timestamp: {DAY}\n"
        "---\n"
    )


def body(d):
    return f"""# {d['id']} — {d['name']}

## Статус
{d['status']}

## Суть решения
{_summary(d['rest'])}

## Провенанс
{d['provenance'] or '—'}

## Источники
- `01-Policies/decisions-registry.md` — строка реестра

## Ждёт слова владельца
[ ] определить вручную (статус реестра: {d['status']})

---

*Авто-сгенерировано из `01-Policies/decisions-registry.md` командой
`10-Deck/_gen/decisions_data.py`. Тело и DoD ведёт исполнитель/ЦУ вручную;
управляемые поля синхронизируются при пересборке.*
"""


def _summary(rest: str) -> str:
    """Короткая суть — до слова 'Провенанс:'."""
    cut = rest.find("Провенанс:")
    if cut == -1:
        return rest.strip()
    return rest[:cut].strip()


def sync_frontmatter(path: pathlib.Path, d):
    """Обновляет только управляемые поля frontmatter; тело не трогает."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    head = text[4:end]
    tail = text[end:]
    managed = {
        "статус": d["status"],
        "отметка_слова": d["date"],
        "ведомство": "ЦУ",
        "проценанс": d["provenance"],
    }
    lines = head.splitlines()
    seen = set()
    for i, line in enumerate(lines):
        mm = re.match(r"^([A-Za-zа-яёА-ЯЁ_]+):", line)
        if not mm:
            continue
        key = mm.group(1)
        if key in managed:
            lines[i] = f"{key}: {managed[key]}"
            seen.add(key)
    for key, val in managed.items():
        if key not in seen:
            lines.append(f"{key}: {val}")
    new = "---\n" + "\n".join(lines).rstrip("\n") + tail
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    decisions = parse_registry()
    if not decisions:
        raise SystemExit(
            "Реестр решений не распарсен — формат строк сломан "
            f"({REGISTRY})"
        )

    DEC_DIR.mkdir(parents=True, exist_ok=True)
    created, updated = [], []
    for d in decisions:
        fname = f"{d['id']}-{make_slug(d['name'])}.md"
        path = DEC_DIR / fname
        if path.exists():
            if sync_frontmatter(path, d):
                updated.append(fname)
            continue
        path.write_text(frontmatter(d) + body(d), encoding="utf-8")
        created.append(fname)

    print(f"решений в реестре: {len(decisions)}")
    print(f"файлов решений создано: {len(created)}, обновлено полей: {len(updated)}")
    for c in created:
        print("  +", c)
    for u in updated:
        print("  ~", u)


if __name__ == "__main__":
    main()
