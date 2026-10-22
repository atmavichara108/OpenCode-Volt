#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deck v2 — генератор вложенных canvas-карт (Служитель Обсидиан, ref: deck-v2).

Иерархия (слово владельца 2026-10-22, basis: quoted):
  L0 Корабль (галактика) → L1 грани = ПРОЕКТЫ → L2 ВЕДОМСТВА с гранями
  (подведомства/навыки/журналы/агенты) → L3 пути/роадмапы/артефакты-производные.

Принципы: вложенность точная — только реально существующие файлы и ссылки
файл:строка; ssot:false; узел type=file с .canvas = вложенная карта
(Obsidian рендерит её внутри). ID стабильны (crc32) — дерево не «прыгает».
Пересборка: python3 10-Deck/_gen/deck_levels.py из корня волта.
"""
import json
import pathlib
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]  # корень волта
D = ROOT / "10-Deck"
DAY = "2026-10-22"

def sid(s: str) -> str:
    """Стабильный короткий id из строки."""
    return f"{zlib.crc32(s.encode()) & 0xffffff:06x}"

def W(rel: str) -> bool:
    return (ROOT / rel).is_file() or (ROOT / rel).is_dir()

def tnode(nid, text, x, y, w=380, h=160, color=None):
    n = {"id": nid, "type": "text", "text": text, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def fnode(nid, file, x, y, w=380, h=260, color=None):
    n = {"id": nid, "type": "file", "file": file, "x": x, "y": y, "width": w, "height": h}
    if color:
        n["color"] = color
    return n

def edge(eid, a, b, **kw):
    return {"id": eid, "fromNode": a, "toNode": b, **kw}

def write_canvas(name, nodes, edges):
    (D / name).write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"✔ {name}: {len(nodes)} узлов, {len(edges)} рёбер")

# ─── ФАКТЫ (файл:строка из реестров) ────────────────────────────────────────
MIN = {
    "ic":      ("ИЦ — Инженерный центр", "sysop · dotfiles · инженерный центр", "peer-registry.md:15"),
    "master":  ("Мастерская Багфикс", "sysop · багфикс-цех", "peer-registry.md:16"),
    "lab":     ("Абилити лаб", "Dr.Who · ~/Projects/ability-lab · Р-007", "peer-registry.md:17"),
    "ippt":    ("ИПТ", "librarian · исследования", "peer-registry.md:18"),
    "hpf":     ("ХПФ", "librarian · практическая философия / гейты", "peer-registry.md:19"),
    "tsu":     ("ЦУ — Центральный Узел", "*** · координация / реестры", "peer-registry.md:20"),
    "ct":      ("Control-top", "top · SSA/control · владелец-панель", "peer-registry.md:21"),
    "dvhub":   ("ДВ-Хаб", "временный шлюз · путь к dev-статусу", "peer-registry.md:22"),
    "servant": ("Служитель Обсидиан", "obsidian-servant · 10-Deck · canvas-карты · Пип-Бой (Deck = прототип)",
                "peer-registry.md:23"),
}

FACETS = {  # (метка, вид, источник файл:строка)
    "ic": [
        ("Отдел Приложений", "подведомство", "01-Policies/organ-structure…:32"),
        ("Отдел Движков", "подведомство", "01-Policies/organ-structure… §2"),
        ("Отдел Реверс-Инженерии · навык Панхарвестинг", "подведомство+навык", "01-Policies/organ-structure… §3"),
        ("dotfiles: 15 агентов (sysop+субагенты)", "агенты", "~/dotfiles/AGENTS.md «Роли агентов»"),
    ],
    "master": [
        ("поток flow-defects", "навык", "~/dotfiles/AGENTS.md «Пайплайны»"),
        ("queued-noise-fix — принят", "линия", "04-Memory/session-log/2026-10-20.md:138"),
    ],
    "lab": [
        ("Dr.Who — primary (Р-007)", "агент", "04-Memory/peer-registry.md:17"),
        ("lab-instrument", "субагент", "04-Memory/peer-registry.md:17"),
        ("L9 · итерация 1 ЗАКРЫТА (PASS 6/6)", "линия", "04-Memory/session-log/2026-10-20.md:135"),
        ("⚠️ карточка проекта ability-lab отсутствует в 03-Projects", "дефект-грань", "ls 03-Projects · 2026-10-22"),
    ],
    "ippt": [
        ("исследования · внешние стыки как класс", "навык", "04-Memory/peer-registry.md:18 · 01-Policies/organ-structure…:69"),
        ("методы-дистилляты (исполнение — meta/ИЦ)", "правило", "04-Memory/active-context.md (ИПТ-инцидент)"),
    ],
    "hpf": [
        ("гейт методов (rudrakshas: «соответствует»)", "навык-гейт", "01-Policies/decisions-registry.md:34"),
        ("структурные/философские концепты", "навык", "04-Memory/peer-registry.md:19"),
    ],
    "tsu": [
        ("сверхнавыки tsu-* ×5", "навыки", "~/dotfiles/opencode-global/.config/opencode/skill/"),
        ("Реестр ведомств (адресация)", "реестр", "04-Memory/peer-registry.md"),
        ("Реестр решений (SSOT)", "реестр", "01-Policies/decisions-registry.md"),
        ("журналы session-log", "журнал", "04-Memory/session-log/"),
    ],
    "ct": [
        ("SSA-панель владельца", "грань", "04-Memory/peer-registry.md:21"),
        ("путь работы: ~/Projects/SSA/control", "путь", "04-Memory/peer-registry.md:21"),
    ],
    "dvhub": [
        ("C1/C2 приняты, merge; сверка карточки после", "линия", "04-Memory/session-log/2026-10-20.md:136"),
        ("Р-020 две зоны двух SDK (эпизод T-159 закрыт)", "решение", "01-Policies/decisions-registry.md:37"),
        ("путь к NVIDIA-статусу — ждёт письмо", "линия", "04-Memory/session-log/2026-10-20.md:140"),
    ],
    "servant": [
        ("мостик: карточки решений", "продукт", "10-Deck/decisions-deck.md"),
        ("ризома решений deck.canvas", "продукт", "10-Deck/deck.canvas"),
        ("карты уровней L0–L3 (Deck v2)", "продукт", f"10-Deck/map-L0-ship.canvas · слово владельца {DAY}"),
        ("Пип-Бой-тайлы · Deck = прототип", "сверхзадача", f"слово владельца {DAY} (через ЦУ): «сверхзадача — перманентная модернизация канвасов и создание макета для пипбоя — тайлы»"),
        ("⚠️ последняя живая версия Pip-Boy = v11 (multiplexer: up/open/status/down, rofi, deep-link #models)", "факт-сверка", "07-Runbooks/pipboy-v11-user-guide.md · main · PR#1 7848a46e (10-16)"),
        ("v9 TERRARIUM (b30f239d) — мокап на ветке pipboy-v8-rethink, в main не слиян", "референс эстетики", "06-Specs/Vault/pipboy-v9-terrarium.md · ветка pipboy-v8-rethink"),
    ],
}

ARTS = {  # L3: реальные пути; суффикс " ::вне волта" или " ::ветка" => текстовый узел
    "tsu": ["01-Policies/decisions-registry.md", "04-Memory/peer-registry.md",
            "04-Memory/facts.md", "04-Memory/stream-registry.md",
            "DEVELOPMENT-ROADMAP.md", "04-Memory/route-log/", "01-Policies/"],
    "dvhub": ["03-Projects/dv-hub.md", "~/Projects/dv-hub/ ::вне волта"],
    "servant": ["10-Deck/decisions-deck.md", "10-Deck/deck.canvas", "10-Deck/PIPELINE.md",
                "07-Runbooks/pipboy-v11-user-guide.md",
                "06-Specs/Vault/pipboy-v9-terrarium.md ::ветка pipboy-v8-rethink (b30f239d)"],
}

PROJECTS = [
    ("vault",         "03-Projects/vault.md",         ["tsu", "ippt", "hpf", "dvhub", "servant"]),
    ("dotfiles",      "03-Projects/dotfiles.md",      ["ic", "master"]),
    ("dv-hub",        "03-Projects/dv-hub.md",        ["dvhub"]),
    ("SSA",           "03-Projects/SSA.md",           ["ct"]),
    ("ChaT",          "03-Projects/ChaT.md",          []),
    ("AndroidOS",     "03-Projects/AndroidOS.md",     []),
    ("rudra-ai",      "03-Projects/rudra-ai.md",      []),
    ("rudra-phone",   "03-Projects/rudra-phone.md",   []),
    ("SERPlux",       "03-Projects/SERPlux.md",       []),
    ("seo-outreach",  "03-Projects/seo-outreach.md",  []),
    ("recruiting-hr", "03-Projects/recruiting-hr.md", []),
    ("prod-monitor",  "03-Projects/prod-monitor.md",  []),
]

def l3_canvas(mid):
    name, sub, src = MIN[mid]
    nodes = [tnode(f"l3-{mid}", f"# 📦 L3 · артефакты · {name}\nПути-производные (роадмапы, реестры, спеки). {DAY} · ssot:false",
                   -300, -340, 620, 110, "4")]
    edges, y = [], -160
    for p in ARTS[mid]:
        kind = ""
        if " ::" in p:
            clean, kind = p.split(" ::", 1)
        else:
            clean = p
        nid = f"a{sid(clean)}"
        if not kind and W(clean):
            nodes.append(fnode(nid, clean.rstrip("/"), -300, y, 560, 280, "3"))
            y += 320
        else:
            nodes.append(tnode(nid, f"📁 `{clean}`\n*{kind}*", -300, y, 560, 90, "3"))
            y += 130
        edges.append(edge(f"ea{sid(clean)}", f"l3-{mid}", nid))
    write_canvas(f"map-L3-{mid}.canvas", nodes, edges)

def l2_canvas(mid):
    name, sub, src = MIN[mid]
    nodes = [tnode(f"l2-{mid}", f"# 🏛️ L2 · {name}\n{sub}\nист: {src}", -320, -420, 680, 150, "4")]
    edges, x = [], -320
    for label, kind, s in FACETS[mid]:
        nid = f"f{sid(mid + label)}"
        nodes.append(tnode(nid, f"**{label}**\n*{kind}*\nист: {s}", x, -180, 320, 170, "5"))
        edges.append(edge(f"ef{sid(nid)}", f"l2-{mid}", nid))
        x += 360
    x = -320
    if mid in ARTS:
        nid = f"e3{sid(mid)}"
        nodes.append(fnode(nid, f"10-Deck/map-L3-{mid}.canvas", x, 80, 600, 420, "3"))
        edges.append(edge(f"e3e{sid(mid)}", f"l2-{mid}", nid, label="L3 артефакты"))
        x += 640
    extras = {"servant": [("10-Deck/deck.canvas", "мостик", "1")],
              "tsu":     [("00-WORLD.canvas", "ризома мира", "6")]}.get(mid, [])
    for f, lab, col in extras:
        nid = f"ex{sid(mid + f)}"
        nodes.append(fnode(nid, f, x, 80, 600, 420, col))
        edges.append(edge(f"exe{sid(nid)}", f"l2-{mid}", nid, label=lab, style="dashed"))
        x += 640
    write_canvas(f"map-L2-{mid}.canvas", nodes, edges)

def l1_canvas(proj, card, minis):
    ok_card = W(card)
    nodes = [tnode(f"p{sid(proj)}", f"# 🪐 L1 · грань «{proj}»\nГрань Корабля. Внутри — ведомства-обитатели (L2), у каждого свои грани и артефакты.\nист: {card if ok_card else '⚠️ карточка отсутствует'}",
                   -320, -420, 640, 140, "4")]
    edges, x = [], -320
    if ok_card:
        nid = f"pc{sid(proj)}"
        nodes.append(fnode(nid, card, x, -200, 460, 300, "6"))
        edges.append(edge(f"ep{sid(proj)}", f"p{sid(proj)}", nid, label="карточка проекта"))
        x += 500
    for m in minis:
        nid = f"e{sid(proj + m)}"
        nodes.append(fnode(nid, f"10-Deck/map-L2-{m}.canvas", x, -160, 560, 400, "5"))
        edges.append(edge(f"em{sid(proj + m)}", f"p{sid(proj)}", nid, label=MIN[m][0], fromEnd="arrow"))
        x += 600
    if not minis:
        nodes.append(tnode(f"pn{sid(proj)}", "грань без ведомств-обитателей", -320, -160, 400, 90, "2"))
    write_canvas(f"map-L1-{proj}.canvas", nodes, edges)

def l0_canvas():
    nodes = [tnode("l0", f"# 🚢 L0 · КОРАБЛЬ — галактика\nТочная вложенность (слово владельца {DAY}): корабль → **грани = проекты (L1)** → **ведомства с гранями: подведомства / навыки / журналы / агенты (L2)** → **пути · роадмапы · артефакты-производные (L3)**.\nОткрой любой узел-карту — она вложена прямо здесь. ssot:false · истина в реестрах.",
                   -360, -660, 880, 170, "4")]
    nodes.append(fnode("mdeck", "10-Deck/deck.canvas", 580, -700, 560, 220, "1"))
    edges = [edge("emdeck", "l0", "mdeck", label="капитанский мостик (решения)")]
    x, y, n = -360, -420, 0
    for proj, card, minis in PROJECTS:
        nid = f"s{sid(proj)}"
        nodes.append(fnode(nid, f"10-Deck/map-L1-{proj}.canvas", x, y, 420, 300, "6" if minis else "2"))
        edges.append(edge(f"es{sid(proj)}", "l0", nid, label=f"{len(minis)} ведомств" if minis else "грань"))
        n += 1
        x += 460
        if n % 4 == 0:
            x, y = -360, y + 340
    nodes.append(tnode("pnote", "⚠️ замечено: у ведомства «Абилити лаб» нет карточки-грани в 03-Projects (наведено ЦУ).",
                       x, y, 420, 120, "2"))
    write_canvas("map-L0-ship.canvas", nodes, edges)

if __name__ == "__main__":
    for mid in ARTS:
        l3_canvas(mid)
    for mid in MIN:
        l2_canvas(mid)
    for proj, card, minis in PROJECTS:
        l1_canvas(proj, card, minis)
    l0_canvas()
    print("Deck v2 собран.")
