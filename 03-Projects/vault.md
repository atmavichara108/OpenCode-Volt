---
type: project
repo: /home/rudra/Projects/OpenCode-Vault
kind: справочник
stack: markdown + OpenCode
---
# vault (этот волт)

Дашборд-справочник по OpenCode и проектам. OKF v0.1 Knowledge Bundle + OpenCode-проект.

**Запуск:** `opencode` в папке волта.
**Агент:** librarian (primary) — читает и ведёт знания, наружу ходит только для `/project` (external_directory: allow, bash ограничен).

## Структура (OKF)
- `index.md` + `log.md` — OKF bundle root
- `00-INDEX.md` — дашборд (type: Dashboard)
- `01-Reference/` — справочник OpenCode (type: Reference)
- `02-Methods/` — приёмы (type: Method)
- `03-Projects/` — карточки (type: Project Card)
- `04-Memory/` — OKF-подбандл памяти
- `TASKS.md` — трекер задач (type: Task Tracker)
- `99-Inbox.md` — буфер (type: Inbox)
- `AGENTS.md` — правила (type: Agent Instructions)
- `Architecture.md` — архитектура (type: Architecture)
- `DEVELOPMENT-ROADMAP.md` — дорожная карта (type: Roadmap)

## Агент (.opencode/agent/)
| Агент | Назначение |
|-------|-----------|
| librarian | ответы по волту, ведение заметок, разгребание инбокса |

## Команды (.opencode/command/)
/ask · /capture · /project

## Состояние
- [x] OKF v0.1 — все концепты имеют YAML frontmatter с type
- [x] index.md + log.md (корень + 04-Memory)
- [x] структура
- [x] librarian + команды
- [x] Reference — все разделы заполнены (memory.md — OKF-based)
- [x] карточки SERPlux, dv-hub, vault
- [x] 04-Memory — OKF-подбандл памяти (index + log + 3 концепта)
- [x] DEVELOPMENT-ROADMAP — полный план с приоритетами
- [x] rules-AGENTS.md — наполнен
- [x] TASKS.md — трекер задач создан
- [ ] opencode.json в корне волта — T-001 (Active)
- [ ] методы 02-Methods/ — 6 файлов пусты (заполняет пользователь)
- [ ] 05-Templates/ — не создан
- [ ] dotfiles — после создания репо
- [ ] единая таблица статусов «Методы × Проекты»

## Лог изменений
- 2026-06-26: волт заведён и наполнен готовыми данными
- 2026-06-27: полный аудит, переименован 99-Inbox, убрано claude-mem, создана 04-Memory, DEVELOPMENT-ROADMAP, обновлён librarian (права + память)
