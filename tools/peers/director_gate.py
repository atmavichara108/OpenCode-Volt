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
import re
import subprocess
import sys
import time
from pathlib import Path

ROSTER = {
    "ses_effd908b3ffeNnpC0PZ4zkIf18": {"name": "librarian (Дирижёр, Vault)", "state": "active"},
    "ses_ef6d9ec61ffexSWJ2nYTfQwEW2": {"name": "igraphv2 (граф памяти, Vault)", "state": "active"},
    "ses_ef77a5cfbffeKpXtCXsI6sYL30": {"name": "внедрение (Vault, RECOVERY)", "state": "recovery"},
    "ses_eedd28c45ffeFJU6TDjG69z6A7": {"name": "sysop (dotfiles инфра)", "state": "active"},
}
PROJECT_DIRS = [
    Path("/home/rudra/Projects/OpenCode-Vault"),
    Path("/home/rudra/dotfiles"),
]
QUEUE = Path(__file__).resolve().parents[2] / ("tools/peers/generated/director_queue.jsonl")

FRESH_S = 600
STALE_S = 2 * 3600
DEAD_S = 24 * 3600
OUTPUT_LIMIT = 80
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:bearer|basic)\s+[^\s|]+"),
    re.compile(r"(?i)\b(?:token|password|passwd|secret|api[_-]?key)\s*[:=]\s*[^\s|]+"),
    re.compile(r"\b(?:sk|pk)-[A-Za-z0-9_-]{12,}"),
)


def safe_output(value: str, limit: int = OUTPUT_LIMIT) -> str:
    """Return bounded, single-line, non-secret text for human/JSON output."""
    text = " ".join(value.split())
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text[:limit]


def queue_diagnostic(message: str) -> None:
    print(f"director_queue: {message}", file=sys.stderr)


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


def queue_notes() -> tuple[dict, set[str]]:
    notes = {}
    unknown = set()
    if QUEUE.exists():
        try:
            lines = QUEUE.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            queue_diagnostic(f"cannot read queue: {exc}")
            return {}, set()
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                queue_diagnostic(f"skip malformed JSON at line {line_no}")
                continue
            if not isinstance(r, dict):
                queue_diagnostic(f"skip non-object event at line {line_no}")
                continue
            sid = r.get("session_id")
            if not isinstance(sid, str) or not sid.strip():
                queue_diagnostic(f"skip event with invalid session_id at line {line_no}")
                continue
            task_id = r.get("task_id", "default")
            if not isinstance(task_id, str) or not task_id.strip():
                queue_diagnostic(f"skip event with invalid task_id at line {line_no}")
                continue
            op = r.get("op")
            if not isinstance(op, str):
                queue_diagnostic(f"skip event with invalid op at line {line_no}")
                continue
            for field in ("scope", "next_action"):
                if field in r and not isinstance(r[field], str):
                    queue_diagnostic(f"skip event with invalid {field} at line {line_no}")
                    break
            else:
                notes.setdefault(sid, {})
                if op == "dispatch":
                    if not isinstance(r.get("scope"), str) or not isinstance(r.get("next_action"), str):
                        queue_diagnostic(f"skip dispatch missing scope/next_action at line {line_no}")
                        continue
                    notes[sid][task_id] = r
                elif op in ("complete", "stop", "blocked"):
                    notes[sid].pop(task_id, None)
                else:
                    continue
                if sid not in ROSTER:
                    unknown.add(sid)
    return {sid: list(tasks.values()) for sid, tasks in notes.items() if tasks}, unknown


def main() -> int:
    now_ms = time.time() * 1000
    per = collect()
    notes, unknown = queue_notes()
    rows, worst = [], 0
    for sid, meta in ROSTER.items():
        name = meta["name"]
        s = per.get(sid)
        tasks = notes.get(sid, [])
        if meta["state"] in ("stopped", "recovery"):
            label = "STOPPED" if meta["state"] == "stopped" else "RECOVERY"
            scope = tasks[0].get("scope", "—") if tasks else "—"
            action = tasks[0].get("next_action", "handoff: symptom/repro/status/next") if tasks else "восстановить рабочий канал"
            rows.append((name, "—", label, scope, action))
            worst = max(worst, 1)
            continue
        if not s:
            rows.append((name, "?", "UNSEEN", "—", "сверить session list"))
            worst = max(worst, 1)
            continue
        age_s = max(0.0, (now_ms - s.get("updated", 0)) / 1000.0)
        age_state = state_of(age_s)
        st = age_state
        age_h = age_s / 3600
        scope = safe_output(" | ".join(t.get("scope", "?") for t in tasks)) if tasks else "—"
        action = safe_output(" | ".join(t.get("next_action", "отчёт") for t in tasks)) if tasks else "назначить задачу"
        if not tasks:
            st = "IDLE→ASSIGN"
        elif st == "stale":
            st = "STALE→PING"
        elif st == "dead":
            st = "DEAD→RUDRA"
        rows.append((name, f"{int(age_s//60)}m" if age_s < 3600 else f"{age_h:.1f}h", st, scope, action))
        worst = max(worst, 2 if age_state == "dead" else 1 if (age_state == "stale" or not tasks) else 0)
    for sid in sorted(unknown):
        tasks = notes.get(sid, [])
        scope = safe_output(" | ".join(t.get("scope", "?") for t in tasks)) if tasks else "—"
        action = safe_output(" | ".join(t.get("next_action", "отчёт") for t in tasks)) if tasks else "сверить session roster"
        rows.append((f"UNKNOWN ({safe_output(sid)})", "?", "UNKNOWN", scope, action))
        worst = max(worst, 1)
    fmt = "{:<34} {:>7} {:<15} {:<36} {}"
    if "--json" in sys.argv:
        print(json.dumps([
            {"session": r[0], "age": r[1], "state": r[2], "scope": r[3], "next_action": r[4]}
            for r in rows
        ], ensure_ascii=False, indent=2))
    else:
        print(fmt.format("сессия", "молчит", "статус", "поручение", "следующее действие"))
        for r in rows:
            print(fmt.format(*r))
        stale = [r[0] for r in rows if r[2] in ("stale", "dead", "unseen", "IDLE→ASSIGN", "STALE→PING", "DEAD→RUDRA")]
        if stale:
            print("\nТРЕБУЕТ ДЕЙСТВИЯ:", "; ".join(stale))
    return worst


if __name__ == "__main__":
    sys.exit(main())
