/**
 * LauncherModule — workspace launcher per-проект.
 *
 * Кнопки запуска рабочего окружения проекта: tmux-сессия с окнами
 * (main/files/tests/logs/local), Docker-контейнеры, локальные порты.
 */
import { Module } from "../core/Module.js";

export class LauncherModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); }

  async mount(container) {
    super.mount(container);
    this.on("project:change", () => this.refresh());
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    const project = this.opts.projectId;
    const st = await this.action("workspace-status", { project });
    const running = st.ok && st.tmux_running;
    const windows = (st.ok && st.windows) || [];
    const ports = (st.ok && st.ports) || [];
    const docker = (st.ok && st.docker) || [];
    this.container.innerHTML = `
      <div class="eco-head">WORKSPACE · ${this.esc(project)}</div>
      <div class="ws-status ${running ? "up" : ""}">${running ? "● tmux " + this.esc(st.session) : "○ tmux не запущен"}</div>
      ${windows.length ? `<div class="csect">ОКНА</div><div class="ws-wins">${windows.map(w =>
        `<span class="ws-win">${this.esc(w)}</span>`).join("")}</div>` : ""}
      ${ports.length ? `<div class="csect">ПОРТЫ</div>${ports.map(p =>
        `<div class="ws-row"><span class="ws-port ${p.healthy ? "up" : "down"}">:${p.port}</span>
         <span class="dim grow">${this.esc(p.label || "")}</span>
         <span class="ws-health ${p.healthy ? "up" : "down"}">${p.healthy ? "healthy" : "down"}</span></div>`).join("")}` : ""}
      ${docker.length ? `<div class="csect">DOCKER</div>${docker.map(d =>
        `<div class="ws-row"><span class="mono">${this.esc(d)}</span></div>`).join("")}` : ""}
      <div class="launch-actions">
        <button class="pb-mini up" data-act="open">▸ OPEN WORKSPACE</button>
        ${running ? `<button class="pb-mini" data-act="attach">⧉ attach</button>` : ""}
      </div>`;
    this.container.querySelector("[data-act=open]")?.addEventListener("click", async () => {
      const d = await this.action("workspace-open", { project });
      this.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
      this.refresh();
    });
    this.container.querySelector("[data-act=attach]")?.addEventListener("click", async () => {
      const d = await this.action("workspace-open", { project });
      this.emit("toast", d.ok ? "attach " + d.session : "✗ " + (d.error || ""));
    });
  }
}
