---
type: Provider Card
title: JustDoWork (justwoker) — provider card
description: Операционная карточка провайдера JustDoWork (justwoker, New API/One API style). Status BLOCKED/NO_MODELS: пустой /v1/models. Факты отделены от [проверить].
tags: [reference, provider-card, providers, justwoker]
timestamp: 2026-09-16
---

# JustDoWork — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | JustDoWork |
| `provider_id` | `justwoker` |
| `endpoint` | `https://api.justwoker.icu/v1` |
| `compatibility` | New API / One API style (OpenAI-совместимый по контракту) |
| `status` | ❌ `BLOCKED/NO_MODELS` |
| `checked_at` | 2026-09-16 |
| `source` | реферальная программа JustDoWork |
| `account_kind` | `user/promotional referral` |
| `initial_balance` | `$121.34` (displayed в dashboard), kind `referral/promotional`; фактическая спендируемость не подтверждена `[проверить]` |
| `current_balance` | `$121.34` (последнее наблюдение 2026-09-16, источник: dashboard) |
| `models` | нет известных ID моделей |
| `proxy` | Cloudflare перед endpoint (403 на чат-пробе) |
| `expiry` | неизвестен `[проверить]` |
| `risks` | referral-баланс может быть неспендируем через API |
| `next_action` | запросить у support/admin провайдера, спендируем ли referral-баланс через API, и попросить приаттачить channels/models |
| `config_targets` | не подключён (BLOCKED) |

## Probe evidence (2026-09-16)

- **`GET /v1/models` с auth** вернул `data: []` — пустой список моделей.
  По правилу метода [[02-Methods/promo-provider-protocol]] это
  `DEGRADED`/`BLOCKED` даже при ненулевом dashboard-балансе.
- **Dashboard** показывает баланс `$121.34` (referral/promotional), но
  секций **Models / Channels / Tokens / Top-up** нет.
- **Чат-проб** на `gpt-4o-mini` вернул **Cloudflare 403**.
- **Model IDs отсутствуют** — подключить провайдер нельзя (нет моделей для
  маршрутизации).

## Статус

`❌ BLOCKED/NO_MODELS`. Referral-баланс отображается, но API-спендируемость не
подтверждена; без моделей провайдер не подключается и **не становится default**.

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[01-Reference/providers]] — обзор провайдеров.
- [[01-Reference/provider-cards/linaliapi]] — первая карточка.
- [[04-Memory/facts]] · [[04-Memory/active-context]]
