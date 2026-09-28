"""Тесты HTTP-клиента — без сети (мокается single_request)."""
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from lib import http_client


class Test429Retry:
    def test_retries_twice_then_ok(self, monkeypatch):
        calls = {"n": 0}
        statuses = [429, 429, 200]

        def fake_single(method, url, headers=None, body=None, timeout=15):
            status = statuses[min(calls["n"], 2)]
            calls["n"] += 1
            return {"ok": True, "status": status, "body": "{}",
                    "error_kind": None, "error": None, "latency_ms": 1, "attempts": 1}

        monkeypatch.setattr(http_client, "single_request", fake_single)
        res = http_client.request("GET", "https://x/v1/models", retries=2, pause=0)
        assert res["status"] == 200
        assert res["attempts"] == 3
        assert calls["n"] == 3

    def test_gives_up_after_retries(self, monkeypatch):
        calls = {"n": 0}

        def fake_single(*a, **k):
            calls["n"] += 1
            return {"ok": True, "status": 429, "body": "",
                    "error_kind": None, "error": None, "latency_ms": 1, "attempts": 1}

        monkeypatch.setattr(http_client, "single_request", fake_single)
        res = http_client.request("GET", "https://x/v1/models", retries=2, pause=0)
        assert res["status"] == 429
        assert res["attempts"] == 3
        assert calls["n"] == 3

    def test_no_retry_on_500(self, monkeypatch):
        calls = {"n": 0}

        def fake_single(*a, **k):
            calls["n"] += 1
            return {"ok": True, "status": 500, "body": "",
                    "error_kind": None, "error": None, "latency_ms": 1, "attempts": 1}

        monkeypatch.setattr(http_client, "single_request", fake_single)
        res = http_client.request("GET", "https://x/v1/models", retries=2, pause=0)
        assert res["status"] == 500
        assert calls["n"] == 1

    def test_default_pause_is_20(self):
        import inspect
        sig = inspect.signature(http_client.request)
        assert sig.parameters["pause"].default == 20.0
        assert sig.parameters["retries"].default == 2


class TestNoUrllib:
    def test_transport_is_curl_or_requests(self):
        import inspect
        src = inspect.getsource(http_client)
        assert "urllib" not in src, "urllib запрещён брифом (Cloudflare 1010)"

    def test_http_exception_caught(self):
        import http.client
        import inspect
        src = inspect.getsource(http_client)
        assert "HTTPException" in src
        assert issubclass(http.client.HTTPException, Exception)


class TestSingleRequest:
    def test_curl_404_parsing(self, monkeypatch):
        class FakeProc:
            returncode = 0
            stdout = '{"error":"nope"}\n404'
            stderr = ""

        import subprocess
        monkeypatch.setattr(
            http_client.shutil, "which", lambda name: "/usr/bin/curl")
        monkeypatch.setattr(http_client.subprocess, "run",
                            lambda *a, **k: FakeProc())
        res = http_client.single_request("GET", "https://x/v1/models")
        assert res["status"] == 404
        assert json_body_has_error(res["body"])

    def test_curl_exit_error(self, monkeypatch):
        class FakeProc:
            returncode = 6
            stdout = ""
            stderr = "Could not resolve host"

        monkeypatch.setattr(http_client.shutil, "which", lambda name: "/usr/bin/curl")
        monkeypatch.setattr(http_client.subprocess, "run",
                            lambda *a, **k: FakeProc())
        res = http_client.single_request("GET", "https://x/v1/models")
        assert res["ok"] is False
        assert res["error_kind"] == "network"
        assert "Could not resolve" in res["error"]


def json_body_has_error(body):
    import json
    return json.loads(body).get("error") == "nope"
