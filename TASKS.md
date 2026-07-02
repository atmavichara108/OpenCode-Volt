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
| T-045 | SERPlux: реализовать веб-интерфейс (дашборд, запуск, история, статус) через `/interface` | P1 | [[03-Projects/SERPlux]], `/interface` |

## 🔵 Planned — следующие задачи

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-028 | Планирование новой архитектуры: 4 направления (Phone Remote, VibeAndroid, ProdWatch, Rudra AI) — **пауза, активен SERPlux** | P2 | [[99-Inbox]] |
| T-046 | R-005: Project Orchestrator — оркестрация из волта всеми проектами + Android-управление | P2 | [[99-Inbox]] (R-005) |
| T-015 | Telegram-бот для приёма фич и подходов | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-016 | Классификация фич по проектам (автомат) | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-017 | Команда `/project-upgrade` — авто-внедрение методов | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-029 | VibeAndroid — расширение архитектуры вайбкодинга для Android-разработки (методы, команды, интеграция) | P2 | [[99-Inbox]] (R-002), [[VibeOS]] |
| T-030 | Telegram Bot MVP — статусы проектов + базовые команды (расширение T-015) | P2 | [[rudra-phone]], T-015 |
| T-031 | ProdWatch Фаза 0 — health-check скрипты + Telegram алерты | P2 | [[prod-monitor]] |
| T-032 | Rudra AI Фаза 1 — TODO Planner на Android (первое Android-приложение) | P2 | [[rudra-ai]] |
| T-033 | Настроить Android-окружение (Android Studio, SDK, эмулятор, ADB) | P3 | [[rudra-ai]], [[rudra-phone]] |
| T-034 | API Gateway — центральный хаб для команд к проектам (авторизация, роутинг) | P3 | [[rudra-phone]], [[SERPlux]], [[dv-hub]] |
| T-035 | Создать Android-методы в 02-Methods/ (android-preview-pattern и др.) | P3 | [[00-INDEX#Methods]] |
| T-036 | ProdWatch Фаза 1 — веб-дашборд мониторинга (uptime-kuma или самописный) | P3 | [[prod-monitor]] |
| T-037 | Rudra AI Фаза 2 — интеграция с проектами, чтение статусов, напоминания | P3 | [[rudra-ai]] |
| T-038 | ProdWatch Фаза 2 — Prometheus + node_exporter + алерты с уровнями | P4 | [[prod-monitor]] |
| T-039 | Rudra AI Фаза 3 — Proactive Assistant + локальный LLM | P4 | [[rudra-ai]] |
| T-040 | Android-приложение rudra-phone (нативный UI, Jetpack Compose) | P4 | [[rudra-phone]] |
| T-041 | Rudra AI Фаза 4 — Full Assistant (multi-agent, голос, контекст) | P4 | [[rudra-ai]] |
| T-042 | ProdWatch Фаза 3 — полная observability (логи, метрики, интеграция с rudra-phone) | P4 | [[prod-monitor]] |

## 🟤 Backlog — идеи на потом

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| | _Пока пусто._ | | |

## ✅ Done — выполнено

| ID | Задача | Приоритет | Когда | Связано |
|----|--------|-----------|-------|---------|
| T-044 | SERPlux: создать ui-dev + infra-dev агентов, команды /interface /container /deploy, актуализировать карточку | P1 | 2026-07-02 | [[03-Projects/SERPlux]] |
| T-020 | Создать VibeOS — концептуальный дашборд системы вайбкодинга | P2 | 2026-06-30 | [[VibeOS]] |
| T-021 | Смена модели librarian Claude Sonnet 4.6 → DeepSeek v4-flash-free | P2 | 2026-06-30 | [[04-Memory/facts.md]] |
| T-022 | Ревью волта: исправить 17 багов (статусы, модели, команды, docs) | P1 | 2026-06-30 | [[Architecture]] |
| T-023 | Инициализировать OpenCode в dotfiles — sysop, /sysaudit | P3 | 2026-06-30 | [[03-Projects/dotfiles]] |
| T-024 | dotfiles v2 — мульти-агентная архитектура (7 агентов, 8 пайплайнов) | P2 | 2026-06-30 | [[03-Projects/dotfiles]] |
| T-025 | distill-pipeline + multi-agent-pipeline метод | P2 | 2026-06-30 | [[02-Methods/multi-agent-pipeline]] |
| T-026 | Создать README.md — визитка репозитория как VibeOS | P1 | 2026-06-30 | [[README]] |
| T-027 | Добавить лицензию GPL-3.0 + секция в README (copyleft, коммерция, фонд инженера) | P1 | 2026-06-30 | [[LICENSE]] |
| T-043 | SERP Factory — архитектура в волте: SERPlux как продукт, агенты ux-dev + infra-dev, команды /interface /container /deploy | P1 | 2026-06-30 | [[03-Projects/SERPlux]] |
| T-019 | Инициализировать OpenCode в dotfiles — sysop, /sysaudit | P3 | 2026-06-30 | [[03-Projects/dotfiles]] |
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
| T-018 | Сводка состояния проектов на дашборд | P3 | 2026-06-29 | [[00-INDEX.md]] |

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

Номера ID в Done — T-000 для задач первой волны (без сквозной нумерации), T-001+ для нумерованных задач.
T-044 — последняя закрытая задача. T-045 — следующая (активная) — реализация веб-интерфейса SERPlux.
