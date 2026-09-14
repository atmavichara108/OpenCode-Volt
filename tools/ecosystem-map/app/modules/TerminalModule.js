/**
 * TerminalModule — живой встроенный терминал тайла (xterm.js + termproxy).
 *
 * xterm.js инстанцируется прямо в тайле (не iframe), подключается по WebSocket
 * к termproxy (pty→WS). termproxy поднимается лениво и идемпотентно через
 * /action term-open; порт детерминирован от имени проекта (backend term_port).
 *
 * Жизненный цикл:
 *   mount()  → placeholder + авто-connect (spawn termproxy, если нужен)
 *   refresh()→ re-fit (не рвёт живую сессию)
 *   unmount()→ закрыть WS, dispose term, disconnect observer
 */
import { Module } from "../core/Module.js";

export class TerminalModule extends Module {
  constructor(id, title, opts) { super(id, title, opts);
    this.term = null; this.fit = null; this.ws = null; this.port = null;
    this._observer = null; this._connecting = false;
  }

  async mount(container) {
    super.mount(container);
    this._renderPlaceholder();
    await this._connect();
  }

  async refresh() {
    if (!this.container) return;
    if (this.term) { try { this.fit?.fit(); } catch (e) {} return; }
    if (!this._connecting) await this._connect();
  }

  _renderPlaceholder() {
    this.container.innerHTML = `<div class="term-host">
      <div class="term-bar"><span class="term-proj">${this.esc(this.opts.projectId)}</span>
        <span class="term-status">CONNECTING…</span></div>
      <div class="term-body"><div class="term-note dim">поднимаю терминал…</div></div>
    </div>`;
  }

  async _connect() {
    if (!this.container || this._connecting) return;
    this._connecting = true;
    try {
      const project = this.opts.projectId;
      // 1. idempotent spawn termproxy
      let d = await this.action("term-open", { project });
      if (!d.ok) { this._showError(d.error); return; }
      this.port = d.port;
      // 2. если только что поднят — дождаться готовности
      if (!d.alive) {
        for (let i = 0; i < 15; i++) {
          await this._sleep(200);
          const st = await this.action("term-status", { project });
          if (st.ok && st.alive) { d.alive = true; break; }
        }
      }
      if (!d.alive) { this._showError("termproxy не поднялся"); return; }
      await this._attachXterm();
    } finally {
      this._connecting = false;
    }
  }

  _sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  async _attachXterm() {
    const T = window.Terminal;
    const Fit = window.FitAddon?.FitAddon;
    if (!T) { this._fallbackIframe(); return; }
    this._renderHost();
    this.term = new T({
      cursorBlink: true,
      fontFamily: "JetBrains Mono, ui-monospace, monospace",
      fontSize: 12.5,
      scrollback: 5000,
      allowProposedApi: true,
      theme: { background: "#0a100d", foreground: "#e8f2ea", cursor: "#4ade80",
               green: "#4ade80", cyan: "#22d3ee", red: "#f43f5e", yellow: "#a3e635" },
    });
    if (Fit) { this.fit = new Fit(); this.term.loadAddon(this.fit); }
    const body = this.container.querySelector(".term-body");
    this.term.open(body);
    this._observeResize();
    this.fit?.fit();

    const ws = new WebSocket(`ws://127.0.0.1:${this.port}/ws`);
    this.ws = ws;
    ws.onopen = () => this._setStatus("LIVE");
    ws.onmessage = e => this.term?.write(e.data);
    ws.onerror = () => this._setStatus("WS ERROR");
    ws.onclose = () => this._setStatus("CLOSED");
    this.term.onData(d => { if (ws.readyState === 1) ws.send(d); });
  }

  _renderHost() {
    this.container.innerHTML = `<div class="term-host">
      <div class="term-bar"><span class="term-proj">${this.esc(this.opts.projectId)}</span>
        <span class="term-status" id="term-st">…</span></div>
      <div class="term-body"></div>
    </div>`;
  }

  _setStatus(s) {
    const el = this.container?.querySelector(".term-status");
    if (el) el.textContent = s;
  }

  _observeResize() {
    const body = this.container?.querySelector(".term-body");
    if (!body || typeof ResizeObserver === "undefined") return;
    this._observer = new ResizeObserver(() => this.fit?.fit());
    this._observer.observe(body);
    window.addEventListener("resize", this._onWinResize = () => this.fit?.fit());
  }

  _fallbackIframe() {
    this.container.innerHTML = `<div class="term-host">
      <div class="term-bar"><span class="term-proj">${this.esc(this.opts.projectId)}</span>
        <span class="term-status">IFRAME</span></div>
      <iframe class="term-iframe" src="http://127.0.0.1:${this.port}/"></iframe>
    </div>`;
  }

  _showError(msg) {
    if (!this.container) return;
    const project = this.opts.projectId;
    this.container.innerHTML = `<div class="term-host">
      <div class="term-bar"><span class="term-proj">${this.esc(project)}</span>
        <span class="term-status" style="color:var(--rot)">ERR</span></div>
      <div class="term-body"><div class="term-note">✗ ${this.esc(msg)}</div>
        <button class="pb-mini" data-act="retry">⟳ RETRY</button></div>
    </div>`;
    this.container.querySelector("[data-act=retry]")?.addEventListener("click", () => this._connect());
  }

  unmount() {
    this._observer?.disconnect();
    this._observer = null;
    if (this._onWinResize) window.removeEventListener("resize", this._onWinResize);
    this._onWinResize = null;
    if (this.ws) { try { this.ws.onclose = null; this.ws.close(); } catch (e) {} }
    this.ws = null;
    if (this.term) { try { this.term.dispose(); } catch (e) {} }
    this.term = null; this.fit = null;
    // погасить termproxy, чтобы порт и pty не копились при переключении проекта
    if (this.port) {
      this.action("term-close", { project: this.opts.projectId }).catch(() => {});
      this.port = null;
    }
    super.unmount();
  }
}
