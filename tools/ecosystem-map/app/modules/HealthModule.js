/**
 * HealthModule — project health radar + layer heatmap (визуальная сводка).
 *
 * Два блока:
 *   1. Radar по проектам: доля карточек в «здоровых» стадиях (LIVE/OBSERVE)
 *      vs «в работе» (BUILD/REVIEW/VERIFY/APPROVED) vs «застой» (IDEA/RESEARCH/DESIGN).
 *   2. Heatmap по слоям L0..L4: распределение карточек по lifecycle.
 *
 * Чисто визуализация snapshot данных (read-only). Клик по проекту → фокус.
 */
import { Module } from "../core/Module.js";

const LC_HEALTHY = ["LIVE", "OBSERVE", "IMPROVE"];
const LC_INFLIGHT = ["BUILD", "REVIEW", "VERIFY", "APPROVED"];
const LC_STALE = ["IDEA", "RESEARCH", "DESIGN"];

const HEAT_COLOR = {
  IDEA: "#3a4a40", RESEARCH: "#c084fc", DESIGN: "#a3e635", APPROVED: "#22d3ee",
  BUILD: "#a3e635", REVIEW: "#a3e635", VERIFY: "#22d3ee",
  LIVE: "#4ade80", OBSERVE: "#93a99a", IMPROVE: "#93a99a", RETIRED: "#20261f",
};

export class HealthModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.registry = await this.fetchJson("registry.json");
    if (!this.registry) { this.container.innerHTML = '<span class="dim">registry не загружен</span>'; return; }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _bucket(lc) {
    if (LC_HEALTHY.includes(lc)) return "healthy";
    if (LC_INFLIGHT.includes(lc)) return "inflight";
    if (LC_STALE.includes(lc)) return "stale";
    return "stale";
  }

  _radarBar(name, healthy, inflight, stale) {
    const total = Math.max(1, healthy + inflight + stale);
    const h = Math.round(healthy / total * 100);
    const inf = Math.round(inflight / total * 100);
    const st = Math.round(stale / total * 100);
    return `<div class="hr-proj" data-proj="${this.esc(name)}">
      <span class="hr-name">${this.esc(name)}</span>
      <div class="hr-bar">
        <div class="hr-seg healthy" style="width:${h}%" title="live/observe ${healthy}"></div>
        <div class="hr-seg inflight" style="width:${inf}%" title="в работе ${inflight}"></div>
        <div class="hr-seg stale" style="width:${st}%" title="застой ${stale}"></div>
      </div>
      <span class="hr-nums mono">${healthy}/${inflight}/${stale}</span>
    </div>`;
  }

  _render() {
    const cards = Object.entries(this.registry.cards || {});
    // project radar
    const proj = {};
    for (const [, c] of cards) {
      if (c.retired) continue;
      const p = c.project || "(global)";
      const lc = c.lifecycle || "IDEA";
      const b = this._bucket(lc);
      proj[p] ||= { healthy: 0, inflight: 0, stale: 0 };
      proj[p][b]++;
    }
    const sorted = Object.entries(proj).sort((a, b) =>
      (b[1].healthy + b[1].inflight) - (a[1].healthy + a[1].inflight));

    // layer heatmap
    const layers = {};
    for (const [, c] of cards) {
      if (c.retired) continue;
      const l = c.layer || "?";
      const lc = c.lifecycle || "IDEA";
      layers[l] ||= {};
      layers[l][lc] = (layers[l][lc] || 0) + 1;
    }
    const LCS = ["LIVE", "VERIFY", "REVIEW", "BUILD", "APPROVED", "DESIGN", "RESEARCH", "IDEA"];
    const layerRows = Object.keys(layers).sort().map(l => {
      const cells = LCS.map(lc => {
        const n = layers[l][lc] || 0;
        const color = HEAT_COLOR[lc] || "#3a4a40";
        const opacity = n ? Math.min(1, 0.15 + n * 0.25) : 0.04;
        return `<div class="hm-cell" style="background:${color};opacity:${opacity}" title="${l} ${lc}: ${n}">${n || ""}</div>`;
      }).join("");
      return `<div class="hm-row"><span class="hm-layer">${this.esc(l)}</span>${cells}</div>`;
    }).join("");

    return `<div class="eco-head">HEALTH · radar + heatmap</div>
      <div class="csect">PROJECT RADAR <span class="dim">live/in-flight/застой</span></div>
      <div class="hr-list">${sorted.map(([n, v]) => this._radarBar(n, v.healthy, v.inflight, v.stale)).join("")}</div>
      <div class="csect">LAYER HEATMAP</div>
      <div class="hm">
        <div class="hm-row hm-head"><span class="hm-layer"></span>${LCS.map(lc => `<span class="hm-lc">${lc}</span>`).join("")}</div>
        ${layerRows}
      </div>
      <div class="dep-legend">
        ${LCS.map(lc => `<span class="lg"><i style="background:${HEAT_COLOR[lc]}"></i>${lc}</span>`).join("")}
      </div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-proj]").forEach(el =>
      el.addEventListener("click", () => {
        const p = el.getAttribute("data-proj");
        if (this.app && p !== "(global)") this.app.setActiveProject(p);
        else this.emit("toast", "глобальные карточки");
      }));
  }
}