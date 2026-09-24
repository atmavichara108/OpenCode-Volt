"""Тесты config.py: JSONC-парсинг, resolve_key, redact, socks5h."""
import config


def test_strip_jsonc_keeps_https_url():
    text = '{"options": {"baseURL": "https://anymodel.org/v1"}, "x": 1} // comment'
    stripped = config.strip_jsonc_comments(text)
    assert "https://anymodel.org/v1" in stripped
    assert "// comment" not in stripped


def test_strip_jsonc_removes_only_line_comments():
    text = '{"a": 1}\n// comment line\n{"b": 2}'
    assert "// comment line" not in config.strip_jsonc_comments(text)


def test_strip_jsonc_keeps_inline_url_inside_string():
    text = '{"u": "https://x.y/a//b"}'
    assert config.strip_jsonc_comments(text) == text


def test_resolve_key_env_first(monkeypatch):
    monkeypatch.setenv("ANYMODEL_API_KEY", "env-secret")
    assert config.resolve_key("anymodel") == "env-secret"


def test_redact_hides_key():
    assert config.redact("Bearer abc123 token", "abc123") == "Bearer ***REDACTED*** token"


def test_redact_no_key_noop():
    assert config.redact("hello", "") == "hello"


def test_proxies_socks5h_ignored_with_warning(monkeypatch, caplog):
    monkeypatch.setenv("HTTPS_PROXY", "socks5h://127.0.0.1:9050")
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("ALL_PROXY", raising=False)
    import logging

    with caplog.at_level(logging.WARNING):
        result = config.proxies_from_env()
    assert result is None
    assert any("socks" in r.message for r in caplog.records)


def test_proxies_http_ok(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy:8080")
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("ALL_PROXY", raising=False)
    result = config.proxies_from_env()
    assert result is not None
    assert result.get("https") == "http://proxy:8080"


def test_proxies_none_when_unset(monkeypatch):
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("ALL_PROXY", raising=False)
    assert config.proxies_from_env() is None


def test_resolve_provider_from_jsonc(monkeypatch, tmp_path):
    cfg = tmp_path / "opencode.jsonc"
    cfg.write_text(
        '{"provider": {"anymodel": {"options": {"baseURL": "https://anymodel.org/v1"},'
        ' "models": {"am/free": {}, "cx/gpt-6-astra": {}}}}} // trailing\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "CONFIG_PATHS", [cfg])
    base_url, models = config.resolve_provider("anymodel")
    assert base_url == "https://anymodel.org/v1"
    assert models == ["am/free", "cx/gpt-6-astra"]


def test_resolve_key_env_order(monkeypatch, tmp_path):
    monkeypatch.delenv("ANYMODEL_API_KEY", raising=False)
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    (tmp_path / ".env").write_text("ANYMODEL_API_KEY=dotenv-secret\n", encoding="utf-8")
    assert config.resolve_key("anymodel") == "dotenv-secret"
