---
type: Provider Card
title: Vercel AI Gateway — provider card
description: Операционная карточка провайдера Vercel AI Gateway. Status ACTIVE: каталог 391 модель, smoke-чат PROBE_OK. Ключей API здесь нет.
tags: [reference, provider-card, providers, vercel]
timestamp: 2026-09-28
---

# Vercel AI Gateway — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | Vercel AI Gateway |
| `provider_id` | `vercel` |
| `endpoint` | `https://ai-gateway.vercel.sh/v1` |
| `compatibility` | OpenAI-compatible |
| `status` | ✅ `ACTIVE` |
| `checked_at` | 2026-09-28 |
| `source` | аккаунт пользователя, ключ только в auth.json id `vercel` (в `.env` отсутствует) |
| `account_kind` | `user` с заявленной ежемесячной квотой `[проверить]` — часть моделей со слов пользователя не работает |
| `initial_balance` | неизвестен `[проверить]` |
| `current_balance` | неизвестен `[проверить]` — usage smoke-ответа несёт `cost`/`market_cost`, истина для денег — панель биллинга |
| `models` | 391 в `/v1/models`; подключена 1: `google/gemini-2.5-flash-lite` |
| `proxy` | не нужен |
| `expiry` | неизвестен `[проверить]` |
| `risks` | заявленная monthly-квота не сверена; пользователь сообщает, что часть моделей не работает — расширять список моделей только после smoke каждой |
| `next_action` | smoke-план: дешёвые модели по одной (`tools,fast`), при отказе фиксировать код/тело ошибки в карточку |
| `config_targets` | TUI `vercel` + M Code `vercel` — подключены (auth по id из auth.json, `apiKey` в конфигах нет) |

## Probe evidence (2026-09-28)

- **`GET /v1/models` с auth-ключом** → HTTP 200, **391 модель**.
- **Smoke-чат** `google/gemini-2.5-flash-lite`, `max_tokens: 32` → HTTP 200,
  ответ `PROBE_OK`, `finish_reason: stop`, usage `total_tokens: 12`,
  `cost: 2.4e-06`, `is_byok: false`.
- Ключ резолвится из auth.json (`vercel`), в `.env` переменной нет — туда не добавлять.

## Статус

`✅ ACTIVE`. Каталог и chat проверены живыми запросами. Расширение моделей —
только через индивидуальный smoke.
