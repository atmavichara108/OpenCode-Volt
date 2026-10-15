"""Тесты writer.py — схема узла/рёбер, нумерация, валидация в SANDBOX.

Всё пишется в /tmp/opencode/... ; прод-граф 04-Memory/idea-graph не трогается
и не валидируется (см. conftest.sandbox / seed_graph).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import config
import writer
from conftest import MODULE_DIR, seed_graph

NODE = "world-source-email-gmail"


def _record(**kw) -> dict:
    base = {
        "message_id": "<42@example.com>",
        "subject": "Исследование подходов к benchmark",
        "body": "Нужно сравнить варианты и собрать обзор трендов.",
        "date": "2026-10-07",
        "intent": "research",
    }
    base.update(kw)
    return base


@pytest.fixture
def graph(sandbox: Path):
    nodes = sandbox / "nodes.jsonl"
    edges = sandbox / "edges.jsonl"
    expected = seed_graph(nodes, edges)
    return sandbox, nodes, edges, expected


def _node_ids(nodes: Path) -> list[str]:
    return [json.loads(l)["id"] for l in nodes.read_text(encoding="utf-8").splitlines() if l.strip()]


def _edge_ids(edges: Path) -> list[str]:
    return [json.loads(l)["id"] for l in edges.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_numbering_continues_existing(graph):
    _, nodes, edges, expected = graph
    assert writer.next_intent_number(nodes) == expected["next_intent"]
    assert writer.next_edge_number(edges) == expected["next_edge"]


def test_numbering_on_missing_files_starts_at_one(sandbox: Path):
    assert writer.next_intent_number(sandbox / "nope.jsonl") == 1
    assert writer.next_edge_number(sandbox / "nope.jsonl") == 1


def test_append_node_and_edge_schema(graph):
    _, nodes, edges, expected = graph
    summary = writer.append([_record()], nodes_path=nodes, edges_path=edges, validate=False)

    assert summary["node_ids"] == [f"stream-intent-{expected['next_intent']:03d}"]
    assert summary["edge_ids"] == [f"e-{expected['next_edge']:04d}"]

    node = json.loads(nodes.read_text(encoding="utf-8").splitlines()[-1])
    # обязательные поля по README idea-graph
    for field in ("id", "graph", "kind", "label", "status", "provenance", "projection"):
        assert node.get(field), f"нет обязательного поля {field}"
    assert node["id"] == "stream-intent-018"
    assert node["graph"] == "stream"
    assert node["kind"] == "intent"
    assert node["status"] == "candidate"
    assert node["label"]  # непустой (нормализованный subject)
    assert node["provenance"]["source"] == "email:gmail"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", node["provenance"]["observed_at"])
    assert node["resolution"] in writer.RESOLUTIONS
    assert node["projection"] == ["index"]
    assert node["essence"]

    edge = json.loads(edges.read_text(encoding="utf-8").splitlines()[-1])
    for field in ("id", "graph", "from", "to", "type", "status", "provenance"):
        assert edge.get(field), f"нет обязательного поля {field}"
    assert edge["id"] == "e-0043"
    assert edge["graph"] == node["graph"] == "stream"
    assert edge["from"] == node["id"]
    assert edge["to"] == NODE
    assert edge["type"] == "announces"  # типа "emits" в taxonomy нет
    assert edge["status"] == node["status"]


def test_second_append_does_not_duplicate_ids(graph):
    _, nodes, edges, _ = graph
    writer.append([_record()], nodes_path=nodes, edges_path=edges, validate=False)
    writer.append([_record(message_id="<43@example.com>")], nodes_path=nodes, edges_path=edges, validate=False)
    ids = _node_ids(nodes)
    assert len(ids) == len(set(ids)) == 4  # сид (2) + 2 новых
    assert ids[-1] == "stream-intent-019"
    eids = _edge_ids(edges)
    assert len(eids) == len(set(eids)) == 3  # сид (1) + 2 новых
    assert eids[-1] == "e-0044"


def test_resolution_rejected_outside_taxonomy(graph):
    _, nodes, edges, _ = graph
    with pytest.raises(ValueError):
        writer.append(
            [_record(resolution="pending")],
            nodes_path=nodes,
            edges_path=edges,
            validate=False,
        )
    assert _node_ids(nodes)[-1] == "stream-intent-017"  # ничего не дописано


def test_empty_batch_writes_nothing(graph):
    _, nodes, edges, _ = graph
    before_n = nodes.read_text(encoding="utf-8")
    before_e = edges.read_text(encoding="utf-8")
    summary = writer.append([], nodes_path=nodes, edges_path=edges)
    assert summary["written"] is False
    assert nodes.read_text(encoding="utf-8") == before_n
    assert edges.read_text(encoding="utf-8") == before_e


@pytest.mark.skipif(shutil.which("node") is None, reason="node не установлен")
def test_sandbox_validator_pass_after_append(graph):
    _, nodes, edges, _ = graph
    writer.append([_record()], nodes_path=nodes, edges_path=edges, validate=True)
    ok, output = writer.run_validator(nodes)
    assert ok, output
    assert "PASS" in output
    # sandbox-режим: в выводе не должно быть прод-порогов
    assert "MODE: sandbox" in output


def test_dry_run_cli_writes_nothing(graph, capsys):
    _, nodes, edges, _ = graph
    before_n = nodes.read_text(encoding="utf-8")
    before_e = edges.read_text(encoding="utf-8")
    src = nodes.parent / "batch.json"
    src.write_text(json.dumps([_record()], ensure_ascii=False), encoding="utf-8")

    rc = writer.main(["--dry-run", "--file", str(src), "--nodes", str(nodes), "--edges", str(edges)])
    out = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert out["dry_run"] is True
    assert out["nodes"][0]["id"] == "stream-intent-018"
    assert out["edges"][0]["type"] == "announces"
    assert nodes.read_text(encoding="utf-8") == before_n
    assert edges.read_text(encoding="utf-8") == before_e


def test_cli_filters_non_intent_records(graph, capsys):
    _, nodes, edges, _ = graph
    src = nodes.parent / "mixed.json"
    src.write_text(
        json.dumps([_record(), _record(intent="error", subject="unsubscribe")], ensure_ascii=False),
        encoding="utf-8",
    )
    rc = writer.main(["--dry-run", "--file", str(src), "--nodes", str(nodes), "--edges", str(edges)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert len(out["nodes"]) == 1  # error/шум в граф не попадает


def test_prod_graph_not_touched_by_writer(graph):
    """Сторож: любая операция writer'а в тестах идёт только в sandbox."""
    _, nodes, edges, _ = graph
    prod_before = (
        Path(config.NODES_PATH).stat().st_size,
        Path(config.EDGES_PATH).stat().st_size,
    )
    writer.append([_record()], nodes_path=nodes, edges_path=edges, validate=False)
    prod_after = (
        Path(config.NODES_PATH).stat().st_size,
        Path(config.EDGES_PATH).stat().st_size,
    )
    assert prod_before == prod_after


@pytest.mark.skipif(shutil.which("node") is None, reason="node не установлен")
def test_prod_validator_runs_read_only():
    """Прод-валидатор — read-only прогон (ничего не пишет)."""
    proc = subprocess.run(
        ["node", str(config.VALIDATOR_PATH)],
        cwd=str(MODULE_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS" in proc.stdout
