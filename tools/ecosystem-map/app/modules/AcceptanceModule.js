/**
 * AcceptanceModule — acceptance dashboard: каждая карточка по стадиям
 * RESEARCH → DESIGN → BUILD → REVIEW → VERIFY → LIVE.
 *
 * Для каждой карточки: owner, review-вердикт, acceptance-критерий,
 * evidence-ссылки (artifacts), rollback, residuals (status_note),
 * и что запрещает переход в LIVE.
 */
import { Module } from "../core/Module.js";

const STAGES = ["IDEA", "RESEARCH", "DESIGN", "APPROVED", "BUILD", "REVIEW", "VERIFY", "LIVE"];
const STAGE_COLOR = {
  IDEA: "var(--faint)", RESEARCH: "var(--spore)", DESIGN: "var(--sun)",
  APPROVED: "var(--water)", BUILD: "var(--sun)", REVIEW: "var(--sun)",
  VERIFY: "var(--water)", LIVE: "var(--leaf)",
};

export class AcceptanceModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; this.snap = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.registry = await this.fetchJson("registry.json");
    this.snap = await this.fetchJson("generated/snapshot.json");
    if (!this.registry) { this.container.innerHTML = '<span class="dim">registry не загружен</span>'; return; }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _liveBlockers(c) {
    const bad = [];
    if (!c.depends_on || !c.depends_on.length) return bad;
    for (const d of c.depends_on) {
      const dep = this.registry.cards?.[d];
      const stage = dep?.lifecycle || "IDEA";
      const liveRank = STAGES.indexOf("LIVE");
      const depRank = STAGES.indexOf(stage);
      // OBSERVE/IMPROVE/RETIRED не в STAGES → indexOf -1 → не блокируют LIVE
      if (depRank >= 0 && depRank < liveRank) bad.push(`${d} (${stage})`);
    }
    return bad;
  }

  _card(cid, c) {
    const lc = c.lifecycle || "IDEA";
    const color = STAGE_COLOR[lc] || "var(--dim)";
    const blockers = this._liveBlockers(c);
    const evidence = (c.artifacts || []).map(a => `<a class="ev" data-link="${this.esc(a)}">${this.esc(a.split("/").pop())}</a>`).join(" ");
    return `<div class="acc-card" data-card="${this.esc(cid)}">
      <div class="acc-head">
        <b class="acc-id">${this.esc(cid)}</b>
        <span class="acc-stage" style="color:${color}">${this.esc(lc)}</span>
        <span class="dim grow">${this.esc(c.title || "")}</span>
        ${c.owner ? `<span class="acc-owner">${this.esc(c.owner)}</span>` : '<span class="acc-owner warn">no owner</span>'}
      </div>
      <div class="acc-body">
        ${c.acceptance ? `<div class="acc-line"><span class="lbl">ACCEPT</span> ${this.esc(c.acceptance)}</div>` : ""}
        ${c.review ? `<div class="acc-line"><span class="lbl">REVIEW</span> ${this.esc(c.review)}</div>` : ""}
        ${c.rollback ? `<div class="acc-line"><span class="lbl">ROLLBACK</span> ${this.esc(c.rollback)}</div>` : ""}
        ${blockers.length ? `<div class="acc-line"><span class="lbl rot">BLOCKS LIVE</span> ${blockers.map(this.esc, this).join(", ")}</div>` : ""}
        ${evidence ? `<div class="acc-line"><span class="lbl">EVIDENCE</span> ${evidence}</div>` : ""}
      </div>
    </div>`;
  }

  _render() {
    const cards = Object.entries(this.registry.cards || {});
    const byStage = {};
    for (const [cid, c] of cards) {
      const s = c.lifecycle || "IDEA";
      (byStage[s] ||= []).push([cid, c]);
    }
    const order = STAGES.filter(s => byStage[s]).concat(
      Object.keys(byStage).filter(s => !STAGES.includes(s)));
    return `<div class="eco-head">ACCEPTANCE DASHBOARD</div>
      <div class="acc-meta">карточек: ${cards.length} · в LIVE: ${(byStage.LIVE || []).length}</div>
      ${order.map(stage => `
        <div class="csect"><span style="color:${STAGE_COLOR[stage] || "var(--dim)"}">${stage}</span> · ${byStage[stage].length}</div>
        ${byStage[stage].map(([cid, c]) => this._card(cid, c)).join("")}
      `).join("")}`;
  }

  _wire() {
    this.container.querySelectorAll("[data-link]").forEach(a =>
      a.addEventListener("click", () => {
        const target = a.getAttribute("data-link");
        this.emit("link:resolve", target);
      }));
  }
}
