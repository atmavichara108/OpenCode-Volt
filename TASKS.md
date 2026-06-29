---
type: Task Tracker
title: TASKS — трекер задач по волту
description: Оперативные задачи по доведению волта до рабочего состояния и дальнейшему развитию.
tags: [meta, tasks]
timestamp: 2026-06-27
---
# TASKS — Трекер задач OpenCode Vault

> Основа для планомерной работы. Активную задачу на сессию бери из **Active**.
> Статусы: `🟤 backlog` · `🔵 planned` · `🟡 active` · `✅ done` · `⛔ blocked` · `➖ cancelled`
> Приоритеты: **P0** (блокер) · **P1** (структура) · **P2** (наполнение) · **P3** (полировка) · **P4** (автоматизация)

---

## 🟡 Active — текущая сессия

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-018 | Сводка состояния проектов на дашборд | P3 | [[00-INDEX.md]] |

## 🔵 Planned — следующие задачи

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-006 | Наполнить `plugins.md` — Plugin SDK (@opencode-ai/plugin) | P2 | [[01-Reference/plugins.md]] |
| T-007 | SERPlux — добавить список команд в карточку | P3 | [[03-Projects/SERPlux.md]] |
| T-008 | Обновить карточку SERPlux — актуальные статусы методов | P3 | [[03-Projects/SERPlux.md]] |
| T-009 | Создать единую таблицу «Статус методов × Проекты» | P3 | [[00-INDEX.md]] |
| T-010 | Создать `05-Templates/` — клонируемые шаблоны проектов | P2 | [[Architecture.md]] |
| T-011 | Пре-коммит хук на проверку пустых файлов | P4 | [[DEVELOPMENT-ROADMAP]] |
| T-012 | Плагин валидации викилинков | P4 | [[DEVELOPMENT-ROADMAP]] |
| T-013 | Авто-архивация session-log раз в месяц | P4 | [[DEVELOPMENT-ROADMAP]] |
| T-014 | Команда `/audit` — пакетный обход всех проектов | P3 | [[DEVELOPMENT-ROADMAP]] |
| T-018 | Сводка состояния проектов на дашборд | P3 | [[00-INDEX.md]] |
| T-015 | Telegram-бот для приёма фич и подходов | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-016 | Классификация фич по проектам (автомат) | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-017 | Команда `/project-upgrade` — авто-внедрение методов | P5 | [[DEVELOPMENT-ROADMAP]] |

## 🟤 Backlog — идеи на потом

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| | _Пока пусто._ | | |

## ✅ Done — выполнено

| ID | Задача | Приоритет | Когда | Связано |
|----|--------|-----------|-------|---------|
| T-000 | Переименовать `99-Inbox.md.md` → `99-Inbox.md` | P0 | 2026-06-27 | — |
| T-000 | Убрать claude-mem из всей базы | P0 | 2026-06-27 | [[01-Reference/memory.md]] |
| T-000 | Создать OKF-подбандл памяти `04-Memory/` | P0 | 2026-06-27 | [[04-Memory/index.md]] |
| T-000 | Исправить `external_directory` librarian (ask → allow) | P0 | 2026-06-27 | [[.opencode/agent/librarian.md]] |
| T-000 | Применить OKF v0.1 ко всему волту | P1 | 2026-06-27 | [[index.md]] |
| T-000 | Обновить `00-INDEX.md` под OKF | P1 | 2026-06-27 | [[00-INDEX.md]] |
| T-000 | Обновить `AGENTS.md` — убрать claude-mem, новая память | P1 | 2026-06-27 | [[AGENTS.md]] |
| T-000 | Обновить `Architecture.md` — OKF-структура | P1 | 2026-06-27 | [[Architecture.md]] |
| T-000 | Наполнить `rules-AGENTS.md` | P1 | 2026-06-27 | [[01-Reference/rules-AGENTS.md]] |
| T-000 | Создать `TASKS.md` — трекер задач волта | P1 | 2026-06-27 | [[TASKS.md]] |
| T-000 | Создать команду `/commit` | P1 | 2026-06-27 | [[.opencode/command/commit.md]] |
| T-000 | Прописать авто-документирование в librarian.md | P1 | 2026-06-27 | [[.opencode/agent/librarian.md]] |
| T-000 | Добавить `/commit` в 01-Reference/commands.md | P1 | 2026-06-27 | [[01-Reference/commands.md]] |
| T-001 | Создать `opencode.json` в корне волта (с `$schema`) | P1 | 2026-06-27 | [[opencode.json]] |
| T-002 | Проверить консистентность `wikilink` ссылок по всему волту | P1 | 2026-06-27 | [[DEVELOPMENT-ROADMAP]] |
| T-003 | Наполнить `config.md` — OpenCode Zen провайдер | P2 | 2026-06-27 | [[01-Reference/config.md]] |
| T-004 | Наполнить `config.md` — doom_loop, budget, steps (cost control) | P2 | 2026-06-27 | [[01-Reference/config.md]] |
| T-005 | Наполнить `permissions.md` — skills, doom_loop | P2 | 2026-06-29 | [[01-Reference/permissions.md]] |
| T-006 | Наполнить `plugins.md` — Plugin SDK (@opencode-ai/plugin) | P2 | 2026-06-29 | [[01-Reference/plugins.md]] |
| T-007 | SERPlux — добавить список команд в карточку | P3 | 2026-06-29 | [[03-Projects/SERPlux.md]] |
| T-008 | Обновить карточку SERPlux — актуальные статусы методов | P3 | 2026-06-29 | [[03-Projects/SERPlux.md]] |
| T-009 | Создать единую таблицу «Статус методов × Проекты» | P3 | 2026-06-29 | [[00-INDEX.md]] |
| T-010 | Создать `05-Templates/` — шаблоны проектов и методов | P2 | 2026-06-29 | [[Architecture.md]] |
| T-011 | Пре-коммит хук на проверку пустых файлов | P4 | 2026-06-29 | [[05-Templates/pre-commit-check.sh]] |
| T-012 | Плагин валидации викилинков | P4 | 2026-06-29 | [[05-Templates/pre-commit-check.sh]] |
| T-013 | Авто-архивация session-log раз в месяц | P4 | 2026-06-29 | [[05-Templates/archive-session-log.sh]] |
| T-014 | Команда `/audit` — пакетный обход проектов | P3 | 2026-06-29 | [[.opencode/command/audit.md]] |

---

## Как работать с трекером

1. **Каждая сессия** — librarian читает TASKS.md, выбирает задачу из **Planned**, переносит в **Active**.
2. **Начал задачу** — перемести строку в `🟡 Active`. Обнови `active-context.md`.
3. **Сделал задачу** — перемести строку в `✅ Done`, укажи дату. Обнови `active-context.md`.
4. **Задача заблокирована** — `⛔ blocked` с причиной.
5. **Новая идея** — добавь в `🟤 Backlog` или в `99-Inbox.md`.

Каждая задача содержит:
- **ID** — T-NNN (уникальный номер)
- **Описание** — что конкретно сделать
- **Приоритет** — P0..P4
- **Связано** — `wikilink` на файл/карточку/метод

Номера ID в Done неуникальные (T-000) — при переходе на нумерованные ID проставить сквозную нумерацию.
