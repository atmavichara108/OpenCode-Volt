/**
 * NextActionModule — view «что можно сделать прямо сейчас».
 *
 * Читает backend do_next() (ready/blocked/verify/in_flight с причинами),
 * группирует по actionable-состоянию, сортирует по приоритету P0→P4.
 * Клик по карточке → inspector; блокированные показывают причину блокировки.
 */
import { Module } from "../core/Module.js";

const PR = { P0: 0, P1: 1, P2: 2, P3: 3, P4: 4 };
const PR_COLOR = { P0: "var(--rot)", P1: "var(--sun)", P2: "var(--water)", P3: "var(--dim)", P4: "var(--faint)" };

const SECTIONS = [
  { key: "ready", title: "READY · сделай сейчас", color: "var(--leaf)" },
  { key: "verify", title: "VERIFY · ждёт проверки", color: "var(--water)" },
  { key: "in_flight", title: "IN FLIGHT · в работе", color: "var(--sun)" },
  { key: "blocked", title: "BLOCKED · чем заблокировано", color: "var(--rot)" },
];

export class NextActionModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.action("next", { limit: 50 });
    if (!this.data?.ok) {
      this.container.innerHTML = `<span class="dim">не загружено: ${this.esc(this.data?.error || "")}</span>`;
      return;
    }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _row(r) {
    const pcol = PR_COLOR[r.priority] || "var(--faint)";
    const owner = r.owner ? `<span class="nx-owner">${this.esc(r.owner)}</span>` : `<span class="nx-owner warn">∅</span>`;
    const project = r.project ? `<span class="nx-proj mono">${this.esc(r.project)}</span>` : "";
    const reasons = (r.reasons || []).length
      ? `<div class="nx-reasons">${r.reasons.map(s => `<span class="nx-reason">${this.esc(s)}</span>`).join("")}</div>` : "";
    return `<div class="nx-row" data-card="${this.esc(r.id)}">
      <span class="nx-p" style="color:${pcol}">${this.esc(r.priority || "P?")}</span>
      <div class="nx-main">
        <div class="nx-idline"><b class="mono">${this.esc(r.id)}</b>
          <span class="nx-title dim">${this.esc(r.title || "")}</span></div>
        <div class="nx-meta">${owner}${project}<span class="nx-lc mono">${this.esc(r.next || "")}</span></div>
        ${reasons}
      </div>
    </div>`;
  }

  _render() {
    const c = this.data.counts || {};
    const byKey = { ready: this.data.ready || [], verify: this.data.verify || [],
                    in_flight: this.data.in_flight || [], blocked: this.data.blocked || [] };
    const body = SECTIONS.map(s => {
      const items = byKey[s.key] || [];
      return `<div class="csect" style="color:${s.color}">${s.title} · ${items.length}</div>` +
        (items.length ? items.map(r => this._row(r)).join("") : '<div class="nx-empty dim">—</div>');
    }).join("");
    return `<div class="eco-head">NEXT ACTION</div>
      <div class="acc-meta">готово к действию <b>${c.ready || 0}</b> · всего actionable <b>${(c.ready||0)+(c.verify||0)+(c.in_flight||0)}</b></div>
      <div class="nx-filter">
        <button class="pb-mini nx-active" data-f="all">все</button>
        <button class="pb-mini" data-f="ready">ready</button>
        <button class="pb-mini" data-f="blocked">blocked</button>
      </div>
      ${body}`;
  }

  _wire() {
    this.container.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-card"))));
    this.container.querySelectorAll("[data-f]").forEach(b =>
      b.addEventListener("click", () => {
        this.container.querySelectorAll("[data-f]").forEach(x => x.classList.remove("nx-active"));
        b.classList.add("nx-active");
        this._applyFilter(b.getAttribute("data-f"));
      }));
  }

  _applyFilter(f) {
    this.container.querySelectorAll(".csect").forEach(sec => {
      const title = (sec.textContent || "").toLowerCase();
      const key = title.includes("ready") ? "ready" : title.includes("verify") ? "verify"
        : title.includes("in flight") ? "in_flight" : "blocked";
      let show = f === "all" ? true : key === f;
      sec.style.display = show ? "" : "none";
      const rows = [];
      let sib = sec.nextElementSibling;
      while (sib && !sib.classList.contains("csect")) { rows.push(sib); sib = sib.nextElementSibling; }
      rows.forEach(r => r.style.display = show ? "" : "none");
    });
  }
}