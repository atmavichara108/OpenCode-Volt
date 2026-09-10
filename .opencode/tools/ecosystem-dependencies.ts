import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-dependencies — граф зависимостей карточки (read-only).
 *
 * depends_on / blocks / critical path (кто транзитивно держит максимум) /
 * orphan-карточки. No mutation.
 */
export default tool({
  description:
    "Ecosystem dependency graph: depends_on, blocks, critical path (ranked by transitively held cards), orphans. Read-only.",
  args: {
    card: tool.schema.string().optional().describe("Card id (e.g. ECO-006); empty = whole graph"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "actions.py")
    const parts: string[] = [script, "dependencies"]
    if (args.card) parts.push("--card", args.card)
    const result = await Bun.$`python3 ${parts}`.text()
    return result.trim()
  },
})