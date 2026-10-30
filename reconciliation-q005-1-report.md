# Q-005.1 — Reconciliation Report: providers.json ↔ model-catalog.json ↔ opencode.jsonc

**Generated:** 2026-10-23  
**Session:** ses_e9884e4aeffe7okjn4f7RtavmG (UAS session- bearer)  
**Owner:** sysop (primary УАС)  
**Related Kвест:** Q-005 (6 подквестов)  
**Status:** ✅ Complete  

---

## 1. Sources Compared

| Source | File | Providers Count | Status |
|---|---|---|---|
| `providers.json` | `/home/rudra/Projects/OpenCode-Vault/tools/key-rotator/providers.json` | **22** | Live catalog of all known providers |
| `model-catalog.json` | `/home/rudra/Projects/OpenCode-Vault/control-plane/model-catalog.json` | **9** | Curated catalog with model listings per provider |
| `opencode.jsonc` | `/home/rudra/dotfiles/opencode-global/.config/opencode/opencode.jsonc` | **1 active model** | Current OpenCode runtime configuration |

---

## 2. Discrepancies

### A. Providers in `providers.json` but NOT in `model-catalog.json` (15)

These providers exist in the full registry but are not yet catalogued with model details:

- `agentrouter`
- `ai-furry-vg`
- `ai-hdd-sb`
- `deepseek-bloodthemes`
- `eirouter`
- `freeai-railway`
- `google`
- `htai91`
- `linaliapi`
- `mistral`
- `nova-vcrauo`
- `openrouter`
- `tabitoken`
- `tokenbom`
- `tokenin-my-id`

**Action:** Either add model details to `model-catalog.json` for these, or mark them as `SKIPPED` if intentionally excluded.

---

### B. Providers in `model-catalog.json` but NOT in `providers.json` (2)

These are catalogue entries without a registered provider slot:

- `local-deepseek`
- `modelhub`

**Action:** Either add to `providers.json` or remove from `model-catalog.json` if obsolete.

---

### C. Common Providers (7 — overlap)

These are properly registered in both catalogs:

- `amd-radeon`
- `anymodel`
- `apinex`
- `justwoker`
- `opencode`
- `opencode-go`
- `vercel`

---

### D. Current Model Coverage

- **Current model in opencode.jsonc:** `opencode-go/glm-5.3-flash`
- **Provider `opencode-go`**: ✅ Present in both `providers.json` and `model-catalog.json`
- **Model availability**: The model is tracked and operational

---

## 3. Summary Statistics

- Total unique providers across both catalogs: **24** (22 + 9 - 7 overlap)
- Coverage gap: **17 providers** need attention (15 missing from catalog + 2 catalog-only)
- Current runtime model: **fully covered** (opencode-go/glm-5.3-flash)

---

## 4. Recommendations (for Q-005 continuation)

1. **Decide on 15 "extra" providers** in `providers.json` — either add model entries or remove/archived them.
2. **Handle 2 catalog-only providers** (`local-deepseek`, `modelhub`) — verify if they should be in the provider registry.
3. **Update `model-catalog.json`** to include all 22 providers from `providers.json` for a single source of truth (SSOT).
4. **Run probe checks** on the 2 gap providers to determine their status (ACTIVE/DEGRADED/BLOCKED/SKIPPED).
5. **Update telemetry** `provider-health.jsonl` with reconciliation events.

---

## 5. Report Recipients

- **Central Node (ЦУ):** `ses_eceb23a71ffeJO9QnFou8VngZC`
- **UAS Special Rotator Department:** Card `03-Projects/uas-special-rotator.md`
- **Peer-comms channel:** For delivery via standard handshake protocol

---

*This report is append-only record in the UAS infrastructure. Next step: Q-005 block execution per DoD point 1 (SSOT alignment).*