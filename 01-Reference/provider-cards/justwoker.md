---
type: Provider Card
title: JustDoWork (justwoker) — provider card
description: Операционная карточка провайдера JustDoWork (justwoker, New API/One API style). Status DEGRADED (non-stream-only): Anthropic-style /messages работает только без стрима; стриминг шлюза не отдаёт content_block-события. OpenAI-style /chat/completions закрыт Cloudflare. Баланс $300+.
tags: [reference, provider-card, providers, justwoker]
timestamp: 2026-10-07
---

# JustDoWork — provider card

> Каноническая операционная запись по провайдеру. Schema и lifecycle:
> [[02-Methods/promo-provider-protocol]]. Ключей API здесь нет.

| Поле | Значение |
|------|----------|
| `display_name` | JustDoWork |
| `provider_id` | `justwoker` |
| `endpoint` | `https://api.justwoker.icu/v1` |
| `compatibility` | Anthropic-style; OpenAI-style заблокирован CF |
| `status` | 🟡 `DEGRADED` (non-stream-only, 2026-10-07); шим стабилен по крашам (crash-guard `dee6f15`), но открыт TimeoutError ~300с на больших non-stream — расследуется |
| `checked_at` | 2026-10-07 |
| `source` | реферальная программа JustDoWork |
| `account_kind` | `user/promotional referral` |
| `initial_balance` | `$300+` (displayed в dashboard), kind `referral/promotional` |
| `current_balance` | `$300+` (последнее наблюдение 2026-10-07, пользовательский отчёт) |
| `models` | 1 модель: `claude-opus-4-8` |
| `proxy` | не требуется для anthropic-пути |
| `expiry` | неизвестен `[проверить]` |
| `risks` | **стриминг шлюза сломан** (регрессия New API) — OpenCode всегда стримит, поэтому «напрямую» модель отдаёт пустоту; OpenAI-путь закрыт CF |
| `next_action` | временный мост: локальный стриминг-шим (см. ниже) до перевода провайдера каналом New API ([[docs/specs/newapi-gateway-layer]]) |
| `config_targets` | TUI + M Code через `@ai-sdk/anthropic`; в конфиге — шим-baseURL |

## Probe evidence (2026-10-07, диагноз)

Проверено вживую (curl напрямую в upstream, ключ из auth.json):

- **`POST /v1/messages`, `stream` отсутствует/false** → **HTTP 200**, корректный
  JSON: `{"content":[{"type":"text","text":"ACK"}], ...}` — non-stream работает.
- **`POST /v1/messages`, `stream: true`** → HTTP 200, но SSE содержит **только**
  `message_start` → `message_delta` → `message_stop`. События
  `content_block_start` / `content_block_delta` / `content_block_stop`
  (в которых лежит текст) **отсутствуют**. 3/3 попытки, один раз пустое тело.
  → шлюз проглатывает content-блоки в стриме; текст до клиента не доходит.
- **`POST /v1/chat/completions`** (Bearer и x-api-keyhop) → **HTTP 403 Cloudflare**,
  путь закрыт полностью; `/v1/completions` → 401.
- **`GET /v1/models`** (Bearer) → 200, `["claude-opus-4-8"]`, `supported_endpoint_types: ["anthropic","openai"]`.

**Root cause:** регрессия New API-шлюза justwoker на стриминговом
anthropic-пути. Зафиксирована в памяти ещё 2026-10-03 («SSE-блоки режутся,
плагин невиновен»).

**Почему это блокер для OpenCode:** OpenCode всегда использует стриминг
(AI SDK `streamText`); опции «отключить стрим» в конфиге OpenCode нет (проверено
по официальной схеме `https://opencode.ai/config.json`). Поэтому прямой провайдер
`justwoker` в OpenCode отвечает пустотой.

## Временный мост: локальный стриминг-шим (2026-10-07)

Решение оператора: до подъёма слоя New API поднять локальный шим-прокси.

- Шим принимает стрим-запрос от OpenCode → форвардит в upstream **non-stream** →
  сам генерирует корректный SSE (с `content_block_start/delta/stop`, включая
  tool_use-блоки). Non-stream запросы проксируются прозрачно.
- provider-блок `justwoker` в `opencode.jsonc` смотрит на шим
  (`baseURL: http://127.0.0.1:<PORT>/v1`), пакет `@ai-sdk/anthropic` сохранён.
- **Статус шима:** реализация в работе (meta-субагент). Это **временный** мост:
  при переводе justwoker каналом New API (гибридная архитектура) шим снимается.

## Связь с гибридной архитектурой New API (2026-09-28)

justwoker — key-based провайдер (`transport: anthropic` в `tools/key-rotator/providers.json`,
roles coding/general, priority 15). По [[docs/specs/newapi-gateway-layer]]
целевое состояние — **канал New API** (`newapi/<alias>`), а не отдельный
provider-блок. Шим — переходное решение; bench-gate (`probe ACTIVE → model-bench
PASS → канал`) для permanent-варианта сохраняется.

## Probe evidence (2026-09-28, победа до регрессии)

- **`POST /v1/messages`** (заголовок `x-api-key`, модель `claude-opus-4-8`,
  `max_tokens: 8`) → **HTTP 200**, ответ `PROBE_OK`, usage `input_tokens: 6655`
  (скрытая подсказка ~6.6K — учитывать в учёте), `output_tokens: 3`, cost `0.000634`.
- Ключ: Bearer для каталога + x-api-key для chat — один ключ, разные заголовки.
- **Зависимость рантайма:** пакет `@ai-sdk/anthropic` НЕ встроен в opencode и сам
  не ставится — без него провайдер молча отсутствует в списке моделей
  (`opencode models | grep justwoker` пуст при валидном конфиге). Фикс на чистой
  машине: `cd ~/.config/opencode && bun add @ai-sdk/anthropic`.

## Probe evidence (2026-09-28)

- **`GET /v1/models`** → HTTP 200, `["claude-opus-4-8"]` (каталог жив).
- **`POST /v1/chat/completions`** (Bearer-ключ) → HTTP 403 Cloudflare.
- **`POST /v1/messages`** (x-api-key, напрямую и через прокси) → HTTP 403
  `server: cloudflare`, пустое тело.

## Probe evidence (2026-09-28, мобильная сеть оператора)

- **`GET /v1/models` с телефона** → DNS/TCP/TLS проходят, HTTP 200.
- **`POST /v1/chat/completions` с телефона** → та же Cloudflare 403
  `Attention Required!`. Первый POST дал `000`, повтор — стабильный 403.
- **Итог:** блок chat глобальный, не IP-специфичный.

## Probe evidence (2026-09-24)

- **`GET /v1/models`** → HTTP 200, 1 модель `claude-opus-4-8` (ранее пустой `data: []`).
- **`POST /v1/chat/completions`** → HTTP 403 Cloudflare challenge (три варианта UA).
- **В конфиги не добавлен** — подключать нечего, пока chat отдаёт капчу.

## Probe evidence (2026-09-16)

- **`GET /v1/models` с auth** вернул `data: []` — пустой список моделей.
- **Dashboard** показывает баланс `$121.34` (referral/promotional), секций
  Models / Channels / Tokens / Top-up нет.
- **Чат-проб** на `gpt-4o-mini` → Cloudflare 403.

## Статус

`🟡 DEGRADED (non-stream-only)`. Anthropic-style `/messages` работает только без
стрима; стриминг шлюза не отдаёт content_block, поэтому прямой OpenCode-провайдер
отвечает пустотой. Временный фикс — локальный стриминг-шим; целевое — канал New API.

**Шим (2026-10-07, вечер):** стабилен по крашам — второй фикс (crash-guard стрима,
`dee6f15`) закрыл краш bun-процесса при отмене клиента. **Открыто:** `TimeoutError`
ровно через ~300с (240–300с) на больших non-stream запросах Opus — пользователь
видит `api_error: shim: TimeoutError`; гипотеза — Bun игнорирует `headersTimeout: 0`/
`requestTimeout: 0` и рвёт по дефолтному HeadersTimeout 300с. Расследуется отдельным
агентом (`task/opus-transport-*` в dotfiles). См. [[04-Memory/facts]] (T-168, фикс 2
и открытая проблема).

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[docs/specs/newapi-gateway-layer]] — гибридная архитектура (шим = временный мост).
- [[01-Reference/providers]] — обзор провайдеров.
- `tools/key-rotator/providers.json` — запись провайдера (probe-слой).
- [[04-Memory/facts]] · [[04-Memory/active-context]]