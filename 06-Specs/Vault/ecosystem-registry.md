---
type: Execution Spec
title: Ecosystem Registry — canonical matrix/registry/kanban design
status: proposed
date: 2026-08-31
owner: librarian
source_plan: "[[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]"
tags: [spec, vault, registry, kanban, matrix, lifecycle]
---
# Ecosystem Registry — canonical design (2026-08-31)

> Canonical execution spec для структурного реестра экосистемы:
> Layers × Facets matrix, card schema, lifecycle, one-source/multiple-
> projections. Machine-readable canonical данные:
> `tools/ecosystem-map/registry.json`. Этот spec — источник правды по
> schema; registry.json — источник правды по данным; все остальные
> представления (Pip-Boy views, kanban, matrix, observer snapshot) —
> проекции.

## 1. Schema levels

| Уровень | Артефакт | Роль |
|---------|----------|------|
| **S0 design** | этот spec (`06-Specs/Vault/ecosystem-registry.md`) | schema + правила lifecycle/projections |
| **S1 canonical data** | `tools/ecosystem-map/registry.json` | единственный источник карточек/слоёв/фасетов/агентов |
| **S2 projections (committed)** | `tools/ecosystem-map/data.json` (skills-граф, исторический T-069) | отдельная предметная проекция навыков; не дублирует registry-карточки |
| **S3 projections (generated)** | `tools/ecosystem-map/generated/snapshot.json` | observer output; gitignored; не источник правды |

Правило: **one source, multiple projections.** Карточка экосистемы
определяется один раз (S1); любое представление (Kanban-колонка, ячейка
matrix, узел графа, строка дашборда) — проекция S1/S3, читаемая, не
копируемая. Запрещены вторые редактируемые копии карточек в других
файлах.

## 2. Layers и Facets

- **Layers:** `L0 Kernel` (инварианты/контракты), `L1 Control Plane`
  (маршрутизация/наблюдение/память экосистемы), `L2 Agent Workspace`
  (task contract/capsule/tool firewall/budget/verify), `L3 Project
  Build` (проектные агенты/команды/тесты), `L4 Interface`
  (человек-читаемые поверхности).
- **Facets:** `memory`, `routing`, `telemetry`, `verification`,
  `knowledge`, `interface`.
- Карточка занимает одну ячейку `layer × primary facet`; вторичные
  фасеты — массив `facets` (primary всегда первый).

## 3. Lifecycle stages

```
IDEA → RESEARCH → DESIGN → APPROVED → BUILD → REVIEW → VERIFY → LIVE → OBSERVE → IMPROVE → RETIRED
```

- Переходы только вперёд по цепочке либо в `RETIRED` (из любого stage);
  откат назад — явным decision-note в карточке (`status_note`).
- **VERIFY → LIVE** запрещён без runtime evidence + независимого
  verifier acceptance (см. plan v2 gates). Self-declared marker — не
  evidence (прецедент facts.md).
- `OBSERVE` — LIVE-компонент под наблюдением (telemetry/observer);
  `IMPROVE` — запланированное улучшение LIVE-компонента.
- `RETIRED` — окончательный; карточка сохраняется в registry для
  истории с `retired: true` и датой.

## 4. Card schema (registry.json, `cards`)

```json
"ECO-NNN": {
  "title": "...",
  "layer": "L0..L4",
  "facets": ["primary", "...secondary"],
  "lifecycle": "IDEA|RESEARCH|DESIGN|APPROVED|BUILD|REVIEW|VERIFY|LIVE|OBSERVE|IMPROVE|RETIRED",
  "owner": "librarian|meta|project-agent|user",
  "depends_on": ["ECO-NNN"],
  "oss_first": {"approved": true|false, "note": "..."},
  "review": "кто/как ревьюит (reviewer-роль или пользователь)",
  "acceptance": "что считается доказательством перехода lifecycle",
  "risk": "главный риск",
  "rollback": "как откатить без потери canonical-данных",
  "artifacts": ["пути к файлам-артефактам"],
  "tasks": ["T-NNN"],
  "status_note": "свободная заметка о текущем состоянии/блокерах",
  "retired": false
}
```

Обязательные поля для `APPROVED` и дальше: `acceptance`, `rollback`,
`owner`, `review`. Карточка без них не может покинуть `DESIGN`.

## 5. Дополнительные секции registry.json

- `meta`: `schema: "ecosystem-registry/1.0"`, `canonical: true`,
  `updated`, `source_of_truth` (этот spec), `projections` (список путей).
- `layers`, `facets`, `lifecycle` — определения (см. §2–3).
- `agents` — реестр агентов экосистемы: `{id, name, scope
  (global|vault|project), role, status: confirmed|candidate|frozen,
  note}`. Статусы только с evidence (confirmed = smoke/verifier или
  файловая реальность; candidate = planned; frozen = user-freeze).
- `workspace` — Agent Workspace manifest-контур (design-поля, см. plan
  v2 §5); помечен `lifecycle: DESIGN`.
- `blockers_policy` — откуда берутся blockers в проекциях: TASKS.md
  (⛔) + observer drift signals; registry не дублирует оперативные
  блокеры.

## 6. Observer contract (S3)

- `tools/ecosystem-map/observer.py` — read-only детерминированный CLI:
  входы (карточки `03-Projects/*.md`, `TASKS.md`, `04-Memory/route-log/
  *.md`, `registry.json`, git status/HEAD vault) → выход
  `generated/snapshot.json`.
- Гарантии: no mutation (кроме output), no network, no root, no
  commits; детерминизм (без wall-clock; `input_digest` = sha256 по
  отсортированным хешам входов); `--dry-run` — печать в stdout без
  записи.
- Drift signals (минимальный набор): repo-путь карточки не существует;
  artifact из registry не существует; TASKS-блокеры; dirty-файлы vault.
- Snapshot не источник правды: при расхождении canonical = S1/S2.

## 7. Kanban projection (правила)

- Kanban-колонки = lifecycle stages; карточки раскладываются по
  `lifecycle`; порядок внутри колонки — по `depends_on` (топологический,
  без циклов).
- Пустые стадии отображаются (серым) — видно «пробел» pipeline.
- TASKS.md связывается через поле `tasks` карточки; TASKS — оперативный
  трекер, registry — структурное состояние; двойного учёта нет (TASKS
  ссылается на ECO-NNN, не наоборот дублирует описание).

## 8. Валидация и pre-commit

- Текущая валидация — ручная (schema-проверка в observer: unknown
  layer/facet/lifecycle → warning в snapshot).
- Later (gate): JSON-schema валидация registry.json в pre-commit-check
  (кандидат; не реализовано в этой сессии).

## 9. Initial MVP cards (2026-08-31)

Восемь стартовых карточек (см. registry.json): ECO-001 OSS-first
skill/artifact gate; ECO-002 audit-log/token-budget telemetry; ECO-003
workspace manifest; ECO-004 tmux/link resolver; ECO-005 sqlite-vec/
repo-map (tree-sitter/ast-grep как independent tools); ECO-006 Pip-Boy
projection; ECO-007 read-only observer; ECO-008 read-only MCP
(implementation blocked, spec-only).

Статусы честные: ничего не LIVE; реализованное в этой сессии —
BUILD/REVIEW с явным «verifier acceptance pending» в status_note.
*(Обновление 2026-08-31, после независимого verifier PASS: ECO-006/007
переведены в VERIFY — MVP acceptance подтверждён; ECO-008 остаётся
DESIGN (implementation BLOCKED); ничего не LIVE.)*

## 10. Definition of Done (для этого spec)

- Spec описывает schema/lifecycle/projections без противоречий с plan
  v2 — выполнено (текущая сессия).
- registry.json валиден (JSON parse + schema-поля) — проверяется
  observer/ручно.
- Pip-Boy отображает все проекции из registry — проверяется вручную
  (browser smoke), verifier acceptance — PASS 2026-08-31.
- Изменения schema — только новой версией spec + bump
  `meta.schema` (minor) в registry.
