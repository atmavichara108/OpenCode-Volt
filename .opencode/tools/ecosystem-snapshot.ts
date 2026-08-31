import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-snapshot — read-only local endpoint (preferred path vs MCP).
 *
 * Запускает детерминированный read-only observer
 * (tools/ecosystem-map/observer.py --dry-run) и возвращает
 * machine-readable JSON снимок состояния экосистемы:
 * projects / tasks / route_log / registry_cards / drift_signals.
 *
 * Гарантии: no network, no mutation (dry-run), no secrets.
 * Контракт: 06-Specs/Vault/mcp-readonly.md (§5), 06-Specs/Vault/ecosystem-registry.md (§6).
 * Runtime loading в OpenCode [проверить] — live smoke не выполнялся (2026-08-31).
 */
export default tool({
  description:
    "Read-only deterministic ecosystem state snapshot (projects, tasks, route log, registry cards, drift signals). No network, no mutation. Source of truth remains registry.json + vault cards.",
  args: {},
  async execute(_args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "observer.py")
    const result = await Bun.$`python3 ${script} --dry-run`.text()
    return result.trim()
  },
})
