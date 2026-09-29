---
type: Provider Card
title: ModelHub — provider card
description: Операционная карточка провайдера ModelHub (приватный хаб друга-вайбкодера, models.dev-стиль каталога). Status ACTIVE: каталог 69 моделей, smoke и бенч tools/fast пройдены. Ключей API здесь нет.
tags: [reference, provider-card, providers, modelhub]
timestamp: 2026-09-29
---

# ModelHub — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | ModelHub |
| `provider_id` | `modelhub` |
| `endpoint` | `https://modelhub.134.209.223.63.sslip.io/v1` |
| `compatibility` | OpenAI-compatible |
| `status` | ✅ `ACTIVE` |
| `checked_at` | 2026-09-29 |
| `source` | ключ друга-вайбкодера (`MODELHUB_API_KEY` в `.env`, в git не попадает) |
| `account_kind` | `дружественный доступ` — баланс/лимиты неизвестны `[проверить]` |
| `initial_balance` | неизвестен `[проверить]` |
| `current_balance` | неизвестен `[проверить]` |
| `models` | 69 в `/v1/models` (models.dev-стиль: `free`, `availability`, `providers`-waterfall, `pricing`); подключены 2: `gemini-3.1-flash-lite`, `codestral-latest` |
| `proxy` | не нужен |
| `expiry` | неизвестен `[проверить]` |
| `risks` | чужой ключ — тратить экономно, только free-модели; `kimi-k3` мёртв на апстриме (HTTP 000 дважды); часть каталога может не отвечать |
| `next_action` | расширять только поштучным smoke + `tools,fast`; следить за лимитами друга |
| `config_targets` | TUI `modelhub` + M Code `modelhub` — подключены (ключ из `.env`, `apiKey` в конфигах нет) |

## Probe evidence (2026-09-29)

- **`GET /v1/models`** → HTTP 200, **69 моделей** (gemini-flash семейство,
  nemotron, kimi, glm, codestral, cascade-* и др.).
- **Smoke** `gemini-3.1-flash-lite` (`max_tokens: 64`) → HTTP 200 `PROBE_OK`,
  `finish: stop`, 205 токенов. Урок: reasoning съедает бюджет ответа —
  меньше ~64 для smoke не ставить.
- **Smoke** `codestral-latest` → HTTP 200 `PROBE_OK`, 215 токенов.
- **`kimi-k3` недоступна**: дважды HTTP 000 (нет соединения, upstream
  `nvidia/moonshotai/kimi-k3` мёртв) — в конфиги не добавлена.
- **Бенч** `tools,fast` k=1: обе модели tools 1.0 (5/5), fast 1.0,
  cost $0.0 (coeff 0 в таблице — `free:true` + `pricing 0` в каталоге).
  Матрица: `modelhub / gemini-3.1-flash-lite`, `modelhub / codestral-latest`.

## Статус

`✅ ACTIVE`. Каталог, smoke и бенч проверены живыми запросами.
Расширение — только через индивидуальный smoke. Ключ чужой — экономия
обязательна.
