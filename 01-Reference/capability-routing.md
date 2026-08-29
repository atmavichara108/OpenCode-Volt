---
type: Reference
title: Capability Routing Runtime Reference
description: Подтверждённые scoped runtime-маршруты capability-routing.
tags: [reference, routing, runtime]
timestamp: 2026-08-29
---
# Capability Routing Runtime Reference

## Runtime routes

| Capability | Role/agent | Status | Boundary |
|---|---|---|---|
| `system-audit` | `sysop` | `runtime-smoke-confirmed` | only exact global primary smoke |
| `read-research` | `researcher` | `runtime-smoke-confirmed` | only exact dated smoke; [[04-Memory/route-log/2026-08-29-researcher-smoke]] |
| `quality-review` | `reviewer` | `runtime-smoke-confirmed` | only exact dated smoke; [[04-Memory/route-log/2026-08-29-reviewer-smoke]] |
| `orchestration` | `librarian` | `runtime-smoke-confirmed` | only exact dated smoke; [[04-Memory/route-log/2026-08-29-orchestration-smoke]] |
| `meta-infrastructure` | `meta` | `registry/documented` | global infrastructure changes/audit; runtime availability requires evidence |

`system-audit -> sysop` подтверждён только для exact global primary smoke. Это
не orchestration/general rollout и не разрешение использовать `sysop` как task
subagent: `sysop` работает в режиме `primary`.

Пользовательский primary route выбирается через `Tab` или `switch_agent`, после
чего пользователь задаёт natural intent для `system-audit`. `general` не
является fallback. Если scope выходит за exact global primary smoke, нужно
остановиться как `UNROUTABLE`.

`sysop` остаётся read-only. `system-ops` apply — отдельный local extension и
отдельный маршрут с собственным approval и acceptance; эта запись его не
подтверждает.

## Ecosystem orchestration boundary

**Status:** `documented/control-plane`; exact orchestration smoke is confirmed
only for its dated evidence, while an automatic runtime router is not
implemented. This is an ecosystem-wide boundary, not a librarian-only upgrade.

### Levels and ownership

| Level | Responsibility | Boundary |
|---|---|---|
| Vault/librarian | Cross-project coordination and control-plane | Selects/records routes and coordinates evidence; does not own every runtime pipeline |
| Global role kernel | Shared role contracts | `researcher` = artifact/repo research; `reviewer` = quality; `verifier` = acceptance; `sysop` = machine/system primary; `meta` = agent infrastructure |
| Project-local extensions | Project execution and acceptance | `planner`, `build`, `domain-dev`, `ui`, `infra`, and local `verifier`, only when present in project registry/status |
| Commands/pipelines | Execution surfaces | Must name the role/agent and acceptance path; never generic `general` |

The global list is limited to roles confirmed by the current registry/status and
route evidence. `guardian`, `prompt-engineer`, `task-compiler`, and any new
runtime are not existing roles here. Local names are extension slots, not a
claim that every project implements all of them.

### Route composition

Compose each route as `intent -> scope/node -> capability -> named role/agent ->
review -> verifier/acceptance -> evidence`. Apply layers A (engineering
conventions), B (language/runtime), and C (capability, role, risk and order).
Vault/librarian coordinates across projects; the project primary coordinates the
local planner/build/domain/UI/infra pipeline and project-specific acceptance.

- `researcher`, `reviewer`, and `verifier` are named subagent dispatches only via
  explicit `task(agent=<name>)` or `@<name>` when permission allows it.
- `sysop` is a primary handoff for the confirmed `system-audit` smoke: the user
  switches with `Tab`/`switch_agent` and supplies natural intent. It is not a
  task subagent; system apply is a separate local route.
- For mutable work, reviewer quality precedes verifier acceptance. A project
  local verifier is required when that project owns the acceptance surface.
- Risk and mutability separate read-only, docs-only, project-edit and infra-edit
  routes. Medium/high-risk or irreversible work needs explicit approved
  override and rollback/stop conditions.
- Missing role, capability, scope, permission or acceptance boundary is
  `UNROUTABLE`; there is no silent fallback to `general`.
- Route decisions, handoffs and evidence are append-only route-log records.
  Self-declared markers are not evidence and there is no self marker.

This contract separates route selection/recording from execution. It adds no
runtime router, prompt-normalizer, task-compiler, plugin, MCP or new agent.

Independent verifier подтвердил smoke по runtime trace: primary session
переключена на `agent=sysop`, `mode=primary`, model
`opencode-go/deepseek-v4-flash`; выполнены только read-only audit commands,
`edit`/`task`/mutating `bash` отсутствовали, `stow -n` выполнен как simulation,
general fallback не наблюдался. Самодекларированный marker доказательством не
считается.

Evidence: [[04-Memory/route-log/2026-08-29-sysop-smoke]],
[[04-Memory/route-log/2026-08-29-orchestration-smoke]],
[[04-Memory/facts]], [[04-Memory/active-context]].

Открыты negative deny smoke, local extension merge, uncommitted artifacts,
automatic orchestration runtime и literal tool output limits.
