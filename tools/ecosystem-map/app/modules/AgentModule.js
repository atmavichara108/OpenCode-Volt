/**
 * AgentModule — agent cockpit: кто реально способен выполнить следующий шаг.
 *
 * Совмещает:
 *   registry.cards (workload: сколько активных карточек у owner)
 *   snapshot.agents (роль, статус: confirmed/candidate/frozen)
 *   snapshot.route_log (последние маршруты → доступность)
 *   snapshot.tasks (blocked/frozen задачи по карточкам)
 *
 * Каждая строка агента кликабельна → card inspector для его карточек.
 */
import { Module } from "../core/Module.js";

const STATUS_STYLE = {
  confirmed: { label: "CONFIRMED", color: "var(--leaf)" },
  candidate: { label: "CANDIDATE", color: "var(--sun)" },
  frozen: { label: "FROZEN", color: "var(--rot)" },
};

const ACTIVE_LC = ["RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY"];

export class AgentModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; this.snap = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.snap = await this.fetchJson("generated/snapshot.json");
    this.registry = await this.fetchJson("registry.json");
    if (!this.registry) { this.container.innerHTML = '<span class="dim">registry не загружен</span>'; return; }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _agentWorkload(owner) {
    const cards = Object.entries(this.registry.cards || {});
    const active = [];
    const done = [];
    const blocked = [];
    for (const [cid, c] of cards) {
      if ((c.owner || "") !== owner) continue;
      if (c.retired || c.lifecycle === "RETIRED") continue;
      const lc = c.lifecycle || "IDEA";
      if (ACTIVE_LC.includes(lc)) active.push([cid, c]);
      else if (["LIVE", "OBSERVE", "IMPROVE"].includes(lc)) done.push([cid, c]);
      const reasons = [];
      for (const d of (c.depends_on || [])) {
        const dc = this.registry.cards?.[d];
        const dl = dc?.lifecycle || "IDEA";
        if (["LIVE"].includes(dl)) {} else if (dl !== "LIVE") { /* deps ниже LIVE — возможный блок */ }
      }
      if (/BLOCKED/i.test(c.status_note || "")) blocked.push([cid, c]);
    }
    return { active, done, blocked };
  }

  _agentRow(name, meta) {
    const st = (meta && meta.status) || "candidate";
    const ss = STATUS_STYLE[st] || STATUS_STYLE.candidate;
    const w = this._agentWorkload(name);
    const total = w.active.length + w.done.length;
    return `<div class="agent-row" data-agent="${this.esc(name)}">
      <div class="agent-avatar" style="border-color:${ss.color}">${this.esc(name[0] || "?").toUpperCase()}</div>
      <div class="agent-main">
        <div class="agent-top">
          <b class="agent-name">${this.esc(name)}</b>
          <span class="agent-status" style="color:${ss.color}">${ss.label}</span>
        </div>
        <div class="agent-role dim">${this.esc(meta?.role || "")}</div>
        <div class="agent-cards">
          <span class="chip" title="активных">▸ ${w.active.length}</span>
          <span class="chip dim" title="done/live">✓ ${w.done.length}</span>
          ${w.blocked.length ? `<span class="chip rot">⛔ ${w.blocked.length}</span>` : ""}
        </div>
      </div>
    </div>`;
  }

  _render() {
    const agents = this.snap?.agents || {};
    const names = Object.keys(agents).sort((a, b) => this._agentWorkload(b).active.length - this._agentWorkload(a).active.length);
    const confirmed = names.filter(n => agents[n]?.status === "confirmed").length;
    const frozen = names.filter(n => agents[n]?.status === "frozen").length;
    const routes = this.snap?.route_log || [];
    const routed = routes.filter(r => r.status === "ROUTED").length;
    const unroutable = routes.filter(r => /UNROUTABLE|blocked|failed/i.test(r.status || "")).length;
    return `<div class="eco-head">AGENT COCKPIT</div>
      <div class="acc-meta">агентов ${names.length} · confirmed ${confirmed} · frozen ${frozen} · в полёте ${names.filter(n => this._agentWorkload(n).active.length).length}</div>
      ${names.map(n => this._agentRow(n, agents[n])).join("")}
      <div class="csect">МАРШРУТЫ · route_log</div>
      <div class="agent-routes">
        <span class="chip">ROUTED ${routed}</span>
        ${unroutable ? `<span class="chip rot">UNROUTABLE ${unroutable}</span>` : ""}
      </div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-agent]").forEach(el =>
      el.addEventListener("click", async () => {
        const agent = el.getAttribute("data-agent");
        const w = this._agentWorkload(agent);
        const cid = w.active[0]?.[0];
        if (cid) this.emit("card:click", cid);
        else this.emit("toast", `${agent}: нет активных карточек`);
      }));
  }
}