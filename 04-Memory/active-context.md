---
type: Active Context
title: Активный контекст
description: Phase 1 (kernel stabilization) ЗАВЕРШЕНА 2026-08-04. Текущая модельная настройка завершается 2026-08-17; следующий фокус — capability-routing rollout.
tags: [memory]
timestamp: 2026-08-17
---

# Активный контекст

> Автоматически обновляется librarian. Читается при старте каждой сессии.

## Текущий фокус
- **Runbook layer (2026-08-17):** создан `07-Runbooks/` как отдельный operational
  use layer; handbook фиксирует текущее применение, changelog — подтверждённые
  shifts. Следить за freshness только по реальным изменениям практики.
- **Модельная настройка (2026-08-17):** текущая конфигурация Luna/DeepSeek Go
  завершается; после перезапуска OpenCode считать её активной.
- **Следующий фокус:** capability-routing rollout для замены временной статической
  политики.
- **ChaT:** bootstrap завершён 2026-08-14. Интервью Макса остаётся следующим
  проектным шагом после capability-routing rollout.
- **Phase 1 (kernel stabilization) ЗАВЕРШЕНА 2026-08-04.** Все задачи
  T-084..T-089 + T-096..T-098 перенесены в Done с датой. Коммиты:
  vault (память), SERPlux (агентский слой), dotfiles (`done.md`).
- **Модель general (vault `opencode.json`):** `opencode-go/gpt-5.6-luna`.
  Историческая запись о временном переводе субагентов на бесплатные Zen
  сохранена в `facts.md`.
- **Следующий gate:** Phase 2 (SERPlux first adoption по ecosystem upgrade
  plan v1) + dotfiles/global hardening (Phase 3). dv-hub — recovery case,
  не первая цель.
- **Residuals `[проверить]` (честно открыты, не закрыты):**
  - T-089/T-097: commit-guard на реальном `git commit` (real commit smoke)
    и реальный compaction event session-dispatch — безопасно
    непротестированы (нужна живая сессия в serp, не vault).
  - T-085: merge behavior permissions allowlist (local override global) —
    наблюдение, strict isolation не объявлена.
  - T-089: payload capture для subagent/task в `tool.execute.after`
    (полный `verifier PASS` marker gate) — не подтверждён.
  - T-084: реальный compaction session-dispatch.
- **Открытый техдолг (по решению пользователя, реализуется ИМ при
  проектной работе):** sync test-metrics claims в SERPlux
  (`serp/docs/techdebt.md`, запись 2026-08-04 «Test-metrics claims не
  синхронизированы с каноном»): README/AGENTS/CANON/verification/
  user-guide/TASKS содержат 224/172/95/111, канон = 256/256 executed на
  HEAD `f7ccd3e`, definitions 212. Записано идемпотентно и централизованно.
- **Working tree:** изменения документации и модельной конфигурации Vault
  незакоммичены. Отдельно сохраняются pre-existing bootstrap/WIP-изменения в
  ChaT, dotfiles и SERPlux; они не откатываются и не объявляются частью этой
  сессии.

## Активная задача
- **Завершение текущей настройки моделей:** политика подтверждена через
  `opencode models` и merged config debug; требуется перезапуск OpenCode.
- Следующее: capability-routing rollout, затем Phase 2/3 планирование
  (SERPlux adoption + global layer hardening) — по
  ecosystem upgrade plan v1 (`06-Audits/2026-08-03-ecosystem-upgrade-plan-v1.md`),
  либо закрытие residuals Phase 1 через живую сессию в serp.

## Завершённые изменения (все сессии)
- [x] **Phase 1 kernel stabilization (2026-08-04, T-084..T-089, T-096..T-098):**
  plugin loader/compaction contract (named exports, `event` catch-all,
  `experimental.session.compacting`), SERPlux plugin stabilization
  (commit-guard ESM fix, env-guard webfetch gap), project-local
  `.opencode/agents/verifier.md` (acceptance-only, VERDICT PASS/FAIL),
  global `/done` memory-model branches (vault-based / docs-based / fallback),
  test-metrics канон `serp/docs/test-metrics.md` (executed 256/256 на
  HEAD f7ccd3e, definitions 212), техдолг-запись sync claims, execution
  sequence note (Phase 1→4). Коммиты во все 3 репо.
- [x] (T-098) WIP SERPlux смёржен в HEAD f7ccd3e; executed run = 256/256
  pass, exit 0; `docs/test-metrics.md` обновлён до канона; sync claims →
  техдолг (за пользователем).
- [x] (T-097) Live Bun import/registration всех 4 SERPlux плагинов +
  function-level hook fire подтверждены; residuals (real commit smoke,
  real compaction dispatch) открыты `[проверить]`.
- [x] (T-096) Execution sequence note: SERPlux first → dotfiles/global
  hardening → dv-hub recovery; global layer на полшага впереди.
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
- Когда возвращать Go-модели субагентам (T-048/T-049)?
- Как закрывать residuals Phase 1 (real commit smoke / compaction dispatch) — нужна живая сессия в serp?

## Последнее обновление
2026-08-17 — **Временная модельная политика подтверждена**:
primary/сложные роли используют `opencode-go/gpt-5.6-luna`, дешёвые
read-only/research/reviewer/verifier — `opencode-go/deepseek-v4-flash`.
Доступность подтверждена `opencode models`, merged config debug проходит;
для применения нужен перезапуск OpenCode. Изменения незакоммичены; pre-existing
bootstrap/WIP в ChaT, dotfiles и SERPlux сохранены. Следующий фокус —
capability-routing rollout.

2026-08-17 — **Создан runbook operational layer**: `07-Runbooks/` отделён от
Methods, Audits и `AGENTS.md`; следующий фокус сохраняется за capability-routing
rollout, затем Phase 2/3 adoption и hardening. Residuals не изменены.

2026-08-14 — **Bootstrap ChaT завершён; модель general обновлена**:
синхронизированы проектная карточка
и память волта. `general` использует `opencode-go/gpt-5.6-luna`.
Следующий шаг — интервью Макса. Phase 1 ранее завершена
2026-08-04: T-084..T-089, T-096..T-098 Done.
Исторический перевод meta/verifier на бесплатные Zen-модели отмечен в facts.md.
SERPlux: executed 256/256 на HEAD f7ccd3e, канон test-metrics обновлён,
техдолг sync claims записан (за пользователем). Коммиты: vault (память),
SERPlux (агентский слой), dotfiles (done.md). Residuals `[проверить]`
открыты в facts.md. Следующий gate: Phase 2 (SERPlux adoption) / Phase 3
(dotfiles hardening) / residuals через живую сессию.
