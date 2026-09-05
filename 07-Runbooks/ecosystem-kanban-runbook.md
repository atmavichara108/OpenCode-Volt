---
type: Runbook
title: Ecosystem Kanban Runbook — control plane для апгрейдов экосистемы
description: Как пользователю читать и вести Layers × Facets / Kanban control plane (canonical registry, Pip-Boy, TASKS, observer).
tags: [runbooks, operations, ecosystem, kanban, registry, pip-boy]
---
# Ecosystem Kanban Runbook

## Purpose

Как оператору (Max Rudra) пользоваться Kanban control plane экосистемы:
видеть всю картину апгрейдов, выбирать следующий шаг, управлять переходами
lifecycle через librarian/approval. Это runbook пользования, не дизайна:
архитектура, schema и gates — в [[06-Specs/Vault/ecosystem-registry]] и
[[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]; здесь на них только
ссылки.

## Карта источников правды (кто чем управляет)

| Слой | Файл | Роль | Кто мутирует |
|------|------|------|--------------|
| Canonical registry | `tools/ecosystem-map/registry.json` | единственный источник карточек ECO-NNN, слоёв/фасетов/агентов | только librarian-контур по approval |
| Operational queue | [[TASKS]] | оперативные задачи T-NNN по сессиям | librarian по ходу сессии |
| Pip-Boy | `tools/ecosystem-map/index.html` | read-only проекция (все views) | не мутируется как данные |
| Observer snapshot | `tools/ecosystem-map/generated/snapshot.json` | generated снимок (gitignored) | только `observer.py` |

Правило: **one source, multiple projections.** Pip-Boy и observer никогда
не редактируются как «данные»: правка карточки = правка registry.json,
правка задачи = правка TASKS.md. Дублирование карточек в других файлах
запрещено.

## Как читать Layers × Facets (view MATRIX)

- Слои (вертикаль): **L0 Kernel** (инварианты/контракты) → **L1 Control
  Plane** (маршрутизация/наблюдение/память) → **L2 Agent Workspace**
  (task contract/capsule/budget/verify) → **L3 Project Build** (проектные
  агенты/тесты) → **L4 Interface** (человек-читаемые поверхности).
- Фасеты (горизонталь, сквозные): memory · routing · telemetry ·
  verification · knowledge · interface.
- Ячейка = layer × primary facet; у карточки могут быть вторичные фасеты.
- Вопросы, на которые отвечает матрица: где пусто (пробел покрытия), где
  скопление (затор слоя), где VERIFY без движения (нужен runtime smoke).

## Как пользоваться Kanban (view KANBAN)

- **Master Kanban** — все карточки по lifecycle
  IDEA→RESEARCH→DESIGN→APPROVED→BUILD→REVIEW→VERIFY→LIVE→OBSERVE→IMPROVE→RETIRED.
- **Facet/project Kanban** — тот же board с включённым фильтром FACET
  (primary или secondary) или PROJECT: доска показывает только этот срез.
- Фильтры **LAYER / OWNER / PRIORITY / STAGE** и **SEARCH** (по
  id/title/owner/status_note) работают во всех registry-views; STAGE в
  Kanban прячет колонки — фокус на нужных стадиях.
- Пустые колонки (сейчас REVIEW/LIVE/OBSERVE/IMPROVE) — честный статус
  «пробел pipeline», не ошибка. RETIRED — история (Aider), не бэклог.
- Клик по карточке → detail-панель: dependencies, blocks, acceptance,
  evidence (artifacts + tasks), rollback, status note.

## Как выбрать следующую карточку

1. Сверь [[04-Memory/active-context]] — текущий фокус и известные блокеры.
2. Открой KANBAN: сначала колонки BUILD/VERIFY (незакрытое), затем
   DESIGN/APPROVED (готовое к запуску).
3. Включи фильтр PRIORITY P0/P1 — приоритет наследуется из plan v2/TASKS.
4. Проверь view DEPS: карточка с незакрытыми `depends_on` не стартует
   (или стартует как явное решение с note, почему зависимость обойдена).
5. Проверь view BLOCKERS: ⛔ TASKS + drift signals + карточки с
   implementation BLOCKED в status_note.
6. Прими решение и озвучь его librarian'у (свободный запрос или
   slash-команда). Librarian маршрутизирует исполнение; изменения
   canonical registry — только после твоего approval.

## Переходы lifecycle (кто двигает карточки)

- Переход инициирует **librarian** (исполнение через субагентов) по
  подтверждению пользователя; самоперевод статусов агентом запрещён.
- **VERIFY→LIVE** — только с runtime evidence + независимым verifier
  acceptance (plan v2 gates). Сейчас LIVE/OBSERVE пустые — это честно.
- Откат назад — явным decision-note в `status_note` карточки (пример:
  ECO-006 VERIFY→BUILD 2026-08-31 при расширении scope).
- **RETIRED** — окончательно, карточка остаётся в registry для истории
  (пример: Aider, ECO-026).

## Как интерпретировать blockers / dependencies / acceptance

- **BLOCKERS** (view BLOCKERS) = TASKS ⛔/frozen + observer drift signals
  (`repo_missing`, `artifact_missing`, `task_ref_missing`,
  `registry_schema`, `task_blocked`) + implementation BLOCKED в
  status_note карточек. Registry оперативные блокеры не дублирует.
- **DEPENDENCIES** (view DEPS) = `depends_on` — структурные предусловия;
  «blocks» — обратные зависимости (кто ждёт эту карточку). Зависимость в
  DESIGN не блокирует research, но блокирует BUILD.
- **ACCEPTANCE** (view ACCEPT) = доказательство перехода lifecycle;
  evidence = artifacts + tasks + verifier-записи. Self-declared маркеры
  («PASS» от самого агента) — не evidence.

## Как обновлять canonical registry / TASKS

- Новая карточка или переход: попроси librarian'а → proposal (diff
  registry.json) → твоё approval → правка → `python3
  tools/ecosystem-map/observer.py` → Pip-Boy отражает.
- Новая задача: строка T-NNN в TASKS.md; связка с карточкой — через поле
  `tasks` карточки (и Related в TASKS). TASKS — оперативный трекер,
  registry — структурное состояние; описания не дублируются.
- Не создавать вторых редактируемых копий карточек; проекции (Pip-Boy,
  snapshot) руками не править.
- После любой правки registry перегенерируй snapshot observer'ом —
  детерминированный, безопасно перезапускать.

## Static vs generated vs future live

- **STATIC** (committed, git): `registry.json`, `data.json` (skills-граф
  T-069), `index.html`.
- **GENERATED** (gitignored): `generated/snapshot.json` — обновляется
  запуском observer; отражает TASKS/проекты/git на момент снимка.
- **LIVE**: не заявляется. SSE `/event` ingestion — отдельный later gate
  (T-128 / ECO-018); до его реализации и подтверждения словами
  «real-time» никто не пользуется.

## Rollback и запрет silent mutation

- Rollback каждой карточки — в её поле `rollback` (view ACCEPT /
  detail-панель); общий rollback — git: registry/index — committed файлы,
  snapshot — простая перегенерация.
- Pip-Boy — **read-only projection**: никаких edit-кнопок; единственный
  localStorage — прогресс skills-графа T-069 (пользовательские отметки,
  не canonical-данные).
- **No silent mutation**: любое изменение канона — через librarian-контур
  с approval; локальные permission-overrides не ослабляют этот контракт.

## Типовой цикл (5 минут)

1. `python3 tools/ecosystem-map/observer.py` — свежий snapshot.
2. `python3 -m http.server` в `tools/ecosystem-map/` → открой
   `index.html` в браузере.
3. KANBAN → выбери карточку → DEPS/ACCEPTANCE → решение → librarian.

## Ссылки

- Schema/контракт: [[06-Specs/Vault/ecosystem-registry]] (canonical),
  [[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]] (план v2).
- Операционная модель: [[07-Runbooks/vibecoding-operator-handbook]];
  история практики: [[07-Runbooks/vibecoding-changelog]].
- MCP-политика: [[06-Specs/Vault/mcp-readonly]] (implementation BLOCKED).
