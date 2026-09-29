---
type: Provider Card
title: DeepSeek local bridge — provider card
description: Операционная карточка локального моста к бесплатному веб-чату DeepSeek (Tsuev/opencode-deepseek). Status ACTIVE: PROBE_OK, tool_calls эмулируются, бенч tools 5/5. Без API-ключа и оплаты. Ключей API здесь нет.
tags: [reference, provider-card, providers, deepseek, local-bridge]
timestamp: 2026-09-29
---

# DeepSeek local bridge — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет
> (мост игнорирует `Authorization`; в конфиге заглушка `apiKey: "unused"` —
> не секрет, а требование SDK).

| Поле | Значение |
|------|----------|
| `display_name` | DeepSeek (local bridge) |
| `provider_id` | `local-deepseek` |
| `endpoint` | `http://127.0.0.1:8000/v1` |
| `compatibility` | OpenAI-compatible (мост FastAPI) |
| `status` | ✅ `ACTIVE` |
| `checked_at` | 2026-09-29 |
| `source` | `~/Projects/deepseek-bridge` (форк Tsuev/opencode-deepseek), аккаунт пользователя chat.deepseek.com |
| `account_kind` | `личный бесплатный веб-аккаунт` |
| `initial_balance` | n/a (веб-чат без счётчика) |
| `current_balance` | n/a |
| `models` | 2: `deepseek-chat`, `deepseek-expert` |
| `proxy` | мост ходит напрямую (в unit вычищены *_PROXY — socks ломал httpx) |
| `expiry` | пока живёт веб-сессия (автообновление ~5ч; при смерти — `503`, повторный вход) |
| `risks` | запросы строго по очереди (один аккаунт) — параллельных агентов не вешать; tool calling эмулируется текстом (менее надёжен на длинных цепочках); аккаунт можно улететь в бан при хаммере; сессия `session/` — только локально, в git не идёт |
| `next_action` | держать systemd-unit `deepseek-bridge` активным; при 503 — проверить сессию |
| `config_targets` | TUI `local-deepseek` + M Code `local-deepseek` — подключены |

## Probe evidence (2026-09-29)

- `/healthz` → `{"status":"ok"}`; `/v1/models` → `deepseek-chat`, `deepseek-expert`.
- **Smoke** `deepseek-chat` → `PROBE_OK`, `finish_reason: stop`.
- **Tool-call smoke** (`tools=[write]`) → `finish_reason: tool_calls`,
  корректный `function.name=write` с аргументами — агентское использование
  подтверждено сквозняком.
- **Бенч** `tools,fast` k=1: tools 1.0 (5/5), fast 1.0, $0.0.
- Плагин `deepseek-tool-discipline.js` из репозитория моста поставлен
  в `~/.config/opencode/plugins/`.

## Эксплуатация

- systemd user-unit `deepseek-bridge` (enable + active): автоподъём при
  входе, рестарт при падении. Юнит: `~/.config/systemd/user/deepseek-bridge.service`.
- Вход: `cd ~/Projects/deepseek-bridge && .venv/bin/python -m deepseek.auth`
  (патч: `_safe_evaluate` в первом чтении токена + таймаут 900с).
  Альтернатива без капчи: войти в своём Chromium → закрыть → скопировать
  профиль → headless-захват токена системным `/usr/bin/chromium`.
- Сессия: `~/Projects/deepseek-bridge/session/session.json` (git-ignored).

## Статус

`✅ ACTIVE`. Мост, tool calling, бенч и автозапуск проверены живыми запросами.
