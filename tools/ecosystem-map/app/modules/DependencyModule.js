/**
 * DependencyModule — граф зависимостей карточек (кастомный SVG DAG,
 * без внешних библиотек). Показывает:
 *   - слоистую раскладку по lifecycle-рангу (IDEA → LIVE);
 *   - критический путь (карточки, блокирующие больше всего);
 *   - orphan-карточки (нет deps и никто не блокирует);
 *   - карточки без owner;
 *   - циклы (обратные рёбра).
 *
 * Zoom/pan: колесо — зум (к курсору), drag — пан, кнопки + / − / ⟲ сброс.
 */
import { Module } from "../core/Module.js";

const RANK = ["IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED"];
const COLORS = {
  IDEA: "#5a6e62", RESEARCH: "#c084fc", DESIGN: "#a3e635", APPROVED: "#22d3ee",
  BUILD: "#a3e635", REVIEW: "#a3e635", VERIFY: "#22d3ee", LIVE: "#4ade80",
  OBSERVE: "#93a99a", IMPROVE: "#93a99a", RETIRED: "#3a4a40",
};

export class DependencyModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null;
    this._zoom = 1; this._tx = 0; this._ty = 0; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.action("dependencies", {});
    if (!this.data?.ok) {
      this.container.innerHTML = `<span class="dim">граф не загружен: ${this.esc(this.data?.error || "")}</span>`;
      this.badge = null;
      return;
    }
    // бейдж: циклы (красный) → frozen-блоки (янтарный) → нет acceptance (янтарный)
    const cyc = (this.data.cycles || []).length;
    const frozen = new Set((this.data.blocked_by_task || []).flatMap(b => b.cards));
    const na = (this.data.no_acceptance || []).length;
    this.badge = cyc ? { n: cyc, level: "rot", text: `циклов в зависимостях: ${cyc}` }
      : frozen.size ? { n: frozen.size, level: "warn", text: `блокировано frozen-задачами: ${frozen.size}` }
      : na ? { n: na, level: "warn", text: `без acceptance: ${na}` }
      : null;
    this.container.innerHTML = this._render();
    this._draw();
    this._wirePanZoom();
    this._wireAlerts();
  }

  _wireAlerts() {
    this.container.querySelectorAll("[data-cid]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-cid"))));
  }

  _render() {
    const cp = (this.data.critical_path || []).slice(0, 5);
    const orphans = this.data.orphans || [];
    const noOwner = this.data.no_owner || [];
    const noAccept = this.data.no_acceptance || [];
    const cycles = this.data.cycles || [];
    const blockedBy = this.data.blocked_by_task || [];
    const noAcceptIds = new Set(noAccept);
    const cycleIds = new Set(cycles.flat());
    const taskIds = new Set(blockedBy.flatMap(b => b.cards));

    const alerts = [];
    if (cycles.length) alerts.push(`<div class="csect rot">ЦИКЛЫ В ЗАВИСИМОСТЯХ <b>${cycles.length}</b></div>
      <div class="cp-list">${cycles.map(c => `<span class="cp cyc">${c.map(this.esc.bind(this)).join(" → ")}</span>`).join("")}</div>`);
    if (noAccept.length) alerts.push(`<div class="csect">БЕЗ ACCEPTANCE-КРИТЕРИЯ <b>${noAccept.length}</b></div>
      <div class="cp-list">${noAccept.map(id => `<span class="cp na" data-cid="${this.esc(id)}">${this.esc(id)}</span>`).join("")}</div>`);
    if (blockedBy.length) alerts.push(`<div class="csect">БЛОКИРУЮТ ЗАМОРОЖЕННЫЕ ЗАДАЧИ</div>
      <div class="cp-list">${blockedBy.map(b => `<span class="cp bt">${this.esc(b.task)} → ${b.cards.map(c => `<b data-cid="${this.esc(c)}">${this.esc(c)}</b>`).join(" ")}</span>`).join("")}</div>`);

    return `<div class="eco-head">DEPENDENCY GRAPH</div>
      <div class="dep-stats">
        <span class="stat">узлов <b>${(this.data.nodes || []).length}</b></span>
        <span class="stat">рёбер <b>${(this.data.edges || []).length}</b></span>
        <span class="stat warn">orphans <b>${orphans.length}</b></span>
        <span class="stat warn">без owner <b>${noOwner.length}</b></span>
        <span class="stat warn">без acceptance <b>${noAccept.length}</b></span>
        ${cycles.length ? `<span class="stat rot">циклы <b>${cycles.length}</b></span>` : ""}
        ${taskIds.size ? `<span class="stat rot">frozen-блок <b>${taskIds.size}</b></span>` : ""}
      </div>
      ${cp.length ? `<div class="csect">КРИТИЧЕСКИЙ ПУТЬ (кто блокирует больше всего)</div>
      <div class="cp-list">${cp.map(c => `<span class="cp" data-cid="${this.esc(c.id)}">${this.esc(c.id)} <b>×${c.holds}</b></span>`).join("")}</div>` : ""}
      ${alerts.join("")}
      <div class="dep-toolbar">
        <button class="pb-mini" data-z="+">+</button>
        <button class="pb-mini" data-z="-">−</button>
        <button class="pb-mini" data-z="reset">⟲</button>
        <span class="dim mono dep-zoom-label" id="dep-zoom">100%</span>
      </div>
      <div class="dep-svg-wrap" id="dep-wrap"><svg class="dep-svg" id="dep-svg"></svg></div>
      <div class="dep-legend">
        ${RANK.filter(r => COLORS[r]).slice(0, 8).map(r => `<span class="lg"><i style="background:${COLORS[r]}"></i>${r}</span>`).join("")}
        <span class="lg"><i style="background:none;border:1px dashed #f43f5e"></i>нет acceptance</span>
        <span class="lg"><i style="background:none;border:1.5px solid #fbbf24"></i>frozen-блок</span>
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
    const W = Math.max(760, nodes.length * 8);
    const H = 560;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.innerHTML = "";
    const colW = W / Math.max(1, Object.keys(cols).length || 1);
    const pos = {};
    const maxInCol = Math.max(1, ...Object.values(cols).map(a => a.length));
    const rowH = H / Math.max(1, maxInCol + 1);
    const r = Math.min(24, colW / 3);
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
    const noAcceptIds = new Set(this.data.no_acceptance || []);
    const cycleIds = new Set((this.data.cycles || []).flat());
    const taskIds = new Set((this.data.blocked_by_task || []).flatMap(b => b.cards));
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
      // нет acceptance → красный пунктирный ореол
      if (noAcceptIds.has(n.id)) {
        const na = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        na.setAttribute("r", r + 6); na.setAttribute("fill", "none");
        na.setAttribute("stroke", "#f43f5e"); na.setAttribute("stroke-width", 1);
        na.setAttribute("stroke-dasharray", "4 2");
        g.appendChild(na);
      }
      // блокируется замороженной задачей → янтарная рамка
      if (taskIds.has(n.id)) {
        const bt = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        bt.setAttribute("r", r + 3); bt.setAttribute("fill", "none");
        bt.setAttribute("stroke", "#fbbf24"); bt.setAttribute("stroke-width", 1.4);
        g.appendChild(bt);
      }
      // в цикле → фиолетовое кольцо
      if (cycleIds.has(n.id)) {
        const cy = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        cy.setAttribute("r", r + 9); cy.setAttribute("fill", "none");
        cy.setAttribute("stroke", "#c084fc"); cy.setAttribute("stroke-width", 1.2);
        cy.setAttribute("stroke-dasharray", "1 3");
        g.appendChild(cy);
      }
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("dy", "3.5");
      label.setAttribute("font-size", "10");
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
      g.addEventListener("click", () => this.emit("card:click", n.id));
      svg.appendChild(g);
    }
  }

  _applyTransform() {
    const g = this.container?.querySelector("#dep-content");
    const wrap = this.container?.querySelector("#dep-wrap");
    if (g && wrap) {
      g.setAttribute("transform", `translate(${this._tx},${this._ty}) scale(${this._zoom})`);
    }
    const lbl = this.container?.querySelector("#dep-zoom");
    if (lbl) lbl.textContent = Math.round(this._zoom * 100) + "%";
  }

  _wirePanZoom() {
    const wrap = this.container?.querySelector("#dep-wrap");
    const svg = this.container?.querySelector("#dep-svg");
    if (!wrap || !svg) return;
    // обернуть содержимое svg в <g> для трансформации
    const content = document.createElementNS("http://www.w3.org/2000/svg", "g");
    content.setAttribute("id", "dep-content");
    while (svg.firstChild) content.appendChild(svg.firstChild);
    svg.appendChild(content);
    this._applyTransform();

    // zoom buttons
    this.container.querySelectorAll("[data-z]").forEach(b =>
      b.addEventListener("click", () => {
        const z = b.getAttribute("data-z");
        if (z === "+") this._zoom = Math.min(4, this._zoom * 1.25);
        else if (z === "-") this._zoom = Math.max(0.25, this._zoom / 1.25);
        else { this._zoom = 1; this._tx = 0; this._ty = 0; }
        this._applyTransform();
      }));

    // wheel zoom (к курсору)
    wrap.addEventListener("wheel", e => {
      e.preventDefault();
      const rect = wrap.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      const newZoom = Math.min(4, Math.max(0.25, this._zoom * factor));
      // сохраняем точку под курсором
      this._tx = cx - (cx - this._tx) * (newZoom / this._zoom);
      this._ty = cy - (cy - this._ty) * (newZoom / this._zoom);
      this._zoom = newZoom;
      this._applyTransform();
    }, { passive: false });

    // drag pan
    let drag = null;
    wrap.addEventListener("mousedown", e => {
      if (e.target.closest("title")) return;
      drag = { x: e.clientX, y: e.clientY, tx: this._tx, ty: this._ty };
      wrap.style.cursor = "grabbing";
    });
    window.addEventListener("mousemove", e => {
      if (!drag) return;
      this._tx = drag.tx + (e.clientX - drag.x);
      this._ty = drag.ty + (e.clientY - drag.y);
      this._applyTransform();
    });
    window.addEventListener("mouseup", () => {
      if (drag) { drag = null; if (wrap) wrap.style.cursor = "grab"; }
    });
    wrap.style.cursor = "grab";
  }
}