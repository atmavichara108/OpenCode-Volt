---
type: Reference
title: OpenCode — Конфигурация
description: Файлы конфига (глобальный/проектный), скелет JSON, провайдеры, модели.
tags: [opencode, config]
timestamp: 2026-06-27
---
# OpenCode: Конфигурация

> Выжимка из opencode.ai/docs/config. Проверено: 2026-06-26.

## Файлы конфига
- Глобальный: `~/.config/opencode/opencode.json`
- Проектный: `opencode.json` в корне проекта
- Мёрж: проектный накладывается поверх глобального → общее ядро в глобальном, специфика в проектном.

## Скелет
```
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": true,
  "permission": { ... },
  "agent": { ... },
  "command": { ... }
}
```

## Ключевое для моей схемы
- Общие агенты (verifier) → глобальный конфиг, работают во всех проектах.
- Проектные агенты/права → проектный opencode.json.
- Альтернатива JSON-конфигу — markdown-файлы в .opencode/agent/ и .opencode/command/.
- default agent должен быть primary (build/plan или свой custom).

## opencode.json волта
Файл: [[opencode.json]] (корень волта).
- `$schema`: валидация в редакторе
- `default_agent`: `librarian` — при открытии волта сразу librarian
- `lsp`: `true` — навигация по markdown
- `model`: `opencode/claude-sonnet-4-6`

## Провайдеры/модели
- Формат model: `provider/model-id`.
- Мои проекты на OpenCode Zen: `opencode/claude-sonnet-4-6`.

### OpenCode Zen
Рекомендованный провайдер OpenCode. Curated-список моделей, протестированных на совместимость.

**Характеристики:**
| Параметр | Значение |
|----------|----------|
| Тип | Pay-as-you-go (per token) |
| Префикс в model ID | `opencode/` |
| Base URL | `https://opencode.ai/zen/v1/messages` |
| Эндпоинт списка моделей | `https://opencode.ai/zen/v1/models` |
| Подключение | `/connect` в TUI → opencode.ai/auth |
| SDK-совместимость | `@ai-sdk/anthropic` (Claude), `@ai-sdk/openai-compatible` (остальные) |
| Поддержка | streaming, tool calling, reasoning_effort, prompt caching |

**Подключение:**
1. `/connect` в TUI → выбрать OpenCode Zen
2. Откроется браузер → opencode.ai/auth → создать API key
3. Вставить API key в терминал
4. `/models` → выбрать модель (напр. `opencode/claude-sonnet-4-6`)

**Используемые модели волта:**
- `opencode/deepseek-v4-flash-free` — librarian (по умолчанию, бывшая основная модель)
- `opencode/claude-sonnet-4-6` — запасная (для сложных задач, если DeepSeek не тянет)

**Схожие провайдеры OpenCode:**
- **OpenCode Go** — subscription-based (доступ по подписке), curated subset моделей
- **OpenCode Zen** (он же) — pay-as-you-go, полный каталог

### Конфигурация в opencode.json
```json
{
  "model": "opencode/deepseek-v4-flash-free",
  "small_model": "opencode/claude-haiku-4-5"
}
```

## Cost Control

Три механизма контроля стоимости при работе агентов: `steps`, `doom_loop`, `budgetTokens`.

### steps — лимит итераций агента
Максимальное количество agentic-циклов (мысль → действие → результат), которое агент может выполнить до принудительного перевода в текстовый режим.

```
steps: 15   # в frontmatter агента
```

- **Где задаётся:** frontmatter агента (`.opencode/agent/*.md`) или `opencode.json` → `agent.<name>.steps`
- **Когда лимит достигнут:** агент получает системный промпт "подведи итог, рекоментуй следующие шаги" и отвечает только текстом
- **Для чего:** контроль стоимости — каждый шаг потребляет токены
- **Важно:** каждый spawned subagent (через `task`) получает **свой собственный счётчик** `steps`. При `permission.task: allow` рекурсия НЕ ограничена — цепочка primary → subagent → subagent может привести к экспоненциальному росту
- **Deprecated:** старое имя `maxSteps`

**Значения в волте:**
| Агент | steps |
|-------|-------|
| librarian | 15 (DeepSeek v4-flash-free) |
| build (SERPlux) | 30 |
| plan (SERPlux) | 20 |

### doom_loop — recovery-промпты
Разрешение на автоматические recovery-промпты, когда агент застревает в цикле (повторяет одни и те же действия).

- **Где задаётся:** `permission` блок агента или глобально
- **Значения:** `"allow"` / `"ask"` / `"deny"`
  - `allow` — recovery-промпты работают, агент может получить подсказку для выхода из цикла
  - `deny` — агент не получает подсказок (может зависнуть навсегда)
  - `ask` — спрашивать пользователя
- **Ограничение:** детектит повторяющиеся tool calls в рамках ОДНОЙ сессии; не защищает от рекурсивного спавна subagent'ов через `task`

**В волте:** `doom_loop: allow` (librarian) — recovery разрешён.

### budgetTokens — thinking budget
Бюджет токенов на "внутренние размышления" модели (для reasoning-моделей: Anthropic Claude, OpenAI o-серии).

```json
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-sonnet-4-5": {
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 16000
            }
          }
        }
      }
    }
  }
}
```

- **Где задаётся:** `provider.<provider>.models.<model>.options.thinking.budgetTokens`
- **Зачем:** влияет на качество сложных рассуждений и на стоимость
- **Для OpenAI-моделей:** аналог — `reasoningEffort` (`low` / `medium` / `high`)
- **В волте:** не включён — для задач командного центра (grep/read/edit) не требуется

### Сводка

| Механизм | Что ограничивает | Где задаётся | В волте |
|----------|-----------------|-------------|---------|
| `steps` | количество agentic-итераций | frontmatter агента | 15 |
| `doom_loop` | recovery-промпты | permission блок | allow |
| `budgetTokens` | токены на "размышление" | provider.model.options | не используется |
