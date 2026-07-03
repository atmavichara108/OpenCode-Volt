---
type: Fact Registry
title: Реестр фактов
description: Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения [проверить].
tags: [memory]
timestamp: 2026-07-03
---
# Реестр фактов

> Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения `[проверить]`.

## Профиль пользователя
- **Полное имя:** Max Rudra
- **Сокращения:** Rudra (внутренние контексты), mr (аббревиатура)
- **Роль:** вайбкодер, системный инженер, минималист, пермакультурщик
- **Язык:** русский (основной), терминал-нативный стек
- **GitHub:** [max-ai](https://github.com/max-ai)

## OpenCode

### Агенты
- **librarian** — агент командного центра. Режим: primary (default в opencode.json). Запускается без `/agent`. Области: мониторинг проектов, аудит, управление знаниями.
- Дочерние агенты не поддерживаются в агентской архитектуре OpenCode (только subagent в командах/скриптах).

### Конфигурация
- `opencode.json` — корневой конфиг: `default_agent: librarian`, `lsp: true`, `$schema`, модель `opencode-go/deepseek-v4-flash-free` (дефолт для субагентов).
- Модель librarian: `opencode-go/qwen3.7-plus` (сильная модель Go-подписки для дирижёра).
- Субагенты general/build/explore явно зафиксированы на Go-моделях (не наследуют от вызывающего).
- `steps` в агенте = число шагов агента (действий). `steps: 15` достаточно для задач командного центра.
- `doom_loop: allow` — разрешает recovery-промпты при повторах.
- `budgetTokens` — не включён в конфиг волта (не требуется для командного центра).

### Папки агентов и плагины
- Папки агентов: глобальные = `~/.config/opencode/agent/` (ед.ч.), SERPlux = `.opencode/agents/` (мн.ч.). Verifier и meta — глобальные субагенты, видны в проектах через мёрж (OpenCode свежей версии).
- `commit-guard` плагин = неотвратимый гейт на `tool.execute.before`.
- `session-flush` плагин (глобальный, `~/.config/opencode/plugins/`) — копит `file.edited`, при `session.idle` дописывает в `04-Memory/session-log/YYYY-MM-DD.md`. Детерминированный, агентов не вызывает.

### Права и система плагинов
- `permissions` в opencode.json — права доступа для агента (external_directory, bash, edit и т.д.).
- **Skills** — плагины-помощники (SKILL.md), подгружаемые при совпадении задачи; есть белый список путей.
- **Doom loop** — механизм обнаружения зацикливания: агент повторяет одни и те же действия → recovery-промпт.
- **Plugin SDK** (`@opencode-ai/plugin`) — Node.js SDK для создания плагинов с событиями и кастомными инструментами.
- **tool.execute.before** — штатный механизм OpenCode для перехвата инструментов ДО выполнения. Плагин может блокировать вызов (пример: commit-guard блокирует git commit если тесты падают). Это неотвратимый гейт на уровне рантайма.

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

### Границы /loop (closed-loop)
- **Применим:** задачи с быстрой автоматической проверкой (тесты секунды-минуты) и чётким DoD
- **Не применим:** UI-задачи без автопроверки (Apps Script/Sheets), дорогая/долгая проверка, размытые критерии
- **SERPlux:** 111 pytest-тестов → /loop идеален для core-модулей; для Apps Script UI — не сработает, нужен другой механизм

## Проекты

### SERPlux
- Репо: `/home/rudra/Projects/serp`
- GitHub remote: `atmavichara108/SERPlux`
- Стек: Python 3.11+ / requests / gspread / FastAPI / DeepSeek (labeler) / SQLite / Docker
- OpenCode-агенты (Go-подписка, 2026-07-02): 6 агентов — build (kimi-k2.7-code, primary, в opencode.json), plan (glm-5.2, primary), collector-dev (kimi-k2.7-code, subagent), reviewer (glm-5.2, subagent), ui-dev (kimi-k2.7-code, subagent, активен), infra-dev (qwen3.7-plus, subagent)
- Команды OpenCode (5): `/commit` (build, deepseek-v4-flash, subtask), `/interface` (ui-dev), `/container` (infra-dev), `/deploy` (infra-dev), `/dream` (build, memory-flush). Глобально: `/loop` (build)
- Плагины (4): env-guard.js, notify.js, commit-guard.js, compaction.js
- Статус: Core ✅, Docker ✅, Deploy ✅, Web UI ⏸ (ADR: только Sheets). Мультиклиентность ✅ (clients/positions/labels, client_id, domains mode). 111/111 тестов.
- Статус методов: context-as-docs ✅, model-routing ✅, multi-agent-pipeline ✅, distill-pattern ✅, verifier-pattern ✅, closed-loop ✅, memory-management 🟡

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
- Стек: shell / GNU Stow / 23 пакета конфигов / OpenCode multi-agent
- OpenCode: полная мульти-агентная архитектура (2026-06-30 v2)
- 3 primary агента: sysop (инспектор), planner (архитектор), builder (строитель)
- 4 subagent: reviewer, qtile-dev, bash-dev, util-dev
- 8 команд-пайплайнов: /sysaudit, /script, /qtile, /util, /prompt, /notify, /macro, /plugin
- Память: .opencode/memory/ (user-profile.md + decisions.md)
- Все агенты на deepseek-v4-flash-free (тестовый период)
- Статус методов: context-as-docs ✅, distill-pattern ✅, closed-loop 🟡, verifier-pattern 🟡, memory-management 🟡

### vault (OpenCode-Vault)
- Репо: `/home/rudra/Projects/OpenCode-Vault`
- Это командный центр знаний, не код проекта
- 1 агент: librarian (opencode-go/qwen3.7-plus, primary)
- 7 команд: /ask · /capture · /project · /commit · /project-add · /audit · /done (глобальная)
- Pre-commit hook: проверка пустых файлов + валидация викилинков
- 6 методов заполнены в 02-Methods/
- Статус методов (собственные): context-as-docs ✅, distill-pattern ✅, memory-management 🟡, model-routing ➖, closed-loop ✅, verifier-pattern ✅
