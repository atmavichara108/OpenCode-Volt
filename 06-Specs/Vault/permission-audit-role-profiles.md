---
title: Permission Audit & Role Profiles
type: Spec
status: active
created: 2026-09-05
updated: 2026-09-05
scope: global (dotfiles/opencode.json), vault (project config)
scope_note: serp/dv-hub/ChaT have no project-local .opencode/ configs; they inherit global profiles from dotfiles/opencode.json. No project-local implementation for those projects.
---

# Permission Audit & Role Profiles

## Problem

Effective agent configs had critical issues:
1. `git push*` = allow in global (dangerous, should be ask)
2. `verifier` had `systemctl --user restart/start/stop` = allow (mutation!)
3. No explicit meta agent config
4. No decision queue for permission conflicts/UNROUTABLE
5. Role profiles lacked explicit command allowlists

## Solution

### A) Permission fixes (dotfiles/opencode.json)

**Fixed:**
- `git push*`: allow → ask (line 17)
- `verifier`: removed `systemctl --user restart/start/stop` (mutation)
- `verifier`: added explicit read-only git commands (status/diff/log/show/rev-parse/ls-files/branch)
- `verifier`: added validation commands (python -m json.tool, node --check, npm test/lint/build, pytest --collect-only)
- `verifier`: added `task: deny`, `read/glob/grep: allow`, `webfetch: deny`

**Enhanced:**
- `researcher`: added `rg`, git read commands (rev-parse/ls-files/branch/remote/describe/symbolic-ref), validation commands (json.tool/py_compile/node --check)
- `reviewer`: added `rg`, git read commands (blame/rev-parse/ls-files/branch), validation commands (json.tool/py_compile/node --check/npm test/lint/pytest)
- `meta`: new agent for agent infrastructure editing (.opencode/, ~/.config/opencode/, vault)

### B) Role profiles

| Role | Edit | Bash | Task | Git write | Validation | Network |
|------|------|------|------|-----------|------------|---------|
| **researcher** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check | webfetch/websearch allow |
| **reviewer** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check/npm test/lint/pytest | deny |
| **verifier** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check/npm test/lint/build/pytest | deny |
| **meta** | scoped (.opencode/AGENTS.md/vault) | scoped + git ask | reviewer/verifier | ask | json.tool/py_compile/node --check | deny |
| **sysop/system-ops** | deny (scoped allow) | scoped read-only + sudo ask | deny | read-only | systemctl status/journalctl | deny (sudo ask) |
| **builder** | allow | ask | reviewer/verifier/stow-ops/researcher | ask | via subagents | via subagents |

### C) Dangerous commands (explicit deny)

All roles:
- `git reset*`, `git clean*`, `git restore*`, `git rebase*`, `git push --force*`: deny
- `rm -rf*`, `sudo*`, `systemctl start/stop/restart/enable/disable*`: deny (except sysop sudo ask)
- `chmod*`, `chown*`, `mkfs*`, `mount*`, `umount*`: deny

### D) Persistence

Permissions configured in `dotfiles/opencode.json` (persistent config).
Runtime TUI "allow forever" NOT considered persistence evidence until verified.

### E) Project-local coverage

**Implemented:** global profiles in `dotfiles/opencode.json` (researcher, reviewer, verifier, meta, sysop/system-ops, builder, planner, stow-ops, bash-dev, qtile-dev, util-dev, think). Vault project config (`opencode.json`) has project-level bash allowlist.

**Not implemented (uses global inheritance):** serp, dv-hub, ChaT — these projects have no `.opencode/` directories. They inherit global agent profiles from `dotfiles/opencode.json` via OpenCode config merge. No project-local permission overrides exist for these projects.

## Decision Queue

### Storage

`06-Specs/Vault/decision-queue/` — JSON files, append-only.
Schema: `06-Specs/Vault/decision-queue/SCHEMA.md`

**Future:** `~/.local/state/opencode/decision-queue/` (XDG-compliant, requires permission allow)

### Command

`/decisions` — list/show/new/resolve/reject/defer/archive.
Write actions require explicit user confirmation.

### Integration triggers [проверить]

- `permission.asked` event
- `tool blocked` error
- `UNROUTABLE` route conflict
- Acceptance gate issue

Currently manual creation only. Runtime hook integration not confirmed.

### Vault projection

`06-Specs/Vault/decision-queue-log.md` — append-only readable summary.

## Smoke test

See `06-Specs/Vault/permission-smoke-test.sh` for representative safe commands.

## Pending [проверить]

1. Runtime hook integration (automatic decision card creation)
2. `~/.local/state/opencode/` path permissions (may need explicit allow)
3. TUI "allow forever" persistence behavior
4. Project-specific .opencode/ configs (serp, dv-hub, ChaT) — currently no .opencode/ dirs; these projects inherit global profiles from dotfiles/opencode.json. Bootstrap needed only if project-local overrides are required.

## Changelog

- 2026-09-05: Initial spec, permission fixes, role profiles, decision queue
