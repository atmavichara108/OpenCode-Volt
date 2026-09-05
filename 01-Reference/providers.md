---
type: Reference
title: OpenCode Providers — Провайдеры и бесплатные лимиты
description: Полный обзор провайдеров OpenCode с бесплатными лимитами. Проверено: 2026-09-01
tags: [opencode, providers, free-tier, models]
timestamp: 2026-09-01
---

# OpenCode Providers — Исследование бесплатных лимитов

> **Источник:** `opencode models` (465 моделей), официальная документация https://opencode.ai/docs/providers, https://opencode.ai/docs/models
> **Дата проверки:** 2026-09-01

## Обзор доступных провайдеров

| Провайдер | ID | Тип | Описание |
|-----------|-----|-----|----------|
| **OpenCode Zen** | `opencode` | Pay-as-you-go | Curated список моделей, протестированных OpenCode. Рекомендуется для новичков. |
| **OpenCode Go** | `opencode-go` | Subscription | Низкозатратная подписка на популярные open coding модели. |
| **OpenRouter** | `openrouter` | Gateway | Доступ к 100+ провайдерам через единый API. Много бесплатных моделей. |
| **Mistral AI** | `mistral` | Direct | Прямой доступ к моделям Mistral (Codestral, Magistral, Ministral). |

---

## Бесплатные модели по провайдерам

### 1. OpenCode Zen (`opencode/`) — Бесплатные модели

| Модель | Категория | Примечание |
|--------|-----------|------------|
| `opencode/deepseek-v4-flash-free` | Fast/Research | Быстрая, дешёвая — идеальна для research, reviewer, verifier |
| `opencode/ling-3.0-flash-free` | Medium | Сбалансированная бесплатная модель |
| `opencode/nemotron-3-ultra-free` | Strong | Самая сильная из бесплатных Zen — для сложных задач |
| `opencode/nemotron-3.5-lightning-free` | Fast | Молниеносная бесплатная |
| `opencode/mimo-v2.5-free` | Medium | Xiaomi MIMO — неплохая бесплатная |
| `opencode/ling-3.0-flash-fin-free` | Specialized | Финансовая специализация |
| `opencode/muse-spark-1.2-contributor-free` | Medium | Meta Muse Spark contributor edition |

**Доступ:** `/connect` → OpenCode Zen → opencode.ai/auth → API key

---

### 2. OpenCode Go (`opencode-go/`) — Subscription

> **Важно:** OpenCode Go — это **платная подписка**. Бесплатные модели здесь НЕТ. Все модели требуют активной подписки.
> Модели: `gpt-5.6-luna`, `glm-5.2`, `glm-5.3`, `qwen3.7-plus`, `qwen3.8-max`, `kimi-k2.7-code`, `mimo-v2.5-pro`, `deepseek-v4-pro` и др.

**Доступ:** `/connect` → OpenCode Go → opencode.ai/auth → подписка

---

### 3. OpenRouter (`openrouter/`) — Огромный каталог с бесплатными

#### Бесплатные модели (47+ штук с пометкой `:free`):

| Модель | Провайдер | Категория | Примечание |
|--------|-----------|-----------|------------|
| `openrouter/openrouter/free` | OpenRouter | Auto | Автовыбор лучшей бесплатной модели |
| `openrouter/z-ai/glm-5.2:free` | Z.AI | Strong | GLM-5.2 — очень сильная, бесплатная |
| `openrouter/minimax/minimax-m3:free` | MiniMax | Strong | M3 — топовая бесплатная |
| `openrouter/minimax/minimax-m2.7:free` | MiniMax | Strong | M2.7 — сильная бесплатная |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | Strong | Nemotron 3 Ultra — 550B, бесплатная |
| `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | NVIDIA | Strong | Nemotron 3 Super — 120B, бесплатная |
| `openrouter/nvidia/nemotron-3.5-lightning:free` | NVIDIA | Fast | Lightning — молниеносная |
| `openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | NVIDIA | Fast | Nano Omni — reasoning |
| `openrouter/thinkingmachines/inkling:free` | Thinking Machines | Medium | Inkling |
| `openrouter/thinkingmachines/inkling-small:free` | Thinking Machines | Fast | Inkling Small |
| ~~`openrouter/poolside/laguna-s-2.1:free`~~ | ~~Poolside~~ | ~~Strong~~ | ~~RETIRED 2026-09-05: зацикливания, удалена из активной экосистемы~~ |
| ~~`openrouter/poolside/laguna-xs-2.1:free`~~ | ~~Poolside~~ | ~~Medium~~ | ~~RETIRED 2026-09-05: вместе с Laguna S~~ |
| `openrouter/liquid/lfm-2.5-2.6b:free` | Liquid AI | Fast | LFM 2.6B |
| `openrouter/google/gemma-4-26b-a4b-it:free` | Google | Medium | Gemma 4 26B |
| `openrouter/google/gemma-4-31b-it:free` | Google | Medium | Gemma 4 31B |
| `openrouter/inclusionai/ling-3.0-flash-fin:free` | InclusionAI | Specialized | Ling Financial |
| `openrouter/cohere/north-mini-code:free` | Cohere | Fast | North Mini Code |
| `openrouter/dots-studio/dots-3-note-preview:free` | Dots Studio | Specialized | Dots 3 Note |

**Доступ:** `/connect` → OpenRouter → https://openrouter.ai/keys → API key
**Особенность:** Один API ключ даёт доступ ко ВСЕМ моделям OpenRouter (платным и бесплатным)

---

### 4. Mistral AI (`mistral/`) — Платные

Бесплатных моделей у Mistral в OpenCode **нет**. Все модели платные:
- `mistral/codestral-latest` — кодинг
- `mistral/magistral-medium/latest` — reasoning
- `mistral/ministral-3b/8b-latest` — small
- `mistral/mistral-medium/latest` — medium
- `mistral/mistral-large/latest` — large

---

### 5. Дополнительные провайдеры с бесплатными лимитами (через OpenRouter)

Эти провайдеры доступны **только через OpenRouter** (не напрямую в OpenCode):

| Провайдер | Бесплатные модели | Примечание |
|-----------|-------------------|------------|
| **NVIDIA** | Nemotron 3 Ultra/Super/Lightning/Nano | Через `openrouter/nvidia/...:free` |
| **Google** | Gemma 4 26B/31B | Через `openrouter/google/...:free` |
| **Z.AI** | GLM-5.2 | Через `openrouter/z-ai/glm-5.2:free` |
| **MiniMax** | M2.7, M3 | Через `openrouter/minimax/...:free` |
| ~~**Poolside**~~ | ~~Laguna S/XS 2.1~~ | ~~RETIRED 2026-09-05: зацикливания, удалена из экосистемы~~ |
| **Liquid AI** | LFM 2.5-2.6B | Через `openrouter/liquid/...:free` |
| **Cohere** | North Mini Code | Через `openrouter/cohere/...:free` |
| **Thinking Machines** | Inkling, Inkling Small | Через `openrouter/thinkingmachines/...:free` |

---

## Резюме: Провайдеры с ИСТИННЫМИ бесплатными лимитами

| Провайдер | Доступ в OpenCode | Бесплатные модели | Качество топовых бесплатных |
|-----------|-------------------|-------------------|----------------------------|
| **OpenCode Zen** | Прямой (`opencode/`) | 7 моделей | `nemotron-3-ultra-free` — сильная |
| **OpenRouter** | Прямой (`openrouter/`) | 47+ моделей | `glm-5.2:free`, `minimax-m3:free`, `nemotron-3-ultra:free` — очень сильные |
| **OpenCode Go** | Прямой (`opencode-go/`) | **НЕТ** | — |
| **Mistral** | Прямой (`mistral/`) | **НЕТ** | — |
| **NVIDIA (build.nvidia.com)** | Через OpenRouter | 4 модели | Nemotron 3 Ultra — топ |
| **Google (Vertex AI)** | Через OpenRouter | 2 модели | Gemma 4 — хорошая |

**Вывод:** Для бесплатных режимов используем **OpenCode Zen** + **OpenRouter**. OpenCode Go и Mistral — только для платных режимов.

---

## Рекомендуемая стратегия 3-х режимов

### Режим 1: **FREE** — Полностью бесплатный
> Никаких денег, только бесплатные лимиты

| Роль | Модель | Провайдер | Обоснование |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode/nemotron-3-ultra-free` | Zen | Сильнейшая бесплатная Zen |
| **Research / Навигация** | `opencode/deepseek-v4-flash-free` | Zen | Быстрая, дешёвая, отличная для поиска |
| **Build / Реализация** | `openrouter/minimax-m3:free` | OpenRouter | Топ бесплатная для кода |
| **Review / Verifier** | `opencode/ling-3.0-flash-free` | Zen | Дешёвая, детерминированная |
| **Fallback** | `openrouter/openrouter/free` | OpenRouter | Автовыбор лучшей доступной |

---

### Режим 2: **MEDIUM** — Сильные + Бесплатные (баланс цена/качество)
> Используем GPT-5.6 Luna (сильная и дешёвая) + бесплатные для рутины

| Роль | Модель | Провайдер | Обоснование |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode-go/gpt-5.6-luna` | Go | **Сильная и дешёвая** — основная рабочая лошадка |
| **Complex Planning** | `opencode-go/gpt-5.6-luna` | Go | Для сложной декомпозиции |
| **Build / Реализация** | `opencode-go/gpt-5.6-luna` | Go | 79%+ SWE-bench, отличный tool-calling |
| **Research / Навигация** | `opencode/deepseek-v4-flash-free` | Zen | Бесплатная, быстрая |
| **Review** | `opencode/ling-3.0-flash-free` | Zen | Бесплатная, детерминированная |
| **Verifier** | `opencode/deepseek-v4-flash-free` | Zen | Дешёвая проверка |
| **Fallback (дорогой)** | `opencode/claude-sonnet-4-6` | Zen | Резерв на случай ошибок Luna |

---

### Режим 3: **PREMIUM** — Топовые модели (на будущее)
> Когда будет бюджет на лучшие модели

| Роль | Модель | Провайдер | Обоснование |
|------|--------|-----------|-------------|
| **Primary / Координация** | `opencode/claude-opus-4-6` или `opencode/claude-opus-5` | Zen | Лучшая координация/планирование |
| **Complex Planning** | `opencode/claude-opus-5` | Zen | Максимальное качество декомпозиции |
| **Build / Реализация** | `opencode/claude-sonnet-4-6` | Zen | 79.6% SWE-bench, стандарт исполнителя |
| **Code Review** | `opencode/gpt-5.3-codex` | Zen | Самый дотошный на баги/безопасность |
| **Research** | `opencode/gemini-3.7-flash` | Zen | Огромный контекст, быстрая |
| **Verifier** | `opencode/claude-sonnet-4-6` | Zen | Качественная верификация |
| **Fallback** | `opencode/claude-opus-4-6` | Zen | Максимальная надёжность |

---

## Конфигурация переключения режимов

### Вариант А: Через `opencode.json` с `provider` overrides

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/nemotron-3-ultra-free",
  "provider": {
    "opencode": {
      "models": {
        "nemotron-3-ultra-free": {},
        "deepseek-v4-flash-free": {},
        "ling-3.0-flash-free": {}
      }
    },
    "openrouter": {
      "models": {
        "minimax-m3:free": {},
        "glm-5.2:free": {},
        "nemotron-3-ultra-550b-a55b:free": {}
      }
    }
  }
}
```

### Вариант Б: Переменные окружения + скрипт переключения

Создать скрипт `switch-mode.sh`:
```bash
#!/bin/bash
# Usage: ./switch-mode.sh free|medium|premium

MODE=$1
case $MODE in
  free)
    export OPENCODE_MODEL="opencode/nemotron-3-ultra-free"
    export OPENCODE_SMALL_MODEL="opencode/deepseek-v4-flash-free"
    ;;
  medium)
    export OPENCODE_MODEL="opencode-go/gpt-5.6-luna"
    export OPENCODE_SMALL_MODEL="opencode/deepseek-v4-flash-free"
    ;;
  premium)
    export OPENCODE_MODEL="opencode/claude-opus-5"
    export OPENCODE_SMALL_MODEL="opencode/gemini-3.7-flash"
    ;;
esac
opencode
```

### Вариант В: Конфиг с `model` variants (рекомендуемый)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/gpt-5.6-luna",
  "provider": {
    "opencode": {
      "models": {
        "gpt-5.6-luna": {
          "variants": {
            "free": { "model": "opencode/nemotron-3-ultra-free" },
            "medium": { "model": "opencode-go/gpt-5.6-luna" },
            "premium": { "model": "opencode/claude-opus-5" }
          }
        }
      }
    }
  }
}
```

> **Примечание:** OpenCode поддерживает `variant_cycle` keybind для быстрого переключения вариантов.

---

## Команды для настройки

```bash
# Подключить OpenCode Zen (pay-as-you-go)
/connect
# Выбрать OpenCode Zen → авторизация на opencode.ai/auth

# Подключить OpenRouter
/connect
# Выбрать OpenRouter → API key с openrouter.ai/keys

# Подключить OpenCode Go (subscription)
/connect
# Выбрать OpenCode Go → подписка на opencode.ai/auth

# Посмотреть все доступные модели
/models

# Переключить вариант модели (если настроены variants)
# Keybind: variant_cycle
```

---

## Связанные документы

- [[02-Methods/model-routing]] — Политика выбора модели под роль
- [[02-Methods/capability-routing]] — Capability-based routing (ортогонально model-routing)
- [[04-Memory/facts.md]] — Реестр фактов (историческая запись о временном переводе на Zen)
- [[TASKS]] — T-048, T-049 (возврат Zen/Go, профили моделей под провайдера)