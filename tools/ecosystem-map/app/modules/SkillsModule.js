/**
 * SkillsModule — граф навыков из data.json (prereqs → unlocks), T-069.
 * Заявленный ECO-006 view «SKILLS». Статичный источник (data.json, generated 2026-07-13).
 *
 * Слоистая раскладка по рангу (число prereqs в глубину). Свайпать не нужно —
 * компактная SVG с зумом/паном, как dependency graph. Клик по узлу → panel
 * с описанием навыка, prereqs и unlocks.
 */
import { Module } from "../core/Module.js";

export class SkillsModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null;
    this._zoom = 1; this._tx = 0; this._ty = 0; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.fetchJson("data.json");
    if (!this.data?.skills) { this.container.innerHTML = '<span class="dim">data.json не загружен</span>'; return; }
    this.container.innerHTML = this._render();
    this._draw();
  }

  _nodes() {
    const skills = this.data.skills || {};
    const ids = Object.keys(skills);
    const rank = {};
    const dep = {};
    for (const id of ids) dep[id] = skills[id].prereqs || [];
    // глубина = длина самого длинного пути prereqs (без циклов)
    const memo = {};
    const depth = (id, stack) => {
      if (id in memo) return memo[id];
      if (stack.has(id)) return 0;
      stack.add(id);
      let d = 0;
      for (const p of dep[id] || []) d = Math.max(d, 1 + depth(p, stack));
      stack.delete(id);
      memo[id] = d;
      return d;
    };
    for (const id of ids) rank[id] = depth(id, new Set());
    return { ids, skills, rank, dep };
  }

  _render() {
    const { ids, skills } = this._nodes();
    const done = ids.filter(id => (skills[id].quests || []).every(q => q.done)).length;
    const sources = new Set(ids.flatMap(id => (skills[id].unlocks || []).filter(u => !skills[u])));
    return `<div class="eco-head">SKILLS · граф навыков <span class="dim">data.json · T-069</span></div>
      <div class="dep-stats">
        <span class="stat">навыков <b>${ids.length}</b></span>
        <span class="stat">пройдено <b>${done}</b></span>
        <span class="stat warn">отсутствуют в дереве <b>${sources.size}</b></span>
      </div>
      <div class="dep-toolbar">
        <button class="pb-mini" data-z="+">+</button>
        <button class="pb-mini" data-z="-">−</button>
        <button class="pb-mini" data-z="reset">⟲</button>
        <span class="dim mono dep-zoom-label" id="sk-zoom">100%</span>
      </div>
      <div class="dep-svg-wrap" id="sk-wrap"><svg class="dep-svg" id="sk-svg"></svg></div>
      <div class="skill-panel" id="sk-panel"></div>`;
  }

  _draw() {
    const svg = this.container.querySelector("#sk-svg");
    if (!svg) return;
    const { ids, skills, rank, dep } = this._nodes();
    const cols = {};
    for (const id of ids) (cols[rank[id]] ||= []).push(id);
    const W = Math.max(760, ids.length * 26);
    const H = 500;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.innerHTML = "";
    const colW = W / Math.max(1, Object.keys(cols).length);
    const maxInCol = Math.max(1, ...Object.values(cols).map(a => a.length));
    const rowH = H / Math.max(1, maxInCol + 1);
    const r = 22;
    const pos = {};
    for (const [rk, arr] of Object.entries(cols)) {
      const x = colW * (+rk) + colW / 2;
      arr.forEach((n, i) => { pos[n] = { x, y: rowH * (i + 1) }; });
    }
    // рёбра
    for (const id of ids) {
      for (const p of dep[id] || []) {
        if (!pos[id] || !pos[p]) continue;
        const a = pos[p], b = pos[id];
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
        line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
        line.setAttribute("stroke", "rgba(74,222,128,.28)");
        line.setAttribute("stroke-width", 1);
        svg.appendChild(line);
      }
    }
    // узлы
    for (const id of ids) {
      const p = pos[id];
      const sk = skills[id];
      const allDone = (sk.quests || []).every(q => q.done);
      const partial = !allDone && (sk.quests || []).some(q => q.done);
      const color = allDone ? "#4ade80" : partial ? "#a3e635" : "#5a6e62";
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("transform", `translate(${p.x},${p.y})`);
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("r", r);
      c.setAttribute("fill", color);
      c.setAttribute("fill-opacity", "0.18");
      c.setAttribute("stroke", color);
      c.setAttribute("stroke-width", allDone ? 1.6 : 1);
      g.appendChild(c);
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("dy", "3.5");
      label.setAttribute("font-size", "9");
      label.setAttribute("font-family", "JetBrains Mono, monospace");
      label.setAttribute("fill", color);
      label.textContent = id;
      g.appendChild(label);
      g.style.cursor = "pointer";
      g.addEventListener("click", () => this._showPanel(id, sk));
      svg.appendChild(g);
    }
    this._wireZoom();
  }

  _showPanel(id, sk) {
    const panel = this.container.querySelector("#sk-panel");
    if (!panel) return;
    const done = (sk.quests || []).filter(q => q.done).length;
    panel.innerHTML = `<div class="skill-title">${this.esc(sk.name || id)} <span class="dim">${sk.icon || ""}</span></div>
      <div class="dim">${this.esc(sk.desc || "")}</div>
      <div class="skill-meta">quests <b>${done}/${(sk.quests || []).length}</b> · unlocked ${Array.isArray(sk.unlocks) && sk.unlocks.length ? "yes" : "no"}</div>
      <div class="skill-row">prereqs: ${(sk.prereqs || []).map(p => `<code>${this.esc(p)}</code>`).join(" ") || "—"}</div>
      <div class="skill-row">unlocks: ${(sk.unlocks || []).map(u => `<code>${this.esc(u)}</code>`).join(" ") || "—"}</div>
      <div class="skill-quests">${(sk.quests || []).map(q => `<div class="sq ${q.done ? "ok" : ""}">${q.done ? "✓" : "○"} ${this.esc(q.title)} <span class="dim">${this.esc(q.reward || "")}</span></div>`).join("") || '<span class="dim">нет квестов</span>'}</div>`;
  }

  _wireZoom() {
    const wrap = this.container.querySelector("#sk-wrap");
    const svg = this.container.querySelector("#sk-svg");
    if (!wrap || !svg) return;
    const content = document.createElementNS("http://www.w3.org/2000/svg", "g");
    content.setAttribute("id", "sk-content");
    while (svg.firstChild) content.appendChild(svg.firstChild);
    svg.appendChild(content);
    const apply = () => {
      content.setAttribute("transform", `translate(${this._tx},${this._ty}) scale(${this._zoom})`);
      const lbl = this.container.querySelector("#sk-zoom");
      if (lbl) lbl.textContent = Math.round(this._zoom * 100) + "%";
    };
    apply();
    this.container.querySelectorAll("[data-z]").forEach(b =>
      b.addEventListener("click", () => {
        const z = b.getAttribute("data-z");
        if (z === "+") this._zoom = Math.min(4, this._zoom * 1.25);
        else if (z === "-") this._zoom = Math.max(0.25, this._zoom / 1.25);
        else { this._zoom = 1; this._tx = 0; this._ty = 0; }
        apply();
      }));
    wrap.addEventListener("wheel", e => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      this._zoom = Math.min(4, Math.max(0.25, this._zoom * factor));
      apply();
    }, { passive: false });
  }
}