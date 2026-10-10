"""Тесты capture.py — dry-run CLI на моке imaplib (без сети и credentials).

Проверяется контракт спеки S2:
- `--dry-run` печатает JSON писем и НЕ пишет ни state, ни idea-graph;
- `--all` обходит все папки, включая `[Gmail]/All Mail`;
- пустой результат → `[]` и exit 0;
- обычный прогон пишет интенты в (sandbox-)граф и помечает state,
  повторный запуск тех же писем не возвращает.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import capture
import config
import state
from conftest import make_email, seed_graph


class FakeImap:
    """Мок ImapClient: папки → списки RFC822-байтов, без сети."""

    def __init__(
        self,
        mailboxes: dict[str, list[bytes]] | None = None,
        broken: tuple[str, ...] = (),
        **_kw,
    ) -> None:
        self.mailboxes = mailboxes or {}
        self.broken = set(broken)
        self._current: str | None = None
        self.connected = False
        self.closed = False

    def connect(self) -> None:
        self.connected = True

    def close(self) -> None:
        self.closed = True

    def list_folders(self) -> list[str]:
        return list(self.mailboxes)

    def select(self, folder: str) -> int:
        if folder in self.broken:
            raise RuntimeError(f"SELECT failed: {folder}")
        if folder not in self.mailboxes:
            raise RuntimeError(f"no such folder: {folder}")
        self._current = folder
        return len(self.mailboxes[folder])

    def search(self, since: str | None = None) -> list[str]:
        assert self._current is not None, "SELECT до SEARCH"
        return [str(i).encode() for i in range(1, len(self.mailboxes[self._current]) + 1)]

    def fetch_raw(self, num: bytes | str) -> bytes:
        assert self._current is not None, "SELECT до FETCH"
        return self.mailboxes[self._current][int(num) - 1]


@pytest.fixture
def env(sandbox: Path, monkeypatch):
    """Песочница для state и графа + мок IMAP-клиента."""
    nodes = sandbox / "nodes.jsonl"
    edges = sandbox / "edges.jsonl"
    seed_graph(nodes, edges)
    monkeypatch.setattr(config, "STATE_PATH", sandbox / "state" / "processed.jsonl")
    monkeypatch.setattr(config, "NODES_PATH", nodes)
    monkeypatch.setattr(config, "EDGES_PATH", edges)
    return {"dir": sandbox, "nodes": nodes, "edges": edges}


def _patch_client(monkeypatch, mailboxes: dict[str, list[bytes]]) -> FakeImap:
    fake = FakeImap(mailboxes)
    monkeypatch.setattr(capture, "ImapClient", lambda *a, **k: fake)
    return fake


def _read_json(capsys) -> list[dict]:
    return json.loads(capsys.readouterr().out)


def test_dry_run_prints_json_without_writing(env, monkeypatch, capsys):
    mail = {
        "INBOX": [
            make_email("Исследование трендов", "сравнить и сделать обзор", "<1@x>"),
            make_email("Ваша подписка", "newsletter digest недели", "<2@x>"),
            make_email("Спам-письмо", "unsubscribe", "<3@x>"),
        ]
    }
    fake = _patch_client(monkeypatch, mail)

    rc = capture.main(["--folder", "INBOX", "--dry-run"])
    out = _read_json(capsys)

    assert rc == 0
    assert [m["intent"] for m in out] == ["research", "subscriptions", "error"]
    assert out[0]["message_id"] == "<1@x>"
    assert out[0]["subject"]
    # dry-run: ни state, ни idea-graph
    assert not config.STATE_PATH.exists()
    assert len(env["nodes"].read_text(encoding="utf-8").splitlines()) == 2
    assert fake.connected and fake.closed


def test_dry_run_twice_returns_same(env, monkeypatch, capsys):
    mail = {"INBOX": [make_email("Обзор рынка", "исследование подходов", "<1@x>")]}
    _patch_client(monkeypatch, mail)

    capture.main(["--folder", "INBOX", "--dry-run"])
    first = _read_json(capsys)
    capture.main(["--folder", "INBOX", "--dry-run"])
    second = _read_json(capsys)

    assert first == second  # state не растёт в dry-run → выборка стабильна
    assert not config.STATE_PATH.exists()


def test_all_folders_including_gmail_all_mail(env, monkeypatch, capsys):
    mail = {
        "INBOX": [make_email("Письмо в инбоксе", "исследование", "<1@x>")],
        "[Gmail]/All Mail": [
            make_email("Письмо в инбоксе", "исследование", "<1@x>"),  # дубль из архива
            make_email("Статус проекта", "обновление в репо", "<2@x>"),
        ],
        "[Gmail]/Spam": [],
    }
    fake = _patch_client(monkeypatch, mail)

    rc = capture.main(["--all", "--dry-run", "--limit", "10"])
    out = _read_json(capsys)

    assert rc == 0
    assert set(fake.mailboxes) == {"INBOX", "[Gmail]/All Mail", "[Gmail]/Spam"}
    # одно и то же письмо в INBOX и All Mail → одна запись
    assert sorted(m["message_id"] for m in out) == ["<1@x>", "<2@x>"]


def test_empty_result_is_empty_json_exit_zero(env, monkeypatch, capsys):
    _patch_client(monkeypatch, {"INBOX": []})
    rc = capture.main(["--folder", "INBOX", "--dry-run"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "[]"


def test_limit_caps_total(env, monkeypatch, capsys):
    mail = {"INBOX": [make_email(f"Письмо {i}", "исследование рынка", f"<{i}@x>") for i in range(5)]}
    _patch_client(monkeypatch, mail)
    rc = capture.main(["--folder", "INBOX", "--dry-run", "--limit", "2"])
    out = _read_json(capsys)
    assert rc == 0
    assert len(out) == 2


def test_bad_since_date_is_friendly_error(env, monkeypatch, capsys):
    _patch_client(monkeypatch, {"INBOX": []})
    rc = capture.main(["--folder", "INBOX", "--dry-run", "--since", "07.10.2026"])
    assert rc == 2
    assert "--since" in capsys.readouterr().err


def test_missing_credentials_friendly_error(env, monkeypatch, capsys):
    monkeypatch.setattr(config, "IMAP_USER", "")
    monkeypatch.setattr(config, "IMAP_PASS", "")
    rc = capture.main(["--folder", "INBOX", "--dry-run"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "IMAP_USER/IMAP_PASS" in err


def test_run_writes_graph_and_state_then_idempotent(env, monkeypatch, capsys):
    mail = {
        "INBOX": [
            make_email("Исследование подходов", "сравнить и сделать обзор", "<1@x>"),
            make_email("План внедрения", "реализация спеки", "<2@x>"),
            make_email("Реклама дня", "unsubscribe", "<3@x>"),
        ]
    }
    _patch_client(monkeypatch, mail)

    rc = capture.main(["--folder", "INBOX", "--limit", "10"])
    out = _read_json(capsys)
    assert rc == 0
    assert len(out) == 3

    node_lines = [l for l in env["nodes"].read_text(encoding="utf-8").splitlines() if l.strip()]
    edge_lines = [l for l in env["edges"].read_text(encoding="utf-8").splitlines() if l.strip()]
    # сид (2 узла) + 2 интента; error-шум в граф не попадает
    assert len(node_lines) == 4
    assert len(edge_lines) == 3
    new_node = json.loads(node_lines[-1])
    assert new_node["id"] == "stream-intent-019"
    assert new_node["graph"] == "stream"
    new_edge = json.loads(edge_lines[-1])
    assert new_edge["type"] == "announces"
    assert new_edge["to"] == "world-source-email-gmail"

    assert state.is_processed(
        {"message_id": "<1@x>", "subject": "x", "body": "y"}, config.STATE_PATH
    )

    # повторный запуск: новых писем нет, граф и state не растут
    rc2 = capture.main(["--folder", "INBOX", "--limit", "10"])
    out2 = _read_json(capsys)
    assert rc2 == 0
    assert out2 == []
    assert len([l for l in env["nodes"].read_text(encoding="utf-8").splitlines() if l.strip()]) == 4
    assert len([l for l in env["edges"].read_text(encoding="utf-8").splitlines() if l.strip()]) == 3


def test_invalid_folder_skipped_not_fatal(env, monkeypatch, capsys):
    mail = {"INBOX": [make_email("Обзор", "исследование", "<1@x>")], "Trash": []}
    fake = FakeImap(mail, broken=("Trash",))
    monkeypatch.setattr(capture, "ImapClient", lambda *a, **k: fake)
    rc = capture.main(["--all", "--dry-run"])
    out = _read_json(capsys)
    assert rc == 0
    assert [m["message_id"] for m in out] == ["<1@x>"]
    assert fake.closed
