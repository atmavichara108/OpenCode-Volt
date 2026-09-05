# Decision Queue Schema

Persistent machine-readable storage for dilemma cards. Located at `06-Specs/Vault/decision-queue/`.

## File format

Each decision is a separate JSON file: `YYYY-MM-DD-<slug>.json`

```json
{
  "id": "2026-09-05-permission-audit",
  "created": "2026-09-05T12:00:00Z",
  "updated": "2026-09-05T12:30:00Z",
  "status": "pending|approved|rejected|deferred|resolved",
  "risk": "low|medium|high|critical",
  "source": {
    "agent": "meta",
    "session": "abc123",
    "trigger": "permission.asked|tool.blocked|unroutable|acceptance.gate|manual"
  },
  "dilemma": {
    "title": "Short human-readable title",
    "context": "One-line context (no secrets, no full prompts)",
    "options": [
      {"id": "A", "label": "Option A", "pros": ["..."], "cons": ["..."]},
      {"id": "B", "label": "Option B", "pros": ["..."], "cons": ["..."]}
    ],
    "recommendation": "A",
    "reason": "Brief rationale (no chain-of-thought)"
  },
  "resolution": {
    "choice": "A|B|deferred|rejected",
    "approved_by": "user|agent:<name>",
    "approved_at": "2026-09-05T13:00:00Z",
    "evidence": "Optional: link to spec/route-log/session-log"
  },
  "stop_condition": "When this decision can be auto-closed (e.g., 'after 7 days', 'after verifier pass')"
}
```

## Constraints

- **No secrets, no full prompts, no application content** — metadata only
- **Append-only** — never delete, only update status/resolution
- **Short reason** — no chain-of-thought capture
- **Bounded** — auto-archive resolved cards older than 30 days to `archive/`

## Vault projection

Readable summary in `06-Specs/Vault/decision-queue-log.md` (append-only).

## Future location [проверить]

`~/.local/state/opencode/decision-queue/` — XDG-compliant user state path. Currently blocked by external_directory permissions. Requires explicit allow in global config.

## [проверить]

- Runtime hook integration (permission.asked, tool blocked, UNROUTABLE) not yet confirmed
- Fallback: manual card creation via `/decisions new` command

## Runtime integration (T-132, 2026-09-05)

**Plugin:** `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/decision-queue-hook.ts`

**Hook:** `permission.ask` `[проверить exact signature]` с graceful fallback на event catch-all.

**Storage:** Append-only JSONL (`runtime-events.jsonl`) в:
- Canonical: `06-Specs/Vault/decision-queue/runtime-events.jsonl` (если path существует)
- Fallback: `.decision-queue/runtime-events.jsonl` (project root)

**Card shape:** см. выше. Все cards создаются со `status: "pending"`, `resolution: null`. User resolves via `/decisions` command.

**Constraints:**
- Metadata-only: no prompt content, no tool output, no secrets
- Append-only: never delete, only append
- No shell/git/network/file edit actions
- No card resolution, no commit/push

**Smoke test:** `06-Specs/Vault/decision-queue-smoke-test.mjs` (25/25 PASS, pure functions, no live runtime required).

**Integration layer:** plugin создаёт JSONL, `/decisions` command ожидает JSON files. Integration layer не реализован (future work). Currently plugin creates runtime log, manual cards created via `/decisions new` remain separate JSON files.
