---
description: Decision queue management: create, list, resolve dilemma cards. Use when permission blocked, UNROUTABLE, acceptance gate, or user asks "/decisions".
---

# Decision Queue Skill

Manage persistent dilemma cards for permission conflicts, UNROUTABLE routes, acceptance gates, and high-risk decisions.

## When to use

- `permission.asked` event (tool blocked, needs approval)
- `UNROUTABLE` route conflict (no clear agent/capability)
- Acceptance gate issue (verifier/reviewer disagreement)
- High-risk decision (system-ops, force push, destructive git)
- User explicitly asks `/decisions`

## Storage

**Current (canonical):** `06-Specs/Vault/decision-queue/` (JSON files, append-only).
Schema: `06-Specs/Vault/decision-queue/SCHEMA.md`.

**Future (optional):** `~/.local/state/opencode/decision-queue/` — XDG-compliant user state path. Currently blocked by external_directory permissions. Requires explicit allow in global config. Not active.

## Workflow

### 1. Create decision card

Filename: `YYYY-MM-DD-<slug>.json` in `06-Specs/Vault/decision-queue/`.

Use schema from `06-Specs/Vault/decision-queue/SCHEMA.md`:
- `id`: unique identifier
- `status`: pending|approved|rejected|deferred|resolved
- `risk`: low|medium|high|critical
- `source.trigger`: permission.asked|tool.blocked|unroutable|acceptance.gate|manual
- `dilemma.title`: short human-readable title
- `dilemma.context`: one-line context (no secrets)
- `dilemma.options`: array of {id, label, pros, cons}
- `dilemma.recommendation`: option id
- `dilemma.reason`: brief rationale (no chain-of-thought)
- `stop_condition`: when to auto-close

### 2. List decisions

```bash
# List pending decisions (using python3 for JSON parsing)
for f in 06-Specs/Vault/decision-queue/*.json; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(f\"{d['id']} [{d['status']}] [{d['risk']}] {d['dilemma']['title']}\")" "$f"
done

# Show full card
python3 -m json.tool 06-Specs/Vault/decision-queue/<id>.json
```

### 3. Resolve decision

Update card:
- Set `status`: approved|rejected|deferred|resolved
- Set `resolution.choice`: option id or "deferred"/"rejected"
- Set `resolution.approved_by`: "user" or "agent:<name>"
- Set `resolution.approved_at`: ISO timestamp
- Optionally add `resolution.evidence`: link to spec/route-log

### 4. Vault projection

Append summary to `06-Specs/Vault/decision-queue-log.md`:
```markdown
## YYYY-MM-DD HH:MM — <title>
- **Status:** pending|approved|rejected
- **Risk:** low|medium|high|critical
- **Options:** A, B, C
- **Recommendation:** A
- **Resolution:** <choice> by <approved_by> at <approved_at>
```

## Constraints

- **No secrets, no full prompts** — metadata only
- **Append-only** — never delete, only update status
- **Short reason** — no chain-of-thought
- **Bounded** — archive resolved cards older than 30 days

## [проверить]

- Runtime hook integration (automatic card creation on permission.asked) not confirmed
- Fallback: manual creation via `/decisions new` or agent-initiated

## Runtime integration (T-132, 2026-09-05)

**Plugin:** `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/decision-queue-hook.ts`

**Hook:** `permission.ask` `[проверить exact signature]` с graceful fallback на event catch-all.

**Storage:** Append-only JSONL (`runtime-events.jsonl`) в:
- Canonical: `06-Specs/Vault/decision-queue/runtime-events.jsonl` (если path существует)
- Fallback: `.decision-queue/runtime-events.jsonl` (project root)

**Workflow:**
1. Plugin автоматически создаёт metadata-only card на permission events
2. Card сохраняется в JSONL (append-only)
3. User reviews cards via `/decisions list` (показывает manual JSON cards + runtime JSONL)
4. User resolves via `/decisions resolve <id> <choice>` (требует explicit confirmation)

**Constraints:**
- Metadata-only: no prompt content, no tool output, no secrets
- Append-only: never delete, only append
- No shell/git/network/file edit actions
- No card resolution, no commit/push

**Smoke test:** `06-Specs/Vault/decision-queue-smoke-test.mjs` (25/25 PASS, pure functions, no live runtime required).

**Integration layer:** plugin создаёт JSONL, `/decisions` command ожидает JSON files. Integration layer не реализован (future work). Currently plugin creates runtime log, manual cards created via `/decisions new` remain separate JSON files.
