---
type: Reference
title: OpenCode — Команды
description: Определение команд (opencode.json / .opencode/command/), фронтматтер, плейсхолдеры, встроенные.
tags: [opencode, commands]
timestamp: 2026-07-03
---
# OpenCode: Команды

> Выжимка из opencode.ai/docs/commands. Проверено: 2026-06-26.

## Где определять
- Глобально: `~/.config/opencode/command/*.md`
- Проект: `.opencode/command/*.md`
- Или `opencode.json` → блок `command`
- Имя файла = имя команды (`test.md` → `/test`). Вызов: `/имя`.

## Фронтматтер
```
---
description: ...        # ОБЯЗАТЕЛЬНО, показывается в TUI
agent: build|plan|...   # каким агентом исполнять (опц.)
model: provider/model   # переопределить модель (опц.)
subtask: true           # форсить вызов как subagent (не засорять основной контекст)
---
шаблон промпта
```

## Плейсхолдеры в шаблоне
- `$ARGUMENTS` — все аргументы. `/cmd Button` → Button.
- `$1`, `$2`, `$3` — позиционные аргументы.
- !`команда` — подставляет вывод bash в промпт. Напр. !`npm test`, !`git log --oneline -10`.
- `@путь/файл` — подставляет содержимое файла.

## Встроенные
`/init` · `/undo` · `/redo` · `/share` · `/help`. Свои с тем же именем переопределяют встроенные.

## Кастомные команды волта
| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/ask` | librarian | Ответить на вопрос по волту |
| `/capture` | librarian | Оформить инбокс в методы/карточки |
| `/project` | librarian | Сводка по проекту |
| [`/commit`](/.opencode/command/commit.md) | librarian | Закоммитить изменения в волте (subtask) |
| [`/project-add`](/.opencode/command/project-add.md) | librarian | Создать карточку нового проекта: имя путь описание [тип] [стек] |
| [`/audit`](/.opencode/command/audit.md) | librarian | Аудит проектов: pull, сверка карточки с репо. Без аргумента — все проекты |
| [`/done`](~/.config/opencode/command/done.md) | librarian | Протокол завершения задачи: TASKS.md → Done, описание созданного, VibeOS, active-context, коммит |

## Кастомные команды проектов

> Каждый проект определяет свои команды в `.opencode/command/*.md`.
> Команда auto-discover'ится по имени файла (без .md). Вызов: `/имя`.

### SERPlux (`/home/rudra/Projects/serp`)

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/interface` | ui-dev | Google Sheets UI (Apps Script меню, лист Настройки). Web UI ⏸ ADR |
| `/container` | infra-dev | Создать/обновить Dockerfile + docker-compose |
| `/deploy` | infra-dev | Развернуть на сервере: проверка, обновление, proxy, SSL |

### dv-hub (`/home/rudra/Projects/dv-hub`)

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/morning` | plan | Утренний статус: что сделано, что дальше, блокеры |
| `/spec` | plan | Создать спецификацию задачи |
| `/review` | reviewer | Код-ревью последних изменений |
| `/hygiene` | build | Гигиена кода: линтер, формат, неиспользуемые импорты |
| `/sync-context` | build | Синхронизировать контекст с dv-project submodule |
| `/sync-context-self` | build | Синхронизировать свой контекст |
| `/sync-task` | build | Синхронизировать задачу из трекера |

### dotfiles (`/home/rudra/dotfiles`)

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/sysaudit` | sysop | Аудит системы: софт, дрейф конфигов, статус пакетов |
| `/script` | builder | Создать/обновить shell-скрипт |
| `/qtile` | qtile-dev | Конфигурация qtile window manager |
| `/util` | util-dev | Утилита/инструмент |
| `/prompt` | planner | Промпт для задачи |
| `/notify` | builder | Настроить уведомления |
| `/macro` | builder | Макрос/автозамена |
| `/plugin` | builder | Плагин для OpenCode |
