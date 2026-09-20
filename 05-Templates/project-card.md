---
type: project
repo: /path/to/repo
spec-home: /path/to/repo/docs/specs/
kind: коммерция | волонтёрский | система
stack: технологии через /
---

# ИмяПроекта

Краткое описание.

**Окружение:** зависимости, секреты, запуск.
**CI / проверка:** команды для тестов.
**Провайдер:** OpenCode Zen / другой.
**Canonical specs:** `docs/specs/` в этом репозитории (`spec-home` выше) — execution
source of truth; локальный `/spec` резолвит оттуда.

## Агенты (.opencode/agents/)
| Агент | Назначение |
|-------|-----------|
| build (primary) | модель, temp, steps, права |
| plan (primary) | модель, temp, steps, права |

## Команды
/ask · /project · ...

## Плагины (.opencode/plugins/)
список

## Конфиг (opencode.json)
кратко: права, модель, LSP

## Состояние методов
| Метод | Статус |
|-------|--------|
| [[closed-loop]] | ❌ |
| [[verifier-pattern]] | ❌ |
| [[context-as-docs]] | ❌ |
| [[distill-pattern]] | ❌ |
| [[memory-management]] | ❌ |
| [[model-routing]] | ❌ |

## Лог изменений
- YYYY-MM-DD: карточка заведена
