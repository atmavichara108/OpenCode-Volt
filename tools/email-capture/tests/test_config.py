"""Тесты config.py — дефолты без .env и полнота .env.example (приёмка S1)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import config
from conftest import MODULE_DIR

ENV_EXAMPLE = MODULE_DIR / ".env.example"


def test_defaults_without_env():
    """`import config` даёт дефолты, даже если .env отсутствует."""
    assert config.IMAP_HOST == "imap.gmail.com"
    assert config.IMAP_PORT == 993
    assert config.DEFAULT_LIMIT > 0
    assert config.FOLDERS == ["INBOX"]
    assert config.STATE_PATH.name == "processed.jsonl"
    assert config.STATE_PATH.is_absolute()


def test_intent_phrases_cover_six_intents():
    assert set(config.INTENT_PHRASES) == {*config.INTENT_NAMES, "error"}
    assert config.CASCADE[0] == "error"  # error/noise — высший приоритет
    assert config.CASCADE[1:] == config.INTENT_NAMES
    for phrases in config.INTENT_PHRASES.values():
        assert phrases, "список фраз пуст"


def test_env_example_covers_every_variable():
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    declared = set(re.findall(r"^\s*#?\s*([A-Z][A-Z0-9_]*)=", text, re.M))
    used = set(
        re.findall(r'_env(?:_int)?\(\s*"([A-Z][A-Z0-9_]*)"', (MODULE_DIR / "config.py").read_text(encoding="utf-8"))
    )
    missing = used - declared
    assert not missing, f".env.example не покрывает: {sorted(missing)}"


def test_phrases_env_override():
    script = (
        "import json, config;"
        "print(json.dumps(config.INTENT_PHRASES['research'], ensure_ascii=False))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(MODULE_DIR),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "PHRASES_RESEARCH": "гипотеза,выборка"},
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == '["гипотеза", "выборка"]'
