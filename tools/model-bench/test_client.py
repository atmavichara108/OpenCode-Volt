"""Тесты client.py: 429-ретрай, HTTPException, resolve_coefficient (офлайн).

Все сетевые вызовы мокаются через ``config.build_opener``; паузы ретраев
обнуляются, чтобы тесты не спали.
"""
import http.client
import io
import json
import urllib.error

import client
import config


def _no_sleep(monkeypatch):
    monkeypatch.setattr(client, "RETRY_PAUSE_SECONDS", 0.0)
    monkeypatch.setattr(client, "RETRY_429_PAUSE_SECONDS", 0.0)


class _FakeResp:
    """Fake-ответ urllib с телом из строки."""

    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body.encode("utf-8")


class _FakeOpener:
    """OpenerDirector-подмена: отдаёт items по кругу, Exception — пробрасывает."""

    def __init__(self, items):
        self._items = list(items)
        self.calls = 0

    def open(self, req, timeout=None):
        item = self._items[min(self.calls, len(self._items) - 1)]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        return item


def _http_error(code, body=""):
    return urllib.error.HTTPError(
        url="http://x/chat/completions",
        code=code,
        msg="err",
        hdrs={},
        fp=io.BytesIO(body.encode("utf-8")),
    )


def _success_body(content="OK", finish="stop"):
    return json.dumps({
        "choices": [{"message": {"content": content}, "finish_reason": finish}],
        "usage": {"total_tokens": 2},
    })


# --- 429 retry ---------------------------------------------------------------

def test_chat_429_then_success(monkeypatch):
    _no_sleep(monkeypatch)
    opener = _FakeOpener([
        _http_error(429, '{"error": "rate limited"}'),
        _FakeResp(_success_body("OK", "stop")),
    ])
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    reply, usage, latency, err, finish = client.chat("http://x", "k", "m", "p", 10)
    assert err == ""
    assert reply == "OK"
    assert finish == "stop"
    assert opener.calls == 2


def test_chat_persistent_429_returns_rate_limit_error(monkeypatch):
    _no_sleep(monkeypatch)
    opener = _FakeOpener([_http_error(429, "rate")] * 3)
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    reply, usage, latency, err, finish = client.chat("http://x", "k", "m", "p", 10)
    assert reply == ""
    assert err.startswith("HTTP 429")
    # kind rate_limit (семантика run_gate не меняется).
    import bench
    assert bench._classify_error(err) == "rate_limit"
    assert opener.calls == 3


def test_chat_other_4xx_immediate(monkeypatch):
    _no_sleep(monkeypatch)
    opener = _FakeOpener([_http_error(401, '{"error":"unauthorized"}')])
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    reply, usage, latency, err, finish = client.chat("http://x", "k", "m", "p", 10)
    assert err.startswith("HTTP 401")
    assert opener.calls == 1  # без ретрая


# --- HTTPException (BadStatusLine) -------------------------------------------

def test_chat_http_exception_retried_as_network(monkeypatch):
    _no_sleep(monkeypatch)

    class _BadOpener:
        def __init__(self):
            self.calls = 0

        def open(self, req, timeout=None):
            self.calls += 1
            raise http.client.BadStatusLine("bad status line")

    opener = _BadOpener()
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    reply, usage, latency, err, finish = client.chat("http://x", "k", "m", "p", 10)
    assert err.startswith("network error")
    assert opener.calls == 3  # RETRY_COUNT + 1


# --- resolve_coefficient -----------------------------------------------------

def test_resolve_coefficient_table():
    coeff, source = client.resolve_coefficient("anymodel", "cx/gpt-6-astra")
    assert coeff == 8
    assert source == "table"


def test_resolve_coefficient_cli_price():
    coeff, source = client.resolve_coefficient("anymodel", "zzz-unknown", cli_price=0.10)
    assert coeff == 0.10 / client.COST_BASE_USD_PER_1M
    assert source == "cli_price"


def test_resolve_coefficient_live_billing(monkeypatch):
    opener = _FakeOpener([
        _FakeResp('{"billing": {"coefficient": {"input": 3, "output": 5}}}')
    ])
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    coeff, source = client.resolve_coefficient(
        "anymodel", "zzz-unknown", base_url="http://x", key="k"
    )
    assert coeff == 5
    assert source == "live"


def test_resolve_coefficient_live_pricing(monkeypatch):
    opener = _FakeOpener([
        _FakeResp('{"pricing": {"prompt": 0.5, "completion": 1.0}}')
    ])
    monkeypatch.setattr(config, "build_opener", lambda proxies: opener)
    coeff, source = client.resolve_coefficient(
        "anymodel", "zzz-unknown", base_url="http://x", key="k"
    )
    assert coeff == 1.0 / client.COST_BASE_USD_PER_1M
    assert source == "live"


def test_resolve_coefficient_fetch_error_none(monkeypatch):
    class _BadOpener:
        def open(self, req, timeout=None):
            raise OSError("boom")

    monkeypatch.setattr(config, "build_opener", lambda proxies: _BadOpener())
    coeff, source = client.resolve_coefficient(
        "anymodel", "zzz-unknown", base_url="http://x", key="k"
    )
    assert coeff is None
    assert source is None


def test_resolve_coefficient_no_base_or_key_skips_live():
    # без base_url/key живого запроса нет, цена не выдумывается.
    coeff, source = client.resolve_coefficient("anymodel", "zzz-unknown")
    assert coeff is None
    assert source is None
