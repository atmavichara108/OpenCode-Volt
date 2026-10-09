---
type: Provider Card
title: JustDoWork (justwoker) — provider card
description: Операционная карточка провайдера JustDoWork (justwoker, New API/One API style). Status WORKING (через шим): стрим-регрессия шлюза ушла 2026-10-09, апстрим снова отдаёт полный Anthropic SSE; шим стал опциональным мостом. OpenAI-style /chat/completions закрыт Cloudflare. Баланс $300+.
tags: [reference, provider-card, providers, justwoker]
timestamp: 2026-10-09
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
| `status` | 🟢 `WORKING` (через шим, 2026-10-09); стрим-регрессия шлюза ушла — апстрим снова отдаёт полный Anthropic SSE; шим стал опциональным мостом. Инцидент TimeoutError закрыт (три слоя, см. ниже) |
| `checked_at` | 2026-10-09 |
| `source` | реферальная программа JustDoWork |
| `account_kind` | `user/promotional referral` |
| `initial_balance` | `$300+` (displayed в dashboard), kind `referral/promotional` |
| `current_balance` | `$300+` (последнее наблюдение 2026-10-07, пользовательский отчёт) |
| `models` | 1 модель: `claude-opus-4-8` |
| `proxy` | не требуется для anthropic-пути |
| `expiry` | неизвестен `[проверить]` |
| `risks` | **стрим-регрессия шлюза ушла (2026-10-09)** — апстрим снова отдаёт полный Anthropic SSE; остаточный риск нормальный для промо-провайдера (внешний канал дистрибьютора, баланс/квота). OpenAI-путь по-прежнему закрыт CF |
| `next_action` | держать шим как **опциональный** мост; перевод провайдера каналом New API ([[docs/specs/newapi-gateway-layer]]) — по-прежнему целевое, но больше не срочность |
| `config_targets` | TUI + M Code через `@ai-sdk/anthropic`; в конфиге — шим-baseURL |

## Probe evidence (2026-10-09, РАЗРЕШЕНИЕ)

- **Прямой curl к апстриму** `POST /v1/messages`, модель `claude-opus-4-8` →
  **HTTP 200 за ~28с**, реальный ответ.
- **End-to-end через шим** (`127.0.0.1:8787`, `stream:true`) → **3/3 успешных**,
  реальный контент; журнал шима: циклы ~27–30с, строки
  «200 (synthesized SSE, blocks=1..2)».
- **Стрим-регрессия ушла:** апстрим на `stream:true` снова отдаёт **полный**
  Anthropic SSE — `message_start → ping → content_block_start → content_block_delta
  → content_block_stop → message_delta → message_stop`.
- **amd-radeon:** 503 «no_available_workers (all circuits open or unhealthy)» —
  провайдерский предохранитель, сам восстановился; к правкам конфига не относится.

## Probe evidence (2026-10-07, диагноз; статус регрессии снят 2026-10-09)

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

## Временный мост: локальный стриминг-шим (2026-10-07) → опционален (2026-10-09)

Решение оператора: до подъёма слоя New API поднять локальный шим-прокси.

- Шим принимает стрим-запрос от OpenCode → форвардит в upstream **non-stream** →
  сам генерирует корректный SSE (с `content_block_start/delta/stop`, включая
  tool_use-блоки). Non-stream запросы проксируются прозрачно.
- provider-блок `justwoker` в `opencode.jsonc` смотрит на шим
  (`baseURL: http://127.0.0.1:<PORT>/v1`), пакет `@ai-sdk/anthropic` сохранён.
- **2026-10-09:** стрим-регрессия апстрима ушла → шим больше не обязателен,
  стал **опциональным мостом**. Решение о снятии/сохранении — за оператором;
  целевое — канал New API.

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

`🟢 WORKING (через шим, 2026-10-09)`. Прямой curl к апстриму `claude-opus-4-8` →
HTTP 200 за ~28с с реальным ответом; end-to-end через шим (`stream:true`) — 3/3
успешных, циклы ~27–30с вместо прежних 15-минутных висняков. **Стрим-регрессия
апстрима ушла:** гейт снова отдаёт полный Anthropic SSE (`message_start → ping →
content_block_* → message_delta → message_stop`) — первопричина шима исчезла.
Временный фикс (шим) остаётся как **опциональный** мост; целевое — канал New API.

**Инцидент TimeoutError — ЗАКРЫТ (три слоя):** (а) краш шима при отмене клиента —
crash-guard `dee6f15`; (б) фантомный фикс `headersTimeout:0` — Bun fetch
игнорирует эти опции (серверные), реальный лимит — клиентский socket-idle
`BUN_CONFIG_HTTP_IDLE_TIMEOUT`=300с (bun #16682), фикс — `timeout: false` в fetch,
коммит `49d8d74`, потолок 600→900с; (в) висняки ровно 900с (08:44/08:59/09:14
2026-10-09) — мёртвый канал у дистрибьютора провайдера (внешнее), канал ожил ~09:2x.
См. [[04-Memory/facts]] (T-168, раздел 2026-10-09 — РАЗРЕШЕНИЕ).

**Шим (2026-10-07, вечер):** стабилен по крашам — crash-guard стрима `dee6f15`
закрыл краш bun-процесса при отмене клиента. Ранее открытый `TimeoutError`
закрыт 2026-10-09 (см. выше).

## Ссылки

- [[02-Methods/promo-provider-protocol]] — метод приёмки.
- [[docs/specs/newapi-gateway-layer]] — гибридная архитектура (шим = временный мост).
- [[01-Reference/providers]] — обзор провайдеров.
- `tools/key-rotator/providers.json` — запись провайдера (probe-слой).
- [[04-Memory/facts]] · [[04-Memory/active-context]]