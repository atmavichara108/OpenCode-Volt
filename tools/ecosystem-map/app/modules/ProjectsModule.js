/**
 * ProjectsModule — центральная точка «где я сейчас работаю».
 *
 * Показывает все проекты с repo и их живой статус одним батчем
 * (`workspace-status-all`): tmux-сессия и окна, локальные порты с health,
 * Docker-контейнеры (если PIPBOY_DOCKER=1), статус из карточки проекта.
 *
 * Клик по строке → переключить активный проект; кнопка WS → открыть workspace.
 * Строка активного проекта подсвечивается.
 */
import { Module } from "../core/Module.js";

export class ProjectsModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.action("workspace-status-all", {});
    if (!this.data?.ok) {
      this.container.innerHTML = `<div class="eco-head">ПРОЕКТЫ</div>
        <span class="dim">статусы не загружены: ${this.esc(this.data?.error || "")}</span>`;
      this.badge = null;
      return;
    }
    const live = (this.data.projects || []).filter(p => p.tmux_running).length;
    const downPorts = (this.data.projects || [])
      .reduce((n, p) => n + (p.ports || []).filter(x => !x.healthy).length, 0);
    this.badge = live
      ? { n: live, level: downPorts ? "warn" : "leaf",
          text: `живых workspace: ${live}${downPorts ? ` · портов недоступно: ${downPorts}` : ""}` }
      : null;
    this.container.innerHTML = this._render();
    this._wire();
  }

  _portsRow(p) {
    const ports = p.ports || [];
    if (!ports.length) return '<span class="dim pj-none">—</span>';
    return ports.map(x => `<span class="pj-port ${x.healthy ? "up" : "down"}"
      title="${this.esc(x.label || "")} ${x.healthy ? "healthy" : "down"}">:${x.port}</span>`).join("");
  }

  _row(p) {
    if (p.ok === false) {
      return `<div class="proj-row err"><b>${this.esc(p.id)}</b>
        <span class="dim grow">${this.esc(p.error || "")}</span></div>`;
    }
    const active = this.app?.activeProject === p.id;
    const live = p.tmux_running;
    const wins = (p.windows || []).length;
    const docker = p.docker || [];
    const down = (p.ports || []).filter(x => !x.healthy).length;
    return `<div class="proj-row ${active ? "active" : ""}" data-proj="${this.esc(p.id)}">
      <span class="pj-dot ${live ? "up" : "down"}" title="${live ? "tmux " + this.esc(p.session) : "tmux не запущен"}"></span>
      <b>${this.esc(p.id)}</b>
      ${p.status ? `<span class="pj-status">${this.esc(p.status)}</span>` : ""}
      <span class="dim grow">${this.esc((p.kind || "").slice(0, 30))}</span>
      <span class="pj-ports">${this._portsRow(p)}</span>
      <span class="pj-wins" title="окна tmux">${wins ? `${wins}▤` : '<span class="dim">—</span>'}</span>
      <span class="pj-docker" title="docker">${docker.length ? `${docker.length}◫` : (p.docker_enabled ? '<span class="dim">0</span>' : '<span class="dim">off</span>')}</span>
      <button class="pb-mini" data-act="open-ws" data-proj="${this.esc(p.id)}"
        title="открыть workspace ${this.esc(p.id)}">${live ? "⧉" : "▸"}</button>
    </div>`;
  }

  _render() {
    const ps = this.data.projects || [];
    const live = ps.filter(p => p.tmux_running).length;
    const down = ps.reduce((n, p) => n + (p.ports || []).filter(x => !x.healthy).length, 0);
    return `<div class="eco-head">ПРОЕКТЫ · параллельная работа</div>
      <div class="pj-sum dim">
        <span>всего <b>${ps.length}</b></span>
        <span>живых <b class="${live ? "leaf" : ""}">${live}</b></span>
        ${down ? `<span class="warn">портов down <b>${down}</b></span>` : ""}
        <span class="pj-legend">● tmux · :порт · ▤ окна · ◫ docker</span>
      </div>
      <div class="pj-list">${ps.map(p => this._row(p)).join("")}</div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-proj]").forEach(el =>
      el.addEventListener("click", e => {
        if (e.target.dataset.act) return;
        this.app?.setActiveProject(el.dataset.proj);
        this.refresh();
      }));
    this.container.querySelectorAll("[data-act=open-ws]").forEach(b =>
      b.addEventListener("click", async () => {
        const proj = b.dataset.proj;
        b.disabled = true;
        const d = await this.action("workspace-open", { project: proj });
        b.disabled = false;
        this.emit("toast", d.ok ? `tmux ${d.session}` : { text: `✗ ${d.error || ""}`, err: true });
        this.refresh();
      }));
  }
}