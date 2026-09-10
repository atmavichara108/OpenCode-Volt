import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-next — «что можно делать сейчас» (read-only).
 *
 * Возвращает READY / BLOCKED / AWAIT VERIFIER / IN FLIGHT карточки
 * экосистемы по canonical registry + generated snapshot с причиной
 * блокировки (deps/frozen/status_note BLOCKED). No mutation, no network.
 * Семантика — движок nextInfo фронта Pip-Boy, продублированный в Python
 * (tools/ecosystem-map/actions.py do_next).
 */
export default tool({
  description:
    "Ecosystem next actions: READY / BLOCKED / AWAIT VERIFIER / IN FLIGHT card queues with blocking reasons (deps, frozen tasks, BLOCKED status). Read-only, no mutation.",
  args: {
    limit: tool.schema.number().optional().describe("Max cards per queue (default 10)"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "actions.py")
    const limit = args.limit ?? 10
    const result = await Bun.$`python3 ${script} next --limit ${limit}`.text()
    return result.trim()
  },
})