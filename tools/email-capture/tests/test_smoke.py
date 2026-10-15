"""Живой прогон по реальному IMAP — только под маркером `smoke`.

    pytest -m smoke

Без заполненного .env (IMAP_USER/IMAP_PASS) тест пропускается: сеть и
credentials в обычном прогоне `pytest` не используются.
"""
from __future__ import annotations

import json

import pytest

import capture
import config

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(
        not (config.IMAP_USER and config.IMAP_PASS),
        reason="живой аккаунт не настроен: заполни .env (см. README)",
    ),
]


def test_live_list_folders():
    client = capture.ImapClient()
    try:
        client.connect()
        folders = client.list_folders()
    finally:
        client.close()
    assert "INBOX" in folders


def test_live_dry_run_smoke(capsys):
    rc = capture.main(["--folder", "INBOX", "--dry-run", "--limit", "3"])
    out = capsys.readouterr().out
    assert rc == 0
    assert isinstance(json.loads(out), list)  # JSON на stdout, логи на stderr
