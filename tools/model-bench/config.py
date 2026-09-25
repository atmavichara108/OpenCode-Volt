"""Конфигурация модуля model-bench.

Резолвит провайдера (baseURL + модели) из opencode-конфигов, ключ из
env/.env/auth.json, строит proxy-dict для urllib. Ключ никогда не логируется
и не попадает в артефакты — все сообщения об ошибках прогоняются через
``redact``.
"""
import json
import logging
import os
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

BENCHMARK_VERSION = "0.1.0"

# Маппинг provider_id → имя env-переменной с ключом (порядок приоритета №1).
PROVIDER_ENV = {
    "anymodel": "ANYMODEL_API_KEY",
    "amd-radeon": "AMD_RADEON_API_KEY",
    "linaliapi": "LINALIAPI_API_KEY",
    "apinex": "APINEX_API_KEY",
}

# Порог бюджета на один стандартный прогон (k=1).
COST_GUARD_USD = 0.05
DEFAULT_MAX_TOKENS = 512

# Пути opencode-конфигов (порядок чтения baseURL/models).
CONFIG_PATHS = [
    Path.home() / ".config" / "opencode" / "opencode.jsonc",
    Path.home() / ".local" / "share" / "m-code-data" / "config" / "opencode.jsonc",
]

AUTH_JSON_PATH = Path.home() / ".local" / "share" / "opencode" / "auth.json"

# Корень волта (tools/model-bench -> ../../) для поиска .env.
VAULT_ROOT = Path(__file__).resolve().parent.parent.parent

log = logging.getLogger("model-bench")


def strip_jsonc_comments(text):
    """Снимает ``//`` line-комментарии из JSONC, не трогая ``//`` в строках.

    Символ ``//`` вырезается только если он встречается **вне кавычек** —
    иначе ``https://...`` внутри значений поломал бы парсинг. Проход по
    символам с отслеживанием состояния строки (одинарные/двойные кавычки,
    экранирование ``\\``).
    """
    out = []
    i = 0
    n = len(text)
    in_str = False
    quote = None
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                in_str = False
                quote = None
            i += 1
            continue
        # вне строки
        if ch in ('"', "'"):
            in_str = True
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            # line-комментарий — пропускаем до конца строки
            while i < n and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _load_jsonc(path):
    """Читает JSONC-файл и возвращает dict; при ошибке/отсутствии — None."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        raw = p.read_text(encoding="utf-8")
        return json.loads(strip_jsonc_comments(raw))
    except (OSError, json.JSONDecodeError) as exc:  # noqa: BLE001
        log.warning("Не удалось прочитать конфиг %s: %s", p, exc)
        return None


def resolve_provider(provider_id):
    """Возвращает (baseURL, [model_ids]) для провайдера или (None, []).

    Читает opencode-конфиги по порядку CONFIG_PATHS, берёт первый найденный
    провайдер. Возвращает ``provider.<id>.options.baseURL`` и список ID моделей
    из ``provider.<id>.models``.
    """
    for path in CONFIG_PATHS:
        cfg = _load_jsonc(path)
        if not cfg:
            continue
        providers = cfg.get("provider") or {}
        prov = providers.get(provider_id)
        if not prov:
            continue
        options = prov.get("options") or {}
        base_url = options.get("baseURL")
        models = list((prov.get("models") or {}).keys())
        if base_url:
            return base_url, models
    return None, []


def resolve_key(provider_id):
    """Возвращает API-ключ провайдера или "" (пустую строку).

    Порядок приоритетов:
      1. env-переменная из PROVIDER_ENV;
      2. ``.env`` в корне волта (python-dotenv);
      3. ``auth.json`` → ``.<provider_id>.key``.
    """
    env_var = PROVIDER_ENV.get(provider_id)
    if env_var:
        val = os.getenv(env_var)
        if val:
            return val

    load_dotenv(VAULT_ROOT / ".env")
    if env_var:
        val = os.getenv(env_var)
        if val:
            return val

    auth = _load_auth_json()
    if auth:
        entry = auth.get(provider_id) or {}
        val = entry.get("key")
        if val:
            return val
    return ""


def _load_auth_json():
    """Читает auth.json (строгий JSON, не JSONC)."""
    p = Path(AUTH_JSON_PATH)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:  # noqa: BLE001
        log.warning("Не удалось прочитать auth.json: %s", exc)
        return None


def redact(text, key):
    """Заменяет вхождения ``key`` в ``text`` на ``***REDACTED***``."""
    if not key or not text:
        return text
    return text.replace(key, "***REDACTED***")


def proxies_from_env():
    """Строит dict прокси для urllib ProxyHandler или None.

    Читает HTTPS_PROXY/HTTP_PROXY/ALL_PROXY. Схема ``socks5h://`` (и прочие
    socks) urllib не поддерживает — такие переменные игнорируются с warning
    (уже ловили это с M Code).
    """
    result = {}
    for scheme, var in (("https", "HTTPS_PROXY"), ("http", "HTTP_PROXY")):
        val = os.getenv(var) or ""
        if not val and var == "HTTPS_PROXY":
            val = os.getenv("ALL_PROXY") or ""
        if not val:
            continue
        low = val.lower()
        if low.startswith("socks"):
            log.warning(
                "Прокси %s использует socks-схему, urllib её не поддерживает — игнорирую.",
                var,
            )
            continue
        result[scheme] = val
    if not result:
        return None
    return result


def build_opener(proxies):
    """Возвращает urllib OpenerDirector с прокси (если заданы) или None."""
    if not proxies:
        return None
    handler = urllib.request.ProxyHandler(proxies)
    return urllib.request.build_opener(handler)
