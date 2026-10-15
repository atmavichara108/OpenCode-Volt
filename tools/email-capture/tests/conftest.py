"""Общие фикстуры email-capture.

- sys.path: модули (config/classifier/...) импортируются из корня инструмента;
- sandbox: тестовые графы/state живут ТОЛЬКО в /tmp/opencode — против
  прод-графа 04-Memory/idea-graph ничего не валидируется и не пишется.
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid
from email.message import EmailMessage
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Песочница строго вне репозитория (спека S6).
SANDBOX_ROOT = Path("/tmp/opencode/email-capture-tests")


@pytest.fixture
def sandbox() -> Path:
    """Пустой sandbox-каталог на время теста (удаляется после)."""
    path = SANDBOX_ROOT / f"case-{uuid.uuid4().hex[:10]}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def make_email(
    subject: str,
    body: str,
    message_id: str,
    date: str = "Wed, 07 Oct 2026 10:00:00 +0000",
    html: str | None = None,
) -> bytes:
    """RFC822-байты тестового письма для мока IMAP."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "sender@example.com"
    msg["To"] = "rudra@example.com"
    msg["Message-ID"] = message_id
    msg["Date"] = date
    if html:
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(body)
    return msg.as_bytes()


def seed_graph(nodes_path: Path, edges_path: Path) -> dict:
    """Сид прод-подобного состояния: существующий источник, узел и ребро.

    Возвращает номера, которые writer обязан продолжить (не дублировать).
    """
    nodes = [
        {
            "id": "world-source-email-gmail",
            "graph": "world",
            "kind": "source",
            "label": "Email (Gmail)",
            "status": "raw",
            "provenance": {
                "source": "current-dialogue:user-request",
                "observed_at": "2026-10-08",
                "scope": "signal-flow:email-source",
                "basis": "quoted",
            },
            "projection": ["index"],
        },
        {
            "id": "stream-intent-017",
            "graph": "stream",
            "kind": "intent",
            "label": "Сидовый узел",
            "status": "candidate",
            "resolution": "deferred",
            "provenance": {
                "source": "email:gmail",
                "observed_at": "2026-10-01",
                "scope": "signal-flow:email-source",
                "basis": "quoted",
            },
            "projection": ["index"],
        },
    ]
    edges = [
        {
            "id": "e-0042",
            "graph": "stream",
            "from": "stream-intent-017",
            "to": "world-source-email-gmail",
            "type": "announces",
            "status": "candidate",
            "provenance": {
                "source": "email:gmail",
                "observed_at": "2026-10-01",
                "scope": "signal-flow:email-source",
                "basis": "quoted",
            },
        }
    ]
    nodes_path.write_text(
        "".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes),
        encoding="utf-8",
    )
    edges_path.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges),
        encoding="utf-8",
    )
    return {"next_intent": 18, "next_edge": 43}
