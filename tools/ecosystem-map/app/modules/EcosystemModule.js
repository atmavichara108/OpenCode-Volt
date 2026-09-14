/**
 * EcosystemModule — экосистема проекта: READY-очередь, blocked, deps.
 * Read-only проекция registry+snapshot (как v4–v7, но модулем).
 */
import { Module } from "../core/Module.js";

const LC = ["IDEA","RESEARCH","DESIGN","APPROVED","BUILD","REVIEW","VERIFY","LIVE","OBSERVE","IMPROVE","RETIRED"];

export class EcosystemModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; this.snapshot = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.registry = await this.fetchJson("registry.json");
    this.snapshot = await this.fetchJson("generated/snapshot.json");
    if (!this.registry) { this.container.innerHTML = '<span class="dim">registry не загружен</span>'; return; }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _nextInfo(cid, c) {
    if (c.retired || c.lifecycle === "RETIRED") return { state: "done", reasons: [] };
    const need = c.lifecycle === "IDEA" || c.lifecycle === "RESEARCH" ? 0
      : c.lifecycle === "DESIGN" ? LC.indexOf("DESIGN") : LC.indexOf("APPROVED");
    const bad = [];
    for (const d of (c.depends_on || [])) {
      const dc = this.registry.cards[d];
      if (!dc) { bad.push(d + " (нет)"); continue; }
      if (dc.retired || dc.lifecycle === "RETIRED") { bad.push(d + " (RETIRED)"); continue; }
      if (LC.indexOf(dc.lifecycle) < need) bad.push(d + " (" + dc.lifecycle + ")");
    }
    const bl = new Set(this.snapshot?.tasks?.Blocked || []);
    const reasons = bad.length ? ["deps: " + bad.join(", ")] : [];
    (c.tasks || []).filter(t => bl.has(t)).forEach(t => reasons.push("frozen: " + t));
    if (/BLOCKED/i.test(c.status_note || "")) reasons.push("BLOCKED");
    let state;
    if (["LIVE","OBSERVE","IMPROVE"].includes(c.lifecycle)) state = "done";
    else if (c.lifecycle === "VERIFY") state = reasons.length ? "blocked" : "verify";
    else if (["BUILD","REVIEW"].includes(c.lifecycle)) state = reasons.length ? "blocked" : "flight";
    else state = reasons.length ? "blocked" : "ready";
    return { state, reasons };
  }

  _render() {
    const project = this.opts.projectId;
    const cards = Object.entries(this.registry.cards || {})
      .filter(([ ,c]) => project === "—" ? true : (c.project || "—") === project)
      .filter(([ ,c]) => !(c.retired || c.lifecycle === "RETIRED"));
    const ready = cards.filter(([cid,c]) => this._nextInfo(cid,c).state === "ready")
      .sort((a,b) => (a[1].priority||"P9") < (b[1].priority||"P9") ? -1 : 1).slice(0, 6);
    const blocked = cards.filter(([cid,c]) => this._nextInfo(cid,c).state === "blocked").slice(0, 3);
    const col = s => ({ ready: "var(--leaf)", verify: "var(--water)", flight: "var(--sun)", blocked: "var(--rot)", done: "var(--faint)" }[s] || "var(--faint)");
    const row = ([cid, c]) => {
      const ni = this._nextInfo(cid, c);
      return `<div class="eco-row" data-card="${this.esc(cid)}" style="border-left:2px solid ${col(ni.state)}">
        <b class="mono">${this.esc(cid)}</b><span class="grow">${this.esc(c.title)}</span>
        <i class="st" style="color:${col(ni.state)}">${ni.state.toUpperCase()}</i></div>`;
    };
    return `<div class="eco-head">${this.esc(project)} · экосистема</div>
      <div class="csect">READY (${ready.length})</div>${ready.map(row).join("") || '<span class="dim">—</span>'}
      <div class="csect">BLOCKED</div>${blocked.map(row).join("") || '<span class="dim">— чисто —</span>'}`;
  }

  _wire() {
    this.container.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-card"))));
  }
}
