"""Append интентов из писем в idea-graph + прогон валидатора.

Пишет ровно две append-only строки (см. 04-Memory/idea-graph/README.md):

- `nodes.jsonl` — узел `stream-intent-NNN` (graph=stream, kind=intent,
  status=candidate, provenance{source:"email:gmail", observed_at}, projection,
  доменные поля `essence` и `resolution` ∈ accepted|deferred|implemented);
- `edges.jsonl` — ребро `e-NNNN` (graph=stream, from=новый узел,
  to=`world-source-email-gmail`, type=`announces`, status, provenance).

Свободные номера берутся чтением существующих файлов (не дублируем).
Запись под эксклюзивным flock, flush+fsync. После записи — прогон
`node tools/idea-graph/validate.mjs`: FAIL = честная ошибка в stderr и exit 1,
БЕЗ автоотката (страница append-only, откат — ручное решение).

Пути: config.NODES_PATH/EDGES_PATH (env NODES_PATH/EDGES_PATH/GRAPH_DIR),
поэтому тесты пишут в sandbox и гоняют валидатор в sandbox-режиме.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Mapping

try:
    import fcntl
except ImportError:  # noqa: BLE001 — не-Linux (тесты/разработка)
    fcntl = None

import classifier
import config

RESOLUTIONS = ("accepted", "deferred", "implemented")
DEFAULT_RESOLUTION = "deferred"
DEFAULT_STATUS = "candidate"
SOURCE = "email:gmail"
_SCOPE = "signal-flow:email-source"
_TAIL_BYTES = 1 << 20  # читаем хвост файла, если он вдруг огромный

# Прод-путь фиксируется на импорте: тесты перенаправляют config.NODES_PATH
# в sandbox, а валидатор должен понять «это не прод» даже под monkeypatch'ем.
_PROD_NODES = Path(config.VAULT_ROOT) / "04-Memory" / "idea-graph" / "nodes.jsonl"

_INTENT_ID_RE = re.compile(r'"id"\s*:\s*"stream-intent-(\d+)"')
_EDGE_ID_RE = re.compile(r'"id"\s*:\s*"e-(\d+)"')


# --- нумерация (чтение существующего состояния) ----------------------------

def _read_tail(path: Path) -> str:
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open(encoding="utf-8", errors="replace") as f:
        if size > _TAIL_BYTES:
            f.seek(size - _TAIL_BYTES)
            f.readline()  # отрезаем недописанную строку
        return f.read()


def next_intent_number(nodes_path: Path | None = None) -> int:
    """Следующий свободный NNN для `stream-intent-NNN` (существующие не дублируем)."""
    path = Path(nodes_path or config.NODES_PATH)
    nums = [int(m) for m in _INTENT_ID_RE.findall(_read_tail(path))]
    return max(nums, default=0) + 1


def next_edge_number(edges_path: Path | None = None) -> int:
    """Следующий свободный NNNN для `e-NNNN`."""
    path = Path(edges_path or config.EDGES_PATH)
    nums = [int(m) for m in _EDGE_ID_RE.findall(_read_tail(path))]
    return max(nums, default=0) + 1


# --- построение записей ----------------------------------------------------

def _observed_at(message: Mapping) -> str:
    """Дата наблюдения YYYY-MM-DD: ISO из письма, RFC822 Date, иначе сегодня."""
    raw = str(message.get("observed_at") or message.get("date") or "")
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if match:
        return match.group(0)
    if raw:
        try:
            parsed = parsedate_to_datetime(raw)
            if parsed is not None:
                return parsed.date().isoformat()
        except (TypeError, ValueError, IndexError):
            pass
    return time.strftime("%Y-%m-%d")


def _label(message: Mapping, intent: str) -> str:
    subject = classifier.normalize(message.get("subject") or "")
    if subject:
        return subject[:160]
    snippet = classifier.normalize(classifier.text_of(message))
    return (snippet[:160] or f"email intent: {intent}")


def _essence(message: Mapping) -> str:
    body = classifier.normalize(
        str(message.get("body") or message.get("body_text") or classifier.text_of(message))
    )
    return body[:500]


def _provenance(message: Mapping) -> dict:
    return {
        "source": SOURCE,
        "observed_at": _observed_at(message),
        "scope": _SCOPE,
        "basis": "quoted",
    }


def _resolution(message: Mapping) -> str:
    value = str(message.get("resolution") or DEFAULT_RESOLUTION).strip().lower()
    if value not in RESOLUTIONS:
        raise ValueError(f"resolution={value!r} вне {RESOLUTIONS}")
    return value


def build_node(message: Mapping, number: int, intent: str | None = None) -> dict:
    """Узел `stream-intent-NNN` для одного письма-интента."""
    intent = intent or str(message.get("intent") or config.DEFAULT_INTENT)
    if intent not in config.INTENT_NAMES:
        raise ValueError(f"intent={intent!r} не из INTENT_NAMES {config.INTENT_NAMES}")
    return {
        "id": f"stream-intent-{number:03d}",
        "graph": "stream",
        "kind": "intent",
        "label": _label(message, intent),
        "essence": _essence(message),
        "status": DEFAULT_STATUS,
        "resolution": _resolution(message),
        "provenance": _provenance(message),
        "projection": ["index"],
    }


def build_edge(node: Mapping, number: int) -> dict:
    """Ребро `e-NNNN`: новый узел announces источнику Gmail."""
    return {
        "id": f"e-{number:04d}",
        "graph": node["graph"],
        "from": node["id"],
        "to": config.EMAIL_SOURCE_NODE,
        "type": "announces",
        "status": node["status"],
        "provenance": dict(node["provenance"]),
    }


def plan(
    messages: Iterable[Mapping],
    nodes_path: Path | None = None,
    edges_path: Path | None = None,
) -> tuple[list[dict], list[dict]]:
    """Последовательность узлов+рёбер для батча (нумерация сквозная, без дублей)."""
    nodes: list[dict] = []
    edges: list[dict] = []
    node_no = next_intent_number(nodes_path)
    edge_no = next_edge_number(edges_path)
    for message in messages:
        node = build_node(message, node_no)
        nodes.append(node)
        edges.append(build_edge(node, edge_no))
        node_no += 1
        edge_no += 1
    return nodes, edges


# --- запись ----------------------------------------------------------------

def _append_locked(nf, ef, records: Iterable[Mapping]) -> tuple[list[dict], list[dict]]:
    """Нумерация и запись под flock на ОБОИХ файлах (защита от гонки номеров)."""
    for handle in (nf, ef):
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    try:
        nodes, edges = plan(records, Path(nf.name), Path(ef.name))
        for node in nodes:
            nf.write(json.dumps(node, ensure_ascii=False) + "\n")
        for edge in edges:
            ef.write(json.dumps(edge, ensure_ascii=False) + "\n")
        nf.flush()
        ef.flush()
        os.fsync(nf.fileno())
        os.fsync(ef.fileno())
        return nodes, edges
    finally:
        if fcntl is not None:
            for handle in (nf, ef):
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append(
    messages: Iterable[Mapping],
    *,
    nodes_path: Path | None = None,
    edges_path: Path | None = None,
    validate: bool = True,
) -> dict:
    """Append узлов и рёбер в idea-graph. Возвращает сводку результата.

    Ничего не пишет при пустом батче. После записи — прогон валидатора;
    FAIL не откатывает записи, а честно поднимается как ошибка.
    """
    records = list(messages)
    if not records:
        return {"nodes": 0, "edges": 0, "written": False, "validator": "skipped"}

    n_path = Path(nodes_path or config.NODES_PATH)
    e_path = Path(edges_path or config.EDGES_PATH)
    n_path.parent.mkdir(parents=True, exist_ok=True)
    e_path.parent.mkdir(parents=True, exist_ok=True)
    with n_path.open("a+", encoding="utf-8") as nf, e_path.open(
        "a+", encoding="utf-8"
    ) as ef:
        nodes, edges = _append_locked(nf, ef, records)

    summary = {
        "nodes": len(nodes),
        "edges": len(edges),
        "written": True,
        "node_ids": [n["id"] for n in nodes],
        "edge_ids": [e["id"] for e in edges],
        "validator": "skipped",
    }
    if validate:
        ok, output = run_validator(n_path)
        summary["validator"] = "PASS" if ok else "FAIL"
        if output:
            # логи всегда в stderr — stdout остаётся чистым JSON'ом
            print(output, file=sys.stderr)
        if not ok:
            raise SystemExit(
                "writer: валидатор idea-graph FAIL — записи сделаны, откат НЕ выполнялся; "
                "разбери строки вручную"
            )
    return summary


def run_validator(nodes_path: Path | None = None) -> tuple[bool, str]:
    """Прогон `node validate.mjs`. Для не-прод путей — sandbox-режим (без порогов)."""
    n_path = Path(nodes_path or config.NODES_PATH)
    validator = Path(config.VALIDATOR_PATH)
    cmd = ["node", str(validator)]
    is_prod = n_path.resolve() == _PROD_NODES.resolve()
    if not is_prod:
        cmd.append(str(n_path.parent.resolve()))  # sandbox: каталог с *.jsonl
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return False, "writer: node не найден — валидатор не прогнан"
    except subprocess.TimeoutExpired:
        return False, "writer: валидатор завис (>120s)"
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output.strip()


# --- CLI -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="append email-интентов в idea-graph")
    ap.add_argument("--file", help="JSON-массив записей (без файла — stdin)")
    ap.add_argument("--dry-run", action="store_true", help="показать узлы/рёбра, ничего не писать")
    ap.add_argument("--no-validate", action="store_true", help="не гонять validate.mjs")
    ap.add_argument("--nodes", help="переопределить путь nodes.jsonl (sandbox)")
    ap.add_argument("--edges", help="переопределить путь edges.jsonl (sandbox)")
    args = ap.parse_args(argv)

    raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    try:
        messages = json.loads(raw)
        if not isinstance(messages, list):
            raise ValueError("ожидался JSON-массив")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"writer: bad input: {e}", file=sys.stderr)
        return 2

    records = [m for m in messages if m.get("intent") in config.INTENT_NAMES]
    if not records:
        print("writer: нет записей с интентами — ничего не пишем", file=sys.stderr)
        print(json.dumps({"nodes": 0, "edges": 0, "written": False}, ensure_ascii=False))
        return 0

    nodes_path = Path(args.nodes) if args.nodes else None
    edges_path = Path(args.edges) if args.edges else None
    try:
        nodes, edges = plan(records, nodes_path, edges_path)
    except ValueError as e:
        print(f"writer: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(
            json.dumps(
                {"dry_run": True, "nodes": nodes, "edges": edges},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    summary = append(
        records,
        nodes_path=Path(args.nodes) if args.nodes else None,
        edges_path=Path(args.edges) if args.edges else None,
        validate=not args.no_validate,
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
