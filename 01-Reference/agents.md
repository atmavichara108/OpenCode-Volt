---
type: Reference
title: OpenCode — Агенты
description: Типы агентов (primary/subagent), фронтматтер, параллельность, создание.
tags: [opencode, agents]
timestamp: 2026-06-27
---
# OpenCode: Агенты

> Выжимка из opencode.ai/docs/agents. Проверено: 2026-06-26.

## Два типа
- **Primary** — основные, переключаешься через **Tab**. Встроенные: `build`, `plan`.
- **Subagent** — вызываются primary-агентом или вручную через `@имя`. Встроенные: `general`, `explore`, `scout`.

## Встроенные
| Агент | Тип | Назначение |
|-------|-----|-----------|
| build | primary | полный доступ ко всем инструментам, основная разработка |
| plan | primary | read-only анализ/планирование (edit и bash = ask) |
| general | subagent | многошаговые задачи, может править файлы, для параллельной работы |
| explore | subagent | быстрый read-only поиск по кодовой базе |
| scout | subagent | внешние доки и зависимости (клонирует репо в кэш) |
| compaction/title/summary | primary (скрытые) | системные, работают автоматически |

## Где определять
- Глобально: `~/.config/opencode/agent/*.md`
- Проект: `.opencode/agent/*.md`
- Или в `opencode.json` → блок `agent`
- Имя файла = имя агента (`reviewer.md` → агент `reviewer`).

## Фронтматтер markdown-агента
```
---
description: ...        # ОБЯЗАТЕЛЬНО, по нему primary решает когда звать subagent
mode: primary|subagent|all   # по умолчанию all
model: provider/model-id
temperature: 0.0–1.0    # 0–0.2 точность, 0.6+ креатив
steps: N                # макс. итераций до принудительного ответа (контроль стоимости)
permission: { ... }     # см. [[permissions]]
hidden: true            # скрыть subagent из @-автокомплита
color: "#hex"|primary|accent|...
---
системный промпт агента
```


## Параллельность / оркестрация
- Primary раздаёт работу subagent'ам через инструмент **task**.
- Право на вызов: `permission.task` с glob-паттернами (`"*": "deny"`, `"orchestrator-*": "allow"`).
- Навигация по дочерним сессиям: `session_child_cycle`, `session_parent`.

## Создание
`opencode agent create` — интерактивно: место, описание, права, генерит markdown.
