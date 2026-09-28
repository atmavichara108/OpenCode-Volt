"""Минимальный OpenAI-compatible клиент на urllib (без requests/httpx).

``chat()`` делает один non-streaming запрос к ``/chat/completions``, возвращает
(reply_text, usage, latency_ms, error). Стоимость оценивается детерминированными
коэффициентами (см. ``estimate_cost_usd``). Ключ никогда не логируется и не
попадает в ошибки — всё прогоняется через ``redact``.
"""
import http.client
import json
import logging
import time
import urllib.error
import urllib.request

import config  # noqa: F401  (переиспользуем redact/build_opener)

log = logging.getLogger("model-bench")

RETRY_COUNT = 2
RETRY_PAUSE_SECONDS = 2.0
RETRY_429_PAUSE_SECONDS = 20.0

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
    ("apinex", None): 0,  # весь провайдер — free tier
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

# Провайдеры с доказанным завышением usage: панель биллинга — истина, а
# cost_usd_est (считается от raw usage) помечается как оценочный. Решения о
# деньгах принимаются по tokens_estimated, а не по raw usage.
KNOWN_INFLATED_USAGE = {"anymodel"}


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
    if provider_id == "apinex" and model_id.startswith("free/"):
        return 1.0
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


def resolve_coefficient(provider, model, base_url=None, key=None, proxies=None, cli_price=None):
    """Возвращает (coeff|None, source) коэффициента стоимости модели.

    Приоритет источника:
      1. ``table`` — таблица ``COST_COEFFICIENTS`` (+ free-tier правила
         amd-radeon / anymodel am/nemotron*);
      2. ``cli_price`` — флаг ``--price-per-1m`` (абсолют USD/1M → coeff =
         price / ``COST_BASE_USD_PER_1M``);
      3. ``live`` — живой ``GET /models`` (billing.coefficient или pricing);
      4. ``None`` — цена не выдумывается (fetch-ошибка/неизвестная модель).
    """
    coeff = _coefficient(provider, model)
    if coeff is not None:
        return coeff, "table"
    if cli_price is not None:
        return cli_price / COST_BASE_USD_PER_1M, "cli_price"
    if base_url and key:
        coeff = _fetch_coefficient(base_url, key, proxies)
        if coeff is not None:
            return coeff, "live"
    return None, None


def _fetch_coefficient(base_url, key, proxies):
    """Живой ``GET /models`` → коэффициент стоимости или None.

    Парсит два формата:
      - anymodel-стиль: ``billing.coefficient.input/output`` (коэффициенты,
        берём max);
      - абсолют: ``pricing.prompt/completion`` (USD/1M, берём max и делим на
        ``COST_BASE_USD_PER_1M``).
    Любая сетевая/парсинговая ошибка → None (цену не выдумываем).
    """
    url = base_url.rstrip("/") + "/models"
    headers = {
        "User-Agent": "opencode-vault-model-bench/0.1",
        "Authorization": "Bearer " + key,
    }
    try:
        opener = config.build_opener(proxies)
        req = urllib.request.Request(url, headers=headers, method="GET")
        resp = (
            opener.open(req, timeout=30)
            if opener
            else urllib.request.urlopen(req, timeout=30)
        )
        raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None

    billing = (data.get("billing") or {}).get("coefficient") or {}
    if isinstance(billing, dict):
        vals = [
            float(v)
            for v in (billing.get("input"), billing.get("output"))
            if isinstance(v, (int, float))
        ]
        if vals:
            return max(vals)

    pricing = data.get("pricing") or {}
    if isinstance(pricing, dict):
        vals = [
            float(v)
            for v in (pricing.get("prompt"), pricing.get("completion"))
            if isinstance(v, (int, float))
        ]
        if vals:
            return max(vals) / COST_BASE_USD_PER_1M
    return None


def chat(base_url, key, model, prompt, max_tokens, timeout=120, proxies=None):
    """Один запрос к chat/completions.

    Возвращает ``(reply_text, usage_dict, latency_ms, error, finish_reason)``.
    ``error`` — пустая строка при успехе, иначе структурное сообщение (без
    ключа); ``finish_reason`` — ``choices[0].finish_reason`` (OpenAI-стиль)
    или None. При сетевой ошибке/5xx/429 — до RETRY_COUNT повторов с паузой
    (для 429 — RETRY_429_PAUSE_SECONDS); прочие 4xx — сразу ошибка.
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
    last_pause = RETRY_PAUSE_SECONDS
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
            finish_reason = _extract_finish_reason(data)
            return reply, usage, latency_ms, "", finish_reason
        except urllib.error.HTTPError as exc:
            code = exc.code
            if code == 429:
                # 429 — ретраим (rate limit может сброситься), отдельная пауза.
                last_err = _http_error(exc, key)
                last_pause = RETRY_429_PAUSE_SECONDS
            elif 400 <= code < 500:
                return "", {}, 0, _http_error(exc, key), None
            else:
                last_err = _http_error(exc, key)
                last_pause = RETRY_PAUSE_SECONDS
        except http.client.HTTPException as exc:
            # BadStatusLine / IncompleteRead / ResponseNotReady — сетевые сбои,
            # ретраим как network (не падение процесса).
            last_err = "network error: " + _redact_str(exc, key)
            last_pause = RETRY_PAUSE_SECONDS
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = "network error: " + _redact_str(exc, key)
            last_pause = RETRY_PAUSE_SECONDS
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            last_err = "parse error: " + _redact_str(exc, key)
            last_pause = RETRY_PAUSE_SECONDS
        if attempt < RETRY_COUNT:
            time.sleep(last_pause)

    return "", {}, 0, last_err or "unknown error", None


def _extract_reply(data):
    """Достаёт текст ответа из choices[0].message.content."""
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    return msg.get("content") or ""


def _extract_finish_reason(data):
    """Достаёт finish_reason из choices[0] (OpenAI-стиль) или None."""
    choices = data.get("choices") or []
    if not choices:
        return None
    return choices[0].get("finish_reason")


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
