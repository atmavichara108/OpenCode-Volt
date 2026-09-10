import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-blockers — что блокирует прогресс (read-only).
 *
 * Возвращает: blocked-карточки с причинами, observer drift_signals,
 * frozen/blocked задачи TASKS.md и какие карточки они держат. No mutation.
 */
export default tool({
  description:
    "Ecosystem blockers: blocked cards (deps/frozen/BLOCKED), drift signals, frozen TASKS holding cards. Read-only, no mutation.",
  args: {},
  async execute(_args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "actions.py")
    const result = await Bun.$`python3 ${script} blockers`.text()
    return result.trim()
  },
})