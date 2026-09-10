import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-summary — сводка состояния экосистемы (read-only).
 *
 * Объединяет readiness-сводку (actions.py next) и git HEAD/drift из
 * canonical registry + generated snapshot. «Одна строка» для быстрого
 * контекста без раскрытия всех views. No mutation.
 */
export default tool({
  description:
    "Ecosystem summary: readiness totals (ready/blocked/verify/in-flight), snapshot git HEAD, drift signals. Read-only, one-shot overview.",
  args: {},
  async execute(_args, context) {
    const dir = path.join(context.worktree, "tools", "ecosystem-map")
    const next = JSON.parse(await Bun.$`python3 ${dir}/actions.py next --limit 1`.text())
    const observer = JSON.parse(await Bun.$`python3 ${dir}/observer.py --dry-run`.text())
    return JSON.stringify({
      ok: true,
      readiness: next.counts,
      vault_head: observer.meta?.vault_head ? observer.meta.vault_head.slice(0, 7) : "—",
      drift_signals: (observer.drift_signals || []).length,
    }, null, 2)
  },
})