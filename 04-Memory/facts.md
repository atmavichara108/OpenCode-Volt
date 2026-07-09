---
type: Fact Registry
title: Реестр фактов
description: Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения [проверить].
tags: [memory]
timestamp: 2026-07-08
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
Документированы 7 приёмов вайбкодинга:
| Метод | Суть |
|-------|------|
| [[closed-loop]] | Итеративный цикл: план → действие → проверка |
| [[verifier-pattern]] | Проверка через отдельный скрипт/воркфлоу |
| [[context-as-docs]] | Контекстные файлы как документация для ИИ |
| [[distill-pattern]] | Сжатие/структурирование знаний в заметки |
| [[memory-management]] | Управление памятью сессии + файловая память |
| [[model-routing]] | Разные модели для разных шагов (дешёвая/fast → дорогая/точная) |
| [[multi-agent-pipeline]] | Специализированные агенты в цепочках с проверкой |
| [[tool-integration-pattern]] | Внешние API как детерминированные инструменты; «LLM думает, API делает» |

### Границы /loop (closed-loop)
- **Применим:** задачи с быстрой автоматической проверкой (тесты секунды-минуты) и чётким DoD
- **Не применим:** UI-задачи без автопроверки (Apps Script/Sheets), дорогая/долгая проверка, размытые критерии
- **SERPlux:** 111 pytest-тестов → /loop идеален для core-модулей; для Apps Script UI — не сработает, нужен другой механизм

### Внешние инструменты (tools/)
- **Telethon 1.44.0** — единственный живой MTProto-клиент для Python. Pyrogram архивирован (Dec 2024), не поддерживается. Telethon переехал на Codeberg (Feb 2026), 12k stars, MIT license. Выбор для tools/telegram-capture/.
- **Группа @inbox_tools** — открытая Telegram-группа Rudra для сбора постов с интересным софтом. Темы (topics): Приложения, Софт, Вайб, #General, Смарт, Графика, красота, сайтостроение (старое), Обучалки (старое), ИИ, Питонизм (очень старое).
- **Схема маркировки реакциями** (двухуровневая): 👍 ingested (обработан), 🤔 ошибка. Категории: 👨‍💻 dotfiles/Linux UX, 🔥 SERPlux, 🤝 dv-hub, 🏆 VibeOS/метод, 🎉 новый проект. Default для без категории: 👍.
- **EMOJI_MAP (ограничения Telegram)** — Telegram ограничивает доступные реакции (73 шт.). Старые эмодзи (📥⚠️🐧🤖🌐🧠🎯) НЕ доступны → заменены на 👍🤔👨‍💻🔥🤝🏆🎉. Перед использованием нового эмодзи проверять через `client.get_available_reactions()`.
- **tool-integration-pattern** — седьмой метод VibeOS (с 2026-07-07). «LLM думает, API делает». Реализация: tools/ директория, первый инструмент telegram-capture (T-062, внедрён ✅ 2026-07-08).
- **Имя Telegram-приложения** — DesktopWorkspaceManager (short name: manager). Имена «VibeOS Capture»/«vibeos» не прошли валидацию при создании: Telegram требует определённого формата имени приложения.
- **Telethon сам определяет серверы подключения**. Test config (149.154.167.40:443) и Production config (149.154.167.50:443) — дефолтные, явно указывать ip/hash не нужно.
- **Tor SOCKS5 proxy** (127.0.0.1:9050) — обход блокировки Telegram в регионе. Без proxy все DC timeout. Настроен в `.env` (`PROXY_HOST`/`PROXY_PORT`), передаётся в Telethon через python-socks. Критическая инфраструктура для capture.
- **Raw API Telethon** — высокоуровневый метод `send_reaction` НЕ существует в Telethon 1.44.0. Используется raw API: `SendReactionRequest` (из `telethon.tl.functions.messages`) + `ReactionEmoji(emoticon=...)` (из `telethon.tl.types`). Паттерн для будущих интеграций.
- **GetForumTopicsRequest** — импорт из `telethon.tl.functions.messages` (НЕ `channels`). Список тем форума форума получаемый через `client(GetForumTopicsRequest(...))`.
- **peer через get_input_entity** — для запросов raw API нужен `InputPeer`, не entity. Получение: `await client.get_input_entity(peer)` → `InputPeerChannel`/`InputPeerUser`. Передача entity напрямую вызывает ошибки.

### Окружение (direnv + venv)
- **direnv** (v2.37.1) — shell extension для автоматической активации окружения при входе в каталог проекта. Установлен системно (`/usr/bin/direnv`).
- **Паттерн:** в корне каждого Python-проекта — `.envrc` с `source .venv/bin/activate` (или `venv/bin/activate`). После создания/изменения .envrc — один раз `direnv allow`.
- **venv** — Python виртуальное окружение (`.venv/` в корне проекта). Изолирует зависимости. В .gitignore.
- **SERPlux** — эталон: `.envrc` + `venv/`, работает.
- **vault** — внедрено 2026-07-08: `.envrc` + `.venv/` в корне. Зависимости: telethon, python-dotenv, pytest.
- **Конвенция:** каждый новый Python-проект создаёт `.envrc` + `.venv/`, `direnv allow`, зависимости в venv. НЕ глобально.

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
- OpenCode: мульти-агент v3 + verifier + closed-loop + flush-протокол (T-059, T-060, T-061, 2026-07-04)
- 3 primary агента: sysop (инспектор), planner (архитектор), builder (строитель)
- 5 subagent: reviewer, verifier, qtile-dev, bash-dev, util-dev
- 10 команд-пайплайнов: /sysaudit, /script, /qtile, /util, /prompt, /notify, /macro, /plugin, /loop, /flush
- Память: .opencode/memory/ (user-profile.md + decisions.md) + формализованный /flush-протокол
- Все агенты на deepseek-v4-flash-free (тестовый период)
- Статус методов: context-as-docs ✅, distill-pattern ✅, closed-loop ✅, verifier-pattern ✅, memory-management ✅

### vault (OpenCode-Vault)
- Репо: `/home/rudra/Projects/OpenCode-Vault`
- Это командный центр знаний, не код проекта
- 1 агент: librarian (opencode-go/qwen3.7-plus, primary)
- 9 команд: /ask · /capture · /inbox · /project · /commit · /project-add · /audit · /done (глобальная) · /distill-pipeline
- Pre-commit hook: проверка пустых файлов + валидация викилинков
- 7 методов заполнены в 02-Methods/ (+tool-integration-pattern с 2026-07-07)
- Статус методов (собственные): context-as-docs ✅, distill-pattern ✅, memory-management ✅, model-routing ➖, closed-loop ✅, verifier-pattern ✅, tool-integration-pattern ✅ (T-062 внедрён 2026-07-08)
