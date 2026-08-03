---
type: Active Context
title: Активный контекст
description: Локальные аудиты A/B/C/D + dv-hub addendum зафиксированы; ecosystem upgrade plan v1 (draft) создан; следующий major workstream — grounding плана перед любым project-level upgrade execution.
tags: [memory]
timestamp: 2026-08-03
---

# Активный контекст

> Автоматически обновляется librarian. Читается при старте каждой сессии.

## Текущий фокус
- **Проекты:** vault — локальные аудиты вайбкодинг-слоя финализированы
  (Phase A/B vibecoding-layer audit + Phase C SERPlux audit/addendum +
  Phase D dv-hub audit + dv-hub addendum). SERPlux — следующее после
  grounding плана (live proving ground, kernel contracts first). dv-hub —
  recovery-case, не первая цель kernel-апгрейда; recovery gate предшествует
  любому overlay. dotfiles/global contour — evolves in parallel.
- **Задача:** локальные аудиты A/B/C/D + dv-hub addendum зафиксированы.
  Ecosystem upgrade plan v1 создан (draft) с 5 kernel contracts, global
  architecture decisions, engineering-style-contract как planned artifact,
  implementation order (Phase 1–4 candidate/planned) и decision gates.
  **Следующий major workstream = grounding ecosystem plan перед любым
  project-level upgrade execution:** (a) стабилизация 5 kernel contracts
  как design contracts с acceptance criteria/rollback, (b) project-specific
  constraints enforcement (SERPlux first, dv-hub recovery gate no-go до
  recovery), (c) reconciliation declarations vs reality как permanent
  meta-mechanic. Реализация kernel contracts ещё не начата — только план.
- **Новое:** dv-hub recovery gate удерживается; не утверждать, что
  implementation плана началась. Engineering-style-contract — planned
  artifact внутри ecosystem plan v1, не метод в `02-Methods/` и не внедрён.

## Активная задача
(нет активной — ждём Rudra с новыми идеями)
T-045 (SERPlux мультипровайдерность) — отложено до новых вводных.
T-090..T-095 (planning group, экосистемный план) — Planned.

## Завершённые изменения (все сессии)
- [x] README.md — визитка репозитория как VibeOS (для GitHub, основа для лендинга)
- [x] LICENSE — GPL-3.0 (copyleft + коммерция разрешена) + секция в README + упоминание фонда инженера
- [x] SERP Factory — SERPlux как продукт фабрики. Архитектура: ux-dev, infra-dev, команды /interface /container /deploy. multi-agent-pipeline: Factory variant.
- [x] Имя пользователя: Макс/Max → Max Rudra / Rudra / mr — обновлено во всех файлах волта + LICENSE + facts.md
- [x] distill-pipeline + multi-agent-pipeline метод — дистилляция пайплайнов
- [x] dotfiles v3: полная мульти-агентная архитектура (8 агентов, 10 команд, память, UX)
- [x] VibeOS v0.2.0–v0.2.3 — дашборд, ревью 17 багов, dotfiles, distill-pipeline
- [x] opencode.json, config.md, facts.md, 00-INDEX, Architecture.md — обновлены
- [x] Модель librarian: Claude Sonnet 4.6 → DeepSeek v4-flash-free
- [x] OKF v0.1 — полная архитектура волта, 6 методов, 4 карточки проектов, память, трекер
- [x] SERPlux: агенты ui-dev + infra-dev, команды /interface /container /deploy, карточка актуализирована
- [x] Централизованное удаление claude-mem из экосистемы (плагин, AGENTS.md, memory-management.md, бэкап)
- [x] Инфраструктурный техдолг Уровня 0 (T-056): модель librarian qwen3.7-plus, verifier whitelist, факты, /done, session-flush
- [x] Убрана привязка `agent: librarian` из /done — команда работает во всех проектах
- [x] Создан `01-Reference/global-config.md` — документация глобальной инфраструктуры (~/.config/opencode/)
- [x] Фикс commit-guard (T-057): pytest-вывод захвачен через `.quiet()`, TUI чист
- [x] (T-058) SERPlux plan-агент: создан `.opencode/agents/plan.md` с `task.build: allow`. plan делегирует исполнение build через task-tool, сам не редактирует (edit/bash deny). Inline-определение убрано из opencode.json.
- [x] SERPlux T-001: новая схема БД (clients/positions/labels) + migrate.py + тесты
- [x] SERPlux T-002: режим `domains` разметки + справочник `domain_labels` + `confidence` (без LLM)
- [x] SERPlux T-003: идемпотентность migrate.py (любое состояние БД)
- [x] SERPlux T-004: расширение POST /run (client_id, label_mode=domains default, force_relabel) + валидация. 111/111 тестов.
- [x] T-059: verifier-pattern в dotfiles — `.opencode/subagent/verifier.md`, builder whitelist
- [x] T-060: closed-loop в dotfiles — `.opencode/command/loop.md` (build → verify → fix, HARD STOP 5)
- [x] T-061: flush-протокол (dotfiles + vault) — pre-compaction flush, /flush команда, planner scoped edit, librarian flush перед compact
- [x] T-062: tools/telegram-capture/ — рабочий MVP. capture.py + mark.py + config.py, 39 pytest-тестов, Tor SOCKS5 proxy (обход блокировки Telegram), первый capture (тема «Софт», 3 поста). 3 captures в 99-Inbox (C-001..C-003). Скилл capture + команда /capture. /inbox восстановлена. direnv + .venv внедрены в волт. Коммит 768b786 запушен.
- [x] Полный capture 584 постов (11 тем), классификация, 10 паттернов зафиксировано (коммит 13ec706)
- [x] Создан гайд-карточка стороннего софта GTweak — 01-Reference/tools/GTweak.md. Полный гайд с риск-классами операций и чек-листом для использования на чужой машине. Добавлен в 00-INDEX раздел "Сторонний софт".
- [x] T-069: tools/ecosystem-map/ — интерактивная Pip-Boy карта экосистемы. 468 постов → 36 навыков → 326 инструментов. 4 вкладки (НАВЫКИ/СПОСОБНОСТИ/ИНСТРУМЕНТЫ/ПРОЕКТЫ). CRT-эффекты, фильтры, привязка к проектам. Второй инструмент VibeOS.

## Отложено (P5 будущее)
- T-015: Telegram-бот — эволюция T-062 (команда /capture первый шаг)
- T-016: /project-upgrade — автоматический апгрейд проектов
- T-017: Команда /project-upgrade
- T-046: R-005 — Project Orchestrator (оркестрация из волта всеми проектами + Android)
- **Напряжения:** память (flush-протокол), теория vs практика

## Открытые вопросы
- (нет открытых вопросов на данный момент)

## Последнее обновление
2026-08-03 — локальные аудиты вайбкодинг-слоя финализированы (Phase A/B
vibecoding-layer audit + Phase C SERPlux audit/addendum + Phase D dv-hub
audit + dv-hub addendum в `06-Audits/`). Ecosystem upgrade plan v1 создан
(draft, `06-Audits/2026-08-03-ecosystem-upgrade-plan-v1.md`): roles of
nodes, 5 kernel contracts, global architecture decisions (target roles),
methodological principles, project-specific constraints (SERPlux first /
dv-hub recovery gate / dotfiles global contour), implementation order
(Phase 1–4 candidate/planned), engineering-style-contract как planned
artifact, decision gates. Engineering-style-contract развёрнут как
planned core artifact, не метод в `02-Methods/` и не внедрён. Следующий
major workstream = **grounding ecosystem plan** перед любым project-level
upgrade execution: стабилизация kernel contracts как design contracts с
acceptance criteria/rollback, project constraints enforcement,
declarations-vs-reality reconciliation как permanent meta-mechanic.
Реализация kernel contracts ещё не начата.
