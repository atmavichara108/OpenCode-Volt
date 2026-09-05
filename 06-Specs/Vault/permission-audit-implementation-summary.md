# Permission Audit + Role Profiles + Decision Queue — Implementation Summary

**Date:** 2026-09-05
**Task:** T-131 (Done)
**Status:** Verifier PASS 2026-09-05, Done

---

## A) Permission Audit + Fixes

### Critical bugs fixed (dotfiles/opencode.json)

1. **git push* = allow → ask** (line 17)
   - Risk: HIGH — push is destructive, should require confirmation
   
2. **verifier mutation commands removed**
   - Removed: `systemctl --user restart/start/stop` = allow
   - Verifier is read-only validation, not mutation
   
3. **verifier enhanced with read-only git commands**
   - Added: git status/diff/log/show/rev-parse/ls-files/branch
   - Added: validation commands (json.tool/py_compile/node --check/npm test/lint/build/pytest)

### Role profiles implemented

| Role | Edit | Bash | Task | Git write | Validation | Network |
|------|------|------|------|-----------|------------|---------|
| **researcher** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check | webfetch/websearch allow |
| **reviewer** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check/npm test/lint/pytest | deny |
| **verifier** | deny | scoped read-only | deny | read-only | json.tool/py_compile/node --check/npm test/lint/build/pytest | deny |
| **meta** | scoped (.opencode/AGENTS.md/vault) | scoped + git ask | reviewer/verifier | ask | json.tool/py_compile/node --check | deny |
| **sysop/system-ops** | deny (scoped allow) | scoped read-only + sudo ask | deny | read-only | systemctl status/journalctl | deny (sudo ask) |

### Dangerous commands (explicit deny all roles)

- `git reset*`, `git clean*`, `git restore*`, `git rebase*`, `git push --force*`
- `rm -rf*`, `sudo*`, `systemctl start/stop/restart/enable/disable*`
- `chmod*`, `chown*`, `mkfs*`, `mount*`, `umount*`

---

## B) Decision Queue Infrastructure

### Storage

- **Location:** `06-Specs/Vault/decision-queue/` (JSON files, append-only)
- **Schema:** `06-Specs/Vault/decision-queue/SCHEMA.md`
- **Constraints:** no secrets, no full prompts, metadata only, append-only, bounded (30-day archive)
- **Future (optional):** `~/.local/state/opencode/decision-queue/` — XDG-compliant, blocked by external_directory permissions, not active

### Command

- **Location:** `.opencode/command/decisions.md`
- **Subcommands:** list/show/new/resolve/reject/defer/archive
- **Write actions:** require explicit user confirmation
- **Verifier/reviewer:** can comment/accept/reject, but no silent resolution

### Vault projection

- **Location:** `06-Specs/Vault/decision-queue-log.md` (append-only readable summary)
- **Initial cards:** 4 decisions from this session (git push, verifier mutation, meta agent, storage location) — all status `pending`, no fabricated resolutions

### Skill

- **Location:** `.opencode/skills/decision-queue/SKILL.md`
- **Status:** Created but may need permission allow for `.opencode/skills/decision-queue/`

---

## C) Specs and Docs

### Created

1. `06-Specs/Vault/permission-audit-role-profiles.md` — full spec
2. `06-Specs/Vault/decision-queue/SCHEMA.md` — canonical format
3. `06-Specs/Vault/decision-queue-log.md` — append-only log (4 initial cards, status pending)
4. `06-Specs/Vault/permission-smoke-test.sh` — representative safe commands (run via `bash script.sh`; executable bit pending manual chmod)
5. `.opencode/command/decisions.md` — /decisions command
6. `.opencode/skills/decision-queue/SKILL.md` — decision queue skill
7. `04-Memory/session-log/2026-09-05.md` — session log

### Updated

1. `/home/rudra/dotfiles/opencode.json` — permission fixes
2. `TASKS.md` — T-131 added to Active
3. `04-Memory/active-context.md` — current focus updated

---

## D) Validation Results

✓ opencode.json: valid JSON
✓ No secrets found in created files
✓ Frontmatter present in all .md files
✓ Smoke test script created (executable bit pending manual chmod +x; chmod denied in Vault project config; run via `bash script.sh`)
✓ 4 JSON decision cards created with status `pending` (no fabricated resolutions)

---

## E) Pending [проверить]

1. **Runtime hook integration** — automatic decision card creation on permission.asked/tool blocked/UNROUTABLE/acceptance gate not confirmed
2. **`~/.local/state/opencode/` path permissions** — blocked by external_directory, requires explicit allow in global config (future/optional, not current storage)
3. **TUI "allow forever" persistence** — not verified as persistence evidence
4. **Project-specific .opencode/ configs** — serp/dv-hub/ChaT currently have no .opencode/ dirs; they inherit global profiles from dotfiles/opencode.json. Bootstrap needed only if project-local overrides are required.
5. **Decision queue skill permissions** — `.opencode/skills/decision-queue/` may need explicit allow
6. **Smoke test executable bit** — chmod denied in Vault project config; run via `bash script.sh` until manual chmod +x

---

## F) Narrow Verifier Smoke Plan

**Not launched broad verifier yet.** Recommended narrow smoke:

### 1. Permission smoke (manual or verifier)

Run `06-Specs/Vault/permission-smoke-test.sh` in OpenCode TUI:
- Verify each role can execute representative safe commands
- Verify dangerous commands are denied/ask

### 2. Decision queue smoke (manual)

```bash
/decisions list                                    # should show 4 pending cards
/decisions show 2026-09-05-permission-audit       # should display full card
/decisions resolve 2026-09-05-permission-audit A  # should update status (requires confirmation)
```

### 3. Config validation

```bash
python3 -m json.tool < /home/rudra/dotfiles/opencode.json  # validate JSON
```

### 4. No secrets check

```bash
grep -iE "(api[_-]?key|password|secret|token|credential)" \
  /home/rudra/dotfiles/opencode.json \
  /home/rudra/Projects/OpenCode-Vault/.opencode/command/decisions.md \
  /home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/permission-audit-role-profiles.md
```

---

## G) Files Changed

### Modified

- `/home/rudra/dotfiles/opencode.json` — permission fixes (git push, verifier, researcher, reviewer, meta agent)

### Created

- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/permission-audit-role-profiles.md`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue/SCHEMA.md`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue/2026-09-05-git-push-permission.json`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue/2026-09-05-verifier-mutation.json`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue/2026-09-05-meta-agent-creation.json`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue/2026-09-05-decision-queue-storage.json`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/decision-queue-log.md`
- `/home/rudra/Projects/OpenCode-Vault/06-Specs/Vault/permission-smoke-test.sh`
- `/home/rudra/Projects/OpenCode-Vault/.opencode/command/decisions.md`
- `/home/rudra/Projects/OpenCode-Vault/.opencode/skills/decision-queue/SKILL.md`
- `/home/rudra/Projects/OpenCode-Vault/04-Memory/session-log/2026-09-05.md`

### Updated

- `/home/rudra/Projects/OpenCode-Vault/TASKS.md` — T-131 added
- `/home/rudra/Projects/OpenCode-Vault/04-Memory/active-context.md` — current focus updated

---

## H) Constraints Respected

✓ No commit/push (per user request)
✓ No application code touched (only agent infrastructure)
✓ No broad verifier/researcher launched (per user request)
✓ Historical logs preserved (append-only, no rewriting)
✓ facts.md not modified (no unverified runtime claims)
✓ No secrets, no root/system changes, no force/reset/clean

## H.1) Out-of-scope: Vault opencode.json

**Note:** `opencode.json` (Vault project config) has uncommitted changes (permission section added). This change is **pre-existing** (from 2026-08-31 ecosystem kanban session or earlier), NOT part of the current 2026-09-05 permission audit scope. The current audit focused on `dotfiles/opencode.json` (global config). Vault `opencode.json` changes are documented separately and not modified in this session.

---

## I) Next Steps

1. **User reviews changes** and confirms
2. **Run narrow permission smoke** (manual or verifier)
3. **Address pending [проверить] items:**
   - Add `~/.local/state/opencode/` to permissions if needed
   - Investigate runtime hook integration
   - Bootstrap project .opencode/ configs if needed
4. **Commit changes** (after verification)
5. **Update facts.md** with confirmed runtime behaviors

---

## J) Effective Profile Summary

### Researcher (read-only research)

- **Edit:** deny
- **Bash:** scoped read-only (ls/cat/grep/rg/find/git read/validation commands)
- **Task:** deny
- **Network:** webfetch/websearch allow
- **Use case:** repo/artifact research, web research

### Reviewer (read-only quality review)

- **Edit:** deny
- **Bash:** scoped read-only (ls/cat/grep/rg/find/git read/validation commands/npm test/lint/pytest)
- **Task:** deny
- **Network:** deny
- **Use case:** code quality/style review, validation

### Verifier (read-only acceptance)

- **Edit:** deny
- **Bash:** scoped read-only (ls/cat/grep/find/git read/validation commands/npm test/lint/build/pytest)
- **Task:** deny
- **Network:** deny
- **Use case:** acceptance testing, syntax validation

### Meta (agent infrastructure editor)

- **Edit:** scoped (.opencode/**, AGENTS.md, ~/.config/opencode/**, vault)
- **Bash:** scoped (ls/cat/grep/rg/find/git ask/validation commands)
- **Task:** reviewer/verifier allow
- **Network:** deny
- **Use case:** agent infrastructure editing, config management

### Sysop/System-ops (high-risk host apply planner)

- **Edit:** deny (scoped allow for evidence)
- **Bash:** scoped read-only + sudo ask
- **Task:** deny
- **Network:** deny
- **Use case:** system audit, high-risk apply planning

---

**End of summary**

---

## K) Acceptance (2026-09-05)

**Reviewer:** clear (quality verdict)
**Verifier:** VERDICT PASS (acceptance confirmed)
**Date:** 2026-09-05

T-131 → Done. Residuals [проверить] открыты (см. section E). facts.md не тронут. Без commit/push.

Evidence: [[04-Memory/session-log/2026-09-05]]
