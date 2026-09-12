"""Тесты pipeline.py — детерминированный intake-контур capture → signals.

Тестируем только чистую логику: flatten, score, project mapping, upgrade path,
digest. Сетевых вызовов нет; classify импортируется из телеграм-каптчер-каталога,
telethon через conftest.py замокирован.
"""
import hashlib
import json

import pytest

import classify
import pipeline


# ---------------------------------------------------------------------------
# flatten_captures
# ---------------------------------------------------------------------------

def test_flatten_preserves_order_and_tags_topic():
    data = {
        "topics": {
            "Софт": [{"message_id": 1, "text": "a"}],
            "ИИ": [{"message_id": 2, "text": "b"}, {"message_id": 3, "text": "c"}],
        }
    }
    flat = pipeline.flatten_captures(data)
    assert [p["message_id"] for p in flat] == [1, 2, 3]
    assert [p["topic"] for p in flat] == ["Софт", "ИИ", "ИИ"]


def test_flatten_empty_topics():
    assert pipeline.flatten_captures({"topics": {}}) == []


# ---------------------------------------------------------------------------
# load_input (captures_all.json vs JSONL-очередь)
# ---------------------------------------------------------------------------

def test_load_input_from_jsonl(tmp_path):
    q = tmp_path / "inbox.jsonl"
    q.write_text(
        json.dumps({"message_id": 1, "topic": "Софт", "text": "a"}) + "\n"
        + json.dumps({"message_id": 2, "topic": "ИИ", "text": "b"}) + "\n",
        encoding="utf-8",
    )
    flat = pipeline.load_input(q)
    assert [p["message_id"] for p in flat] == [1, 2]
    assert [p["topic"] for p in flat] == ["Софт", "ИИ"]


def test_load_input_from_captures(tmp_path):
    src = tmp_path / "captures_all.json"
    src.write_text(json.dumps({"topics": {"Софт": [{"message_id": 7, "text": "x"}]}}),
                   encoding="utf-8")
    flat = pipeline.load_input(src)
    assert [p["message_id"] for p in flat] == [7]
    assert flat[0]["topic"] == "Софт"


def test_load_input_jsonl_skips_corrupt_lines(tmp_path):
    q = tmp_path / "inbox.jsonl"
    q.write_text("{broken\n" + json.dumps({"message_id": 3, "topic": "Софт", "text": "z"}) + "\n",
                 encoding="utf-8")
    flat = pipeline.load_input(q)
    assert [p["message_id"] for p in flat] == [3]


def test_load_input_from_list_format(tmp_path):
    # новый формат активного сбора: плоский list [post...] с полем topic
    src = tmp_path / "captures_all.json"
    src.write_text(json.dumps([
        {"message_id": 1, "topic": "Софт", "text": "a"},
        {"message_id": 2, "topic": "ИИ", "text": "b"},
    ]), encoding="utf-8")
    flat = pipeline.load_input(src)
    assert [p["message_id"] for p in flat] == [1, 2]
    assert [p["topic"] for p in flat] == ["Софт", "ИИ"]


# ---------------------------------------------------------------------------
# _resolve_captures (date-suffix фолбяк)
# ---------------------------------------------------------------------------

def test_resolve_captures_prefers_canonical(tmp_path):
    (tmp_path / "captures_all.json").write_text("{}", encoding="utf-8")
    (tmp_path / "captures_all-2026-07-12.json").write_text("{}", encoding="utf-8")
    assert pipeline._resolve_captures(tmp_path).name == "captures_all.json"


def test_resolve_captures_falls_back_to_latest_dated(tmp_path):
    (tmp_path / "captures_all-2026-07-12.json").write_text("{}", encoding="utf-8")
    (tmp_path / "captures_all-2026-07-13.json").write_text("{}", encoding="utf-8")
    assert pipeline._resolve_captures(tmp_path).name == "captures_all-2026-07-13.json"


def test_resolve_captures_returns_canonical_when_none_exist(tmp_path):
    assert pipeline._resolve_captures(tmp_path).name == "captures_all.json"


# ---------------------------------------------------------------------------
# relevance_score
# ---------------------------------------------------------------------------

def test_relevance_score_full_signal():
    post = {
        "repo": "https://github.com/foo/bar",
        "title": "Foo Bar",
        "lang": "Rust",
        "text": "x" * 300 + " github.com/foo/bar",
    }
    assert pipeline.relevance_score(post) == 10


def test_relevance_score_minimal():
    post = {"repo": "", "title": "", "lang": "", "text": ""}
    assert pipeline.relevance_score(post) == 0


def test_relevance_score_caps_at_ten():
    post = {
        "repo": "https://github.com/foo/bar",
        "title": "T",
        "lang": "Go",
        "text": ("long " * 100) + " github.com/x",
    }
    assert pipeline.relevance_score(post) == 10


# ---------------------------------------------------------------------------
# project_for / upgrade_path_for
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cat,proj", [
    ("dotfiles", "dotfiles"),
    ("serplux", "SERPlux"),
    ("dv-hub", "dv-hub"),
    ("vibeos", "vault"),
    ("new", "new"),
    ("error", None),
    ("unknown", None),
])
def test_project_for(cat, proj):
    assert pipeline.project_for(cat) == proj


def test_upgrade_path_known_and_fallback():
    assert pipeline.upgrade_path_for("dotfiles").startswith("кандидат")
    assert pipeline.upgrade_path_for("nope") == "триаж"


# ---------------------------------------------------------------------------
# build_signals (сквозной)
# ---------------------------------------------------------------------------

def test_build_signals_counts_and_meta():
    flat = [
        {"message_id": 1, "topic": "Софт", "text": "**Htop**\n\n"
         "Мониторинг процессов, терминал, cli. https://github.com/htop-dev/htop"},
        {"message_id": 2, "topic": "Софт", "text": "дубликат той же сути"},
    ]
    s = pipeline.build_signals(flat)
    assert s["meta"]["schema"] == "capture-signals/1.0"
    assert s["meta"]["total_posts"] == len(flat)
    # категория dotfiles даёт сигнал, error/прочие — не дают
    assert s["meta"]["total_signals"] >= 1
    assert len(s["signals"]) > 0 and s["signals"][0]["project"] == "dotfiles"


def test_build_signals_deterministic_digest():
    flat = [{"message_id": 7, "topic": "ИИ", "text": "Ollama локальная модель llm"}]
    s1 = pipeline.build_signals(flat)
    s2 = pipeline.build_signals([dict(p) for p in flat])  # копия
    assert s1["meta"]["input_digest"] == s2["meta"]["input_digest"]
    assert s1 == s2


def test_build_signals_digest_matches_canonical_json():
    flat = [{"message_id": 9, "topic": "Софт", "text": "x"}]
    s = pipeline.build_signals(flat)
    expected = hashlib.sha256(
        json.dumps(flat, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert s["meta"]["input_digest"] == expected


def test_build_signals_skips_error_category():
    flat = [
        {"message_id": 1, "topic": "Питонизм", "text": "курс за 500 руб без github"},
        {"message_id": 2, "topic": "Софт", "text": "tui файловый менеджер для linux"},
    ]
    s = pipeline.build_signals(flat)
    # курс → error → сигнала нет
    assert all(sig["message_id"] != 1 for sig in s["signals"])
    # dotfiles-пост — сигнал есть
    assert any(sig["message_id"] == 2 for sig in s["signals"])


def test_build_signals_sorted_by_relevance_desc():
    flat = [
        {"message_id": 1, "topic": "Софт", "text": "mcp server для claude code агентов "
         "https://github.com/a/b"},
        {"message_id": 2, "topic": "Софт", "text": "короткий"},
    ]
    s = pipeline.build_signals(flat)
    rels = [sig["relevance"] for sig in s["signals"]]
    assert rels == sorted(rels, reverse=True)