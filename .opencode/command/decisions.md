---
description: Decision queue: list/show/resolve/reject/defer dilemma cards. Write actions require explicit user approval.
agent: librarian
---
# Command: /decisions $ARGUMENTS

Manage persistent dilemma cards for permission conflicts, UNROUTABLE routes, acceptance gates, and high-risk decisions.

Storage: `06-Specs/Vault/decision-queue/` (JSON files, append-only).
Vault projection: `06-Specs/Vault/decision-queue-log.md`.

## Subcommands

### `/decisions` or `/decisions list`
List all pending decisions with title, risk, status.

```bash
# Using jq (allowed in librarian/meta/reviewer/verifier)
for f in 06-Specs/Vault/decision-queue/*.json; do
  jq -r '"\(.id) [\(.status)] [\(.risk)] \(.dilemma.title)"' "$f"
done

# Fallback: python3 (if jq unavailable)
for f in 06-Specs/Vault/decision-queue/*.json; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(f\"{d['id']} [{d['status']}] [{d['risk']}] {d['dilemma']['title']}\")" "$f"
done
```

### `/decisions show <id>`
Show full decision card.

```bash
jq . 06-Specs/Vault/decision-queue/<id>.json
# or: python3 -m json.tool 06-Specs/Vault/decision-queue/<id>.json
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

Write to `06-Specs/Vault/decision-queue/YYYY-MM-DD-<slug>.json`.
Append summary to `06-Specs/Vault/decision-queue-log.md`.

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
