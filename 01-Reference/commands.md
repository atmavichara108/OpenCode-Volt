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
| [`/capture`](/.opencode/command/capture.md) | librarian | Извлечь посты из Telegram @inbox_tools по теме, классифицировать |
| [`/inbox`](/.opencode/command/inbox.md) | librarian | Оформить инбокс в методы/карточки/факты |
| `/project` | librarian | Сводка по проекту |
| [`/commit`](/.opencode/command/commit.md) | librarian | Закоммитить изменения в волте (subtask) |
| [`/route`](/.opencode/command/route.md) | librarian | Сформировать scoped capability route и явный handoff без runtime router |
| [`/project-add`](/.opencode/command/project-add.md) | librarian | Создать карточку нового проекта: имя путь описание [тип] [стек] |
| [`/audit`](/.opencode/command/audit.md) | librarian | Аудит проектов: pull, сверка карточки с репо. Без аргумента — все проекты |
| [`/distill-pipeline`](/.opencode/command/distill-pipeline.md) | librarian | Дистилляция состояния пайплайнов: из .opencode/command/ и агентов → в карточку и VibeOS |
| [`/done`](~/.config/opencode/command/done.md) | librarian (глобальная) | Протокол завершения задачи по memory-model: **vault-based** (`04-Memory/` или vault-репо) → TASKS.md + волт-сущности + VibeOS + active-context; **docs-based** (`docs/` без `04-Memory/`, напр. SERPlux) → локальный TASKS.md/CHANGELOG + progress/decisions/techdebt; **fallback** (ни того, ни другого) → локальный TASKS/README/CHANGELOG. Финальный коммит делегирует проектному `/commit` (`.opencode/command/commit.md`, project-resolved — проверяет доступность в текущем проекте, иначе стоп). ⚠️ T-089: gate `verify=PASS → finalize` — отдельный unresolved контракт, `/done` runtime-гарантию verify НЕ даёт |

### Глобальные команды

| Команда | Source | Назначение |
|---------|--------|-----------|
| [`/bridge`](file:///home/rudra/dotfiles/opencode-global/.config/opencode/command/bridge.md) | `/home/rudra/dotfiles/opencode-global/.config/opencode/command/bridge.md` → `~/.config/opencode/command/bridge.md` | Protocol entrypoint для canonical AndroidOS Coordination Bridge: читает контекст текущего repo, определяет relation и named route, останавливается с `UNROUTABLE` без fallback |
| [`/spec`](file:///home/rudra/dotfiles/opencode-global/.config/opencode/command/spec.md) | `/home/rudra/dotfiles/opencode-global/.config/opencode/command/spec.md` → `~/.config/opencode/command/spec.md` | Читает canonical execution spec из Vault `06-Specs/<project>/`; без selector показывает доступные specs, без локального fallback |

После изменения глобальной команды нужно полностью перезапустить OpenCode:
конфигурация и команды загружаются при старте, hot reload не гарантируется.

## Кастомные команды проектов

> Каждый проект определяет свои команды в `.opencode/command/*.md`.
> Команда auto-discover'ится по имени файла (без .md). Вызов: `/имя`.

### SERPlux (`/home/rudra/Projects/serp`)

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/interface` | ui-dev | Google Sheets UI (Apps Script меню, лист Настройки). Web UI ⏸ ADR |
| `/container` | infra-dev | Создать/обновить Dockerfile + docker-compose |
| `/deploy` | infra-dev | Развернуть на сервере: проверка, обновление, proxy, SSL |

`docs/spec-close-serplux-v1.0.md` — только pointer; canonical spec находится в
`/home/rudra/Projects/OpenCode-Vault/06-Specs/SERPlux/`.

### dv-hub (`/home/rudra/Projects/dv-hub`)

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/morning` | plan | Утренний статус: что сделано, что дальше, блокеры |
| `/spec` | plan | Pointer-compatible wrapper: читать canonical Vault execution spec; локальные task specs не являются fallback |
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
