---
type: project
repo: /home/rudra/Projects/OpenCode-Vault
kind: справочник
stack: markdown + OpenCode
---
# vault (этот волт)

Дашборд-справочник по OpenCode и проектам. OKF v0.1 Knowledge Bundle + OpenCode-проект.

**Запуск:** `opencode` в папке волта.
**Агент:** librarian (primary) — командный центр проектов: мониторинг, апдейты, управление знаниями.

## Структура (OKF)
- `index.md` + `log.md` — OKF bundle root
- `00-INDEX.md` — дашборд (type: Dashboard)
- `01-Reference/` — справочник OpenCode (type: Reference)
- `02-Methods/` — приёмы (type: Method)
- `03-Projects/` — карточки (type: Project Card)
- `04-Memory/` — OKF-подбандл памяти
- `tools/` — скрипты-инструменты VibeOS (внешние API как детерминированные инструменты; telegram-capture в разработке, T-062)
- `TASKS.md` — трекер задач (type: Task Tracker)
- `99-Inbox.md` — буфер (type: Inbox)
- `AGENTS.md` — правила (type: Agent Instructions)
- `Architecture.md` — архитектура (type: Architecture)
- `DEVELOPMENT-ROADMAP.md` — дорожная карта (type: Roadmap)

## Агент (.opencode/agent/)
| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| librarian | primary | opencode/deepseek-v4-flash-free | командный центр: мониторинг проектов, апдейты, управление знаниями |

> Модель сменена с claude-sonnet-4-6 на deepseek-v4-flash-free 2026-06-30.

## Команды (.opencode/command/) — 9
/ask · /capture · /inbox · /project · /commit · /project-add · /audit · /done · /distill-pipeline

> 9 дистиллированных команд — реализация [[distill-pattern]].

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | не применимо к справочнику, но метод описан |
| [[verifier-pattern]] | ❌ | не применимо к справочнику |
| [[context-as-docs]] | ✅ | AGENTS.md + Architecture.md + вся OKF-структура = документация как инфраструктура |
| [[distill-pattern]] | ✅ | 9 команд (8 локальных + /done глобальная) |
| [[memory-management]] | ✅ | 04-Memory/ (active-context + facts + session-log) + flush-протокол в librarian.md + session-flush плагин (глобальный) |
| [[model-routing]] | ➖ | один агент, роутинг не нужен |
| [[tool-integration-pattern]] | 🟡 | директория tools/ создана, первый инструмент `tools/telegram-capture/` (T-062) в разработке; /capture — извлечение постов → librarian классифицирует |

> Волт — единственный проект, где vault-методы (context-as-docs, distill-pattern) реализованы **по назначению**: волт документирует сам себя.

## Состояние
- [x] OKF v0.1 — все концепты имеют YAML frontmatter с type
- [x] index.md + log.md (корень + 04-Memory)
- [x] структура
- [x] librarian + команды
- [x] Reference — все разделы заполнены (memory.md — OKF-based)
- [x] карточки SERPlux, dv-hub, dotfiles, vault
- [x] 04-Memory — OKF-подбандл памяти (index + log + 3 концепта)
- [x] DEVELOPMENT-ROADMAP — полный план с приоритетами (включая P5 будущее)
- [x] rules-AGENTS.md — наполнен
- [x] TASKS.md — трекер задач создан
- [x] opencode.json в корне волта (default_agent: librarian, model: deepseek-v4-flash-free)
- [x] T-002: верификация `wikilink` по всему волту
- [x] методы 02-Methods/ — 6 файлов непусты
- [x] 05-Templates/ — project-card, method, README, pre-commit hook, archive script
- [x] единая таблица статусов «Методы × Проекты» в 00-INDEX.md
- [x] Reference — config.md (Zen + cost control) · permissions.md (skills + doom_loop) · plugins.md (Plugin SDK)
- [x] Команды: `/commit`, `/project-add`, `/audit`
- [x] VibeOS.md — концептуальный дашборд системы вайбкодинга
- [x] dotfiles — репо создан, путь зафиксирован в карточке
- [x] tools/ — директория скриптов-инструментов VibeOS заведена (telegram-capture в разработке, T-062)
- [x] tool-integration-pattern — 7-й метод VibeOS, описан в 02-Methods/
- [ ] дорожная карта P5: Telegram-бот, классификация фич, /project-upgrade

## Окружение
- **direnv + .venv** — Python venv, активируется автоматически при входе в корень волта (`.envrc` → `source .venv/bin/activate`). `direnv allow` выполнен 2026-07-08.
- **Зависимости (в venv):** telethon 1.44.0, python-dotenv 1.2.2, pytest 9.1.1. Python 3.14.5.
- **.envrc** — в git (конфигурация проекта). **.venv/** — в .gitignore (не коммитить).

## Лог изменений
- 2026-06-26: волт заведён и наполнен готовыми данными
- 2026-06-27: полный аудит, переименован 99-Inbox, убрано claude-mem, создана 04-Memory, DEVELOPMENT-ROADMAP, обновлён librarian (права + память)
- 2026-06-29: librarian переписан под командный центр; выполнены T-001 — T-018; Reference дополнен; 05-Templates/; pre-commit hook; /audit; таблица статусов
- 2026-06-30: создан VibeOS; модель → deepseek-v4-flash-free; ревью — добавлены собственные статусы методов (context-as-docs ✅, distill ✅, memory-mgmt 🟡), модель в карточке
- 2026-07-04: T-061 — memory-management 🟡→✅ (flush-протокол в librarian.md + session-flush плагин уже был)
- 2026-07-07: VibeOS v0.3.0 — новый метод tool-integration-pattern (7-й), директория tools/ + tools/telegram-capture (T-062, в разработке), новое направление R-006 Linux UX Lab, /capture как первый шаг к Telegram-интеграции
- 2026-07-08: внедрено direnv + .venv (Python окружение, авт активация). Зависимости: telethon, python-dotenv, pytest. 39/39 тестов PASS в venv.
