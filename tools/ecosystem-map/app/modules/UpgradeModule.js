/**
 * UpgradeModule — централизованный рабочий фреймворк апгрейдов.
 * Вместо разбросанных по чатам записей: вся структура апгрейдов
 * экосистемы (registry ECO-карточки + TASKS) в одном окне.
 */
import { Module } from "../core/Module.js";

export class UpgradeModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.registry = null; }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    this.registry = await this.fetchJson("registry.json");
    if (!this.registry) return;
    const cards = Object.entries(this.registry.cards || {});
    const byStage = {};
    for (const [ ,c] of cards) byStage[c.lifecycle] = (byStage[c.lifecycle] || 0) + 1;
    const layers = this.registry.layers || {};
    this.container.innerHTML = `<div class="eco-head">APGRADE FRAMEWORK · registry</div>
      <div class="csect">КАРТОЧКИ ПО СТАДИЯМ</div>
      <div class="stage-bar">${Object.entries(byStage).map(([st,n]) =>
        `<span class="stage" title="${st}">${st}<b>${n}</b></span>`).join("")}</div>
      <div class="csect">СЛОИ</div>
      ${Object.entries(layers).map(([lid,l]) =>
        `<div class="proj-row"><b class="mono">${lid}</b><span class="dim grow">${this.esc(l.name)}</span></div>`).join("")}
      <div class="csect">БЫСТРЫЕ ДЕЙСТВИЯ</div>
      <button class="pb-mini" data-act="export-md">⧉ экспорт MD</button>
      <button class="pb-mini" data-act="export-json">⧉ экспорт JSON</button>`;
    this.container.querySelectorAll("[data-act]").forEach(b =>
      b.addEventListener("click", () => {
        if (b.dataset.act === "export-json") this._copy(JSON.stringify(this.registry, null, 2));
        else this._copy("# Pip-Boy Upgrade Framework\n" + cards.map(([cid,c]) => `- ${cid} [${c.lifecycle}] ${c.title}`).join("\n"));
        this.emit("toast", "экспорт в буфер");
      }));
  }

  _copy(text) {
    const f = t => { const a = document.createElement("textarea"); a.value = t; document.body.appendChild(a); a.select(); try { document.execCommand("copy"); } catch (e) {} a.remove(); };
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).catch(() => f(text));
    else f(text);
  }
}
