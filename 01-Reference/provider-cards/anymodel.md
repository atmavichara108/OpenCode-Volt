---
type: Provider Card
title: AnyModel — provider card
description: Операционная карточка провайдера AnyModel. OpenAI-compatible шлюз с реферальным оффером 5M токенов за привязку Telegram. Status ACTIVE: probe пройден, 6 моделей подключено.
tags: [reference, provider-card, providers, anymodel]
timestamp: 2026-09-23
---

# AnyModel — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | AnyModel |
| `provider_id` | `anymodel` |
| `endpoint` | `https://anymodel.org/v1` |
| `compatibility` | OpenAI-compatible |
| `status` | ✅ `ACTIVE` |
| `checked_at` | 2026-09-23 |
| `source` | реферальный оффер 5M токенов за привязку Telegram (post 831) |
| `account_kind` | `promotional` |
| `initial_balance` | 5,000,000 tokens (kind: `promotional`, observed_at 2026-09-23, dashboard + подтверждено пользователем) |
| `current_balance` | НЕИЗВЕСТЕН — balance ladder 404 (`/v1/dashboard/billing/subscription|usage` не существуют, нужен fallback measured-учёт) `[проверить]` |
| `models` | 85 в `/v1/models`; конфигурировано 6: `am/free`, `am/nemotron-3-ultra-550b-a55b`, `cc/claude-opus-5`, `cx/gpt-6-astra`, `cx/gpt-5.6-sol`, `kmc/k3`. Вендорные префиксы: `cx/` (xAI/Cerebras), `cc/` (Claude), `kmc/` (Kimi), `am/` (Anymodel free) |
| `proxy` | не нужен |
| `expiry` | неизвестен `[проверить]` |
| `risks` | reasoning-раздувание smoke-запросов; free-роутер `am/free` сжигает ~2K токенов на минимальный запрос (учитывать в лимитах); баланс скрыт (только estimated) |

## Probe evidence (2026-09-23)

- `am/free` — 200 (2115 tok)
- `am/nemotron-3-ultra` — 200 (2163 tok)
- `cc/claude-opus-5` — 200 (9011 tok — reasoning раздувает smoke-запросы, учитывать при оценке расходов)
- balance ladder → 404, нужен fallback measured-учёт

## Prices (база 5¢/1M × коэффициент)

| Модель | Коэффициент |
|--------|-------------|
| `cx/gpt-6-astra` | ×8 |
| `cc/claude-opus-5` | ×6 |
| `cx/gpt-5.6-sol` | ×4 |
| `kmc/k3` | ×3 |
| `am/nemotron-3-ultra`, `am/free` | ×0 |

## Статус

`✅ ACTIVE`. Probe пройден (3/3 smoke), 6 моделей в конфиги, auth TUI + M Code. Баланс скрыт — только estimated.

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[01-Reference/providers]] — обзор провайдеров.
- [[01-Reference/abuse-providers-inbox]] — таблица всех промо-провайдеров.
- [[01-Reference/provider-cards/amd-radeon]] — карточка-аналог.
