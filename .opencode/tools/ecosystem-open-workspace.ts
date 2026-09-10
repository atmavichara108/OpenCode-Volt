import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * ecosystem-open-workspace — открыть workspace проекта (tmux-сессия pb-<проект>).
 *
 * Единственный НЕ read-only ecosystem-инструмент: поднимает внешний tmux
 * (не форк OpenCode). Сопроцесс actions.py files/neovim/tests/local-окна.
 * Требует подтверждения пользователя (side-effect вне vault).
 */
export default tool({
  description:
    "Open a project workspace (tmux session pb-<project> with main/files/tests/logs/local, external tmux not OpenCode). Requires user confirmation — has a side effect outside the vault.",
  args: {
    project: tool.schema.string().describe("Project id (e.g. SERPlux, vault)"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools", "ecosystem-map", "actions.py")
    const result = await Bun.$`python3 ${script} workspace-open ${args.project} --no-term`.text()
    return result.trim()
  },
})