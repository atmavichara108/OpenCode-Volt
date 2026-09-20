---
type: Execution Spec
title: Vault control-plane orchestration smoke
status: approved
scope: vault
date: 2026-08-29
---
# Vault Control-Plane Orchestration Smoke

## Goal

Повторяемо проверить документированный control-plane маршрут Vault без
изменения проектов/кода и без внедрения runtime router.

## Scope

- Target: `OpenCode-Vault` documentation only.
- Scope: `vault`.
- Risk/mutability: `read-only`; delegated agents must not edit or run tasks.
- This spec is an execution procedure, not a runtime router.

## Route schema

Каждый запуск фиксирует:

```yaml
task: exact orchestration smoke
scope: vault
capability: orchestration
role: librarian
agent: librarian
risk: read-only
mutability: read-only
review: reviewer
acceptance: verifier
fallback: UNROUTABLE
runtime_dispatch: exact-smoke-only
```

Capability availability must be supported by runtime evidence; this spec does
not make availability claims beyond the recorded smoke.

## Exact chain

1. `librarian` selects and records the exact `vault` route.
2. Named `researcher` runs the read-only research slice.
3. Named `reviewer` reviews the result and returns a quality verdict.
4. Named `verifier` independently checks runtime/session evidence and returns
   the acceptance verdict.
5. Librarian appends the evidence to
   [[04-Memory/route-log/2026-08-29-orchestration-smoke]].

Order is strictly `researcher -> reviewer -> verifier`; the parent librarian
session is recorded as provenance, not as a substitute for the named chain.

## Stop Conditions

Stop with `UNROUTABLE` if any named role, capability, permission, scope or
acceptance boundary is unavailable. Stop on edits, task dispatch from a
read-only delegated slice, scope drift, missing evidence, or a failed verdict.

## Fallback Boundary

There is no `general` fallback. Do not infer a general automatic router from
this smoke. Do not use a self-declared marker as evidence.

## Sysop Handoff

`sysop` remains a separate primary handoff for the exact `system-audit` smoke;
it is not a step in this orchestration chain and is not dispatched as a task
subagent.

## Gates and Evidence

- `reviewer` gate: quality verdict must be explicit.
- `verifier` gate: independent PASS/FAIL based on runtime/session evidence.
- Route evidence is append-only at
  [[04-Memory/route-log/2026-08-29-orchestration-smoke]].
- Canonical routing contract: [[02-Methods/capability-routing]].

## Rollback

If the smoke fails or scope changes, stop and retain the route-log evidence;
disable/remove only this exact route record or spec revision and return to the
last approved named route. Never broaden permissions or substitute `general`.

## Acceptance Criteria

- Exact sequential `researcher -> reviewer -> verifier` chain is evidenced.
- Researcher and reviewer produce no edits/task in the read-only slice.
- Reviewer returns `REVIEWER VERDICT: clear`.
- Independent verifier returns `PASS`.
- All four session IDs are recorded in the route-log.
- No general fallback or self-marker is used as evidence.
- Automatic runtime orchestration remains explicitly not implemented.
