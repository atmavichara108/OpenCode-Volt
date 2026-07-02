---
type: Reference
title: OpenCode — Агенты
description: Типы агентов (primary/subagent), фронтматтер, параллельность, создание.
tags: [opencode, agents]
timestamp: 2026-07-02
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

## Кастомные агенты по проектам

> Каждый проект определяет своих агентов в `.opencode/agents/*.md`.
> Агент auto-discover'ится по имени файла (без .md).

### SERPlux (`/home/rudra/Projects/serp`)

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| build | primary | opencode-go/kimi-k2.7-code | Основная разработка |
| plan | primary | opencode-go/glm-5.2 | Планирование, анализ |
| collector-dev | subagent | opencode-go/kimi-k2.7-code | Topvisor API + сбор данных |
| reviewer | subagent | opencode-go/glm-5.2 | PASS/FAIL верификация |
| ui-dev | subagent | opencode-go/kimi-k2.7-code | Google Sheets UI (Apps Script). Web UI — будущая опция под ADR |
| infra-dev | subagent | opencode-go/qwen3.7-plus | Docker, deploy, серверная инфраструктура |

### dv-hub (`/home/rudra/Projects/dv-hub`)

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| plan | primary | qwen3.7-max | Планирование, спецификации |
| build | primary | deepseek-v4-flash | Основная разработка |
| infra | primary | qwen3.7-max | Инфраструктура |
| reviewer | subagent | deepseek-v4-pro | Код-ревью |
| researcher | subagent | qwen3.6-plus | Исследование, анализ |

### dotfiles (`/home/rudra/dotfiles`)

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| sysop | primary | deepseek-v4-flash-free | Системный инспектор |
| planner | primary | deepseek-v4-flash-free | Архитектор |
| builder | primary | deepseek-v4-flash-free | Строитель |
| reviewer | subagent | deepseek-v4-flash-free | Код-ревью |
| qtile-dev | subagent | deepseek-v4-flash-free | Конфиг qtile |
| bash-dev | subagent | deepseek-v4-flash-free | Shell-скрипты |
| util-dev | subagent | deepseek-v4-flash-free | Утилиты |

### vault (`/home/rudra/Projects/OpenCode-Vault`)

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| librarian | primary | deepseek-v4-flash-free | Командный центр знаний |
