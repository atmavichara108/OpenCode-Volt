#!/usr/bin/env python3
"""director_gate — гейт простоя сессий команды (zero-LLM, детерминированный).

Показывает Дирижёру и Рудре: какая сессия сколько молчит и требует ли действия.

Правила (team-protocol v1 §stale-status):
- fresh:      отзыв < 10 мин          — работает прямо сейчас
- waiting:    10 мин - 2 ч            активность была, ждём результат
- stale:      2 ч - 24 ч              требует действия Дирижёра
- dead/care:  > 24 ч                  отчёт → Рудре, возобновление/замена

Ростер команды: id + человекочитаемое имя. Сессии ищутся в двух проектах
(Vault + dotfiles); берётся самое свежее time_updated из обеих баз вывода
`opencode session list`. Дополнительные сессии берутся из
tools/peers/generated/director_queue.jsonl (опционально: строка per-session).

Выход:
    director_gate.py            # таблица человеку
    director_gate.py --json     # JSON (ключи стабильны)
Exit codes: 0 все fresh/waiting; 1 есть stale (нужно действие); 2 есть
dead/архив-кандидат (нужно решение Рудры).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROSTER = {
    "ses_effd908b3ffeNnpC0PZ4zkIf18": "librarian (Дирижёр, Vault)",
    "ses_ef6d9ec61ffexSWJ2nYTfQwEW2": "igraphv2 (граф памяти, Vault)",
    "ses_ef77a5cfbffeKpXtCXsI6sYL30": "внедрение (Vault, STOPPED)",
    "ses_eedd28c45ffeFJU6TDjG69z6A7": "sysop (dotfiles инфра)",
}
PROJECT_DIRS = [
    Path("/home/rudra/Projects/OpenCode-Vault"),
    Path("/home/rudra/dotfiles"),
]
QUEUE = Path(__file__).resolve().parents[2] / ("tools/peers/generated/director_queue.jsonl")

FRESH_S = 600
STALE_S = 2 * 3600
DEAD_S = 24 * 3600


def sessions_by_project(cwd: Path) -> dict:
    try:
        out = subprocess.run(
            ["opencode", "session", "list", "-n", "60", "--format", "json"],
            cwd=str(cwd), capture_output=True, text=True, check=False, timeout=60,
        ).stdout
        data = json.loads(out) if out.strip() else []
    except Exception:
        return {}
    return {s["id"]: s for s in data if isinstance(s, dict)}


def collect() -> dict:
    found: dict = {}
    for d in PROJECT_DIRS:
        for sid, s in sessions_by_project(d).items():
            prev = found.get(sid)
            if not prev or s.get("updated", 0) > prev.get("updated", 0):
                s["_dir"] = str(d)
                found[sid] = s
    return found


def state_of(age_s: float) -> str:
    if age_s < FRESH_S:
        return "fresh"
    if age_s < STALE_S:
        return "waiting"
    if age_s < DEAD_S:
        return "stale"
    return "dead"


def queue_notes() -> dict:
    notes = {}
    if QUEUE.exists():
        for line in QUEUE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("op") == "dispatch" and not r.get("closed"):
                notes[r.get("session_id", "?")] = r.get("scope", "?")
    return notes


def main() -> int:
    now_ms = time.time() * 1000
    per = collect()
    notes = queue_notes()
    rows, worst = [], 0
    for sid, name in ROSTER.items():
        s = per.get(sid)
        if not s:
            rows.append((name[:34], "?", "unseen", "-", "-"))
            continue
        age_s = max(0.0, (now_ms - s.get("updated", 0)) / 1000.0)
        st = state_of(age_s)
        age_h = age_s / 3600
        rows.append((name[:34], f"{int(age_s//60)}m" if age_s < 3600 else f"{age_h:.1f}h", st, notes.get(sid, "-"), s.get("title", "")[:26]))
        worst = max(worst, 2 if st == "dead" else 1 if st == "stale" else 0)
    if rows and rows[0][2] == "unseen":
        pass
    fmt = "{:<34} {:>6} {:<8} {:<14} {}"
    if "--json" in sys.argv:
        print(json.dumps([
            {"session": r[0], "age": r[1], "state": r[2], "open_scope": r[3], "last_title": r[4]}
            for r in rows
        ], ensure_ascii=False, indent=2))
    else:
        print(fmt.format("сессия", "молчит", "статус", "открытый scope", "титул"))
        for r in rows:
            print(fmt.format(*r))
        stale = [r[0] for r in rows if r[2] in ("stale", "dead", "unseen")]
        if stale:
            print("\nТРЕБУЕТ ДЕЙСТВИЯ:", "; ".join(stale))
    return worst


if __name__ == "__main__":
    sys.exit(main())
