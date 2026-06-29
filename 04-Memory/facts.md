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
- `opencode.json` — корневой конфиг: `default_agent: librarian`, `lsp: true`, `$schema`, модель `opencode/deepseek-v4-flash-free`.
- Модель librarian изменена с `opencode/claude-sonnet-4-6` на `opencode/deepseek-v4-flash-free` (2026-06-30) — бесплатная модель для работы командного центра.
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
- Стек: Python 3.11+ / requests / gspread / FastAPI / DeepSeek (labeler) / SQLite
- OpenCode-агенты: build (Sonnet 4.6), plan (Sonnet 4.6), collector-dev (Sonnet 4.6, subagent), reviewer (GPT-5.3-codex, subagent)
- Команд OpenCode нет
- Плагины: env-guard.js, notify.js
- Статус методов: context-as-docs 🟡, model-routing 🟡, остальные ❌

### dv-hub
- Репо: `/home/rudra/Projects/dv-hub`
- GitHub remote: `atmavichara108/dv-hub`
- Стек: TypeScript strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
- 5 OpenCode-агентов: plan (qwen3.7-max), build (deepseek-v4-flash), reviewer (deepseek-v4-pro, subagent), researcher (qwen3.6-plus, subagent), infra (qwen3.7-max)
- 7 команд: /morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task
- 3 плагина: compaction.ts · env-guard.ts · notify.ts
- Статус методов: distill-pattern ✅, model-routing ✅, context-as-docs 🟡, memory-management 🟡, closed-loop ❌, verifier-pattern ❌
- Git submodule: context/ → dv-project
- Docs: 8 файлов (architecture, product-vision, roadmap, glossary, infra-runbook, backend-conventions, mirotalk-setup, known-issues)

### dotfiles
- Репо: `/home/rudra/dotfiles`
- GitHub remote: `atmavichara108/dotfiles`
- Стек: shell / GNU Stow / конфиги Manjaro (23 пакета: zsh, nvim, tmux, git, qtile, alacritty, rofi, picom, btop, bat, dunst, htop, lazygit, neofetch, ranger, screenlayout, scripts, systemd, taskwarrior, wal, weathr, x11, xdg)
- OpenCode инициализирован 2026-06-30
- 1 агент: sysop (deepseek-v4-flash-free, primary, read-only, external_directory: allow)
- 1 команда: /sysaudit
- Статус методов: context-as-docs 🟡, distill-pattern 🟡, остальные ❌ или ➖
- Скрипты: stow.sh (массовый stow), add-package.sh (новый пакет)

### vault (OpenCode-Vault)
- Репо: `/home/rudra/Projects/OpenCode-Vault`
- Это командный центр знаний, не код проекта
- 1 агент: librarian (deepseek-v4-flash-free, primary)
- 6 команд: /ask · /capture · /project · /commit · /project-add · /audit
- Pre-commit hook: проверка пустых файлов + валидация викилинков
- 6 методов заполнены в 02-Methods/
- Статус методов (собственные): context-as-docs ✅, distill-pattern ✅, memory-management 🟡, model-routing ➖, closed-loop ❌, verifier-pattern ❌
