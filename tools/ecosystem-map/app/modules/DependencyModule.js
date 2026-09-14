/**
 * DependencyModule — граф зависимостей карточек (кастомный SVG DAG,
 * без внешних библиотек). Показывает:
 *   - слоистую раскладку по lifecycle-рангу (IDEA → LIVE);
 *   - критический путь (карточки, блокирующие больше всего);
 *   - orphan-карточки (нет deps и никто не блокирует);
 *   - карточки без owner;
 *   - циклы (обратные рёбра).
 */
import { Module } from "../core/Module.js";

const RANK = ["IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED"];
const COLORS = {
  IDEA: "#5a6e62", RESEARCH: "#c084fc", DESIGN: "#a3e635", APPROVED: "#22d3ee",
  BUILD: "#a3e635", REVIEW: "#a3e635", VERIFY: "#22d3ee", LIVE: "#4ade80",
  OBSERVE: "#93a99a", IMPROVE: "#93a99a", RETIRED: "#3a4a40",
};

export class DependencyModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null; }

  async mount(container) {
    super.mount(container);
    if (!this._wired) {
      this.on("card:click", cid => this._focus(cid));
      this._wired = true;
    }
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.action("dependencies", {});
    if (!this.data?.ok) {
      this.container.innerHTML = `<span class="dim">граф не загружен: ${this.esc(this.data?.error || "")}</span>`;
      return;
    }
    this.container.innerHTML = this._render();
    this._draw();
  }

  _focus(cid) {
    if (!cid || !this.data) return;
    const n = this.data.nodes?.find(n => n.id === cid);
    if (!n) return;
    this.emit("toast", `${cid} — ${n.title || ""} (${n.lifecycle})`);
  }

  _render() {
    const cp = (this.data.critical_path || []).slice(0, 5);
    const orphans = this.data.orphans || [];
    const noOwner = this.data.no_owner || [];
    return `<div class="eco-head">DEPENDENCY GRAPH</div>
      <div class="dep-stats">
        <span class="stat">узлов <b>${(this.data.nodes || []).length}</b></span>
        <span class="stat">рёбер <b>${(this.data.edges || []).length}</b></span>
        <span class="stat warn">orphans <b>${orphans.length}</b></span>
        <span class="stat warn">без owner <b>${noOwner.length}</b></span>
      </div>
      ${cp.length ? `<div class="csect">КРИТИЧЕСКИЙ ПУТЬ (кто блокирует больше всего)</div>
      <div class="cp-list">${cp.map(c => `<span class="cp" data-cid="${this.esc(c.id)}">${this.esc(c.id)} <b>×${c.holds}</b></span>`).join("")}</div>` : ""}
      <div class="dep-svg-wrap"><svg class="dep-svg" id="dep-svg"></svg></div>
      <div class="dep-legend">
        ${RANK.filter(r => COLORS[r]).slice(0, 8).map(r => `<span class="lg"><i style="background:${COLORS[r]}"></i>${r}</span>`).join("")}
      </div>`;
  }

  _draw() {
    const svg = this.container.querySelector("#dep-svg");
    if (!svg) return;
    const nodes = this.data.nodes || [];
    const edges = this.data.edges || [];
    const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
    const rank = id => {
      const i = RANK.indexOf(byId[id]?.lifecycle || "IDEA");
      return i < 0 ? 0 : i;
    };
    // слои по рангу
    const cols = {};
    for (const n of nodes) (cols[rank(n.id)] ||= []).push(n);
    const W = Math.max(720, nodes.length * 8);
    const H = 520;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.innerHTML = "";
    const colW = W / Math.max(1, Object.keys(cols).length || 1);
    const pos = {};
    const maxInCol = Math.max(1, ...Object.values(cols).map(a => a.length));
    const rowH = H / Math.max(1, maxInCol + 1);
    const r = Math.min(22, colW / 3);
    for (const [rankIdx, arr] of Object.entries(cols)) {
      const x = colW * (+rankIdx) + colW / 2;
      arr.forEach((n, i) => {
        const y = rowH * (i + 1);
        pos[n.id] = { x, y };
      });
    }
    // рёбра (обратные = цикл)
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
    marker.setAttribute("id", "dep-arrow");
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "10"); marker.setAttribute("refY", "5");
    marker.setAttribute("markerWidth", "6"); marker.setAttribute("markerHeight", "6");
    marker.setAttribute("orient", "auto");
    const mp = document.createElementNS("http://www.w3.org/2000/svg", "path");
    mp.setAttribute("d", "M0,0L10,5L0,10z"); mp.setAttribute("fill", "#4ade80");
    marker.appendChild(mp); defs.appendChild(marker); svg.appendChild(defs);
    for (const e of edges) {
      const a = pos[e.source], b = pos[e.target];
      if (!a || !b) continue;
      const isBack = rank(e.target) <= rank(e.source);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
      const mx = (a.x + b.x) / 2;
      line.setAttribute("d", `M${a.x},${a.y} C${mx},${a.y} ${mx},${b.y} ${b.x},${b.y}`);
      line.setAttribute("stroke", isBack ? "#f43f5e" : "rgba(74,222,128,.35)");
      line.setAttribute("stroke-width", isBack ? 1.5 : 1);
      line.setAttribute("fill", "none");
      if (!isBack) line.setAttribute("marker-end", "url(#dep-arrow)");
      svg.appendChild(line);
    }
    // узлы
    const cpIds = new Set((this.data.critical_path || []).map(c => c.id));
    const orphanIds = new Set(this.data.orphans || []);
    const noOwnerIds = new Set(this.data.no_owner || []);
    for (const n of nodes) {
      const p = pos[n.id];
      if (!p) continue;
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("transform", `translate(${p.x},${p.y})`);
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("r", r);
      circle.setAttribute("fill", COLORS[n.lifecycle] || "#5a6e62");
      circle.setAttribute("fill-opacity", "0.18");
      circle.setAttribute("stroke", COLORS[n.lifecycle] || "#5a6e62");
      circle.setAttribute("stroke-width", cpIds.has(n.id) ? 2.5 : 1);
      if (noOwnerIds.has(n.id)) circle.setAttribute("stroke-dasharray", "3 2");
      g.appendChild(circle);
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("dy", "3.5");
      label.setAttribute("font-size", "9");
      label.setAttribute("font-family", "JetBrains Mono, monospace");
      label.setAttribute("fill", COLORS[n.lifecycle] || "#e8f2ea");
      label.textContent = n.id;
      g.appendChild(label);
      if (orphanIds.has(n.id)) {
        const o = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        o.setAttribute("r", r + 3); o.setAttribute("fill", "none");
        o.setAttribute("stroke", "#a3e635"); o.setAttribute("stroke-width", 0.8);
        o.setAttribute("stroke-dasharray", "2 2");
        g.appendChild(o);
      }
      const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
      title.textContent = `${n.id} · ${n.title || ""} · ${n.lifecycle}${n.owner ? " · " + n.owner : ""}`;
      g.appendChild(title);
      g.style.cursor = "pointer";
      g.addEventListener("click", () => this._focus(n.id));
      svg.appendChild(g);
    }
  }
}
