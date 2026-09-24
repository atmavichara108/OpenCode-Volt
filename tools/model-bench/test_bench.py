"""Тесты bench.py с мок-клиентом: прогон гейта, артефакт, cost-guard, dry-run."""
import json

import pytest

import bench
import client
import config
import tasks


def _make_chat(reply_map=None):
    """Строит мок client.chat, возвращающий ответ по первому совпадению needle в промпте."""

    def fake_chat(base_url, key, model, prompt, max_tokens, timeout=120, proxies=None):
        reply = "OK"
        if reply_map:
            for needle, r in reply_map.items():
                if needle in prompt:
                    reply = r
                    break
        return reply, {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}, 10, ""

    return fake_chat


TOOLS_REPLIES = {
    '"name"': '{"name": "x", "age": 1}',
    '"label"': '{"x": 1.0, "y": 2.0, "label": "p"}',
    '"user"': '{"user": {"id": 1, "email": "a@b.c"}, "active": true}',
    '"tags"': '{"tags": ["a"], "count": 1}',
    '"title"': '{"title": "t", "items": [1], "enabled": true}',
}


def test_run_gate_tools_all_pass(monkeypatch):
    monkeypatch.setattr(client, "chat", _make_chat(reply_map=TOOLS_REPLIES))
    res = bench.run_gate("tools", "anymodel", "am/free", "http://x", "k", None, 1)
    assert res["score"] == 1.0
    assert res["passed_threshold"] is True
    assert res["cost_tokens"] == 2 * len(tasks.TOOLS_TASKS)


def test_build_artifact_no_prompts_no_answers():
    gates_result = {
        "tools": {"score": 1.0, "passed_threshold": True, "cost_tokens": 10,
                  "cost_usd_est": 0.0, "latency_ms_median": 100, "notes": ""},
    }
    art = bench.build_artifact("anymodel", "am/free", gates_result, 1)
    s = json.dumps(art, ensure_ascii=False)
    assert "prompt" not in s
    assert "anymodel.org" not in s
    assert "am/free" in s
    assert art["advisory"] is True
    assert art["task_set_hash"] == tasks.TASK_SET_HASH
    assert art["k"] == 1
    assert art["recommendation"] == ["tools"]


def test_build_recommendation_excludes_fast():
    gates = {
        "tools": {"passed_threshold": True},
        "build": {"passed_threshold": False},
        "fast": {"passed_threshold": None},
    }
    assert bench.build_recommendation(gates) == ["tools"]


def test_slugify():
    assert bench.slugify("cx/gpt-6-astra") == "cx_gpt-6-astra"
    assert bench.slugify("a b/c!") == "a_b_c_"


def test_cost_guard_blocks_expensive(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "COST_GUARD_USD", 0.000001)
    monkeypatch.setattr(client, "chat", _make_chat())
    code = bench.main([
        "--provider", "anymodel", "--model", "cx/gpt-6-astra",
        "--gates", "tools", "--k", "1", "--out", str(tmp_path),
    ])
    assert code == 2


def test_cost_guard_free_not_blocked(monkeypatch, tmp_path):
    monkeypatch.setattr(client, "chat", _make_chat(reply_map=TOOLS_REPLIES))
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free",
        "--gates", "tools", "--k", "1", "--out", str(tmp_path),
    ])
    assert code == 0
    assert (tmp_path / "anymodel__am_free.json").exists()


def test_dry_run_no_calls(monkeypatch, capsys):
    called = []
    monkeypatch.setattr(client, "chat", lambda *a, **k: called.append(1))
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free",
        "--dry-run",
    ])
    out = capsys.readouterr().out
    assert code == 0
    assert called == []
    assert "DRY-RUN" in out


def test_unknown_gate_returns_3(capsys):
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free", "--gates", "bogus",
    ])
    assert code == 3
