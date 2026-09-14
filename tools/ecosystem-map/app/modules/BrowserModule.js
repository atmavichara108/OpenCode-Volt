/**
 * BrowserModule — встроенный браузер проекта.
 * Показывает live-превью сервисов проекта (localhost-порты) в iframe.
 * Честный статус: если сервис не отвечает — placeholder с портами.
 */
import { Module } from "../core/Module.js";

const PROJECT_PORTS = {
  SERPlux: [{ port: 8000, label: "API" }, { port: 5173, label: "preview" }],
  vault: [{ port: 8123, label: "pip-boy" }],
};

export class BrowserModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.port = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    const project = this.opts.projectId;
    const ports = PROJECT_PORTS[project] || [];
    if (!ports.length) {
      this.container.innerHTML = `<div class="term-note dim">нет известных портов для ${this.esc(project)}</div>`;
      return;
    }
    const st = await this.action("workspace-status", { project });
    const health = Object.fromEntries((st.ok && st.ports || []).map(p => [p.port, p.healthy]));
    this.container.innerHTML = `<div class="browser-bar">${ports.map(p =>
      `<button class="pb-mini ${health[p.port] ? "up" : ""}" data-port="${p.port}">${this.esc(p.label)} :${p.port}${health[p.port] ? " ↑" : " ↓"}</button>`).join("")}</div>
      <div class="browser-frame" id="bframe"></div>`;
    this.frame = this.container.querySelector("#bframe");
    this.container.querySelectorAll("[data-port]").forEach(b =>
      b.addEventListener("click", () => this._openPort(+b.dataset.port)));
    const firstUp = ports.find(p => health[p.port]);
    if (firstUp) this._openPort(firstUp.port);
  }

  _openPort(port) {
    if (!this.frame) return;
    this.frame.innerHTML = `<iframe src="http://127.0.0.1:${port}/" style="width:100%;height:100%;border:0;border-radius:8px"></iframe>`;
  }
}
