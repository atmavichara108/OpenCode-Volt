"""Минимальный OpenAI-compatible клиент на urllib (без requests/httpx).

``chat()`` делает один non-streaming запрос к ``/chat/completions``, возвращает
(reply_text, usage, latency_ms, error). Стоимость оценивается детерминированными
коэффициентами (см. ``estimate_cost_usd``). Ключ никогда не логируется и не
попадает в ошибки — всё прогоняется через ``redact``.
"""
import json
import logging
import time
import urllib.error
import urllib.request

import config  # noqa: F401  (переиспользуем redact/build_opener)

log = logging.getLogger("model-bench")

RETRY_COUNT = 2
RETRY_PAUSE_SECONDS = 2.0

# Таблица известных коэффициентов стоимости: (base_usd_per_1M, multiplier).
# unknown → None (в артефакт попадёт cost_usd_est: null).
COST_BASE_USD_PER_1M = 0.05
COST_COEFFICIENTS = {
    ("anymodel", "am/free"): 0,
    ("anymodel", "am/nemotron"): 0,  # любой am/nemotron* (свободный)
    ("anymodel", "cx/gpt-6-astra"): 8,
    ("anymodel", "cc/claude-opus-5"): 6,
    ("anymodel", "cx/gpt-5.6-sol"): 4,
    ("anymodel", "kmc/k3"): 3,
    # Коэффициенты ниже сверены с billing.coefficient API 2026-09-25.
    ("anymodel", "cx/gpt-6-sol"): 4,
    ("anymodel", "cx/gpt-6-luna"): 1.5,
    ("anymodel", "cc/claude-opus-5-5"): 6,
    ("anymodel", "cc/claude-sonnet-5"): 3,
    ("anymodel", "kmc/kimi-for-coding"): 1.5,
    ("amd-radeon", None): 0,  # весь провайдер — free tier
}

# Наблюдаемые множители расхода токенов (факт/оценка) по моделям.
# Значения измерены 2026-09-24 полным прогоном 4 гейтов k=1 и являются
# эмпирическими, а НЕ гарантией: предсказание всегда неточно (разброс
# 0.74×..36×). Основная защита бюджета — принудительный останов по
# фактическому расходу (bench.py), а не этот множитель.
OBSERVED_TOKEN_MULTIPLIER = {
    ("anymodel", "cx/gpt-5.6-sol"): 0.8,
    ("anymodel", "kmc/k3"): 1.5,
    ("anymodel", "am/nemotron"): 8.0,
    ("anymodel", "am/free"): 9.0,
    ("anymodel", "cx/gpt-6-astra"): 10.5,
    ("anymodel", "cc/claude-opus-5"): 36.5,
    # Ниже — ПРЕДПОЛОЖЕНИЕ по семейству (не замер), подлежит уточнению
    # после первого прогона.
    ("anymodel", "cx/gpt-6-sol"): 1.7,      # по аналогии с cx/gpt-6-astra
    ("anymodel", "cx/gpt-6-luna"): 3.5,     # то же семейство gen-6
    ("anymodel", "cc/claude-opus-5-5"): 36.5, # opus-семейство, замер opus-5
    ("anymodel", "cc/claude-sonnet-5"): 4.4, # claude не-opus, оценка сверху
    ("anymodel", "kmc/kimi-for-coding"): 1.5, # по аналогии с kmc/k3
}
DEFAULT_TOKEN_MULTIPLIER = 4.0  # неизвестная модель: консервативно выше 1


def _coefficient(provider_id, model_id):
    """Возвращает коэффициент стоимости или None, если модель неизвестна."""
    if provider_id == "amd-radeon":
        return 0
    key = (provider_id, model_id)
    if key in COST_COEFFICIENTS:
        return COST_COEFFICIENTS[key]
    if provider_id == "anymodel" and model_id.startswith("am/nemotron"):
        return 0
    return None


def token_multiplier(provider_id, model_id):
    """Наблюдаемый множитель расхода токенов (факт/оценка) или дефолт.

    Точное совпадение → измеренное значение; ``anymodel`` + ``am/nemotron*``
    → 8.0; иначе ``DEFAULT_TOKEN_MULTIPLIER``.
    """
    key = (provider_id, model_id)
    if key in OBSERVED_TOKEN_MULTIPLIER:
        return OBSERVED_TOKEN_MULTIPLIER[key]
    if provider_id == "anymodel" and model_id.startswith("am/nemotron"):
        return 8.0
    return DEFAULT_TOKEN_MULTIPLIER


def estimate_cost_usd(provider_id, model_id, usage):
    """Оценка стоимости в USD по использованию токенов.

    Возвращает float или None (неизвестная модель — не выдумываем цену).
    """
    coeff = _coefficient(provider_id, model_id)
    if coeff is None:
        return None
    total = (usage or {}).get("total_tokens", 0)
    return COST_BASE_USD_PER_1M * coeff * total / 1_000_000


def chat(base_url, key, model, prompt, max_tokens, timeout=120, proxies=None):
    """Один запрос к chat/completions.

    Возвращает (reply_text, usage_dict, latency_ms, error). ``error`` — пустая
    строка при успехе, иначе структурное сообщение (без ключа). При сетевой
    ошибке/5xx — до RETRY_COUNT повторов с паузой; 4xx — сразу ошибка.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "User-Agent": "opencode-vault-model-bench/0.1",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    }
    opener = config.build_opener(proxies)

    last_err = ""
    for attempt in range(RETRY_COUNT + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            start = time.monotonic()
            resp = opener.open(req, timeout=timeout) if opener else urllib.request.urlopen(req, timeout=timeout)
            latency_ms = int((time.monotonic() - start) * 1000)
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            reply = _extract_reply(data)
            usage = data.get("usage") or {}
            return reply, usage, latency_ms, ""
        except urllib.error.HTTPError as exc:
            code = exc.code
            if 400 <= code < 500:
                return "", {}, 0, _http_error(exc, key)
            last_err = _http_error(exc, key)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = "network error: " + _redact_str(exc, key)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            last_err = "parse error: " + _redact_str(exc, key)
        if attempt < RETRY_COUNT:
            time.sleep(RETRY_PAUSE_SECONDS)

    return "", {}, 0, last_err or "unknown error"


def _extract_reply(data):
    """Достаёт текст ответа из choices[0].message.content."""
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    return msg.get("content") or ""


def _redact_str(exc, key):
    return config.redact(str(exc), key)


def _http_error(exc, key):
    body = ""
    try:
        body = exc.read().decode("utf-8", errors="replace")[:500]
    except Exception:  # noqa: BLE001
        body = ""
    msg = f"HTTP {exc.code}: {body}"
    return config.redact(msg, key)


def emit_telemetry(record):
    """Заглушка телеметрии баланса (reserved slot, см. README §Ограничения).

    TODO(будущая сессия): писать append-only в
    ``control-plane/telemetry/provider-usage.jsonl`` со схемой из спеки §8.
    Сейчас — no-op, чтобы bench-прогоны не зависели от этого контура.
    """
    return None
