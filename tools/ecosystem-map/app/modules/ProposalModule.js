/**
 * ProposalModule — очередь предложений (алгоритмический ecosystem observer).
 *
 * Показывает предложения и (для transition) явную кнопку [APPROVE], которая
 * применяет переход через /action apply. Ничего не применяется молча:
 * каждое действие — клик пользователя.
 */
import { Module } from "../core/Module.js";

const ICONS = { transition: "→", blocked: "⛔", no_owner: "∅", drift: "⚠" };
const COLORS = { transition: "var(--leaf)", blocked: "var(--rot)", no_owner: "var(--sun)", drift: "var(--water)" };

export class ProposalModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.data = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.data = await this.action("proposals", {});
    if (!this.data?.ok) {
      this.container.innerHTML = `<span class="dim">предложения не загружены: ${this.esc(this.data?.error || "")}</span>`;
      return;
    }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _render() {
    const ps = this.data.proposals || [];
    const c = this.data.counts || {};
    const groups = ["transition", "blocked", "no_owner", "drift"];
    const body = groups.map(g => {
      const items = ps.filter(p => p.type === g);
      if (!items.length) return "";
      const head = { transition: "ПЕРЕХОДЫ", blocked: "ЗАБЛОКИРОВАНО", no_owner: "БЕЗ OWNER", drift: "DRIFT" }[g];
      return `<div class="csect" style="color:${COLORS[g]}">${head} · ${items.length}</div>` +
        items.map(p => this._row(p)).join("");
    }).join("");
    return `<div class="eco-head">PROPOSAL QUEUE</div>
      <div class="acc-meta">всего ${ps.length} · переходы ${c.transition || 0} · blocked ${c.blocked || 0} · drift ${c.drift || 0}</div>
      ${body || '<span class="dim">— чисто —</span>'}`;
  }

  _row(p) {
    const icon = ICONS[p.type] || "•";
    const color = COLORS[p.type] || "var(--dim)";
    if (p.type === "transition") {
      return `<div class="prop-row" data-card="${this.esc(p.card)}">
        <i style="color:${color}">${icon}</i>
        <span class="prop-text">${this.esc(p.card)} <span class="dim">${this.esc(p.title)}</span>
          <span class="prop-move">${this.esc(p.from)} → <b>${this.esc(p.to)}</b></span></span>
        <button class="pb-mini up" data-approve="${this.esc(p.card)}" data-to="${this.esc(p.to)}">APPROVE</button>
        ${p.project ? `<button class="pb-mini" data-run="${this.esc(p.project)}" title="открыть workspace ${this.esc(p.project)}">RUN</button>` : ""}
      </div>`;
    }
    if (p.type === "blocked") {
      return `<div class="prop-row" data-card="${this.esc(p.card)}">
        <i style="color:${color}">${icon}</i>
        <span class="prop-text">${this.esc(p.card)} <span class="dim">${this.esc(p.title)}</span>
          <span class="prop-move rot">${this.esc((p.reasons || []).join(", "))}</span></span>
        <button class="pb-mini" data-review="${this.esc(p.card)}" title="открыть карточку">REVIEW</button>
      </div>`;
    }
    if (p.type === "no_owner") {
      return `<div class="prop-row" data-card="${this.esc(p.card)}">
        <i style="color:${color}">${icon}</i>
        <span class="prop-text">${this.esc(p.card)} <span class="dim">${this.esc(p.title)}</span>
          <span class="prop-move">назначь owner</span></span>
        <button class="pb-mini" data-review="${this.esc(p.card)}">REVIEW</button>
      </div>`;
    }
    // drift
    return `<div class="prop-row" data-review="${this.esc(p.subject || '')}">
      <i style="color:${color}">${icon}</i>
      <span class="prop-text">${this.esc(p.subject || p.kind)} <span class="dim">${this.esc(p.detail || "")}</span></span>
    </div>`;
  }

  _wire() {
    this.container.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", e => {
        if (e.target.closest("[data-approve],[data-run],[data-review]")) return;
        this.emit("card:click", el.getAttribute("data-card"));
      }));
    this.container.querySelectorAll("[data-approve]").forEach(b =>
      b.addEventListener("click", async () => {
        const card = b.getAttribute("data-approve");
        const to = b.getAttribute("data-to");
        const d = await this.action("apply", { card, target: to });
        this.emit("toast", d.ok ? `${card} → ${to}` : "✗ " + (d.error || ""));
        await this.refresh();
      }));
    // RUN — открыть workspace проекта карточки
    this.container.querySelectorAll("[data-run]").forEach(b =>
      b.addEventListener("click", async () => {
        const proj = b.getAttribute("data-run");
        const d = await this.action("workspace-open", { project: proj });
        this.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
      }));
    // REVIEW — открыть inspector карточки (или text-клик для drift)
    this.container.querySelectorAll("[data-review]").forEach(b =>
      b.addEventListener("click", () => {
        const card = b.getAttribute("data-review");
        if (card && card.startsWith("ECO-")) this.emit("card:click", card);
        else this.emit("toast", "drift: " + card);
      }));
  }
}
