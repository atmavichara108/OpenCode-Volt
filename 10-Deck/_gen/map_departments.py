#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Карта связей ведомств Корабля (Deck v4, ref: uas-onboard-20261023).

Канон представления (ИЦ, ref: deck-rethink, ADR-028):
- canvas = карта связей 1-го уровня; вершины — узлы-заметки;
- рёбра — только реально существующая отчётность/вхождение;
- никаких атрибутов и таблиц внутри (данные — в frontmatter/Bases).
Тест переноса: убери всё текстовое — граф подчинения остаётся узнаваем.

Источник адресов/состава: 04-Memory/peer-registry.md (SSOT адресации)
и письма ЦУ (uas-onboard, Р-023: УАС в строю 10-23, отчёты — в ЦУ;
спец-отдел «Ротатор моделей» внутри УАС).
Пересборка: python3 10-Deck/_gen/map_departments.py
"""

import json
import pathlib
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DD = ROOT / "10-Deck"


def nid(s):
    return f"d{zlib.crc32(s.encode()) & 0xffffff:06x}"


def text(t, x, y, w=300, h=110, color=None):
    n = {"id": nid(t), "type": "text", "text": t, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n


def file(f, x, y, w=380, h=260, color=None):
    n = {"id": nid(f), "type": "file", "file": f, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n


def edge(a, b, label):
    return {"id": nid(a + b + label), "fromNode": nid(a), "toNode": nid(b), "label": label}


# узел-якорь по имени текстового узла (текст = уникальный ключ)
DEPARTMENTS = [
    ("Центральный Узел (ЦУ)\nкоординация — все линии стекаются сюда", "4"),
    ("Инженерный центр (ИЦ)\nразработка, dotfiles", None),
    ("Мастерская Багфикс\nремонт, INC", None),
    ("Абилити Лаб (Dr.Who)\nлаборатория способностей", None),
    ("ИПТ\nисследования", None),
    ("ХПФ\nфилософия/структуры", None),
    ("Control-top\nSSA-поток", None),
    ("ДВ-Хаб\nкандидат (не калибровать)", None),
    ("Служитель Обсидиан\nUI|UX ecosys (Р-021)", None),
    ("УАС\nкуратор агентского контура\nв строю 10-23 (Р-023)", "4"),
]

nodes = [
    text("# Карта ведомств\n\nУзел = ведомство, ребро = отчётность/вхождение.\nИсточники: peer-registry + Р-023.", -260, -640, 760, 120, "1"),
]
edges = []

coords = [(-620, -420), (-980, -160), (-980, 40), (-980, 240), (-620, -160), (-620, 40), (-620, 240), (-260, -160), (-260, 40), (100, -160)]
for (label, color), (x, y) in zip(DEPARTMENTS, coords):
    nodes.append(text(label, x, y, 320, 130, color))

# file-узлы на существующие карточки УАС (переход кликом)
nodes.append(file("03-Projects/uas.md", 100, 60, 400, 280, "6"))
nodes.append(file("03-Projects/uas-special-rotator.md", 540, 60, 400, 280, "6"))

uas_label = DEPARTMENTS[9][0]
for label, _ in DEPARTMENTS[1:]:
    if label != uas_label:
        edges.append(edge(label, DEPARTMENTS[0][0], "отчитывается"))
edges.append(edge(uas_label, DEPARTMENTS[0][0], "отчёты в ЦУ (Р-023)"))
edges.append(edge("03-Projects/uas-special-rotator.md", uas_label, "отдел внутри УАС"))
edges.append(edge("03-Projects/uas.md", uas_label, "карточка"))

(DD / "map-departments.canvas").write_text(
    json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")
print(f"map-departments.canvas: {len(nodes)} узлов, {len(edges)} рёбер")