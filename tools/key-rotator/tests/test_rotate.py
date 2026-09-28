"""Тесты rotate (Iter-1) — без сети и без реальных правок конфигов."""
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

import rotate
from rotate import (choose_candidate, is_healthy, load_json, read_health_statuses,
                    role_for, split_model)


def make_rot(**kw):
    rot = {
        "default_role": "coding",
        "agent_roles": {"build": "coding", "explore": "general", "librarian": "general"},
        "healthy_statuses": ["ACTIVE", "SKIPPED", "DEGRADED"],
        "failover_statuses": ["BLOCKED", "ERROR"],
        "preferred": {
            "prov-a": {"coding": ["model-x"]},
            "prov-b": {"coding": ["model-z"]},
            "prov-c": {},
        },
    }
    rot.update(kw)
    return rot


def make_catalog():
    return {"providers": {
        "prov-a": {"roles": ["coding"], "priority": 90},
        "prov-b": {"roles": ["coding", "general"], "priority": 80},
        "prov-c": {"roles": ["general"], "priority": 95},
        "prov-skip": {"roles": ["coding"], "priority": 99, "skip": "managed"},
        "prov-dead": {"roles": ["coding"], "priority": 99},
    }}


MODELS = {
    "prov-a": ["model-x", "model-y"],
    "prov-b": ["model-z"],
    "prov-c": ["model-c1"],
    "prov-skip": ["model-s"],
    # prov-dead отсутствует (не объявлен в конфиге)
}


class TestSplitModel:
    def test_two(self):
        assert split_model("anymodel/cx/gpt-6-luna") == ("anymodel", "cx/gpt-6-luna")

    def test_plain(self):
        assert split_model("prov/model") == ("prov", "model")

    def test_none(self):
        assert split_model("") == (None, None)
        assert split_model("noslash") == (None, None)


class TestRoleFor:
    def test_mapped(self):
        assert role_for("build", make_rot()) == "coding"
        assert role_for("explore", make_rot()) == "general"

    def test_default(self):
        assert role_for("unknown-agent", make_rot()) == "coding"


class TestIsHealthy:
    def test_healthy_statuses(self, tmp_path):
        rot = make_rot()
        st = {"a": {"status": "ACTIVE"}, "d": {"status": "DEGRADED"},
              "b": {"status": "BLOCKED"}, "e": {"status": "ERROR"}}
        assert is_healthy("a", st, rot)
        assert is_healthy("d", st, rot)
        assert not is_healthy("b", st, rot)
        assert not is_healthy("e", st, rot)

    def test_no_data_is_unhealthy(self):
        assert not is_healthy("missing", {}, make_rot())


class TestChooseCandidate:
    def st(self):
        return {p: {"status": "ACTIVE"} for p in
                ["prov-a", "prov-b", "prov-c", "prov-skip", "prov-dead"]}

    def test_excludes_current(self):
        c = choose_candidate("prov-a", "coding", self.st(), make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        assert c is not None
        assert c["provider"] == "prov-b"

    def test_prefers_preferred_and_priority(self):
        # prov-a имеет preferred, но он current; prov-b тоже preferred → берём b
        c = choose_candidate(None, "coding", self.st(), make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        assert c is not None
        assert c["provider"] == "prov-a"
        assert c["model"] == "prov-a/model-x"

    def test_skips_skipped_providers(self):
        # prov-skip имеет skip → исключён, хотя priority 99
        c = choose_candidate("prov-b", "coding", self.st(), make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        assert c is not None
        assert c["provider"] == "prov-a"

    def test_skips_unhealthy(self):
        st = self.st()
        st["prov-a"] = {"status": "BLOCKED"}
        c = choose_candidate("prov-b", "coding", st, make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        # prov-a заблокирован → провайдеров по coding не остаётся (prov-dead не виден)
        assert c is None or c["provider"] != "prov-a"

    def test_skips_provider_not_visible_to_router(self):
        # prov-dead здоров в statuses, но нет в MODELS → не кандидат
        c = choose_candidate("prov-b", "coding", self.st(), make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        assert c is None or c["provider"] != "prov-dead"

    def test_respects_role(self):
        c = choose_candidate("prov-a", "general", self.st(), make_rot(),
                             make_catalog(), MODELS, make_catalog()["providers"])
        # general: prov-b (80) и prov-c (95), preferred у prov-b только coding → prov-c выше
        assert c is not None
        assert c["provider"] == "prov-c"

    def test_model_fallback_to_first_available(self):
        # prov-c без preferred для coding; возьмём prov-c только для general
        rot = make_rot(preferred={"prov-c": {}})
        c = choose_candidate("prov-a", "general", self.st(), rot,
                             make_catalog(), MODELS, make_catalog()["providers"])
        assert c is not None
        assert c["model"] == "prov-c/model-c1"

    def test_no_double_prefix(self):
        # collect_models отдаёт id с префиксом провайдера — второй не добавляем
        models = {"prov-a": ["prov-a/model-x"], "prov-b": ["prov-b/model-z"]}
        c = choose_candidate("prov-b", "coding", self.st(), make_rot(),
                             make_catalog(), models, make_catalog()["providers"])
        assert c is not None
        assert c["model"] == "prov-a/model-x"

    def test_none_when_empty(self):
        assert choose_candidate("prov-a", "coding", {}, make_rot(),
                                make_catalog(), MODELS, make_catalog()["providers"]) is None


class TestHealthLog:
    def test_last_record_wins(self, tmp_path):
        p = tmp_path / "h.jsonl"
        p.write_text("\n".join([
            json.dumps({"provider_id": "a", "status": "ERROR"}),
            json.dumps({"provider_id": "a", "status": "ACTIVE"}),
            json.dumps({"provider_id": "b", "status": "BLOCKED"}),
        ]), encoding="utf-8")
        st = read_health_statuses(p)
        assert st["a"]["status"] == "ACTIVE"
        assert st["b"]["status"] == "BLOCKED"

    def test_missing_file(self, tmp_path):
        assert read_health_statuses(tmp_path / "nope.jsonl") == {}

    def test_garbage_lines_ignored(self, tmp_path):
        p = tmp_path / "h.jsonl"
        p.write_text("garbage\n" + json.dumps({"provider_id": "a", "status": "ACTIVE"}),
                     encoding="utf-8")
        st = read_health_statuses(p)
        assert st["a"]["status"] == "ACTIVE"


class TestNotify:
    def test_no_topic_skips(self, monkeypatch):
        from lib import notify
        monkeypatch.delenv("PIPBOY_NTFY", raising=False)
        res = notify.send("hello")
        assert res == {"ok": False, "skipped": "no_topic"}

    def test_uses_curl_not_urllib(self):
        import inspect
        from lib import notify
        src = inspect.getsource(notify)
        assert "import urllib" not in src
        assert "from urllib" not in src
        assert "http_client" in src

    def test_format_switch(self):
        from lib import notify
        msg = notify.format_switch("build", "global", None,
                                   "old/m", "new/m", "provider_blocked")
        assert "build" in msg and "old/m" in msg and "new/m" in msg

    def test_send_posts_via_curl_path(self, monkeypatch):
        from lib import notify
        monkeypatch.setenv("PIPBOY_NTFY", "test-topic")
        calls = {}

        def fake_single(method, url, headers=None, body=None, timeout=15):
            calls.update(method=method, url=url, headers=headers, body=body)
            return {"ok": True, "status": 200, "body": '{"id":"xyz"}',
                    "error_kind": None, "error": None, "latency_ms": 1, "attempts": 1}

        monkeypatch.setattr(notify.http_client, "single_request", fake_single)
        res = notify.send("сообщение", priority="low")
        assert res["ok"] is True
        assert calls["method"] == "POST"
        assert calls["url"].endswith("/test-topic")
        assert calls["headers"]["Priority"] == "low"
        assert calls["body"] == "сообщение"


class TestCatalogs:
    def test_rotation_config_loads(self):
        rot = load_json(TOOL_DIR / "rotation.json")
        assert rot["default_role"]
        assert rot["agent_roles"]
        # нет выдуманных тестовых провайдеров (prov-a/prov-b/... из фикстур)
        import re as _re
        assert not _re.search(r"\bprov-[a-z]\b", json.dumps(rot, ensure_ascii=False))
        # каждый preferred-провайдер есть в каталоге
        catalog = load_json(TOOL_DIR / "providers.json")
        for pid in rot["preferred"]:
            assert pid in catalog["providers"], pid

    def test_preferred_roles_match_provider_roles(self):
        rot = load_json(TOOL_DIR / "rotation.json")
        catalog = load_json(TOOL_DIR / "providers.json")
        for pid, by_role in rot["preferred"].items():
            pcfg = catalog["providers"][pid]
            for role in by_role:
                assert role in pcfg["roles"], f"{pid}: роль {role} не в roles"


class TestDryRunMain:
    """main() в dry-run: applied по diff, kind пробрасывается в apply."""

    def test_dry_run_applied_by_diff(self, monkeypatch, tmp_path, capsys):
        hlog = tmp_path / "h.jsonl"
        hlog.write_text(
            json.dumps({"provider_id": "prov-dead", "status": "ERROR"}) + "\n"
            + json.dumps({"provider_id": "prov-a", "status": "ACTIVE"}) + "\n",
            encoding="utf-8")
        monkeypatch.setattr(rotate, "HEALTH_LOG", hlog)
        calls = {}

        def fake_apply(agent, model, **kw):
            calls.update(kw)
            return {"ok": True, "changed": False, "dry_run": True,
                    "diff": "-old +new"}, None

        monkeypatch.setattr(rotate, "load_json", lambda path: (
            make_catalog() if str(path).endswith("providers.json") else make_rot(
                agent_roles={"build": "coding"})))
        monkeypatch.setattr(rotate.router, "list_agents", lambda project=None: (
            {"ok": True, "agents": [{"agent": "build", "scope": "global",
                                    "project": None, "kind": "config",
                                    "model": "prov-dead/old-model"}]}, None))
        monkeypatch.setattr(rotate.router, "list_models", lambda: (
            {"ok": True, "models": [
                {"provider": "prov-a", "id": "prov-a/model-x"}]}, None))
        monkeypatch.setattr(rotate.router, "apply", fake_apply)
        rc = rotate.main(["--dry-run", "--agent", "build", "--quiet"])
        assert rc == 0
        assert calls["kind"] == "config", "kind должен пробрасываться в apply"
        payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
        results = payload["results"]
        assert results[0]["action"] == "applied"
        assert results[0]["dry_run"] is True
        assert payload["summary"]["dry"] == 1
        assert payload["summary"]["switched"] == 0, "в dry-run реальных switched нет"

    def test_no_diff_is_noop(self, monkeypatch, tmp_path, capsys):
        hlog = tmp_path / "h.jsonl"
        hlog.write_text(
            json.dumps({"provider_id": "prov-dead", "status": "ERROR"}) + "\n"
            + json.dumps({"provider_id": "prov-a", "status": "ACTIVE"}) + "\n",
            encoding="utf-8")
        monkeypatch.setattr(rotate, "HEALTH_LOG", hlog)
        monkeypatch.setattr(rotate, "load_json", lambda path: (
            make_catalog() if str(path).endswith("providers.json") else make_rot(
                agent_roles={"build": "coding"})))
        monkeypatch.setattr(rotate.router, "list_agents", lambda project=None: (
            {"ok": True, "agents": [{"agent": "build", "scope": "global",
                                     "project": None, "kind": "file",
                                     "model": "prov-dead/old-model"}]}, None))
        monkeypatch.setattr(rotate.router, "list_models", lambda: (
            {"ok": True, "models": [
                {"provider": "prov-a", "id": "prov-a/model-x"}]}, None))
        monkeypatch.setattr(
            rotate.router, "apply",
            lambda *a, **k: ({"ok": True, "changed": False, "dry_run": True,
                              "diff": ""}, None))
        rc = rotate.main(["--dry-run", "--agent", "build", "--quiet"])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
        assert payload["results"][0]["action"] == "noop"
