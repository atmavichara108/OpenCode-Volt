---
type: Provider Card
title: JustDoWork (justwoker) — provider card
description: Операционная карточка провайдера JustDoWork (justwoker, New API/One API style). Status DEGRADED: 1 модель claude-opus-4-8 в /v1/models, но chat под Cloudflare 403 captcha. Факты отделены от [проверить].
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
| `status` | 🟡 `DEGRADED` |
| `checked_at` | 2026-09-24 |
| `source` | реферальная программа JustDoWork |
| `account_kind` | `user/promotional referral` |
| `initial_balance` | `$121.34` (displayed в dashboard), kind `referral/promotional`; фактическая спендируемость не подтверждена `[проверить]` |
| `current_balance` | `$121.34` (последнее наблюдение 2026-09-16, источник: dashboard) |
| `models` | 1 модель: `claude-opus-4-8` |
| `proxy` | Cloudflare challenge перед chat-endpoint (403 captcha на любом UA) |
| `expiry` | неизвестен `[проверить]` |
| `risks` | referral-баланс может быть неспендируем через API; chat под Cloudflare captcha |
| `next_action` | для chat нужна браузерная сессия (cookies/JWT/JS-challenge), одного Bearer-ключа мало; подключение в конфиги отложено до снятия Cloudflare-блока |
| `config_targets` | не подключён (DEGRADED — chat недоступен) |

## Probe evidence (2026-09-16)

- **`GET /v1/models` с auth** вернул `data: []` — пустой список моделей.
  По правилу метода [[02-Methods/promo-provider-protocol]] это
  `DEGRADED`/`BLOCKED` даже при ненулевом dashboard-балансе.
- **Dashboard** показывает баланс `$121.34` (referral/promotional), но
  секций **Models / Channels / Tokens / Top-up** нет.
- **Чат-проб** на `gpt-4o-mini` вернул **Cloudflare 403**.
- **Model IDs отсутствуют** — подключить провайдера нельзя (нет моделей для
  маршрутизации).

## Probe evidence (2026-09-24)

- **`GET /v1/models` с auth** вернул HTTP 200 и **1 модель `claude-opus-4-8`**
  (ранее пустой `data: []`) — прогресс относительно прошлого BLOCKED.
- **`POST /v1/chat/completions`** → HTTP 403 Cloudflare challenge
  (`Attention Required! | Cloudflare`, captcha, Ray ID, «Please enable cookies»).
  Пробовали три варианта заголовков (свой UA, браузерный Chrome UA, без UA) —
  все 403. Cloudflare требует браузерную сессию (cookies/JWT/JS-challenge),
  одного Bearer-ключа мало.
- **В конфиги не добавлен** — подключать нечего, пока chat отдаёт капчу.

## Статус

`🟡 DEGRADED`. Каталог ожил (1 модель `claude-opus-4-8` в `/v1/models`, HTTP 200),
но chat отдаёт Cloudflare 403 captcha при любом UA — браузерной сессии
(cookies/JWT/JS-challenge) у API-ключа нет. В конфиги не добавлен и
**не становится default**.

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[01-Reference/providers]] — обзор провайдеров.
- [[01-Reference/provider-cards/linaliapi]] — первая карточка.
- [[04-Memory/facts]] · [[04-Memory/active-context]]
