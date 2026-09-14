/**
 * TerminalModule — терминальный тайл проекта (ttyd-интеграция).
 * Пока — iframe-обёртка над ttyd-портом проекта; если ttyd не поднят,
 * показывает честный статус и кнопку запуска через /action.
 */
import { Module } from "../core/Module.js";

export class TerminalModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    const project = this.opts.projectId;
    const st = await this.action("workspace-status", { project });
    const running = st.ok && st.tmux_running;
    this.container.innerHTML = running
      ? `<div class="term-box"><div class="term-note">tmux ${this.esc(st.session)} запущен (окна: ${(st.windows||[]).length})</div>
         <button class="pb-mini" data-act="attach">▸ ATTACH</button></div>`
      : `<div class="term-box"><div class="term-note dim">tmux не запущен для ${this.esc(project)}</div>
         <button class="pb-mini" data-act="open">⚡ START</button></div>`;
    this.container.querySelector("[data-act]")?.addEventListener("click", async () => {
      const d = await this.action("workspace-open", { project });
      this.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
      this.refresh();
    });
  }
}
