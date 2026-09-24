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


# --- валидация --budget -----------------------------------------------------

@pytest.mark.parametrize("budget", ["nan", "inf", "-1", "0"])
def test_invalid_budget_returns_3_no_calls(monkeypatch, budget):
    calls = {"n": 0}

    def fake_chat(*a, **k):
        calls["n"] += 1
        return "OK", {"total_tokens": 2}, 10, ""

    monkeypatch.setattr(client, "chat", fake_chat)
    code = bench.main([
        "--provider", "anymodel", "--model", "cx/gpt-5.6-sol",
        "--gates", "tools", "--budget", budget,
    ])
    assert code == 3
    assert calls["n"] == 0


# --- дедупликация гейтов -----------------------------------------------------

def test_duplicate_gates_run_once(monkeypatch, tmp_path):
    calls = {"n": 0}

    def fake_chat(base_url, key, model, prompt, max_tokens, timeout=120, proxies=None):
        calls["n"] += 1
        return "OK", {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}, 10, ""

    monkeypatch.setattr(client, "chat", fake_chat)
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free",
        "--gates", "tools,tools", "--k", "1", "--out", str(tmp_path),
    ])
    assert code == 0
    assert calls["n"] == len(tasks.TOOLS_TASKS)
    art = json.loads((tmp_path / "anymodel__am_free.json").read_text(encoding="utf-8"))
    assert "tools" in art["gates"]


# --- token_multiplier -------------------------------------------------------

def test_token_multiplier_exact_match():
    assert client.token_multiplier("anymodel", "cc/claude-opus-5") == 36.5
    assert client.token_multiplier("anymodel", "cx/gpt-5.6-sol") == 0.8


def test_token_multiplier_nemotron_prefix():
    assert client.token_multiplier("anymodel", "am/nemotron-3-ultra-550b-a55b") == 8.0


def test_token_multiplier_unknown_default():
    assert client.token_multiplier("anymodel", "zzz-unknown") == client.DEFAULT_TOKEN_MULTIPLIER
    assert client.token_multiplier("other", "any/model") == client.DEFAULT_TOKEN_MULTIPLIER


# --- estimate_run_cost ------------------------------------------------------

def test_estimate_run_cost_includes_prompt_tokens():
    # fast: 3 ping-задачи, max_tokens=16 каждая → только max_tokens дали бы 48.
    cost, tokens_est = bench.estimate_run_cost(
        "anymodel", "cc/claude-opus-5", ["fast"], 1
    )
    assert tokens_est > 3 * 16
    assert cost is not None


def test_estimate_run_cost_applies_multiplier():
    # base = 3 * (len("Reply with: OK") // 4 + 16) = 3 * (3 + 16) = 57
    base = sum(len(t["prompt"]) // 4 + t["max_tokens"] for t in tasks.FAST_TASKS)
    cost, tokens_est = bench.estimate_run_cost("anymodel", "cc/claude-opus-5", ["fast"], 1)
    assert tokens_est == int(base * 36.5)


def test_estimate_run_cost_unknown_model_returns_none_cost_but_tokens():
    cost, tokens_est = bench.estimate_run_cost("anymodel", "zzz-unknown", ["fast"], 1)
    assert cost is None
    assert tokens_est > 0


# --- накопительный бюджет ---------------------------------------------------

def _make_chat_expensive():
    calls = {"n": 0}

    def fake_chat(base_url, key, model, prompt, max_tokens, timeout=120, proxies=None):
        calls["n"] += 1
        return "OK", {"prompt_tokens": 1, "completion_tokens": 49999, "total_tokens": 50000}, 10, ""

    return fake_chat, calls


def test_budget_stop_skips_remaining_gates(monkeypatch, tmp_path):
    fake_chat, calls = _make_chat_expensive()
    monkeypatch.setattr(client, "chat", fake_chat)
    code = bench.main([
        "--provider", "anymodel", "--model", "cx/gpt-5.6-sol",
        "--gates", "tools,build,reasoning,fast", "--k", "1",
        "--budget", "0.02", "--out", str(tmp_path),
    ])
    assert code == 0
    # tools-гейт (5 задач) превышает бюджет → build/reasoning/fast не прогоняются.
    assert calls["n"] == len(tasks.TOOLS_TASKS)
    art = json.loads((tmp_path / "anymodel__cx_gpt-5.6-sol.json").read_text(encoding="utf-8"))
    assert art["budget_stop"] is True
    assert art["gates_skipped"] == ["build", "reasoning", "fast"]
    assert set(art["gates"].keys()) == {"tools"}


def test_budget_force_bypasses_stop(monkeypatch, tmp_path):
    fake_chat, calls = _make_chat_expensive()
    monkeypatch.setattr(client, "chat", fake_chat)
    code = bench.main([
        "--provider", "anymodel", "--model", "cx/gpt-5.6-sol",
        "--gates", "tools,build,reasoning,fast", "--k", "1",
        "--budget", "0.02", "--force", "--out", str(tmp_path),
    ])
    assert code == 0
    total_tasks = sum(len(tasks.TASKS_BY_GATE[g]) for g in ["tools", "build", "reasoning", "fast"])
    assert calls["n"] == total_tasks
    art = json.loads((tmp_path / "anymodel__cx_gpt-5.6-sol.json").read_text(encoding="utf-8"))
    assert art["budget_stop"] is False
    assert art["gates_skipped"] == []


def test_preliminary_guard_uses_min_budget(monkeypatch, tmp_path):
    # COST_GUARD_USD высокий, но --budget ужесточает лимит → cost-guard срабатывает.
    monkeypatch.setattr(config, "COST_GUARD_USD", 100.0)
    monkeypatch.setattr(client, "chat", _make_chat())
    code = bench.main([
        "--provider", "anymodel", "--model", "cx/gpt-6-astra",
        "--gates", "tools", "--k", "1",
        "--budget", "0.000001", "--out", str(tmp_path),
    ])
    assert code == 2


# --- авто-генерация матрицы -------------------------------------------------

def test_matrix_generated_after_run(monkeypatch, tmp_path):
    monkeypatch.setattr(client, "chat", _make_chat(reply_map=TOOLS_REPLIES))
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free",
        "--gates", "tools", "--k", "1", "--out", str(tmp_path),
    ])
    assert code == 0
    assert (tmp_path / "matrix.md").exists()


def test_skip_matrix_no_matrix_file(monkeypatch, tmp_path):
    monkeypatch.setattr(client, "chat", _make_chat(reply_map=TOOLS_REPLIES))
    code = bench.main([
        "--provider", "anymodel", "--model", "am/free",
        "--gates", "tools", "--k", "1", "--skip-matrix", "--out", str(tmp_path),
    ])
    assert code == 0
    assert (tmp_path / "anymodel__am_free.json").exists()
    assert not (tmp_path / "matrix.md").exists()
