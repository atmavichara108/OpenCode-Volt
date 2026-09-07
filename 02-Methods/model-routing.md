---
type: method
status: stable
tags: [method]
---
# Model Routing

## Проблема
Один модель на все роли = два провала одновременно: переплата на простых задачах (Opus на навигацию по файлам — 5x дороже Haiku без выигрыша) и просадка качества на сложных (Haiku на планирование → кривая декомпозиция, ошибки каскадом вниз). Стоимость петель верификации на дешёвой модели тоже считается (Fable 5, 2026).

## Решение
Static routing — модель под роль (подходит для фиксированных пайплайнов как у меня, без ML-классификатора). Экономия ~51% против uniform Opus при сохранении качества там, где оно влияет на исход.

## 3 Режима выбора моделей (2026-09-01)

Для экономичного использования созданы **3 программно переключаемых режима**:

| Режим | Назначение | Цена | Primary модель |
|-------|------------|------|----------------|
| **FREE** 🆓 | 100% бесплатные модели | $0 | `opencode/nemotron-3-ultra-free` |
| **MEDIUM** ⚖️ | Сильные + бесплатные | ~$0.02/1K | `opencode-go/gpt-5.6-luna` |
| **PREMIUM** 💎 | Топовые модели | ~$3-5/1K | `opencode/claude-opus-5` |

**Детали:** [[config-modes]], [[providers]]

### FREE Mode (полностью бесплатный)
| Роль | Модель | Провайдер |
|------|--------|-----------|
| Primary / Координация | `opencode/nemotron-3-ultra-free` | Zen |
| Complex Tasks | `opencode/nemotron-3-ultra-free` | Zen |
| Research / Navigation | `opencode/deepseek-v4-flash-free` | Zen |
| Build / Implementation | `openrouter/minimax-m3:free` | OpenRouter |
| Review / Verifier | `opencode/ling-3.0-flash-free` | Zen |

### MEDIUM Mode (баланс цена/качество) — **Текущий рабочий**
| Роль | Модель | Провайдер |
|------|--------|-----------|
| Primary / Координация | `opencode-go/gpt-5.6-luna` | Go |
| Complex Planning | `opencode-go/gpt-5.6-luna` | Go |
| Build / Implementation | `opencode-go/gpt-5.6-luna` | Go |
| Research / Navigation | `opencode/deepseek-v4-flash-free` | Zen |
| Review | `opencode/ling-3.0-flash-free` | Zen |
| Verifier | `opencode/deepseek-v4-flash-free` | Zen |
| Fallback | `opencode/claude-sonnet-4-6` | Zen |

### PREMIUM Mode (на будущее)
| Роль | Модель | Провайдер |
|------|--------|-----------|
| Primary / Координация | `opencode/claude-opus-5` | Zen |
| Complex Planning | `opencode/claude-opus-5` | Zen |
| Build / Implementation | `opencode/claude-sonnet-4-6` | Zen |
| Code Review | `opencode/gpt-5.3-codex` | Zen |
| Research | `opencode/gemini-3.7-flash` | Zen |
| Verifier | `opencode/claude-sonnet-4-6` | Zen |

## Таблица ролей (Claude-стек, цены апрель 2026)
| Роль | Модель | Почему |
|------|--------|--------|
| Координация/планирование | Opus 4.6 ($5/$25) | декомпозиция каскадит вниз, тут нельзя экономить |
| Реализация (build) | Sonnet 4.6 ($3/$15) | 79.6% SWE-bench, меньше tool-calls, дефолт исполнителя |
| Навигация/поиск/линт | Haiku 4.5 ($1/$5) | простой retrieval, 3-5x дешевле |
| Верификация | Sonnet (или Opus) | корректность важнее скорости |
| Code review (async) | GPT-5.2 ($1.75/$14) | самый дотошный на баги/безопасность |

## Реализация в OpenCode
В `model` агента (фронтматтер или opencode.json). Сейчас оба моих проекта на `opencode/claude-sonnet-4-6` для build И plan — это нормально для 2-3-агентных пайплайнов, но plan можно поднять, а verifier удешевить.

Практический тест Haiku: если его вывод требует правки Sonnet'ом чаще 20% случаев — экономия съедена ре-промптингом. Мониторить первую неделю.

**Переключение режимов:** через `model variants` (keybind `variant_cycle`) или переменные окружения. См. [[config-modes]].

## Когда применять / когда НЕ применять
- Применять: как только появляется >2 ролей или петля гоняет verifier часто.
- НЕ усложнять dynamic-роутингом: при <500 вызовов/день overhead классификатора дороже экономии. Мне хватает static.

## SERPlux economical policy — planned / target (2026-09-05)

> **Status: planned/target policy, not yet implemented.** Ниже описана целевая модель маршрутизации для SERPlux. Фактическая текущая конфигурация SERPlux см. в карточке проекта `03-Projects/SERPlux.md` и его локальных agent-фронтматтерах.

Цель — economical model routing для минимизации costs при сохранении качества:

### Cheap/free модели (navigation/docs/simple analysis/reviewer/verifier)
| Роль | Модель | Почему |
|------|--------|--------|
| Navigation / file search | `opencode/deepseek-v4-flash-free` | Free, быстрый retrieval |
| Documentation reading | `opencode/deepseek-v4-flash-free` | Free, достаточно для read-only |
| Simple analysis | `opencode/deepseek-v4-flash-free` | Free, pattern matching |
| Reviewer (quality/style) | `opencode/ling-3.0-flash-free` | Free, read-only review |
| Verifier (acceptance) | `opencode/deepseek-v4-flash-free` | Free, syntax/check validation |

### Luna only (strict/complex)
| Роль | Модель | Почему |
|------|--------|--------|
| Complex planning | `opencode-go/gpt-5.6-luna` | Декомпозиция каскадит вниз |
| Complex build (architecture) | `opencode-go/gpt-5.6-luna` | Критичные решения |
| Coordination (librarian) | `opencode-go/gpt-5.6-luna` | Cross-project context |

### Named workflow
`plan (Luna) → build (Luna) → reviewer (free) → verifier (free)`

Capability routing ортогонален model routing: capability отвечает за "кто делает", model за "какая модель". UNROUTABLE вместо generic fallback при отсутствии named capability.

## Oracle route — break-glass второе мнение

Иногда маршрутизация по ролям недостаточна: дирижёр стоит перед **выбором с
дорогой ошибкой** (архитектурное решение, миграция данных, security-изменение)
и не уверен в собственном суждении. Для этого — отдельный канал к **более
сильной модели** по запросу, а не как штатный шаг пайплайна.

- **Semantics (референс M Code oracle, P6 #37):** break-glass, второе мнение.
  Не рутинная проверка — `reviewer`/`verifier` закрывают штатные гейты; oracle
  зовут, когда цена ошибки высока и решение неоднозначно (trade-off между
  несколькими архитектурами, миграция, публичное API).
- **Триггер:** дирижёр сам формирует вопрос и признаёт, что застрял. Это не
  `UNROUTABLE`-фолбэк и не подмена capability routing — capability отвечает
  «кто делает», model routing «какая модель», oracle «второе мнение по
  конкретному решению».
- **Контракт:** question с узкой постановкой + context (фрагменты кода/diff,
  варианты A/B и их trade-off). Ответ — входной аргумент для решения, не
  verdict и не исполнение.
- **Ограничения:** ручная, а не автоматическая стадия; не заменяет
  `verifier`-acceptance (тот проверяет факт, oracle советует по выбору).
- **В TUI:** глобального `oracle`-хука нет (в бинаре 1.18.5 «oracle» — это
  провайдер Model Oracle AI, не орган движка). Канал реализуется политикой:
  дирижёр на model-routing для спорного решения запрашивает более сильную
  модель через явный model-выбор или отдельный агент. См. [[01-Reference/mcode-desktop]] § «Oracle — второе мнение».

## Связанные
- Reference: [[config]], [[agents]], [[config-modes]], [[providers]]
- Влияет на: [[verifier-pattern]], [[closed-loop]] (стоимость петли)
- Внедрён в: [[dv-hub]] ✅ (5 агентов, 4 модели: qwen3.7-max / deepseek-v4-flash / deepseek-v4-pro / qwen3.6-plus), [[SERPlux]] 🟡 (target: economical policy above — planned; actual config см. `03-Projects/SERPlux.md`), [[vault]] ➖ (один агент)
- Ортогонально: [[capability-routing]] — capability routing отвечает за "кто делает", model routing за "какая модель"
