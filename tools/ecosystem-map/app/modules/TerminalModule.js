/**
 * TerminalModule — терминальный тайл проекта (termproxy-интеграция).
 *
 * Показывает iframe с termproxy (pty→WebSocket→xterm.js) или
 * tmux-статус с кнопками запуска, если termproxy недоступен.
 */
import { Module } from "../core/Module.js";

export class TerminalModule extends Module {
  constructor(id, title, opts) { super(id, title, opts); }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    const project = this.opts.projectId;
    const tpPort = 8200 + this._hashProject(project);

    // Проверяем доступность termproxy
    const tpAlive = await this._checkTermproxy(tpPort);

    if (tpAlive) {
      this.container.innerHTML = `
        <div class="term-iframe-wrap">
          <div class="term-bar">
            <span class="term-proj">${this.esc(project)}</span>
            <span class="term-status">LIVE</span>
          </div>
          <iframe class="term-iframe" src="http://127.0.0.1:${tpPort}/" 
                  sandbox="allow-scripts allow-same-origin" 
                  allow="clipboard-read; clipboard-write"></iframe>
        </div>`;
    } else {
      // Fallback: tmux-статус
      const st = await this.action("workspace-status", { project });
      const running = st.ok && st.tmux_running;
      this.container.innerHTML = running
        ? `<div class="term-box"><div class="term-note">tmux ${this.esc(st.session)} (окна: ${(st.windows || []).length})</div>
           <button class="pb-mini" data-act="term-open">▸ TERMINAL</button></div>`
        : `<div class="term-box"><div class="term-note dim">терминал не запущен</div>
           <button class="pb-mini" data-act="term-open">⚡ START</button></div>`;
      this.container.querySelector("[data-act]")?.addEventListener("click", async () => {
        await this.action("term-open", { project, port: tpPort });
        this.emit("toast", `терминал ${project} запускается...`);
        setTimeout(() => this.refresh(), 1500);
      });
    }
  }

  async _checkTermproxy(port) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/healthz`, { 
        method: "GET", 
        cache: "no-store",
        signal: AbortSignal.timeout(500) 
      });
      const d = await r.json();
      return d.termproxy === true;
    } catch {
      return false;
    }
  }

  _hashProject(project) {
    let h = 0;
    for (let i = 0; i < project.length; i++) {
      h = ((h << 5) - h + project.charCodeAt(i)) | 0;
    }
    return Math.abs(h) % 100;
  }
}
