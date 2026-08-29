---
description: Select and describe a scoped named capability route.
---
# Route

Use the ecosystem control-plane route protocol for `vault`, `global`, or
`project:<name>` scope. This command selects and records a route; it does not
execute the selected command and does not provide an automatic runtime router.
The exact orchestration smoke is documented at
[[06-Specs/Vault/control-plane-smoke]].

## Required decision

Before delegation, form the canonical route decision from
[[02-Methods/capability-routing]] and [[01-Reference/capability-routing]] with
    task, scope (`vault` | `global` | `project:<name>`), registered capability, role, explicit agent, layers, inputs,
outputs, risk, mutability, review, acceptance, fallback, and override. Check the
capability registry and the available scope/permissions. Natural user intent is
the input; a prompt-normalizer or task-compiler runtime is not implied.

Missing or unavailable capability, role, agent, scope, permission, or acceptance
boundary is `UNROUTABLE`. Never silently substitute `general`.

## Dispatch versus primary handoff

- **Subagent dispatch:** named `researcher`, `reviewer`, or `verifier` may be
  called only explicitly with `task(agent=<name>)` or `@<name>`, and only when
  task permission is allowed.
- **Primary handoff:** `sysop` is `mode=primary`, not a task subagent. Librarian
  prepares natural intent and exact scope; the user selects `sysop` with `Tab`
  or `switch_agent`.
- **Project primary:** for `project:<name>`, the project primary coordinates the
  local planner/build/domain/ui/infra pipeline and local verifier. This command
  records that composition; it does not run those commands.

For mutable work, `reviewer` quality verdict precedes `verifier` acceptance.
Acceptance must use independent evidence, including project-local verifier
evidence where applicable; a self-declared marker is not evidence. Append route
decisions, handoffs, and evidence to route-log; do not rewrite history or claim
an unperformed smoke.

`system-ops` apply is a separate local route and is not implied by
`system-audit`. This protocol adds no plugin, MCP, model routing, new agent, or
runtime router.
