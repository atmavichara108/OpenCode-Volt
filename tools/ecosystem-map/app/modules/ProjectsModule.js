/**
 * ProjectsModule — переключение проектов + пер-проектные под-модули
 * (docker, порты, статус). Центральная точка «где я сейчас работаю».
 */
import { Module } from "../core/Module.js";

export class ProjectsModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.snap = null; }

  async mount(container) {
    super.mount(container);
    if (!this._wired) {
      this.on("project:change", () => this.refresh());
      this._wired = true;
    }
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.snap = await this.fetchJson("generated/snapshot.json");
    const projects = (this.snap?.projects || []).filter(p => p.repo);
    this.container.innerHTML = `<div class="eco-head">ПРОЕКТЫ · параллельная работа</div>
      ${projects.map(p => `
        <div class="proj-row" data-proj="${this.esc(p.id)}">
          <b>${this.esc(p.id)}</b>
          <span class="dim grow">${this.esc((p.kind || "").slice(0, 26))}</span>
          <button class="pb-mini" data-act="open-ws" data-proj="${this.esc(p.id)}">WS</button>
        </div>`).join("")}`;
    this.container.querySelectorAll("[data-proj]").forEach(el =>
      el.addEventListener("click", e => {
        if (e.target.dataset.act) return;
        this.app.setActiveProject(el.dataset.proj);
      }));
    this.container.querySelectorAll("[data-act=open-ws]").forEach(b =>
      b.addEventListener("click", async () => {
        const d = await this.action("workspace-open", { project: b.dataset.proj });
        this.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
      }));
  }
}
