---
description: Decision queue: list/show/resolve/reject/defer dilemma cards. Write actions require explicit user approval.
agent: librarian
---
# Command: /decisions $ARGUMENTS

Manage persistent dilemma cards for permission conflicts, UNROUTABLE routes, acceptance gates, and high-risk decisions.

Storage: `control-plane/decision-queue/` (JSON files, append-only).
Vault projection: `control-plane/decision-queue-log.md`.

## Subcommands

### `/decisions` or `/decisions list`
List all pending decisions with title, risk, status.

```bash
# Using jq (allowed in librarian/meta/reviewer/verifier)
for f in control-plane/decision-queue/*.json; do
  jq -r '"\(.id) [\(.status)] [\(.risk)] \(.dilemma.title)"' "$f"
done

# Fallback: python3 (if jq unavailable)
for f in control-plane/decision-queue/*.json; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(f\"{d['id']} [{d['status']}] [{d['risk']}] {d['dilemma']['title']}\")" "$f"
done
```

### `/decisions show <id>`
Show full decision card.

```bash
jq . control-plane/decision-queue/<id>.json
# or: python3 -m json.tool control-plane/decision-queue/<id>.json
```

### `/decisions new <title>`
Create new decision card interactively. Agent asks:
1. Title (short, human-readable)
2. Context (one-line, no secrets)
3. Options (A/B/C with pros/cons each)
4. Recommendation (which option)
5. Reason (brief, no chain-of-thought)
6. Risk (low/medium/high/critical)
7. Stop condition (when to auto-close)

Write to `control-plane/decision-queue/YYYY-MM-DD-<slug>.json`.
Append summary to `control-plane/decision-queue-log.md`.

### `/decisions resolve <id> <choice>`
Mark decision as resolved. Requires explicit user confirmation.
- Update `status` → "resolved"
- Set `resolution.choice` to selected option
- Set `resolution.approved_by` → "user"
- Set `resolution.approved_at` → current ISO timestamp
- Append resolution to Vault projection

### `/decisions reject <id> [reason]`
Mark decision as rejected. Requires explicit user confirmation.
- Update `status` → "rejected"
- Set `resolution.choice` → "rejected"
- Append to Vault projection

### `/decisions defer <id> [until]`
Defer decision. Update `status` → "deferred".
- Optionally set `stop_condition` with date/condition

### `/decisions archive`
Move resolved cards older than 30 days to `archive/` subdirectory.

## Constraints

- **Write actions (new/resolve/reject/defer) require explicit user confirmation**
- **No secrets, no full prompts** — metadata only
- **Append-only** — never delete, only update status
- **Verifier/reviewer can comment/accept/reject, but no silent resolution**

## Integration triggers [проверить]

Runtime hook integration not yet confirmed. Currently manual creation only.
Future: automatic card creation on permission.asked, tool blocked, UNROUTABLE, acceptance gate.

## Runtime integration (T-132, 2026-09-05)

**Plugin:** `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/decision-queue-hook.ts`

**Hook:** `permission.ask` and event catch-all are implemented; live event fire remains `[проверить]`.

**Storage:** Append-only JSONL (`runtime-events.jsonl`) в:
- Canonical: `control-plane/decision-queue/runtime-events.jsonl` (если path существует)
- Fallback: structured application log only; no project-root file is created.

**Workflow:**
1. Plugin автоматически создаёт metadata-only card на permission events
2. Card сохраняется в JSONL (append-only)
3. User reviews manual JSON cards via `/decisions list`; runtime JSONL remains separate until projection is implemented.
4. User resolves via `/decisions resolve <id> <choice>` (требует explicit confirmation)

**Constraints:**
- Metadata-only: no prompt content, no tool output, no secrets
- Append-only: never delete, only append
- No shell/git/network/file edit actions
- No card resolution, no commit/push

**Smoke test:** `control-plane/decision-queue-smoke-test.mjs` (shared pure helpers, no live runtime required).

**Integration layer:** plugin JSONL and manual JSON cards remain separate; JSONL projection is future work and is not claimed.
