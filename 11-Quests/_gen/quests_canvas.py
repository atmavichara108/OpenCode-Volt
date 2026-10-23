#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quests v0 — генератор ризомы квестов (Служитель Обсидиан, ref: quests-v0).

Читает SSOT-реестр 11-Quests/quests.md (таблица ЦУ) и строит одной командой:
  1. 11-Quests/quests.canvas        — ризома главных квестов (+ вложенные sub-карты)
  2. 11-Quests/quests-Q001.canvas   — подквесты Q-001 (предусловие→открывает)
  3. 11-Quests/quests-Q002.canvas   — подквесты Q-002
  4. 11-Quests/quests-index.md      — триггеры «чем заняться сейчас»

Принципы (11-Quests/00-README.md): квест=узел; рёбра — только реальные
зависимости из поля «Предусловие»; ssot:false (источник — quests.md).
Неквестовые предусловия (слово владельца, внешнее) — пометка на узле, не ребро.
Пересборка: python3 11-Quests/_gen/quests_canvas.py из корня волта.
"""
import json
import pathlib
import re
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
QDIR = ROOT / "11-Quests"
DAY = "2026-10-23"

COLORS = {"active": "4", "ready": "3", "locked": "2", "parked": None, "done": "4"}

def sid(s):
    return f"{zlib.crc32(s.encode()) & 0xffffff:06x}"

def tnode(nid, text, x, y, w=380, h=150, color=None):
    n = {"id": nid, "type": "text", "text": text, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def fnode(nid, file, x, y, w=460, h=320, color=None):
    n = {"id": nid, "type": "file", "file": file, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def edge(eid, a, b, **kw):
    return {"id": eid, "fromNode": a, "toNode": b, **kw}

def write_canvas(name, nodes, edges):
    (QDIR / name).write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"✔ {name}: {len(nodes)} узлов, {len(edges)} рёбер")

# ── парсер реестра (SSOT: 11-Quests/quests.md) ─────────────────────────────
def parse_registry():
    text = (QDIR / "quests.md").read_text(encoding="utf-8")
    quests = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*\*{0,2}(Q-\d+(?:\.\d+)?)\*{0,2}\s*\|\s*(.+?)\s*\|\s*"
                     r"(active|ready|locked|parked|done)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*$", line)
        if m:
            qid, name, status, owner, pre = m.groups()
            quests.append({"id": qid, "name": name, "status": status,
                           "owner": owner, "pre": pre})
    return quests

def quest_edges(q, all_quests):
    """Рёбра из поля Предусловие: только ссылки на существующие квесты."""
    deps = re.findall(r"Q-\d+(?:\.\d+)?", q["pre"] or "")
    out = []
    for d in deps:
        if any(x["id"] == d for x in all_quests):
            out.append(d)  # предусловие d → открывает q
    return sorted(set(out))

def waits_note(q):
    """Неквестовое предусловие → пометка «ждёт» на узле."""
    pre = (q["pre"] or "").strip()
    if not pre or pre == "—":
        return ""
    if quest_edges(q, [q]):
        # кроме квестовых зависимостей может быть и неквестовое условие
        rest = re.sub(r"Q-\d+(?:\.\d+)?", "", pre).strip(" ,;/+")
        return f"\nждёт: {rest}" if rest else ""
    return f"\nждёт: {pre}"

# ── главная ризома ──────────────────────────────────────────────────────────
def main_canvas(quests):
    main = [q for q in quests if re.fullmatch(r"Q-\d+", q["id"])]
    subs = [q for q in quests if "." in q["id"]]
    nodes = [tnode("q-root", f"# 🗺️ РИЗОМА КВЕТОВ (v0)\nУзел=квест, ребро=зависимость (предусловие→открывает).\nSSOT: 11-Quests/quests.md · ЦУ · {DAY}. Грубо сейчас, красиво потом (слово владельца).",
                   -340, -560, 800, 140, "4")]
    edges = []
    x = -340
    by_id = {q["id"]: q for q in quests}
    sub_groups = {}
    for q in subs:
        sub_groups.setdefault(q["id"].split(".")[0], []).append(q)
    for q in main:
        nid = f"q{sid(q['id'])}"
        nodes.append(tnode(nid, f"## {q['id']} · {q['status'].upper()}\n**{q['name']}**\nвладелец: {q['owner']}{waits_note(q)}",
                           x, -340, 400, 190, COLORS.get(q["status"])))
        edges.append(edge(f"er{sid(q['id'])}", "q-root", nid))
        # вложенная карта подквестов
        if q["id"] in sub_groups:
            subf = f"quests-{q['id']}.canvas"
            snid = f"sub{sid(q['id'])}"
            nodes.append(fnode(snid, f"11-Quests/{subf}", x, -100, 420, 300, "6"))
            edges.append(edge(f"es{sid(q['id'])}", nid, snid, label="открывает", fromEnd="arrow"))
        x += 460
    write_canvas("quests.canvas", nodes, edges)

# ── sub-карты подквестов ────────────────────────────────────────────────────
def sub_canvas(parent_id, parent, subs):
    nodes = [tnode(f"sq{sid(parent_id)}", f"# 🧩 {parent_id} · подквесты\n**{parent['name']}**\nстатус родителя: {parent['status']} · {DAY}",
                   -320, -480, 700, 130, "4")]
    edges = []
    x = -320
    for q in sorted(subs, key=lambda z: z["id"]):
        nid = f"q{sid(q['id'])}"
        nodes.append(tnode(nid, f"## {q['id']} · {q['status'].upper()}\n**{q['name']}**\nвладелец: {q['owner']}{waits_note(q)}",
                           x, -280, 360, 180, COLORS.get(q["status"])))
        edges.append(edge(f"er{sid(q['id'])}", f"sq{sid(parent_id)}", nid, label="открывает", fromEnd="arrow"))
        x += 400
    # зависимости между подквестами (предусловие → открывает)
    ids = {q["id"] for q in subs}
    for q in subs:
        for d in quest_edges(q, subs):
            if d != q["id"] and d in ids:
                edges.append(edge(f"ed{sid(d + '->' + q['id'])}", f"q{sid(d)}", f"q{sid(q['id'])}",
                                  label="предусловие", fromEnd="arrow"))
    write_canvas(f"quests-{parent_id}.canvas", nodes, edges)

# ── quests-index.md (триггеры «чем заняться сейчас») ────────────────────────
def index_md(quests):
    act = [q for q in quests if q["status"] == "active"]
    ready = [q for q in quests if q["status"] == "ready"]
    locked = [q for q in quests if q["status"] == "locked"]
    parked = [q for q in quests if q["status"] == "parked"]
    lines = [f"""---
type: Index
title: Квесты — чем заняться сейчас
status: активен (генерируется, руками не править)
timestamp: {DAY}
---

# Чем заняться сейчас (триггеры)

> Генератор: `python3 11-Quests/_gen/quests_canvas.py` (источник — quests.md, ЦУ).
> Одна строка = один квест. Грубо сейчас, красиво потом.

## 🔥 Сейчас (active)"""]
    for q in act:
        lines.append(f"- **{q['id']}** {q['name']} — {q['owner']}{waits_note(q)}")
    if not act:
        lines.append("- (пусто)")
    lines.append("\n## ▶️ Готово к старту (ready)")
    for q in ready:
        pre = q["pre"].strip()
        trig = f" · триггер: {pre}" if pre and pre != "—" else ""
        lines.append(f"- **{q['id']}** {q['name']} — {q['owner']}{trig}")
    if not ready:
        lines.append("- (пусто)")
    lines.append("\n## 🔒 Ждут (locked)")
    for q in locked:
        lines.append(f"- **{q['id']}** {q['name']} — ждёт: {q['pre']}")
    lines.append("\n## 🅿️ Отложено (parked)")
    for q in parked:
        lines.append(f"- **{q['id']}** {q['name']} — {q['pre']}")
    (QDIR / "quests-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("✔ quests-index.md")

if __name__ == "__main__":
    quests = parse_registry()
    if not quests:
        raise SystemExit("реестр пуст — quests.md не распарсен")
    main_canvas(quests)
    subs_by_parent = {}
    for q in quests:
        if "." in q["id"]:
            subs_by_parent.setdefault(q["id"].split(".")[0], []).append(q)
    by_id = {q["id"]: q for q in quests}
    for pid, subs in sorted(subs_by_parent.items()):
        sub_canvas(pid, by_id[pid], subs)
    index_md(quests)
    print(f"Quests v0 собран ({len(quests)} квестов).")
