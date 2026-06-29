# Bundle Update Log

## 2026-06-29
* **T-001**: `opencode.json` — default_agent: librarian, LSP, $schema
* **T-002**: Верификация `wikilink` по всему волту (исправлено 8 файлов)
* **T-003—T-004**: `config.md` — OpenCode Zen + cost control (steps, doom_loop, budgetTokens)
* **T-005**: `permissions.md` — skills, doom_loop recovery
* **T-006**: `plugins.md` — Plugin SDK (@opencode-ai/plugin), events, custom tools
* **T-007—T-008**: SERPlux — команды (нет), статусы 6 методов
* **T-009**: Единая таблица «Статус методов × Проекты» в 00-INDEX.md
* **T-010**: `05-Templates/` — project-card, method, README, pre-commit-check.sh, archive-session-log.sh
* **T-011—T-012**: Pre-commit hook — проверка пустых файлов + валидация викилинков
* **T-013**: Скрипт архивации session-log (старше 30 дней)
* **T-014**: Команда `/audit` — пакетный обход проектов
* **T-018**: Сводка состояния проектов на дашборд
* **AGENTS.md**: переписан под командный центр
* **librarian**: переписан (steps:15, doom_loop:allow, startup: init memory)
* **Факты**: `facts.md` — полный реестр, `active-context.md` — финализирован
* **Карточки**: vault.md, dv-hub.md, dotfiles.md — синхронизированы

## 2026-06-27
* **OKF migration**: Applied Open Knowledge Format v0.1 to entire vault
* **Creation**: Root `index.md` and `log.md` per OKF spec
* **Creation**: `04-Memory/index.md` and `04-Memory/log.md` as OKF sub-bundle
* **Update**: Added YAML frontmatter (`type`, `title`, `description`, `timestamp`) to all concept files
* **Update**: Librarian permission fixed: `external_directory: allow`, bash whitelist expanded
* **Update**: All claude-mem references replaced with OKF-backed file memory
* **Creation**: DEVELOPMENT-ROADMAP.md with P0–P4 priorities
* **Fix**: Renamed `99-Inbox.md.md` → `99-Inbox.md` (double extension bug)

## 2026-06-26
* **Initialization**: Created vault structure, reference files, project cards, librarian agent
