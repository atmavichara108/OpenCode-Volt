---
type: Upgrade Plan
title: Ecosystem upgrade plan v2 — Layers × Facets, OSS-first, workspace и observer
date: 2026-08-31
status: draft
sources:
  - "[[99-Inbox/vault-upgrade-research-2026-08-02]] (включая Addendum 2026-08-31)"
  - "[[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]]"
  - "[[06-Audits/2026-08-03-execution-sequence-note]]"
  - "[[06-Audits/2026-08-22-androidos-open-source-first]]"
  - "[[06-Specs/Vault/ecosystem-registry]]"
tags: [upgrade-plan, draft, ecosystem, layers-facets, oss-first, workspace, observer, pip-boy]
---
# Ecosystem upgrade plan v2 (2026-08-31)

> **Рабочий план v2 — addendum/эволюция плана v1, не его отмена.** v1
> (kernel contracts, Phase 1–4 sequence) остаётся историческим
> canonical-артефактом; v2 добавляет структурную рамку Layers × Facets,
> OSS-first gate, Agent Workspace, observer, read-only MCP-политику и
> Pip-Boy как planning UI. Всё ниже — candidate/planned, если не указано
> «подтверждено» с источником. Без ложных статусов «done»; runtime-claims
> только с evidence.

---

## 1. Отношение к v1 и что меняется

- **Наследуется из v1 без изменений:** 5 kernel contracts (plugin loader,
  reviewer/verifier split, runtime enforcement, memory model, test
  metrics), execution sequence Phase 1→4 (SERPlux first, dotfiles
  hardening, dv-hub recovery-last), decision gates, engineering-style
  contract как planned artifact.
- **Добавляется в v2:**
  1. **Layers × Facets matrix** — единая структурная рамка экосистемы
     (вместо плоского списка задач/агентов); canonical registry + проекции.
  2. **OSS-first gate** — любой новый инструмент/сервис экосистемы
     проходит OSS-first фильтр до внедрения.
  3. **Telemetry/context compiler** (P0 из research: audit-log /
     token-budget → context capsule) — измеримость как обязательный
     первый шаг.
  4. **Agent Workspace** — task contract + context capsule + tool
     firewall + budget + verification gate как scoped рабочее место
     агента (harness-идея research, уменьшенная до workspace-границы).
  5. **Read-only observer** — детерминированный snapshot состояния
     экосистемы (без real-time claims).
  6. **Read-only MCP policy** — MCP только read-only и только после
     context-overhead оценки; prefer custom tools.
  7. **Pip-Boy как planning UI MVP** — multi-view визуализация
     (Matrix/Kanban/Projects/Agents/Blockers/Workspace) поверх canonical
     registry + generated snapshot.
- **Уточнение UI/UX-поверхности:** по research Addendum 2026-08-31 —
  TUI-виджеты не документированы `[проверить]`; server SSE `/event`,
  `/tui/*` endpoints, references, custom tools — подтверждённые точки
  интеграции.

---

## 2. Layers × Facets matrix

> Canonical schema и card-контракт — в [[06-Specs/Vault/ecosystem-registry]];
> machine-readable registry — `tools/ecosystem-map/registry.json`.
> Здесь — только состав слоёв/фасетов и принцип.

### Layers (вертикальные слои экосистемы)

| Layer | Имя | Что держит | Примеры |
|-------|-----|-----------|---------|
| **L0** | Kernel | Инварианты и контракты, общие для всех | kernel contracts v1, OSS-first gate, engineering-style contract (planned) |
| **L1** | Control Plane | Маршрутизация, наблюдение, память экосистемы | librarian, capability-routing, registry, observer, telemetry |
| **L2** | Agent Workspace | Рабочее место агента: task contract, capsule, tool firewall, budget, verify gate | workspace manifest (design), context compiler (design) |
| **L3** | Project Build | Проектные агенты/команды/тесты | SERPlux build/plan/reviewer, dv-hub, dotfiles roles |
| **L4** | Interface | Человек-читаемые поверхности | Pip-Boy, TUI, web, runbooks, дашборды |

### Facets (горизонтальные фасеты сквозь слои)

`memory` · `routing` · `telemetry` · `verification` · `knowledge` · `interface`

### Правила matrix

- **One source, multiple projections:** canonical registry — единственный
  источник карточек; Pip-Boy/Kanban/Matrix/observer — проекции, не копии.
- Карточка живёт в **одной ячейке** layer × primary facet (может
  затрагивать несколько facets вторично).
- Каждая карточка имеет lifecycle, owner, dependencies, acceptance,
  risk, rollback (schema — в spec).
- Matrix не заменяет TASKS.md: TASKS — оперативный трекер сессий,
  registry — структурное состояние экосистемы; связка через ID карточек
  (ECO-NNN) в TASKS-строках.

---

## 3. OSS-first gate (L0, policy)

- **Источник:** [[06-Audits/2026-08-22-androidos-open-source-first]] (принят
  для AndroidOS) — v2 поднимает до экосистемного gate.
- **Правило:** любой новый инструмент/сервис/зависимость экосистемы
  проходит фильтр ДО внедрения: (1) open-source с публичным репо и
  лицензией; (2) self-hostable без обязательного cloud; (3) не нарушает
  anti-goals (файловая git-версионная память, не замена OpenCode, не код
  приложений из librarian-контура); (4) интеграция через
  OpenCode-native путь (custom tool / plugin / skill / MCP / reference),
  не патч OpenCode.
- **Rollback:** любой внедрённый через gate компонент удаляется без
  потери canonical-данных (данные — в git-файлах волта).
- **Статус:** policy approved в этом плане; enforcement — ревью карточек
  registry (каждая карточка имеет поле `oss_first`).

---

## 4. Telemetry / context compiler (L1→L2)

- **P0 (из research, без изменений приоритета):** custom tools
  `token-budget` + `audit-log` → честная telemetry по агент/модель/
  проект; без неё все «экономии» — unverifiable claims.
- **Затем:** context capsule (content-addressed, детерминированный,
  source hashes, stale-invalidation) + repo/knowledge map compiler
  (tree-sitter/ast-grep как **independent tools** — см. exclusions).
- **Workspace-граница:** capsule компилируется для task contract'а
  workspace'а, не «глобально для волта» — это уменьшенная реализация
  harness-идеи из research (полный Vault Harness Kernel остаётся
  long-term направлением, не MVP).
- **Acceptance:** replay-set A/B (из research §8) — без измерения
  эффект не заявляется.

---

## 5. Agent Workspace (L2, design)

> Design-контур, не реализация. Workspace = scoped рабочее место агента
> для одной задачи.

- **Workspace manifest (поля):** `task_id`, `goal/DoD`, `scope
  (allowed_paths)`, `base_ref`, `context_capsule` (ref), `model_policy`,
  `token/time budget`, `allowed_tools` (capability groups), `verification
  (test command + diff scope)`, `max_repair_cycles`, `artifacts_dir`.
- **Границы:** workspace не заменяет агентов; он задаёт контракт, внутри
  которого работает существующий агент (OpenCode agent loop не
  патчится). Verifier gate `verify=PASS → finalize` — через
  plugin/custom tool контур (runtime enforcement contract v1 #3).
- **OpenCode-native точки (подтверждено docs 2026-08-31):** custom tools
  (context {directory, worktree}), references (внешние директории без
  копирования), permissions per-agent, plugins `tool.execute.before`.
- **`[проверить]`:** interceptor перед LLM-call для capsule injection;
  lazy tool definitions per-agent.
- **MVP-шаг:** workspace manifest schema + одна пилотная задача через
  manifest (после telemetry P0).

---

## 6. Read-only observer (L1, MVP в этой сессии)

- **Что:** детерминированный read-only snapshot CLI (`tools/ecosystem-map/
  observer.py`): читает карточки проектов, TASKS, route-log, registry,
  git status (только vault) → machine-readable `generated/snapshot.json`
  (gitignored, explicit generated location).
- **Гарантии:** no mutation (кроме своего output), no network, no root,
  no commits; детерминизм — тот же вход → тот же output (без wall-clock).
- **Не real-time:** observer — snapshot-генератор; live event ingestion
  (SSE `/event`, `file.watcher.updated`) — later, отдельный gate.
- **Статус:** implementation в этой сессии; runtime smoke `[проверить]`
  (запуск вручную подтверждён — см. session-log; независимый verifier
  acceptance — PASS 2026-08-31, см. session-log).

---

## 7. Read-only MCP policy (L1, blocked implementation)

- **Policy:** MCP-серверы экосистемы — только read-only, только local,
  только с минимальным числом tools (context caveat подтверждён docs
  2026-08-31). Любой MCP — через OSS-first gate.
- **Реализация:** **BLOCKED** — полный контракт в
  [[06-Specs/Vault/mcp-readonly]] (tools: `ecosystem_state`,
  `ecosystem_card`, `ecosystem_kanban`; stdio local; без secrets).
  Причины block: (a) MCP context overhead vs 3 tools; (b) новая
  dependency (MCP SDK) без нужды; (c) прецедент user-freeze MCP facade
  (T-110). **Preferred path:** custom tool `ecosystem-snapshot`
  (`.opencode/tools/ecosystem-snapshot.ts`) — read-only local endpoint
  без новых зависимостей; runtime loading `[проверить]`.
- **Unblock-условия:** подтверждённая потребность внешнего MCP-клиента
  (не OpenCode-агента) в ecosystem state; отдельный approval.

---

## 8. Pip-Boy как planning UI MVP (L4)

- **MVP (реализуется в этой сессии):** multi-view поверх
  `registry.json` + `data.json` + `generated/snapshot.json` (если
  сгенерирован): **SKILLS** (существующий граф), **MATRIX** (Layers ×
  Facets), **KANBAN** (lifecycle-колонки), **PROJECTS**, **AGENTS**,
  **BLOCKERS/DRIFT**, **WORKSPACE**. Vanilla HTML/JS, без новых
  зависимостей; static/generated данные.
- **Явные метки:** «static registry» / «generated snapshot» / «live:
  нет» — real-time не заявляется до observer event ingestion.
- **Later:** SSE `/event` ingestion, OSC8 links `[проверить]`, tmux
  integration `[проверить]`.
- **Статус:** implementation в этой сессии; загрузка/отображение
  проверяются вручную; verifier acceptance — PASS 2026-08-31.

---

## 9. Project adoption sequence (наследует v1 + v2-дополнения)

1. **Phase 1 (kernel stabilization)** — завершена 2026-08-04 (см.
   active-context); residuals `[проверить]` открыты.
2. **Phase 2 (SERPlux first adoption)** — unchanged (v1); v2 добавляет:
   telemetry custom tools могут пилотироваться в SERPlux-контуре через
   проектных агентов (не librarian-правки кода).
3. **Phase 3 (dotfiles/global hardening)** — unchanged; v2 добавляет:
   observer/registry/Pip-Boy живут в vault (control plane), глобальные
   роли — по v1 extraction sequence.
4. **Phase 4 (dv-hub recovery)** — unchanged (recovery gate first).
5. **v2-cross (параллельно, vault-scope only):** registry → observer →
   Pip-Boy MVP → telemetry P0 → workspace manifest pilot → (blocked)
   MCP. Каждый шаг — evidentiary gate; никакой шаг не трогает код
   приложений SERPlux/dv-hub/AndroidOS.

---

## 10. Exclusions и policy по внешним системам

- **Aider — ПОЛНОСТЬЮ RETIRED из active/watch roadmap.** Не кандидат,
  не watch, не «паттерн для внедрения». Исторические упоминания
  сохраняются только в research-артефакте 2026-08-02 (append-only) и
  этом плане с явным статусом **retired 2026-08-31**. Причина: anti-goal
  «не замена OpenCode» + docs.aider.chat instability (404 в research).
- **tree-sitter / ast-grep — independent tools** (не «Aider repo-map
  паттерн»): используются напрямую как OSS-инструменты для repo/knowledge
  map compiler (L2), без привязки к Aider.
- **Goose / OpenHands / SWE-agent — architectural references only**
  (не устанавливаются, не watch-кандидаты; заимствуются паттерны:
  ACI/trajectory — SWE-agent; event-stream/sandbox — OpenHands).
- **Letta — watch (не внедрять):** только memory-only self-hosted, если
  появится Letta-memory-as-MCP; V1-server legacy (research 2026-08-02).
- **GPTCache — watch (не внедрять):** semantic cache опасен в
  agentic-контексте; только для idempotent LLM-tasks (research).
- **Graphiti — watch с триггерами:** facts > 1000 / мульти-instance
  проекты / конфликтующая хронология (research); требует Neo4j/FalkorDB.
- **Langfuse — P1 опция после LiteLLM** (research B2); self-host only;
  не первый шаг.
- **Mem0 — не первый шаг** (research librarian-синтез): только как layer
  поверх event-sourced facts, self-hosted only, после telemetry+compiler.
- **LiteLLM — P1** (research B1): gateway/spend tracking; отдельный
  approval (массовая правка opencode.json через meta-контур).

---

## 11. Decision gates v2 (дополнение к v1 gates)

- **No LIVE status without runtime evidence.** Карточка registry не
  переходит в LIVE без подтверждённого smoke + verifier acceptance
  (прецедент: capability-routing scoped smokes).
- **No real-time claims without event ingestion.** Pip-Boy/observer —
  static/generated до SSE/watcher ingestion реализован и подтверждён.
- **No MCP without context-overhead assessment.** Число tools и
  token-cost MCP-поверхности оценивается до включения (docs caveat).
- **Every card has acceptance + rollback.** Schema-требование registry
  (см. spec); карточка без acceptance/rollback — не APPROVED.
- **OSS-first gate обязателен** для всех новых внешних компонентов.

---

## 12. MVP vs later (сводка)

| Компонент | MVP (эта сессия) | Later (gate) |
|-----------|------------------|--------------|
| Registry + schema | canonical `registry.json` + spec | автоматическая валидация schema в pre-commit |
| Observer | детерминированный snapshot CLI | live SSE ingestion, cross-repo runtime |
| Pip-Boy | multi-view static/generated | live-режим, OSC8 `[проверить]`, tmux `[проверить]` |
| Telemetry | — (design, P0 из research) | custom tools + replay baseline |
| Workspace | manifest schema (design) | пилотная задача через manifest |
| MCP | spec/contract, implementation BLOCKED | unblock по потребности + approval |
| Custom tool | `ecosystem-snapshot.ts` (файл создан) | runtime loading smoke `[проверить]` |
