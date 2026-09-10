import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-query — текстовый поиск по карточкам экосистемы (read-only).
 *
 * По id/title/owner/lifecycle/layer/facet/priority/status_note.
 * Фильтры: --q (поиск), --facet, --project. No mutation.
 */
export default tool({
  description:
    "Search ecosystem registry cards by text query, facet, or project. Read-only, deterministic.",
  args: {
    q: tool.schema.string().optional().describe("Text query (card id/title/owner/note)"),
    facet: tool.schema.string().optional().describe("Filter by facet (memory/routing/...)"),
    project: tool.schema.string().optional().describe("Filter by project id (vault/SERPlux/...)"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "actions.py")
    const parts: string[] = [script, "query"]
    if (args.q) parts.push("--q", args.q)
    if (args.facet) parts.push("--facet", args.facet)
    if (args.project) parts.push("--project", args.project)
    const result = await Bun.$`python3 ${parts}`.text()
    return result.trim()
  },
})