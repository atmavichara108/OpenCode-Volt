---
type: project
repo: /home/rudra/Projects/OpenCode-Vault
spec-home: /home/rudra/Projects/OpenCode-Vault/docs/specs/
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
- `tools/` — скрипты-инструменты VibeOS (внешние API как детерминированные инструменты):
  telegram-capture (T-062), ecosystem-map (Pip-Boy/Kanban), playwright-browser (T-134),
  verify-cache (P6 #33), peers (P6 #31)
- `TASKS.md` — трекер задач (type: Task Tracker)
- `99-Inbox.md` — буфер (type: Inbox)
- `AGENTS.md` — правила (type: Agent Instructions)
- `Architecture.md` — архитектура (type: Architecture)
- `DEVELOPMENT-ROADMAP.md` — дорожная карта (type: Roadmap)

## Агент (.opencode/agent/)
| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| librarian | primary | opencode-go/gpt-5.6-luna | командный центр: мониторинг проектов, апдейты, управление знаниями |

> Временная модельная политика до capability-routing: GPT-5.6 Luna как fallback и для librarian, DeepSeek Go для дешёвых вспомогательных ролей.

## Команды (.opencode/command/) — 12
/ask · /capture · /inbox · /project · /commit · /project-add · /audit · /decisions · /distill-pipeline · /handoff · /route · /verify

> 12 дистиллированных команд — реализация [[distill-pattern]] (/done — глобальная, не считается).

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | не применимо к справочнику, но метод описан |
| [[verifier-pattern]] | ✅ | tools/verify-cache (tree-hash гейты, P6 #33) + /verify; verify-subagent acceptance (P6 #34) |
| [[context-as-docs]] | ✅ | AGENTS.md + Architecture.md + вся OKF-структура = документация как инфраструктура |
| [[distill-pattern]] | ✅ | 12 команд |
| [[memory-management]] | ✅ | 04-Memory/ (active-context + facts + session-log) + flush-протокол в librarian.md + session-flush плагин (глобальный) |
| [[model-routing]] | ✅ | librarian opencode-go/gpt-5.6-luna; oracle route (P6 #37, break-glass) в model-routing.md |
| [[capability-routing]] | 🟡 | peers-реестр (P6 #31) + route.log; полная маршрутизация — design contract |
| [[tool-integration-pattern]] | ✅ | 5 инструментов в tools/: telegram-capture, ecosystem-map, playwright-browser, verify-cache, peers |

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
- [x] opencode.json в корне волта (default_agent: librarian, fallback: opencode-go/gpt-5.6-luna)
- [x] T-002: верификация `wikilink` по всему волту
- [x] методы 02-Methods/ — 6 файлов непусты
- [x] 05-Templates/ — project-card, method, README, pre-commit hook, archive script
- [x] единая таблица статусов «Методы × Проекты» в 00-INDEX.md
- [x] Reference — config.md (Zen + cost control) · permissions.md (skills + doom_loop) · plugins.md (Plugin SDK)
- [x] Команды: `/commit`, `/project-add`, `/audit`
- [x] VibeOS.md — концептуальный дашборд системы вайбкодинга (v0.3.1)
- [x] dotfiles — репо создан, путь зафиксирован в карточке
- [x] tools/ — 5 инструментов: telegram-capture, ecosystem-map, playwright-browser (T-134), verify-cache (P6 #33), peers (P6 #31)
- [x] tool-integration-pattern — метод VibeOS; внедрён в vault полностью (5 tools)
- [x] P6 — порт органов M Code Desktop в TUI-стек: replay-budget, noop-guard, input-security (плагины в dotfiles), sandbox/serpctl/release pipeline (в serp), parallel /audit, verify-subagent, oracle route. Реф: [[01-Reference/mcode-desktop]]
- [ ] дорожная карта P5: Telegram-бот, классификация фич, /project-upgrade

## Окружение
- **direnv + .venv** — Python venv, активируется автоматически при входе в корень волта (`.envrc` → `source .venv/bin/activate`). `direnv allow` выполнен 2026-07-08.
- **Зависимости (в venv):** telethon 1.44.0, python-dotenv 1.2.2, pytest 9.1.1. Python 3.14.5.
- **.envrc** — в git (конфигурация проекта). **.venv/** — в .gitignore (не коммитить).

## Лог изменений
- 2026-06-26: волт заведён и наполнен готовыми данными
- 2026-06-27: полный аудит, переименован 99-Inbox, убрано claude-mem, создана 04-Memory, DEVELOPMENT-ROADMAP, обновлён librarian (права + память)
- 2026-06-29: librarian переписан под командный центр; выполнены T-001 — T-018; Reference дополнен; 05-Templates/; pre-commit hook; /audit; таблица статусов
- 2026-08-17: временная модельная политика до capability-routing: fallback и librarian → `opencode-go/gpt-5.6-luna`, дешёвые роли → `opencode-go/deepseek-v4-flash`.
- 2026-07-04: T-061 — memory-management 🟡→✅ (flush-протокол в librarian.md + session-flush плагин уже был)
- 2026-07-07: VibeOS v0.3.0 — новый метод tool-integration-pattern (7-й), директория tools/ + tools/telegram-capture (T-062, в разработке), новое направление R-006 Linux UX Lab, /capture как первый шаг к Telegram-интеграции
- 2026-07-08: внедрено direnv + .venv (Python окружение, авт активация). Зависимости: telethon, python-dotenv, pytest. 39/39 тестов PASS в venv.
- 2026-09-07: P6 апгрейд — порт органов M Code → TUI (replay budget, doom-loop/no-op guard, санитизация/redaction, playwright-browser, verify-cache + /verify, peers, parallel /audit, verify-subagent, oracle route); 5 tools; 12 команд; VibeOS v0.3.1. Коммиты 4a16790/cba43c5/bfa6c7e/3437182 (+dotfiles 0e46291, serp 05ef81b/f519328)
