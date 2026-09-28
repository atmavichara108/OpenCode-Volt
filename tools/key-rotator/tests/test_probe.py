"""Тесты key-rotator probe — без сети (мокается http_client.request)."""
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from lib import keys as key_store
from lib import redact as redact_mod
from lib.http_client import is_cloudflare_fingerprint
from probe import classify_models, load_catalog, probe_provider


def make_resp(status=None, body="", error_kind=None):
    return {"ok": status is not None, "status": status, "body": body,
            "error_kind": error_kind, "error": None, "latency_ms": 10, "attempts": 1}


CFG = {
    "endpoint": "https://example.test/v1",
    "endpoints": ["https://example.test/v1"],
    "env": "TEST_PROVIDER_KEY",
    "auth_id": None,
    "transport": "openai",
    "roles": ["coding"],
    "priority": 50,
}


def ok_models_body(ids):
    return json.dumps({"data": [{"id": i} for i in ids]})


class TestCatalog:
    def test_catalog_loads(self):
        catalog = load_catalog()
        assert catalog["providers"]
        assert "amd-radeon" in catalog["providers"]
        for pid, cfg in catalog["providers"].items():
            assert "endpoint" in cfg or "endpoints" in cfg, pid
            assert "transport" in cfg, pid
            assert "priority" in cfg, pid


class TestClassify:
    def test_active_with_models(self):
        status, warnings, count, ids = classify_models(
            make_resp(200, ok_models_body(["m1", "m2"])), CFG)
        assert status == "ACTIVE"
        assert count == 2
        assert ids == ["m1", "m2"]
        assert "balance_unknown" in warnings

    def test_blocked_empty_models(self):
        status, warnings, count, _ = classify_models(
            make_resp(200, json.dumps({"data": []})), CFG)
        assert status == "BLOCKED"
        assert "empty_models" in warnings

    def test_blocked_401(self):
        status, warnings, _, _ = classify_models(make_resp(401, ""), CFG)
        assert status == "BLOCKED"
        assert "http_401" in warnings

    def test_blocked_403_cloudflare_1010(self):
        body = "<html>error code: 1010</html>"
        status, warnings, _, _ = classify_models(make_resp(403, body), CFG)
        assert status == "BLOCKED"
        assert "cloudflare_1010_client_fingerprint" in warnings

    def test_degraded_429(self):
        status, warnings, _, _ = classify_models(make_resp(429, ""), CFG)
        assert status == "DEGRADED"
        assert "rate_limited" in warnings

    def test_error_network(self):
        status, warnings, _, _ = classify_models(
            make_resp(None, "", error_kind="network"), CFG)
        assert status == "ERROR"
        assert "network" in warnings

    def test_error_500(self):
        status, _, _, _ = classify_models(make_resp(500, ""), CFG)
        assert status == "ERROR"

    def test_blocked_non_json(self):
        status, warnings, _, _ = classify_models(make_resp(200, "not-json"), CFG)
        assert status == "BLOCKED"
        assert "non_json_body" in warnings


class TestCloudflare:
    def test_detects_1010(self):
        assert is_cloudflare_fingerprint("error code: 1010")
        assert not is_cloudflare_fingerprint("error code: 1009")
        assert not is_cloudflare_fingerprint("")


class TestKeyResolve:
    def test_env_priority(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "from-env")
        key, source = key_store.resolve_key("TEST_PROVIDER_KEY", None,
                                            env={"TEST_PROVIDER_KEY": "from-env"},
                                            dotenv={}, auth={})
        assert key == "from-env"
        assert source == "env"

    def test_dotenv_fallback(self):
        key, source = key_store.resolve_key("TEST_PROVIDER_KEY", None,
                                            env={}, dotenv={"TEST_PROVIDER_KEY": "dv"},
                                            auth={})
        assert key == "dv"
        assert source == "dotenv"

    def test_auth_fallback(self):
        key, source = key_store.resolve_key(None, "amd-radeon",
                                            env={}, dotenv={},
                                            auth={"amd-radeon": {"type": "api", "key": "ak"}})
        assert key == "ak"
        assert source == "auth.json"

    def test_none(self):
        key, source = key_store.resolve_key("NOPE", "nope", env={}, dotenv={}, auth={})
        assert key == ""
        assert source == "none"


class TestRedact:
    def test_redacts_key(self):
        secret = "sk-test-abcdefghijklmnop123456"
        text = f"error for key {secret} in url"
        assert secret not in redact_mod.redact(text, keys=[secret])
        assert "***REDACTED***" in redact_mod.redact(text, keys=[secret])

    def test_pattern_fallback_without_known_key(self):
        assert "sk-" not in redact_mod.redact("bad sk-abcdefghijklmnopqrstuvwxyz012345", keys=[])

    def test_redact_obj_nested(self):
        secret = "sk-nested-abcdefghijklmnop123"
        obj = {"a": [f"x {secret}", {"b": secret}], "n": 5}
        dumped = json.dumps(redact_mod.redact_obj(obj, keys=[secret]))
        assert secret not in dumped


class TestProbeProvider:
    def test_active(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "sk-unit-test-key-000111222333")
        monkeypatch.setattr(
            "probe.http_client.request",
            lambda *a, **k: make_resp(200, ok_models_body(["deepseek-v4-flash"])))
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "ACTIVE"
        assert rec["models_count"] == 1
        assert rec["exit"] == 0
        assert rec["model_ids_sample"] == ["deepseek-v4-flash"]

    def test_blocked_empty(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "sk-unit-test-key-000111222333")
        monkeypatch.setattr(
            "probe.http_client.request",
            lambda *a, **k: make_resp(200, json.dumps({"data": []})))
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "BLOCKED"
        assert rec["exit"] == 2

    def test_no_key(self, monkeypatch):
        monkeypatch.delenv("TEST_PROVIDER_KEY", raising=False)
        monkeypatch.setattr("probe.key_store.resolve_key",
                            lambda e, a: ("", "none"))
        called = []
        monkeypatch.setattr("probe.http_client.request",
                            lambda *a, **k: called.append(1) or make_resp())
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "ERROR"
        assert "no_key" in rec["warnings"]
        assert not called, "HTTP не должен вызываться без ключа"

    def test_no_endpoint(self, monkeypatch):
        cfg = dict(CFG, endpoints=[], endpoint=None)
        rec = probe_provider("test", cfg, timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "BLOCKED"
        assert "no_endpoint" in rec["warnings"]

    def test_skipped(self):
        cfg = dict(CFG, skip="endpoint_dynamic")
        rec = probe_provider("test", cfg, timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "SKIPPED"

    def test_smoke_fail_degrades(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "sk-unit-test-key-000111222333")

        def fake_request(method, url, **kw):
            if method == "POST":
                return make_resp(500, "")
            return make_resp(200, ok_models_body(["m1"]))

        monkeypatch.setattr("probe.http_client.request", fake_request)
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=True, smoke_model="m1")
        assert rec["status"] == "DEGRADED"
        assert rec["smoke"]["ok"] is False
        assert "smoke_failed" in rec["warnings"]

    def test_smoke_without_model_warns(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "sk-unit-test-key-000111222333")
        monkeypatch.setattr(
            "probe.http_client.request",
            lambda *a, **k: make_resp(200, ok_models_body(["m1"])))
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=True, smoke_model=None)
        assert rec["status"] == "ACTIVE"
        assert "smoke_skipped_no_model" in rec["warnings"]

    def test_multiline_second_endpoint(self, monkeypatch):
        monkeypatch.setenv("TEST_PROVIDER_KEY", "sk-unit-test-key-000111222333")
        cfg = dict(CFG, endpoints=["https://bad.test/v1", "https://good.test/v1"])
        calls = []

        def fake_request(method, url, **kw):
            calls.append(url)
            if "bad.test" in url:
                return make_resp(404, "")
            return make_resp(200, ok_models_body(["m-good"]))

        monkeypatch.setattr("probe.http_client.request", fake_request)
        rec = probe_provider("test", cfg, timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        assert rec["status"] == "ACTIVE", "404 на первом → ищем дальше до ACTIVE"
        assert rec["endpoint"] == "https://good.test/v1"
        assert rec["models_count"] == 1
        assert len(calls) == 2


class TestNoSecretsInOutput:
    def test_key_never_in_record(self, monkeypatch):
        secret = "sk-unit-test-key-000111222333"
        monkeypatch.setenv("TEST_PROVIDER_KEY", secret)
        body = json.dumps({"error": {"message": f"bad key {secret}"}})
        monkeypatch.setattr("probe.http_client.request",
                            lambda *a, **k: make_resp(500, body))
        rec = probe_provider("test", dict(CFG), timeout=5, retries=0, pause=0,
                             smoke=False, smoke_model=None)
        redacted = redact_mod.redact_obj(rec, keys=[secret])
        assert secret not in json.dumps(redacted)
