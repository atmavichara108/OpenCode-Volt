/**
 * MatrixModule — матрица layers L0..L4 × facets × lifecycle (структурализм).
 * Заявленный ECO-006 view «MATRIX». Read-only, клик по ячейке → inspector карточки.
 *
 * Три проекции (кнопки-табы):
 *   layers  — L0..L4 (строки) × lifecycle (колонки), ячейка = список карточек
 *   facets  — 6 facets × lifecycle
 *   owners  — owner × lifecycle
 */
import { Module } from "../core/Module.js";

const COLS = ["IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY", "LIVE"];
const LC_COLOR = {
  IDEA: "#5a6e62", RESEARCH: "#c084fc", DESIGN: "#a3e635", APPROVED: "#22d3ee",
  BUILD: "#a3e635", REVIEW: "#a3e635", VERIFY: "#22d3ee", LIVE: "#4ade80",
};

export class MatrixModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; this._axis = "layers"; }

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

  _cells(groupBy, rows, rowLabel) {
    const cards = Object.entries(this.registry.cards || {});
    const grid = {};
    for (const r of rows) grid[r] = {};
    for (const [cid, c] of cards) {
      if (c.retired) continue;
      let key;
      if (groupBy === "layers") key = c.layer || "?";
      else if (groupBy === "facets") key = (c.facets || [])[0] || "?";
      else key = c.owner || "?";
      const lc = c.lifecycle || "IDEA";
      if (!(key in grid)) grid[key] = {};
      (grid[key][lc] ||= []).push(cid);
    }
    const rowsShown = rows.slice();
    for (const k of Object.keys(grid)) if (!rowsShown.includes(k)) rowsShown.push(k);
    return rowsShown.map(r => {
      const cells = COLS.map(lc => {
        const list = grid[r]?.[lc] || [];
        return `<div class="mx-cell" style="--c:${LC_COLOR[lc] || "#5a6e62"}">
          ${list.length ? `<b>${list.length}</b>` : ""}
          ${list.slice(0, 3).map(id => `<span class="mx-chip" data-card="${this.esc(id)}">${this.esc(id)}</span>`).join("")}
        </div>`;
      }).join("");
      return `<div class="mx-row"><span class="mx-key">${this.esc(rowLabel(r))}</span>${cells}</div>`;
    }).join("");
  }

  _render() {
    const layers = ["L0", "L1", "L2", "L3", "L4"];
    const facets = ["memory", "routing", "telemetry", "verification", "knowledge", "interface"];
    const axis = this._axis;
    const isLayers = axis === "layers";
    const isFacets = axis === "facets";
    const rows = isLayers ? layers : isFacets ? facets : [];
    const body = isLayers ? this._cells("layers", rows, r => r)
      : isFacets ? this._cells("facets", rows, r => r)
      : this._cells("owner", rows, r => r);
    const tabs = [["layers", "LAYERS"], ["facets", "FACETS"], ["owner", "OWNERS"]].map(([k, l]) =>
      `<button class="pb-mini ${axis === k ? "on" : ""}" data-axis="${k}">${l}</button>`).join("");
    return `<div class="eco-head">MATRIX · layers × facets × lifecycle</div>
      <div class="mx-tabs">${tabs}</div>
      <div class="mx-scroll">
        <div class="mx-row mx-head"><span class="mx-key"></span>${COLS.map(lc => `<span class="mx-lch" style="--c:${LC_COLOR[lc]}">${lc}</span>`).join("")}</div>
        ${body}
      </div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-axis]").forEach(b =>
      b.addEventListener("click", () => { this._axis = b.getAttribute("data-axis"); this.refresh(); }));
    this.container.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-card"))));
  }
}