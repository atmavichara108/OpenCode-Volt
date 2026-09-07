#!/usr/bin/env python3
"""peer_role — файл-реестр ролей сессий (порт P6 #31 в TUI).

Переносим подмножество ring-of-peers M Code, которое не требует engine-native
механики: claim/list/release ролей через append-only файл-реестр. Письма/wake
(peer_message, пробуждение) остаются M Code-only — их в TUI не перенести.

Семантика (1:1 с M Code peer_role):
  - claim ГРАНТУЕТ НИЧЕГО и БЛОКИРУЕТ НИКОГО: это сигнализация «я беру X»,
    а не распределённый лок. Сессия, смотрящая peers, видит, кто что держит.
  - overlap НЕ запрещён: заявка на роль, которую уже держит сосед, успешна
    и просто говорит «кто ещё это держит» — конфликт решается разговором,
    а не исключением.
  - release по claim_id, не по имени (id недвусмысленен); release дважды — не ошибка.

Реестр: tools/peers/generated/claims.jsonl (gitignored) — append-only, одна запись
на строку. Активный claim = есть op:claim и нет более позднего op:release.

Использование:
    python3 tools/peers/peer_role.py claim --role "auth refactor" --scope "packages/core/src/auth"
    python3 tools/peers/peer_role.py list
    python3 tools/peers/peer_role.py holds      # кто что держит + пересечения
    python3 tools/peers/peer_role.py release --claim-id <id из claim>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from uuid import uuid4

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = VAULT_ROOT / "tools" / "peers" / "generated" / "claims.jsonl"


def _read_ledger() -> list[dict]:
    if not REGISTRY.exists():
        return []
    out = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _fold(ledger: list[dict]) -> dict[str, dict]:
    """Свернуть ledger в активные claim'ы: claim активен, если нет release после."""
    active: dict[str, dict] = {}
    for rec in ledger:
        op = rec.get("op")
        cid = rec.get("claim_id")
        if op == "claim" and cid:
            active[cid] = rec
        elif op == "release" and cid:
            active.pop(cid, None)
    return active


def _append(rec: dict) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with REGISTRY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def cmd_claim(args) -> int:
    claim_id = f"role_{int(time.time() * 1000)}_{uuid4().hex[:6]}"
    rec = {
        "op": "claim",
        "claim_id": claim_id,
        "role": args.role,
        "scope": args.scope,
        "session": args.session,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _append(rec)

    # Сказать, кто ещё держит ту же роль (overlap именован, не заблокирован)
    overlap = [c for c in _fold(_read_ledger()).values()
               if c["role"] == args.role and c["claim_id"] != claim_id]
    out = {"claimed": claim_id, "role": args.role, "scope": args.scope}
    if overlap:
        out["held_also_by"] = [{"claim_id": c["claim_id"], "session": c.get("session")} for c in overlap]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args) -> int:
    active = list(_fold(_read_ledger()).values())
    print(json.dumps(active, ensure_ascii=False, indent=2))
    return 0


def cmd_holds(args) -> int:
    active = _fold(_read_ledger()).values()
    by_role: dict[str, list[dict]] = {}
    for c in active:
        by_role.setdefault(c["role"], []).append(c)
    rows = []
    for role, claims in sorted(by_role.items()):
        rows.append({
            "role": role,
            "holders": sorted({c.get("session", "?") for c in claims}),
            "claims": [c["claim_id"] for c in claims],
            "overlap": len(claims) > 1,
        })
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_release(args) -> int:
    active = _fold(_read_ledger())
    if args.claim_id not in active:
        print(json.dumps({"released": args.claim_id, "was_active": False}, ensure_ascii=False))
        return 0
    _append({"op": "release", "claim_id": args.claim_id,
             "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print(json.dumps({"released": args.claim_id, "was_active": True}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="peer_role — файл-реестр ролей сессий (P6 #31)")
    p.add_argument("--session", default=None, help="id своей сессии (опционально)")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("claim", help="заявить роль (сигнализация, не лок)")
    c.add_argument("--role", required=True, help="что беру: 'auth refactor'")
    c.add_argument("--scope", default=None, help="над чем именно: путь/тикет")
    c.set_defaults(func=cmd_claim)

    l = sub.add_parser("list", help="все активные claim'ы")
    l.set_defaults(func=cmd_list)

    h = sub.add_parser("holds", help="кто что держит + пересечения")
    h.set_defaults(func=cmd_holds)

    r = sub.add_parser("release", help="снять роль по claim_id")
    r.add_argument("--claim-id", dest="claim_id", required=True)
    r.set_defaults(func=cmd_release)

    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except OSError as e:
        print(json.dumps({"error": "registry_io", "message": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())