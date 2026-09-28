---
type: Architecture Spec
title: New API gateway layer — единый модельный слой для всех агентов
status: design
scope: vault + dotfiles (opencode) + m-code
date: 2026-09-28
owner: sysop (impl), librarian (oversight)
---

# New API gateway layer

> Решение (2026-09-28): New API становится **единой OpenAI-совместимой точкой
> входа**, на которую смотрят ВСЕ агенты — и в M Code, и в OpenCode. Агент
> привязан к New API один раз на сессию; какой реальный провайдер/модель под
> капотом — решает New API (channels + failover), агент этого не видит и в
> течение сессии остаётся на `newapi`, а не на конкретной модели.

## 1. Правило приёмки (bench-gate)

**Любая модель добавляется каналом New API ТОЛЬКО с пройденным бенчем.**
ACTIVE по probe — необходимо, но недостаточно. Порядок:
`probe ACTIVE → model-bench PASS (tools/build/reasoning) → канал New API`.
Модель без PASS в роутер не попадает. Детали и место в lifecycle:
[[02-Methods/promo-provider-protocol]] (раздел «Правило bench-gate»).

Причина: канал существует, чтобы агент **не** получал говнокод, кривое
понимание задач и случайные/вредные действия. Реле (tokenin, htai91,
ai-hdd-sb, ai-furry-vg, deepseek-bloodthemes) проходят строже — заявленный
флагман ≠ рабочий.

## 2. Что значит «привязка к New API, не к модели»

Формулировка оператора: агент «перехватывается один раз… и остаётся на New API
пока сессия активна, не на модели, а на New API». Это в точности семантика
**шлюза с per-request failover**:

- В конфиге агента `model: newapi/<alias>` — фиксирован, на сессию не меняется.
- New API на каждый запрос выбирает реальный канал (priority → weighted random),
  при ошибке падает на следующий канал тем же запросом. Смена провайдера
  происходит **под капотом, без перезапуска сессии**.
- Никакой per-session «липучести» к конкретной модели инженерить не нужно —
  привязка стабильна именно к endpoint'у New API, что и требовалось.

Это строго лучше, чем правка `model:` в конфиге на лету: failover мгновенный,
на запрос, без релоуда сессии.

## 3. Жёсткое ограничение: client-locked модели (гибрид, не полная замена)

`opencode-go` и `opencode-zen` отдают **бесплатные модели, залоченные на клиент
opencode** (анти-абуз: запросы вне приложения opencode отклоняются). Их
**физически нельзя** проксировать через self-hosted New API — шлюз для них
мёртв. Поэтому архитектура — **гибрид**, а не замена:

| Слой | Покрывает | Механизм | Failover |
|------|-----------|----------|----------|
| **New API (шлюз)** | все key-based провайдеры (amd, google, mistral, реле) | агент → `newapi/<alias>`, каналы внутри | per-request, прозрачный |
| **Config-rotator (существующий)** | ТОЛЬКО `opencode-go`/`opencode-zen` free (client-locked) | правка `model:` агента через model-router | по probe, с релоудом |

«Покрыть всех агентов» = дать всем агентам единый доступ к key-based
провайдерам через New API. Доступ к zen/go free остаётся прямым в клиенте —
это ограничение провайдера, обойти его шлюзом нельзя.

## 4. Роль ротатора меняется

- Для **key-based** тира ротатор больше НЕ правит конфиги агентов. Его работа
  сдвигается в **управление каналами New API**: probe → bench → регистрация/
  дизейбл каналов (планируемый `tools/key-rotator/newapi_sync.py` через admin
  API New API). Bench-gate — здесь.
- Для **zen/go** тира ротатор остаётся как есть (Iter-1 `rotate.py`,
  правка `model:`), потому что шлюз их не покрывает.
- `probe.py` / `provider-health.jsonl` используются обоими: питают и решение о
  каналах, и failover-статусы.

## 5. Целевая конфигурация агентов

Все агенты (M Code + OpenCode), key-based тир:
```
model: newapi/free-code      # роль coding
model: newapi/free-general   # роль general
model: newapi/free-vision    # роль vision
```
`newapi` — провайдер-блок в opencode.jsonc (openai-compatible, baseURL
`http://127.0.0.1:3000/v1`, ключ = New API user-token). Алиасы `free-*` — это
model-mapping New API на группы каналов по ролям.

zen/go-агенты (если оператор хочет именно бесплатные zen/go) остаются на
`opencode-go/*` / `opencode/*` напрямую.

> Правка provider-блоков и agent `model:` в `opencode.jsonc`/`mcode` — **red-line
> для агента** (встроенный запрет ядра). Блоки готовит агент, вставляет оператор.

## 6. Шаги внедрения

1. **Сервис up (durable):** оператор — `systemctl --user enable --now new-api`
   (у агента systemctl запрещён).
2. **Admin wizard:** оператор создаёт админа на `http://127.0.0.1:3000`.
3. **Каналы (bench-gated):** для каждой bench-PASS модели — канал New API
   (admin API / будущий `newapi_sync.py`). Группировка в алиасы `free-code` и др.
4. **User-token New API** → в `~/.local/share/opencode/auth.json` как `newapi`.
5. **Provider-блок `newapi`** (baseURL 127.0.0.1:3000/v1) + перевод агентов на
   `newapi/free-*` — снипеты готовит агент, вставляет оператор (см. будущий
   апдейт `provider-config-snippets.md`).
6. **Перезапуск** OpenCode + M Code.
7. **Проверка:** запрос через `newapi/free-code`; дизейбл топового канала →
   ответ уходит на следующий тем же запросом (прозрачный failover).

## 7. Открытые вопросы

- Session-affinity: подтверждено НЕ нужна (привязка к endpoint, не к модели).
- Учёт расхода: считать по панели New API, не по `usage` (реле врут — см.
  бенч-бриф).
- M Code AppImage: путь конфига после обновления — подтвердить, что `newapi`
  provider-блок читается (симлинк `~/.config/mcode`).

## 8. Ссылки

- [[02-Methods/promo-provider-protocol]] — lifecycle + bench-gate.
- `tools/key-rotator/` — probe/rotate/providers/rotation + README.
- `tools/model-bench/` — бенч (gate PASS).
- `docs/specs/key-rotator-probe-hook.md` — Iter-0/1 ротатора.
- `tools/key-rotator/provider-config-snippets.md` — блоки провайдеров.
