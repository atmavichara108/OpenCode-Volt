---
name: capability-routing
description: Scoped routing guidance for named capabilities.
---
# Capability Routing

This guidance applies to the whole ecosystem, not only to librarian. Compose a
pipeline as `intent -> scope/node -> capability -> named role/agent -> review ->
verifier/acceptance -> evidence`.

## Role responsibilities

- `librarian` coordinates cross-project scope and control-plane records; it does
  not own project execution.
- Global kernel roles are bounded: `researcher` investigates artifact/repo
  reality, `reviewer` judges quality, `verifier` judges acceptance, `sysop`
  inspects machine/system as primary, and `meta` handles `meta-infrastructure`
  changes/audit. Registry presence does not prove runtime availability.
- A project primary coordinates local `planner`, `build`, `domain-dev`, `ui`,
  and `infra` extensions plus local verifier when registered. Local acceptance
  remains project-specific.
- `guardian`, `prompt-engineer`, and `task-compiler` are not runtime roles in
  this slice.

- `system-audit` routes only to the global primary `sysop` for the exact
  runtime-smoke-confirmed scope.
- `sysop` is `mode=primary`, not a task subagent. The user selects it with
  `Tab` or `switch_agent`, then states the audit intent naturally.
- Keep `sysop` read-only. `system-ops` apply is a separate local extension and
  route; do not merge it into this route.
- Do not use `general` as fallback. An unconfirmed scope is `UNROUTABLE`.
- Acceptance requires an independent verifier using runtime/session evidence;
  a self-declared marker is not proof.

## Orchestration slice

The slice is a control-plane protocol, not a runtime router, prompt normalizer,
or task compiler. For every delegation, first write the route decision using the
canonical schema in `02-Methods/capability-routing.md` and
`01-Reference/capability-routing.md`; check registry, scope, risk, mutability,
review, acceptance, and fallback.

### Read-only research

1. Librarian classifies intent and records the route decision.
2. Dispatch named `researcher` only through explicit `task(agent=researcher)` or
   `@researcher`, when task permission allows it.
3. Send evidence to named `reviewer` when quality review is required.
4. Require verifier only when the decision declares an acceptance gate; otherwise
   `acceptance: none` is explicit.
5. Append the decision and evidence to route-log; do not treat a self-declared
   marker as evidence.

### Mutable project work

1. The project primary declares `scope: project:<name>`, mutability, risk, outputs, review and the
   project-local acceptance boundary before dispatch.
2. Dispatch the explicitly named project-capable subagent; never substitute
   `general`.
3. Obtain the `reviewer` quality verdict before the `verifier` acceptance verdict.
4. Require project-local verifier evidence against the project DoD, then append
   the route-log record. Missing role, scope, permission, or gate is
   `UNROUTABLE`.

### System audit

1. Librarian prepares natural intent, exact scope, read-only risk/mutability and
   the route decision for `system-audit`.
2. `sysop` is a primary handoff: the user selects it through `Tab` or
   `switch_agent`; do not dispatch it through `task` or `@mention`.
3. Review and independent verifier acceptance use runtime/session evidence; a
   marker or declaration alone is insufficient.
4. Append the handoff and evidence without rewriting prior route-log entries.

There is no automatic runtime router in this slice: status is
`documented/control-plane`; the dated orchestration smoke is confirmed only for
its exact evidence. Route selection/recording is separate from command
execution. Missing route, scope, permission, or acceptance boundary stops as
`UNROUTABLE`; there is no silent fallback. Do not add or imply a
prompt-normalizer/task-compiler runtime, model routing, plugin, MCP, or new
agent.
