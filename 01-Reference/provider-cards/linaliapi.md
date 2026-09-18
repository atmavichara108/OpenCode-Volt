---
type: Provider Card
title: LinaliAPI — provider card
description: Операционная карточка провайдера LinaliAPI (OpenAI-compatible шлюз). Источник правды по состоянию провайдера; факты отделены от [проверить].
tags: [reference, provider-card, providers, linaliapi]
timestamp: 2026-09-06
---

# LinaliAPI — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `provider_id` | `linaliapi` |
| `endpoint` | `https://api.linaliapi.com/v1` |
| `compatibility` | OpenAI-compatible (также Anthropic-совместимый шлюз) |
| `status` | ✅ `ACTIVE` |
| `checked_at` | 2026-09-06 |
| `source` | linaliapi.com (кастомный шлюз; история: [[04-Memory/session-log/2026-09-06]]) |
| `account_kind` | `promotional/provider account` `[проверить]` — точный вид аккаунта не доказан |
| `initial_balance` | неизвестен `[проверить]` |
| `current_balance` | неизвестен `[проверить]` |
| `models` | 6 известных (см. ниже) |
| `proxy` | нет (TUI работает напрямую); M Code — см. `probe_evidence` |
| `expiry` | неизвестен `[проверить]` |
| `risks` | balance-остаток не измерен; M Code upstream issue (исторически) |
| `next_action` | balance hook (spec: /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md) |
| `config_targets` | TUI `linaliapi` — подключён (auth/config); M Code — см. `probe_evidence` |

## Models

6 известных моделей (ID с вендорными префиксами):

- `anthropic/claude-opus-5`
- `openai/gpt-5.6-sol`
- `openai/gpt-5.6-luna`
- `google/gemini-3.8-flash`
- `z-ai/glm-5.3`
- `deepseek/deepseek-v4-pro`

## Probe evidence

- **TUI models работают** — подтверждено пользователем (smoke в TUI).
- **Auth/config подключены** — config-блок + auth-store ID совпадают
  (`linaliapi`), `apiKey` не хардкодится ([[04-Memory/facts]] § LinaliAPI).
- **M Code upstream issue** — исторически наблюдалась проблема на стороне
  upstream M Code при работе с этим провайдером; в TUI не воспроизводится.
- **Proxy/TUI distinction** — TUI ходит напрямую; M Code Desktop (`mcode`)
  — отдельный target, auth после рестарта GUI `[проверить]`.
- **Balance** — фактический стартовый/текущий баланс не измерен `[проверить]`.

## Ссылки

- [[01-Reference/providers]] — обзор провайдеров.
- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[01-Reference/provider-cards/justwoker]] — вторая карточка.
- /home/rudra/dotfiles/docs/specs/linaliapi-provider-canon.md — spec канонизации LinaliAPI.
- [[04-Memory/facts]] · [[04-Memory/session-log/2026-09-06]]
