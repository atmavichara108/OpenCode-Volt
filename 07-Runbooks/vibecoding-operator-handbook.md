---
type: Runbook
title: Vibecoding Operator Handbook
description: Текущее рабочее руководство по координации VibeOS.
tags: [runbooks, operations, vibecoding]
---
# Vibecoding Operator Handbook

## Purpose

Фиксирует текущий способ практического использования координационного слоя
VibeOS: кто что делает, как проходит типовая работа и какие сигналы считаются
достаточными для обновления операционной практики.

## Operating model

- **user** — задаёт intent, ограничения и критерий результата; подтверждает
  решения и изменения практики.
- **librarian** — coordination node: читает vault-контекст, маршрутизирует,
  фиксирует подтверждённые результаты и обновляет vault.
- **meta** — проактивный наблюдатель global layer: ищет drift и повторяющиеся
  patterns, но не является автоматическим редактором handbook.
- **sysop** — инспектирует ecosystem/global infrastructure и поднимает
  operational facts.
- **researcher** — собирает внешние и локальные evidence до решения.
- **reviewer** — проверяет качество, полноту и соответствие intent.
- **verifier** — acceptance-only проверка DoD; выдаёт явный verdict.

## Core principles of practical use

- Vault — coordination node, а не место исполнения проектного кода.
- Global layer развивается под управлением Volt; локальные инструменты — limbs
  агентов, а не замена координации.
- Project reality важнее declarations в карточках, индексах и планах.
- Сначала minimal kernel, затем adoption по проектам; не делать big-design-upfront.
- Operational memory должна быть low-noise: писать только actionable,
  confirmed и пригодное для следующего оператора.

## Standard workflows

### Orchestrated route

1. `intent -> scope/node -> capability route` по canonical schema.
2. Global named role или project primary/local named pipeline выполняет
   разрешённый slice; route selection/recording не является execution.
3. `reviewer` выдаёт quality verdict, затем `verifier` проверяет acceptance;
   project work требует project-local DoD/verifier.
4. Librarian добавляет decision, handoff и evidence в append-only route-log.
5. Для `sysop` primary пользователь переключается через `Tab`/`switch_agent`;
   missing role/capability/acceptance означает `UNROUTABLE`, без silent fallback.

Librarian остаётся только cross-project coordinator. Project primary owns the
local pipeline. `sysop` primary requires user handoff; subagents use explicit
`task`/`@mention`. Self-declared markers are not evidence. Automatic runtime
router is not implemented.

Orchestrated smoke is now confirmed for the exact Vault slice: librarian route
selection -> named researcher -> reviewer -> verifier. The chain is sequential,
read-only, and evidence-gated; this confirmation does not enable an automatic
runtime router. `sysop` primary handoff remains separate.

### Coordination Bridge

 Пользовательский порядок работы с единым Git-backed bridge protocol и командой
 `/bridge` описан в [[07-Runbooks/coordination-bridge-operator-guide]]. Bridge — это canonical
file contract, а не отдельный agent; фасад-команда или MCP могут появиться
  позже, но не становятся source of truth. Bridge records named-role
  claim/handoff/evidence and stops at `UNROUTABLE`, `BLOCKED`, stale or
  conflict; automatic runtime routing is not implemented. Пользователь задаёт
  intent/scope/owner/DoD и одобряет commit/push; review и verify остаются
  отдельными gates.

### Read-only audit

1. Librarian фиксирует scope и не меняет target repository.
2. Researcher/sysop собирает evidence; reviewer проверяет трактовку.
3. Librarian оформляет dated findings в [[06-Audits/README]] и residuals в memory.

Для `system-audit` пользователь выбирает global primary `sysop` через `Tab`/
`switch_agent` и задаёт natural intent. `sysop` read-only; `system-ops` apply —
отдельный route. Acceptance выполняется independent verifier по runtime evidence.

### Named route smoke

После изменения agent/config требуется restart. Named route сначала проверяется
controlled smoke: reviewer даёт quality verdict, verifier — acceptance. При
отсутствии named route результат — `UNROUTABLE`.

### Agent dispatch and evidence

- Primary role переключается через `Tab` или настроенный keybind
  `switch_agent`.
- Subagent вызывается через `@mention` или `task`.
- Пользователь задаёт intent естественным языком; технический prompt и
  acceptance marker от пользователя не требуются.
- Evidence и verdict проверяются независимым verifier по session/runtime
  artifacts, а не по самодекларации агента или строке вроде
  `SYSOP SMOKE: PASS`.
- `/agents` может быть пользовательской командой выбора модели и не является
  универсальным способом переключения agent role; конкретную реализацию не
  предполагать без подтверждения.

### Addendum

1. Продолжать существующий audit только при том же scope и новом evidence.
2. Отделять confirmed facts, open questions и proposals.
3. Не переписывать исходный снимок; ссылаться через addendum.

### Ecosystem planning

1. Сначала сверить [[04-Memory/facts]] и активный контекст.
2. Описывать contracts, gates и sequence, а не loose agent descriptions.
3. Отделять planned artifacts от уже внедрённых возможностей.

### Project adoption

1. Выбрать следующий project gate из подтверждённой sequence.
2. Зафиксировать contract и DoD до делегирования.
3. Делегировать локальному build/sysop-агенту; reviewer и verifier закрывают
   quality и acceptance.
4. Обновить карточку и memory только после подтверждения результата.

### Project recovery

1. Сначала восстановить acceptance surface и operational health.
2. Не накладывать kernel overlay на проект с неподтверждённым recovery gate.
3. Зафиксировать residuals и следующий gate отдельно от optimistic status.

### Memory/update

1. Session facts писать в [[04-Memory/session-log/2026-08-04]].
2. Stable confirmed facts добавлять в [[04-Memory/facts]].
3. Текущий focus и residuals держать в [[04-Memory/active-context]].
4. Runbook менять только после подтверждённого shift практики; историю писать в
   append-only [[07-Runbooks/vibecoding-changelog]].

### Atomic commit

1. Проверить scope и `git diff` только в vault.
2. Запустить обязательные проверки и verifier/guardian gate, если они доступны.
3. Сделать один атомарный commit согласованного набора; не смешивать project
   repositories и vault.

## Typical scenarios

- **Urgent SERPlux debugging:** librarian держит scope в SERPlux, build чинит,
  reviewer оценивает, verifier подтверждает DoD; vault получает только итог и
  residuals.
- **Parallel dotfiles tuning:** sysop/build работают по независимым slices,
  librarian сохраняет global/local boundary и сводит подтверждённые изменения.
- **dv-hub recovery later:** сначала recovery gate и acceptance surface, затем
  adoption; dv-hub не становится первым kernel target.
- **Recurring method:** повторяющийся подтверждённый pattern сначала проходит
  distill/review, затем становится reusable Method, а usage остаётся здесь.
- **Actionable capture idea:** capture даёт сигнал, librarian классифицирует и
  превращает его в task/plan только после проверки применимости.
- **Declaration/reality mismatch:** read-only audit сравнивает declaration с
  repo evidence; mismatch фиксируется как finding, не маскируется обновлением
  статуса.

## Prompt patterns

Шаблоны короткие и strict: scope, роль, действие, evidence и DoD обязательны.

### Librarian task

```text
Librarian task: [цель]. Scope: [vault/project]. Read: [источники].
Do not touch: [границы]. Delegate: [role]. Evidence: [что подтвердить].
Output: [артефакты + residuals]. No extra prose.
```

### Audit

```text
Read-only audit. Target: [repo/path]. Check: [scope]. Do not edit.
Return: confirmed findings, evidence paths, open questions, impact. No fixes.
```

### Addendum

```text
Audit addendum to: [file]. New evidence: [scope]. Preserve original snapshot.
Separate confirmed facts / open questions / proposals. Output only addendum.
```

### Plan synthesis

```text
Synthesize plan from: [audits/facts]. Use contracts, gates, sequence.
Mark planned vs implemented. Include dependencies and residuals. No code changes.
```

### Task fixation

```text
Fix task: [one outcome]. Owner: [agent]. Scope: [files/repo]. DoD: [checks].
Forbidden: [files/actions]. Evidence required: [artifact/verdict].
```

### Commit fixation

```text
Commit fixation. Repo: [vault/project]. Scope: [files]. Verify: [commands].
Commit only this set. Do not touch other repos. Return hash and checks only.
```

### No extra prose

```text
No extra prose: return only [requested format]. Do not summarize, speculate,
or propose unrequested work.
```

## Update discipline

- Не превращать planned или `[проверить]` в live practice без evidence.
- Не копировать Methods, Audits или `AGENTS.md`; ссылаться на них.
- Не смешивать operational guidance с project status и implementation details.
- Каждое изменение handbook должно иметь подтверждённый practice shift и
  короткую append-only запись в changelog.

## Meta proactivity integration

meta не переписывает handbook автоматически, может находить drift/new recurring
patterns через hooks/skills, librarian превращает подтверждённые deltas в
handbook updates, changelog append-only.
