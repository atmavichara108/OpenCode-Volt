---
type: Execution Spec
title: Risk-based orchestration — lightweight vs strict execution modes
status: proposed
scope: vault
date: 2026-08-30
---
# Risk-Based Orchestration: Lightweight vs Strict Execution Modes

## Goal

Сохранить human-in-the-loop, но перестать прогонять простые docs/config задачи
через тяжёлую цепочку `meta -> reviewer -> verifier -> evidence -> повторный
verifier`. Ввести два режима маршрутизации по risk/mutability/reversibility,
снизить orchestration overhead без ослабления safety-гейтов.

Это design spec для отдельной будущей сессии/апгрейда. Runtime-реализация на
сегодня НЕ существует; spec не делает заявлений о runtime enforcement (см.
Unresolved Questions).

## Problem Statement

- Простые docs-only задачи (spec authoring, правка карточек, inbox-обработка)
  проходят ту же цепочку, что project/system/runtime-изменения: избыточные
  dispatch, повторное чтение одних и тех же файлов разными агентами,
  дублирующий verifier после каждого шага.
- Следствие: рост tool calls и tokens, латентность, потеря фокуса контекста —
  при неизменном risk-профиле задачи.

### Non-goals

- НЕ отключать approval для edits/task (глобальные `task: ask`, `edit: ask`
  остаются).
- НЕ создавать silent automatic router: route/capability неясны → `UNROUTABLE`
  или уточняющий вопрос, не silent fallback на `general`.
- НЕ ослаблять high-risk gates: project/system/runtime/commit-задачи всегда
  strict-режим с reviewer и verifier.
- НЕ внедрять runtime enforcement в этом spec — только контракт и критерии.

## Scope

- Target: агентная инфраструктура экосистемы (`**/.opencode/**`,
  `~/.config/opencode/**`, vault docs).
- Scope: `vault` (docs-only для самого spec; апгрейд по staged rollout ниже).
- Mutability: docs-only.
- Код приложений (`*.py`, `*.gs`, prod-конфиги) — вне scope всегда.

## Route schema

Расширение существующего route decision schema (см.
[[02-Methods/capability-routing]]). Новые поля:

```yaml
task: <exact task>
scope: vault
capability: <capability>
role: meta
agent: meta
risk: low|high
mutability: docs-only|read-only|project|system|runtime
review: none|reviewer
acceptance: named-acceptance-gate|verifier
fallback: UNROUTABLE
# --- additions ---
execution_mode: lightweight|strict
confirmation_state: pending|confirmed:<scope-hash>
context_bundle: <paths+summary, передаваемый в handoff>
max_agents: <int>
max_attempts: <int>
stop_conditions: [no-progress, repeated-intent, empty-handoff, timeout, scope-drift]
```

`confirmation_state` фиксирует, какой именно scope подтверждён пользователем;
расширение scope инвалидирует состояние → новый proposal.

## Modes

### Lightweight

Критерии (все должны выполняться):
- risk: low; mutability: read-only или docs-only (vault/agent-инфраструктура);
- reversibility: тривиальная (git revert одного docs-коммита);
- acceptance surface: сам пользователь читает результат; нет runtime-эффекта.

Правила:
- Минимальное число агентов: 1 (сам meta или один subagent); reviewer/verifier
  НЕ нужны.
- Запрещено повторное чтение уже переданного контекста: агент получает
  `context_bundle` и не перечитывает файлы из него без причины (изменение
  файла = причина, фиксируется в handoff).
- Короткий output contract: exact path, line count, checks, residuals — без
  длинных пересказов.
- Budget: max_agents ≤ 2, max_attempts ≤ 2 на шаг; сверх budget → stop.

### Strict

Критерии (любое из):
- mutability: project / system / runtime / commit;
- risk: high; reversibility: нетривиальная или неизвестная;
- acceptance surface: runtime-поведение, prod-конфиги, внешние системы.

Правила:
- Полная цепочка: reviewer ПЕРЕД verifier; evidence обязателен; acceptance —
  именованный verifier gate, не self-marker.
- Повторный verifier после правок — только если правки меняют acceptance
  surface, не после каждого шага.

### Выбор режима

Неоднозначность критериев (например, docs-only но high-risk policy-изменение)
→ strict. Понижение режима в середине задачи запрещено; повышение —
разрешено с новым route decision.

## Confirmation Gate

Обязательное подтверждение пользователя до dispatch/edit сохраняется ВО ВСЕХ
режимах, включая lightweight и read-only discussion. Правила глобального
контракта ([[AGENTS.md]] human-in-the-loop) не ослабляются режимом:
- lightweight сокращает цепочку агентов, НЕ гейт подтверждения;
- runtime-гейты `task: ask` / `edit: ask` остаются ожидаемым поведением;
- подтверждение привязано к scope (`confirmation_state`); расширение scope =
  остановка + новый proposal.

## Context Handoff

- В каждый dispatch передаётся `context_bundle`: summary задачи, key evidence,
  changed paths, route decision. Агент НЕ перечитывает весь набор файлов.
- Canonical source of truth: execution spec в `06-Specs/<project>/` (для
  SERPlux — локальный `docs/specs/`); route contract —
  [[02-Methods/capability-routing]]; глобальный контракт — `AGENTS.md`.
- Invalidation: изменение scope, изменение файла из bundle, смена режима →
  bundle пересобирается; старый bundle не переиспользуется молча.

## Stop Conditions

- `max_attempts` исчерпаны → stop, отчёт, без автоматического retry.
- No-progress / repeated-intent: агент повторяет тот же intent/запрос без
  новой информации → stop.
- Empty handoff: получен пустой/невалидный `context_bundle` → НЕ делать
  немедленный blind retry; вернуть отправителю `HANDOFF-INVALID` с причиной,
  повторная попытка — только после исправления bundle (в пределах
  max_attempts).
- Timeout/abort: превышение budget сессии или user abort → stop, состояние
  фиксируется в отчёте.
- Scope drift, unauthorized mutation, недоступность canonical spec → `BLOCKED`
  (для обычных проектов; SERPlux — по локальному контракту).

## Acceptance Criteria

Измеримые метрики (baseline → target), фиксируются в route-log:

| Метрика | Baseline (тяжёлая цепочка) | Target (lightweight) |
|---|---|---|
| task dispatch на docs-задачу | 3–5 | ≤ 2 |
| tool calls (повторные чтения тех же файлов) | 2–3× чтение | ≤ 1× на файл |
| tokens/steps на docs-задачу | baseline замерить | ≤ 50% baseline |
| correctness (verdict пользователя/verifier) | — | не ниже strict-цепочки |
| unauthorized mutations | 0 | 0 (инвариант) |

Test matrix:
1. Lightweight docs-only задача (spec authoring) — метрики выше, подтверждение
   получено, ноль правок вне scope.
2. Strict project-задача — цепочка reviewer→verifier→evidence сохранена.
3. Пограничная задача (docs-only, high-risk) — уходит в strict.
4. Empty handoff — `HANDOFF-INVALID`, без blind retry.
5. Scope drift в lightweight — stop + новый proposal.

Acceptance gate: именованный (verifier или пользователь для lightweight);
self-marker не является evidence.

## Rollback

- Откат = возврат к единой тяжёлой цепочке (текущее состояние); режимы
  удаляются из route schema одним коммитом, история route-log сохраняется.
- Staged rollout:
  1. **Design-only** (этот spec): режимы описаны, не применяются.
  2. **Controlled read-only smoke**: lightweight применяется к read-only
     задаче, метрики фиксируются, сравниваются с baseline.
  3. **Low-risk docs/config**: lightweight для vault docs/agent-инфраструктуры
     после успешного smoke.
  4. **Project/system**: strict остаётся единственным режимом; расширение
     lightweight на project/system — только после отдельного spec с
     evidence.
- Любая unauthorized mutation или провал метрики correctness → откат на
  предыдущую стадию.

## Unresolved Questions

1. **Runtime enforcement**: как именно режимы и `max_attempts` enforced —
   permissions, agent rules, или только prompt-контракт? Сейчас — только
   prompt-контракт; runtime-механизм не реализован.
2. **Telemetry**: чем замерять tokens/steps и повторные чтения (route-log
   вручную vs автоматический capture)?
3. **Local override merge**: как lightweight/strict взаимодействуют с
   project/agent permission overrides (agent rules take precedence)?
4. **Task compiler / prompt normalizer**: нужен ли отдельный компилятор
   задачи в context_bundle, или достаточно ручного handoff от meta?

Ни один из этих пунктов не считается решённым до отдельного подтверждённого
spec/апгрейда.
