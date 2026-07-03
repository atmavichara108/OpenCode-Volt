---
type: Reference
title: OpenCode — Глобальная конфигурация
description: Структура ~/.config/opencode/ — глобальные агенты, команды, плагины. Не в гите, но часть экосистемы.
tags: [opencode, config, global]
timestamp: 2026-07-03
---
# OpenCode: Глобальная конфигурация

> Каталог `~/.config/opencode/` — глобальная конфигурация OpenCode. Не попадает в гит проектов, но является частью единой агентской сети.

## Структура каталога

```
~/.config/opencode/
├── agent/              # Глобальные субагенты (видны во всех проектах)
│   ├── meta.md         # Мета-агент инфраструктуры
│   └── verifier.md     # Strict acceptance verifier
├── command/            # Глобальные команды (видны во всех проектах)
│   ├── done.md         # Протокол завершения задачи
│   └── loop.md         # Closed-loop implementation
├── plugins/            # Глобальные плагины
│   ├── session-flush.ts # Автодокументирование в session-log
│   └── claude-mem.js.bak # Бэкап (удалён из экосистемы)
├── AGENTS.md           # Глобальные инструкции агентам (пустой)
├── opencode.jsonc      # Глобальный конфиг (минимальный: $schema)
├── package.json        # Зависимости для плагинов
├── bun.lock            # Bun lockfile
└── node_modules/       # Установленные зависимости
```

## Глобальные агенты

Агенты в `~/.config/opencode/agent/` видны во **всех проектах** через механизм мёржа (OpenCode свежей версии).

| Агент | Модель | Назначение |
|-------|--------|-----------|
| **meta** | opencode-go/glm-5.2 | Мета-агент инфраструктуры: правит `.opencode/**`, `~/.config/opencode/**`, vault. НЕ трогает код приложений |
| **verifier** | opencode-go/glm-5.2 | Strict acceptance verifier. `edit: deny`, bash whitelist. Returns PASS/FAIL, never edits |

**Важно:**
- Папка `agent/` (единственное число) — для глобальных агентов
- В проектах папка `agents/` (множественное число) — для проектных агентов
- Глобальные агенты мёржатся с проектными (OpenCode свежей версии)

## Глобальные команды

Команды в `~/.config/opencode/command/` доступны во **всех проектах**.

| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/done` | (активный агент) | Протокол завершения задачи: TASKS.md → Done, описание созданного, VibeOS, active-context, коммит |
| `/loop` | build | Closed-loop implementation until acceptance passes (arg1=goal, arg2=ci command) |

**Важно:**
- `/done` не привязан к конкретному агенту (`agent:` убран из frontmatter), чтобы работать в любом проекте
- librarian существует только в vault, поэтому команды с `agent: librarian` падают в других проектах

## Глобальные плагины

Плагины в `~/.config/opencode/plugins/` загружаются во **всех проектах**.

| Плагин | Назначение |
|--------|-----------|
| **session-flush.ts** | Копит `file.edited`, при `session.idle` дописывает в `04-Memory/session-log/YYYY-MM-DD.md`. Детерминированный, агентов не вызывает |
| claude-mem.js.bak | Бэкап удалённого плагина (не активен) |

## Связь с проектными конфигурациями

**Порядок загрузки:**
1. Глобальный config (`~/.config/opencode/opencode.jsonc`)
2. Проектный config (`<project>/opencode.json`)
3. Глобальные plugins/ (`~/.config/opencode/plugins/`)
4. Проектные plugins/ (`<project>/.opencode/plugins/`)

**Мёрж агентов:**
- Глобальные агенты (`~/.config/opencode/agent/`) + проектные (`<project>/.opencode/agents/`) = полный набор
- При конфликте имён — проектный агент переопределяет глобальный [проверить]

## Что не попадает в гит

| Путь | Причина |
|------|---------|
| `~/.config/opencode/` | Глобальный конфиг пользователя, вне репозиториев |
| `<project>/.opencode/node_modules/` | Зависимости для плагинов (в `.gitignore`) |
| `<project>/.opencode/package-lock.json` | Lockfile (в `.gitignore`) |

## Документирование в волте

Состояние глобальной конфигурации фиксируется в волте:
- Агенты → `01-Reference/agents.md` (секция "Экосистемные агенты (глобальные)")
- Команды → `01-Reference/commands.md`
- Плагины → `01-Reference/plugins.md`
- Факты → `04-Memory/facts.md`

Это позволяет отслеживать изменения глобальной инфраструктуры даже though она не в гите.
