---
type: Fact Registry
title: Реестр фактов
description: Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения [проверить].
tags: [memory]
timestamp: 2026-06-27
---
# Реестр фактов

> Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения `[проверить]`.

## OpenCode

### Агенты
- **librarian** — агент командного центра. Режим: primary (default в opencode.json). Запускается без `/agent`. Области: мониторинг проектов, аудит, управление знаниями.
- Дочерние агенты не поддерживаются в агентской архитектуре OpenCode (только subagent в командах/скриптах).

### Конфигурация
- `opencode.json` — корневой конфиг: `default_agent: librarian`, `lsp: true`, `$schema`, модель `opencode/claude-sonnet-4-6`.
- `steps` в агенте = число шагов агента (действий). `steps: 15` достаточно для задач командного центра.
- `doom_loop: allow` — разрешает recovery-промпты при повторах.
- `budgetTokens` — не включён в конфиг волта (не требуется для командного центра).

### Права и система плагинов
- `permissions` в opencode.json — права доступа для агента (external_directory, bash, edit и т.д.).
- **Skills** — плагины-помощники (SKILL.md), подгружаемые при совпадении задачи; есть белый список путей.
- **Doom loop** — механизм обнаружения зацикливания: агент повторяет одни и те же действия → recovery-промпт.
- **Plugin SDK** (`@opencode-ai/plugin`) — Node.js SDK для создания плагинов с событиями и кастомными инструментами.

### Методы (02-Methods/)
Документированы 6 приёмов вайбкодинга:
| Метод | Суть |
|-------|------|
| [[closed-loop]] | Итеративный цикл: план → действие → проверка |
| [[verifier-pattern]] | Проверка через отдельный скрипт/воркфлоу |
| [[context-as-docs]] | Контекстные файлы как документация для ИИ |
| [[distill-pattern]] | Сжатие/структурирование знаний в заметки |
| [[memory-management]] | Управление памятью сессии + файловая память |
| [[model-routing]] | Разные модели для разных шагов (дешёвая/fast → дорогая/точная) |

## Проекты

### SERPlux
- Репо: `/home/rudra/Projects/serp`
- GitHub remote: `atmavichara108/SERPlux`
- Стек: DeepSeek labeler + Zen primary
- OpenCode-агенты: build/plan, collector-dev, reviewer (primary/subagent без команды)
- Команд OpenCode нет
- Статус методов: context-as-docs ✅, memory-management ❌, всё остальное ❌

### dv-hub
- Репо: `/home/rudra/Projects/dv-hub`
- GitHub remote: `atmavichara108/dv-hub`
- Стек: TypeScript strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
- 6 OpenCode-агентов: plan, build, reviewer, researcher, infra (+ sysop для деплоя)
- 9 команд: /morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task · /problem · /plan
- 3 плагина: compaction.ts · env-guard.ts · notify.ts
- Статус методов: ❌ все 6
- Git submodule: context/ → dv-project

### dotfiles
- Репо: `/home/rudra/dotfiles`
- GitHub remote: `atmavichara108/dotfiles`
- Стек: shell / Manjaro configs
- OpenCode не инициализирован

### vault (OpenCode-Vault)
- Репо: `/home/rudra/Projects/OpenCode-Vault`
- Это командный центр знаний, не код проекта
- 1 агент: librarian
- 6 команд: /ask · /capture · /project · /commit · /project-add · /audit
- Pre-commit hook: проверка пустых файлов + валидация викилинков
- 6 методов заполнены в 02-Methods/
