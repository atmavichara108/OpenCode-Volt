/**
 * SearchModule — поиск + фильтр по карточкам registry.
 *
 * Строка поиска (backend do_query: id/title/owner/lifecycle/layer/project/
 * facets/priority/status_note) + фильтр по facet и project. Результаты
 * кликабельны → inspector. Debounce 250ms, мгновенный отклик.
 */
import { Module } from "../core/Module.js";

export class SearchModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this._t = null; this.lastQ = ""; }

  async mount(container) {
    super.mount(container);
    this.container.innerHTML = `
      <div class="eco-head">SEARCH · registry</div>
      <input class="search-input" placeholder="поиск: карточка, owner, title, project, facet…"
             autocomplete="off" spellcheck="false">
      <div class="search-facets" id="search-facets"></div>
      <div class="search-count dim" id="search-count"></div>
      <div class="search-results" id="search-results"></div>`;
    this.input = this.container.querySelector(".search-input");
    this.facetsBox = this.container.querySelector("#search-facets");
    this.count = this.container.querySelector("#search-count");
    this.results = this.container.querySelector("#search-results");
    this.input.addEventListener("input", () => {
      clearTimeout(this._t);
      this._t = setTimeout(() => this._run(), 250);
    });
    // сразу показать всё (кэш из registry) — приятнее для первого взгляда
    const reg = await this.fetchJson("registry.json");
    if (reg) { this._registry = reg; await this._run(); }
  }

  async _run() {
    if (!this.container) return;
    const q = this.input.value.trim();
    this.lastQ = q;
    const d = await this.action("query", { q });
    if (!d.ok) { this.results.innerHTML = `<span class="rot">✗ ${this.esc(d.error)}</span>`; return; }
    this._cardsById = Object.fromEntries(d.cards.map(c => [c.id, c]));
    this._renderFacets(d.cards);
    this.count.textContent = `найдено: ${d.count}`;
    this.results.innerHTML = d.cards.map(c => this._row(c)).join("") || '<span class="dim">— ничего —</span>';
    this.results.querySelectorAll("[data-card]").forEach(el =>
      el.addEventListener("click", () => this.emit("card:click", el.getAttribute("data-card"))));
    this.facetsBox.querySelectorAll("[data-facet]").forEach(b =>
      b.addEventListener("click", () => {
        b.classList.toggle("on");
        this._applyFacets();
      }));
  }

  _row(c) {
    const proj = c.project ? `<span class="mono sr-proj">${this.esc(c.project)}</span>` : "";
    return `<div class="sr-row" data-card="${this.esc(c.id)}">
      <b class="mono">${this.esc(c.id)}</b>
      <span class="sr-title">${this.esc(c.title)}</span>
      <span class="sr-meta">${this.esc(c.lifecycle)} · ${this.esc(c.owner || "∅")}</span>
      ${proj}
    </div>`;
  }

  _renderFacets(cards) {
    // собрать живые facets из результата (ограничить 12 самыми частыми)
    const freq = {};
    for (const c of cards) for (const f of (c.facets || [])) freq[f] = (freq[f] || 0) + 1;
    const top = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([f]) => f);
    this.facetsBox.innerHTML = top.map(f => `<button class="facet-chip" data-facet="${this.esc(f)}">${this.esc(f)}</button>`).join("")
      || '<span class="dim">нет facet</span>';
  }

  _applyFacets() {
    const on = new Set([...this.facetsBox.querySelectorAll("[data-facet].on")].map(x => x.getAttribute("data-facet")));
    if (!on.size) return;
    this.results.querySelectorAll("[data-card]").forEach(el => {
      const cid = el.getAttribute("data-card");
      const card = this._cardsById?.[cid];
      const match = card && (card.facets || []).some(f => on.has(f));
      el.style.display = match ? "" : "none";
    });
  }
}