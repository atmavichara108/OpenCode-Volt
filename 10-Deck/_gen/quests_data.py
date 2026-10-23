#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deck v4 — квесты как данные, а не как нарисованный холст (ref: deck-rethink).

ПОЧЕМУ ПЕРЕПИСАНО: владелец 2026-10-23 не принял Deck с "макаронами из
канвасов" — 30+ статических canvas, ручное точечное описание, мгновенное
устаревание (слова владельца, basis: quoted). Новый принцип: **данные живут
в frontmatter, представление — Obsidian Bases (живое, само обновляется)**.
Canvas остаётся только тонким скелетом навигации (5-7 узлов-ссылок).

Что делает эта команда:
  1. 11-Quests/Q-NNN-<slug>.md — по одному файлу на квест, с frontmatter
     (id/тип/имя/статус/владелец/предусловие/открывает/parent + DoD/награда).
     Существующие файлы НЕ перезаписываются: тело и DoD ведёт исполнитель,
     а поля статуса/владельца/предусловия синхронизируются из реестра ЦУ.
  2. Отчёт, какие файлы созданы/обновлены (без шума по неизменённым).

Пересборка: python3 10-Deck/_gen/quests_data.py  (из корня волта)
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
QD = ROOT / "11-Quests"
DAY = "2026-10-23"

STATUSES = ("active", "ready", "locked", "parked", "done")

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def parse_registry():
    """Читает таблицу SSOT 11-Quests/quests.md (ведёт ЦУ)."""
    text = (QD / "quests.md").read_text(encoding="utf-8")
    out = []
    pattern = (
        r"^\|\s*\*{0,2}(Q-\d+(?:\.\d+)?)\*{0,2}\s*\|\s*(.+?)\s*\|\s*"
        r"(active|ready|locked|parked|done)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*$"
    )
    for line in text.splitlines():
        m = re.match(pattern, line)
        if m:
            qid, name, status, owner, pre = m.groups()
            out.append(
                dict(id=qid, name=name, status=status, owner=owner, pre=pre)
            )
    return out


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
    return (s[:40].rstrip("-") or "quest")


def quest_ids_in(text: str):
    return re.findall(r"Q-\d+(?:\.\d+)?", text or "")


def sync_frontmatter(path: pathlib.Path, q, opens):
    """Обновляет только управляемые поля; тело и DoD не трогает."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    head = text[4:end]
    tail = text[end:]
    managed = {
        "статус": q["status"],
        "владелец": q["owner"],
        "предусловие": "[" + ", ".join(quest_ids_in(q["pre"])) + "]",
        "открывает": "[" + ", ".join(opens) + "]",
    }
    lines = head.splitlines()
    seen = set()
    for i, line in enumerate(lines):
        m = re.match(r"^([A-Za-zа-яёА-ЯЁ_]+):", line)
        if not m:
            continue
        key = m.group(1)
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


def build_body(q, parent):
    return f"""# {q['id']} — {q['name']}

**Статус:** {q['status']} · **Владелец:** {q['owner']}

## Цель
(исполнитель заполняет; без DoD квест не открывается — 11-Quests/00-README.md)

## Предусловие
{q['pre'] or '—'}

## Шаги
- [ ] …

## DoD
- [ ] …

## Evidence
(закрытие — только с evidence)
"""


def main():
    quests = parse_registry()
    if not quests:
        raise SystemExit("quests.md не распарсен — реестр пуст или формат таблицы сломан")

    created, updated = [], []
    for q in quests:
        contains_parent = "." in q["id"]
        parent = q["id"].split(".")[0] if contains_parent else None
        opens = [
            o["id"]
            for o in quests
            if q["id"] in quest_ids_in(o["pre"]) and o["id"] != q["id"]
        ]
        fname = f"{q['id']}-{make_slug(q['name'])}.md"
        path = QD / fname
        if path.exists():
            if sync_frontmatter(path, q, opens):
                updated.append(fname)
            continue
        fm = (
            "---\n"
            "type: quest\n"
            f"id: {q['id']}\n"
            "тип: квест\n"
            f'имя: "{q["name"]}"\n'
            f"статус: {q['status']}\n"
            f"владелец: {q['owner']}\n"
            f"предусловие: [{', '.join(quest_ids_in(q['pre']))}]\n"
            f"открывает: [{', '.join(opens)}]\n"
            f"parent: {parent or ''}\n"
            "DoD: []\n"
            "награда: []\n"
            f"timestamp: {DAY}\n"
            "---\n"
        )
        path.write_text(fm + build_body(q, parent), encoding="utf-8")
        created.append(fname)

    print(f"файлов квестов создано: {len(created)}, обновлено полей: {len(updated)}")
    for c in created:
        print("  +", c)
    for u in updated:
        print("  ~", u)


if __name__ == "__main__":
    main()