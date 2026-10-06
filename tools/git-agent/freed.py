#!/usr/bin/env python3
"""Git Freed — детектор владения деревом (первый контур: волт).

Детерминированный read-only скан: ветка/main-щит, грязное дерево по путям,
активные leases (claims.jsonl), маркеры конфликтов, предупреждение о гонке
параллельных писателей общего поля (04-Memory/idea-graph/*.jsonl).

LLM внутри нет — «данные, а не решения»; выводы делает агент (git-freed).

Команды:
    freed.py detect      # полный снапшот: JSON в stdout (ключи стабильны)
    freed.py check       # гейт перед commit: 0 ok | 1 warn | 2 blocked
    freed.py lease-list  # активные leases с TTL (текстом)
Exit-семантика check:
    0 — поддержка чистая, гейт пройден
    1 — предупреждения: чужие leases рядом, общее поле dirty, много чужих
    2 — блокировка: merge/unmerged-путь/конфликт-маркер, main/master
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLAIMS = REPO / "tools" / "peers" / "generated" / "claims.jsonl"
COMMON_DIR = "04-Memory/idea-graph"
COMMON_FILES = {"nodes.jsonl", "edges.jsonl", "protocol.jsonl"}
LEASE_TTL_MIN = 30


def run(args: list[str]) -> str:
    try:
        return subprocess.run(
            args, cwd=str(REPO), capture_output=True, text=True, check=False
        ).stdout.strip()
    except FileNotFoundError:
        return ""


def is_conflict() -> tuple[bool, str]:
    git = REPO / ".git"
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        if (git / marker).exists():
            return True, marker
    if "unmerged" in run(["git", "status", "--porcelain=v1"]):
        return True, "unmerged-path"
    return False, ""


def dirty_map() -> dict[str, str]:
    out = run(["git", "status", "--porcelain=v1"])
    res: dict[str, str] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        code, path = line[:2], line[3:].strip().strip('"')
        res[path] = code
    return res


def active_claims() -> list[dict]:
    """Fold claims.jsonl: claim активен если нет позже release; TTL окно."""
    recs: list[dict] = []
    if not CLAIMS.exists():
        return recs
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("op") == "claim":
            rec["_open"] = True
        elif rec.get("op") == "release":
            for r in recs:
                if r.get("claim_id") == rec.get("claim_id"):
                    r["_open"] = False
        if rec.get("op") == "claim":
            recs.append(rec)
    now_ms = time.time() * 1000
    live = []
    for r in recs:
        if not r.get("_open"):
            continue
        ts = r.get("ts") or r.get("time") or 0
        fresh = (now_ms - ts) <= LEASE_TTL_MIN * 60_000 if ts else True
        live.append(
            {
                "claim_id": r.get("claim_id", "?"),
                "holder": r.get("session") or r.get("holder", "?"),
                "role": r.get("role", "?"),
                "scope": r.get("scope", "?"),
                "fresh": fresh,
            }
        )
    return live


def classify(dirty: dict[str, str]) -> dict:
    common_dirty = [
        p for p in dirty
        if p.startswith(COMMON_DIR + "/") and Path(p).name in COMMON_FILES
    ]
    trash = [p for p, c in dirty.items() if c in {"??", "A ", "AM"} and
             (p.startswith("/tmp") or p == ".DS_Store")]
    return {
        "common_field_dirty": common_dirty,
        "junk_candidates": trash,
        "tracked_dirty": [p for p, c in dirty.items() if c[0] in "M " and c != "??"],
        "untracked": [p for p, c in dirty.items() if c == "??"],
    }


def detect() -> dict:
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "?"
    head = run(["git", "rev-parse", "HEAD"])[:12]
    dirty = dirty_map()
    conf, marker = is_conflict()
    claims = active_claims()
    cls = classify(dirty)
    warnings: list[str] = []
    blocked: list[str] = []
    if conf:
        blocked.append(f"merge-state:{marker}")
    if branch in ("main", "master"):
        blocked.append("branch:main-denied")
    if cls["common_field_dirty"]:
        warnings.append("common-field:" + ",".join(cls["common_field_dirty"]))
    live = [c for c in claims if c["fresh"]]
    if live:
        warnings.append("leases:" + ",".join(c["claim_id"] for c in live))
    if len(dirty) > 40:
        warnings.append(f"tree-churn:{len(dirty)}")
    return {
        "ts": round(time.time() * 1000),
        "branch": branch,
        "head": head,
        "dirty_count": len(dirty),
        "classify": cls,
        "claims": claims,
        "warnings": warnings,
        "blocked": blocked,
        "ok": not blocked,
    }


def cmd_detect() -> int:
    print(json.dumps(detect(), ensure_ascii=False, indent=2))
    return 0


def cmd_check() -> int:
    d = detect()
    if d["blocked"]:
        print("BLOCKED: " + "; ".join(d["blocked"]))
        return 2
    if d["warnings"]:
        print("WARN: " + "; ".join(d["warnings"]))
        return 1
    print(f"OK: no blocks (dirty_count={d['dirty_count']}, branch={d['branch']})")
    return 0


def cmd_lease_list() -> int:
    live = [c for c in active_claims() if c["fresh"]]
    if not live:
        print("no active leases")
        return 0
    for c in live:
        print(f"{c['claim_id']}  {c['holder']}  role={c['role']}")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "detect"
    if cmd == "detect":
        return cmd_detect()
    if cmd == "check":
        return cmd_check()
    if cmd == "lease-list":
        return cmd_lease_list()
    print(f"unknown command: {cmd} (detect|check|lease-list)", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main())
