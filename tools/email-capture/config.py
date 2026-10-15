"""Конфигурация модуля email-capture.

Загружает `.env` из директории скрипта (не из cwd) и определяет:
- IMAP-параметры подключения (хост/порт/логин/app password);
- папки ящика, путь state-файла, дефолтный limit;
- `INTENT_PHRASES` — контрольные фразы по шести интентам вайбкодинга;
- `INTENT_NAMES` / `CHOICES` — для argparse.

Всё живёт здесь и в `.env`, не в логике capture/classifier (DoD спеки).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Директория модуля — точка отсчёта для .env и относительных путей,
# чтобы запуск из любого cwd давал один и тот же результат.
MODULE_DIR = Path(__file__).resolve().parent

# .env из директории скрипта; отсутствие файла — не ошибка (дефолты работают).
load_dotenv(MODULE_DIR / ".env")


def _env(name: str, default: str) -> str:
    val = os.getenv(name)
    return default if val is None or val == "" else val


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _resolve_path(raw: str) -> Path:
    """Относительный путь (`.state/...`) трактуем отсительно модуля."""
    p = Path(raw)
    return p if p.is_absolute() else (MODULE_DIR / p)


# --- IMAP / ящик -----------------------------------------------------------
IMAP_HOST = _env("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = _env_int("IMAP_PORT", 993)
IMAP_USER = _env("IMAP_USER", "")
IMAP_PASS = _env("IMAP_PASS", "")

# --- Папки / выборка -------------------------------------------------------
# CSV-список папок по умолчанию; `--all` обходит всё, что отдал LIST().
FOLDERS = [f.strip() for f in _env("FOLDERS", "INBOX").split(",") if f.strip()]
STATE_PATH = _resolve_path(_env("STATE_PATH", ".state/processed.jsonl"))
DEFAULT_LIMIT = _env_int("DEFAULT_LIMIT", 50)

# --- idea-graph (куда дописывать интенты) ----------------------------------
# Корень волта = две директории вверх от модуля (tools/email-capture → vault).
VAULT_ROOT = MODULE_DIR.parent.parent
GRAPH_DIR = _resolve_path(_env("GRAPH_DIR", str(VAULT_ROOT / "04-Memory/idea-graph")))
NODES_PATH = _resolve_path(_env("NODES_PATH", str(GRAPH_DIR / "nodes.jsonl")))
EDGES_PATH = _resolve_path(_env("EDGES_PATH", str(GRAPH_DIR / "edges.jsonl")))
VALIDATOR_PATH = _resolve_path(
    _env("VALIDATOR_PATH", str(VAULT_ROOT / "tools/idea-graph/validate.mjs"))
)
# Узел-источник Gmail уже существует в графе — ребро всегда целится в него.
EMAIL_SOURCE_NODE = _env("EMAIL_SOURCE_NODE", "world-source-email-gmail")

# --- Интенты ---------------------------------------------------------------
# Каскад в порядке проверки (см. classifier): error/noise → интенты → default.
INTENT_NAMES = [
    "research",
    "implementation",
    "correction",
    "projects",
    "subscriptions",
]
DEFAULT_INTENT = "default"
ERROR_INTENT = "error"
# CHOICES для argparse-фильтров (интенты + служебные исходы классификации).
CHOICES = [*INTENT_NAMES, DEFAULT_INTENT, ERROR_INTENT]

# Контрольные фразы (RU/EN) по интентам спеки. Ключи INTENT_NAMES + error.
# Переопределяются env'ом PHRASES_<INTENT> через запятую, напр.
#   PHRASES_RESEARCH=обзор,benchmark,landscape
INTENT_PHRASES: dict[str, list[str]] = {
    "research": [
        "исследование",
        "research",
        "изучить",
        "сравнить",
        "обзор",
        "тренды",
        "benchmark",
        "state of",
        "landscape",
    ],
    "implementation": [
        "внедрение",
        "реализация",
        "implement",
        "портировать",
        "интеграция",
        "подключить",
        "адаптировать",
        "roadmap",
        "спека",
        "spec",
    ],
    "correction": [
        "коррекция",
        "исправить",
        "отменить",
        "канон-коррекция",
        "уточнить",
        "вердикт",
        "ратифицировать",
        "пересмотреть",
        "correct",
        "revert",
        "amend",
    ],
    "projects": [
        "проект",
        "project",
        "vibeos",
        "opencode",
        "dotfiles",
        "serplux",
        "dv-hub",
        "репо",
        "github.com/",
    ],
    "subscriptions": [
        "подписка",
        "subscribe",
        "newsletter",
        "рассылка",
        "digest",
        "weekly",
        "follow",
        "notify",
    ],
    # error/noise — высший приоритет: перебивает интент-фразы в том же тексте.
    ERROR_INTENT: [
        "unsubscribe",
        "спам",
        "реклама",
        "promo",
        "выписка",
        "квитанци",
        "no-reply",
        "notifications@",
    ],
}

# env-переопределение фраз: PHRASES_<INTENT_IN_UPPER_CASE>=фраза,фраза,...
for _intent in list(INTENT_PHRASES):
    _override = os.getenv(f"PHRASES_{_intent.upper()}")
    if _override:
        _phrases = [p.strip().lower() for p in _override.split(",") if p.strip()]
        if _phrases:
            INTENT_PHRASES[_intent] = _phrases

# Порядок каскада интентов (без error — он всегда первый).
CASCADE = [ERROR_INTENT, *INTENT_NAMES]
