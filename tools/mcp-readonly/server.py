#!/usr/bin/env python3
"""Read-only MCP server — ecosystem state (stdio JSON-RPC, stdlib only).

Контракт: 06-Specs/Vault/mcp-readonly.md (§2, §3, §4).

3 tools (минимальный surface, read-only):
  ecosystem_state  — сводка: projects/tasks/route_log counts, drift_signals,
                     input_digest, vault_head
  ecosystem_card   — одна карточка registry (card_id: ECO-NNN)
  ecosystem_kanban — карточки по lifecycle (опц. filter: layer L0..L4)

Гарантии read-only: только open(...'r')/read_text; НЕТ write-открытий,
НЕТ os.remove/shutil, НЕТ сетевых импортов. Детерминизм: повторный вызов
ecosystem_state на том же входе → идентичный вывод.

Включение: НЕ включать в opencode.json без явного approval (см. spec §1
unblock-условия). Это implementation, не runtime-enablement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP_DIR = HERE.parent / "ecosystem-map"
REGISTRY = MAP_DIR / "registry.json"
SNAPSHOT = MAP_DIR / "generated" / "snapshot.json"

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "ecosystem-readonly"
SERVER_VERSION = "1.0.0"

LIFECYCLE_ORDER = [
    "IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD",
    "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED",
]


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _registry() -> dict:
    return _read_json(REGISTRY)


def _snapshot() -> dict:
    return _read_json(SNAPSHOT)


def _input_digest() -> str:
    import hashlib
    h = hashlib.sha256()
    for p in (REGISTRY, SNAPSHOT):
        if p.exists():
            h.update(p.read_bytes())
        else:
            h.update(b"<missing>")
    return h.hexdigest()


def tool_ecosystem_state() -> str:
    snap = _snapshot()
    reg = _registry()
    tasks = snap.get("tasks", {})
    out = {
        "projects": [(p.get("id"), p.get("kind")) for p in snap.get("projects", [])],
        "tasks": {k: len(v) if isinstance(v, list) else v for k, v in tasks.items()},
        "route_log": len(snap.get("route_log", [])),
        "drift_signals": snap.get("drift_signals", []),
        "registry_cards": len(reg.get("cards", {})),
        "input_digest": _input_digest(),
        "vault_head": (snap.get("git") or {}).get("head", ""),
        "meta_updated": (reg.get("meta") or {}).get("updated", ""),
    }
    return json.dumps(out, ensure_ascii=False, indent=2)


def tool_ecosystem_card(card_id: str) -> str:
    cards = _registry().get("cards", {})
    card = cards.get(card_id)
    if not card:
        return json.dumps({"error": f"нет карточки {card_id}"}, ensure_ascii=False)
    return json.dumps({card_id: card}, ensure_ascii=False, indent=2)


def tool_ecosystem_kanban(layer: str = "") -> str:
    cards = _registry().get("cards", {})
    by_lc: dict[str, list[dict]] = {}
    for cid, c in cards.items():
        if layer and c.get("layer") != layer:
            continue
        lc = c.get("lifecycle", "IDEA")
        by_lc.setdefault(lc, []).append({
            "id": cid, "title": c.get("title", ""), "layer": c.get("layer", ""),
            "owner": c.get("owner", ""), "priority": c.get("priority", ""),
            "project": c.get("project") or "", "depends_on": c.get("depends_on", []),
        })
    ordered = {lc: by_lc.get(lc, []) for lc in LIFECYCLE_ORDER}
    ordered.update({k: v for k, v in by_lc.items() if k not in LIFECYCLE_ORDER})
    return json.dumps(ordered, ensure_ascii=False, indent=2)


TOOLS = [
    {
        "name": "ecosystem_state",
        "description": "Сводка состояния экосистемы: projects/tasks/route_log counts, drift_signals, input_digest, vault_head. Read-only, детерминирован.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ecosystem_card",
        "description": "Одна карточка registry по id (ECO-NNN) — все поля card schema. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"card_id": {"type": "string", "description": "id карточки, напр. ECO-014"}},
            "required": ["card_id"],
        },
    },
    {
        "name": "ecosystem_kanban",
        "description": "Карточки, сгруппированные по lifecycle (опц. фильтр layer L0..L4). Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"layer": {"type": "string", "description": "опц. фильтр по слою L0..L4"}},
        },
    },
]

TOOL_FNS = {
    "ecosystem_state": lambda args: tool_ecosystem_state(),
    "ecosystem_card": lambda args: tool_ecosystem_card(args.get("card_id", "")),
    "ecosystem_kanban": lambda args: tool_ecosystem_kanban(args.get("layer", "")),
}


def _send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg: dict) -> None:
    method = msg.get("method", "")
    msg_id = msg.get("id")

    if method == "initialize":
        _send({
            "jsonrpc": "2.0", "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        })
    elif method == "notifications/initialized":
        pass  # no response
    elif method == "tools/list":
        _send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        params = msg.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        fn = TOOL_FNS.get(name)
        if not fn:
            _send({"jsonrpc": "2.0", "id": msg_id,
                   "result": {"content": [{"type": "text", "text": f"unknown tool: {name}"}],
                              "isError": True}})
            return
        try:
            text = fn(args)
            _send({"jsonrpc": "2.0", "id": msg_id,
                   "result": {"content": [{"type": "text", "text": text}], "isError": False}})
        except Exception as e:  # noqa: BLE001 — вернуть текст ошибки
            _send({"jsonrpc": "2.0", "id": msg_id,
                   "result": {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}],
                              "isError": True}})
    else:
        _send({"jsonrpc": "2.0", "id": msg_id,
               "error": {"code": -32601, "message": f"method not found: {method}"}})


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        handle(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
