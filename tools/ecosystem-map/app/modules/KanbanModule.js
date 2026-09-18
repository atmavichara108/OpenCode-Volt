/**
 * KanbanModule — control plane: карточки разложены по lifecycle-колонкам
 * (каждая карточка — read-only, клик → card inspector).
 *
 * Заявленный ECO-006 view «KANBAN». Read-only (перенос = proposal, не мутация).
 * Фильтры: project (активный проект наследуется через project:change).
 */
import { Module } from "../core/Module.js";

const COLS = ["IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY", "LIVE", "OBSERVE", "IMPROVE", "RETIRED"];
const COL_COLOR = {
  IDEA: "var(--faint)", RESEARCH: "var(--spore)", DESIGN: "var(--sun)",
  APPROVED: "var(--water)", BUILD: "var(--sun)", REVIEW: "var(--sun)",
  VERIFY: "var(--water)", LIVE: "var(--leaf)", OBSERVE: "var(--dim)",
  IMPROVE: "var(--dim)", RETIRED: "#3a4a40",
};

export class KanbanModule extends Module {
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

  _render() {
    const cards = Object.entries(this.registry.cards || {});
    const byCol = {};
    for (const col of COLS) byCol[col] = [];
    for (const [cid, c] of cards) {
      const lc = c.lifecycle || "IDEA";
      (byCol[lc] ||= []).push([cid, c]);
    }
    const total = cards.filter(([, c]) => !c.retired).length;
    const cols = COLS.filter(col => byCol[col].length).map(col => {
      const items = byCol[col].map(([cid, c]) => `
        <div class="kb-card" data-card="${this.esc(cid)}" title="${this.esc(c.title || "")}">
          <span class="kb-id">${this.esc(cid)}</span>
          <span class="kb-title">${this.esc((c.title || "").slice(0, 42))}</span>
          <span class="kb-meta">${this.esc(c.owner || "—")} · ${this.esc(c.priority || "—")}</span>
        </div>`).join("");
      const dot = `style="--c:${COL_COLOR[col]}"`;
      return `<div class="kb-col">
        <div class="kb-colhead" ${dot}><span>${col}</span><b>${byCol[col].length}</b></div>
        <div class="kb-list">${items || '<span class="dim kb-empty">—</span>'}</div>
      </div>`;
    }).join("");
    return `<div class="eco-head">KANBAN · control plane</div>
      <div class="kb-count dim">карточек <b>${total}</b> · read-only (перенос — proposal)</div>
      <div class="kb-scroll">${cols}</div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-card"))));
  }
}