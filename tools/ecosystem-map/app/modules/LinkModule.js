/**
 * LinkModule — резолвер ссылок (wikilink / Markdown / путь / URL / localhost).
 *
 * Ввод → классификация + предпросмотр резолва (backend link-resolve) →
 * действия: open in nvim / browser / tmux / copy path.
 */
import { Module } from "../core/Module.js";

export class LinkModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); this.last = null; }

  async mount(container) {
    super.mount(container);
    if (!this._wired) {
      this.on("link:resolve", target => this._openFromEvent(target));
      this._wired = true;
    }
    this.container.innerHTML = `
      <div class="eco-head">LINK RESOLVER</div>
      <form class="link-form">
        <input class="link-input" placeholder="[[wikilink]] · /path/file.md · https://… · localhost:8000"
               autocomplete="off" spellcheck="false">
        <button class="pb-mini" type="submit">⟳ resolve</button>
      </form>
      <div class="link-result dim">введи ссылку для резолва</div>
      <div class="link-actions"></div>`;
    this.input = this.container.querySelector(".link-input");
    this.result = this.container.querySelector(".link-result");
    this.actions = this.container.querySelector(".link-actions");
    this.container.querySelector("form").addEventListener("submit", e => {
      e.preventDefault();
      this._resolve(this.input.value.trim());
    });
  }

  async _openFromEvent(target) {
    this.input.value = target;
    await this._resolve(target);
  }

  async _resolve(target) {
    if (!target) return;
    const d = await this.action("link-resolve", { target });
    if (!d.ok) { this.result.innerHTML = `<span class="rot">✗ ${this.esc(d.error)}</span>`; this.actions.innerHTML = ""; return; }
    this.last = target;
    const kind = { wikilink: "WIKILINK", url: "URL", path: "PATH" }[d.kind] || d.kind;
    this.result.innerHTML = d.exists
      ? `<span class="lk-kind">${kind}</span> <span class="lk-path">${this.esc(d.resolved || d.target)}</span>`
      : `<span class="lk-kind">${kind}</span> <span class="rot">не найден: ${this.esc(d.target)}</span>`;
    this.actions.innerHTML = `
      <button class="pb-mini" data-mode="nvim">▸ nvim</button>
      <button class="pb-mini" data-mode="browser">▸ browser</button>
      <button class="pb-mini" data-mode="tmux">▸ tmux</button>
      <button class="pb-mini" data-mode="copy">⧉ copy</button>`;
    this.actions.querySelectorAll("[data-mode]").forEach(b =>
      b.addEventListener("click", () => this._act(b.getAttribute("data-mode"))));
  }

  async _act(mode) {
    if (!this.last) return;
    if (mode === "copy") {
      try {
        await navigator.clipboard.writeText(this.last);
        this.emit("toast", "путь в буфер: " + this.last);
      } catch (e) {
        this.emit("toast", "✗ копирование: " + e.message);
      }
      return;
    }
    const d = await this.action("link-open", { target: this.last, mode });
    this.emit("toast", d.ok ? `открыто (${mode})` : "✗ " + (d.error || ""));
  }
}
