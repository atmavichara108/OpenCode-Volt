/**
 * PipBoyApp — главный класс приложения (фасад).
 *
 * Собирает всё воедино: eventBus, workspace, модули, топбар, статус-бар,
 * горячие клавиши, SSE-канал. Модули регистрируются через registerModule().
 */
import { EventBus } from "./EventBus.js";
import { Workspace } from "./Workspace.js";
import { EcosystemModule } from "../modules/EcosystemModule.js";
import { ProjectsModule } from "../modules/ProjectsModule.js";
import { UpgradeModule } from "../modules/UpgradeModule.js";
import { TerminalModule } from "../modules/TerminalModule.js";
import { BrowserModule } from "../modules/BrowserModule.js";
import { AcceptanceModule } from "../modules/AcceptanceModule.js";
import { DependencyModule } from "../modules/DependencyModule.js";
import { LinkModule } from "../modules/LinkModule.js";
import { LauncherModule } from "../modules/LauncherModule.js";

const LAYOUTS = [
  ["grid", "⊞"],
  ["columns", "▤"],
  ["focus", "▣"],
  ["rows", "≡"],
];

export class PipBoyApp {
  constructor(rootEl) {
    this.root = rootEl;
    this.eventBus = new EventBus();
    this.modules = new Map(); // id -> ModuleClass
    this.workspace = null;
    this.activeProject = null;
    this.feed = [];
    this._sseLive = false;
    this._layoutIdx = 0;
  }

  registerModule(id, ModuleClass) {
    this.modules.set(id, ModuleClass);
    return this;
  }

  async init() {
    // 1. скелет UI
    this.root.innerHTML = `
      <header class="pb-topbar">
        <span class="pb-logo">PIP<b>BOY</b></span>
        <span class="pb-tag">v10 · tiling multiplexer</span>
        <nav class="pb-projects" id="pb-projects"></nav>
        <span class="spacer"></span>
        <span class="pb-layouts" id="pb-layouts" title="пресет лейаута (L)"></span>
        <button class="pb-btn" id="pb-notify" title="push на телефон (ntfy)">◈</button>
        <button class="pb-btn" id="pb-keys" title="клавиши (?)">?</button>
        <button class="pb-btn" id="pb-refresh" title="обновить данные (R)">⟳</button>
      </header>
      <main class="pb-main" id="pb-main"></main>
      <footer class="pb-sbar" id="pb-sbar">
        <span>SSE <b id="pb-sse">…</b></span>
        <span>HEAD <b id="pb-head">—</b></span>
        <span>READY <b id="pb-ready">—</b></span>
        <span class="spacer"></span>
        <span><kbd>L</kbd> лейаут · <kbd>Alt+1..9</kbd> тайлы · <kbd>?</kbd> клавиши</span>
      </footer>
      <div class="pb-kmap" id="pb-kmap" style="display:none"></div>
    `;
    this.topbar = this.root.querySelector("#pb-projects");
    this.main = this.root.querySelector("#pb-main");
    this.workspace = new Workspace(this.main);
    this._layoutIdx = LAYOUTS.findIndex(l => l[0] === this.workspace.layout);
    if (this._layoutIdx < 0) this._layoutIdx = 0;

    // 2. модули по умолчанию
    this.registerModule("ecosystem", EcosystemModule)
        .registerModule("projects", ProjectsModule)
        .registerModule("upgrade", UpgradeModule)
        .registerModule("terminal", TerminalModule)
        .registerModule("browser", BrowserModule)
        .registerModule("acceptance", AcceptanceModule)
        .registerModule("dependency", DependencyModule)
        .registerModule("link", LinkModule)
        .registerModule("launcher", LauncherModule);

    // 3. проекты (пер-проект модули)
    await this._loadProjects();

    // 4. горячие клавиши + SSE + layout-кнопки
    this._wireKeys();
    this._wireLayoutBtns();
    this._initSSE();
    this._initMobile();

    // 5. первичная отрисовка
    this.workspace.render();
    this._renderProjectsBar();
    this._renderLayoutBtns();
    this._renderSbar();
  }

  /* создаёт инстанс модуля для проекта (каждый проект — свои модули) */
  instantiate(moduleId, projectId, opts = {}) {
    const M = this.modules.get(moduleId);
    if (!M) throw new Error(`модуль ${moduleId} не зарегистрирован`);
    const inst = new M(moduleId, moduleId, { projectId, ...opts });
    inst.app = this;
    return inst;
  }

  async _loadProjects() {
    const snap = await fetch("generated/snapshot.json", { cache: "no-store" }).then(r => r.ok ? r.json() : null).catch(() => null);
    this.projects = (snap && snap.projects) || [];
    this._readyCount = (snap && snap.registry_cards) ? Object.values(snap.registry_cards).filter(c => c.lifecycle === "APPROVED").length : 0;
    this._head = (snap && snap.git && snap.git.head) ? (snap.git.head.slice(0, 8)) : null;
    // параллельные проекты: для каждого создаём свои тайлы
    for (const p of this.projects) {
      if (!p.repo) continue;
      this.workspace.addTile(p.id, this.instantiate("launcher", p.id));
      this.workspace.addTile(p.id, this.instantiate("ecosystem", p.id), { size: "wide" });
      this.workspace.addTile(p.id, this.instantiate("terminal", p.id));
      this.workspace.addTile(p.id, this.instantiate("browser", p.id));
    }
    // глобальные (без проекта) тайлы
    this.workspace.addTile("—", this.instantiate("upgrade", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("dependency", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("acceptance", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("link", "—"));
    if (this.projects.length) this.setActiveProject(this.projects.find(p => p.repo)?.id || null);
  }

  setActiveProject(projectId) {
    this.activeProject = projectId;
    this.workspace.setActiveProject(projectId);
    this.eventBus.emit("project:change", { projectId });
    this._renderProjectsBar();
  }

  _renderProjectsBar() {
    const globalBtn = `<button class="pb-proj ${!this.activeProject ? "active" : ""}" data-proj="">ALL</button>`;
    this.topbar.innerHTML = globalBtn + this.projects.filter(p => p.repo).map(p =>
      `<button class="pb-proj ${this.activeProject === p.id ? "active" : ""}" data-proj="${this._esc(p.id)}">${this._esc(p.id)}</button>`).join("");
    this.topbar.querySelectorAll("[data-proj]").forEach(b =>
      b.addEventListener("click", () => this.setActiveProject(b.getAttribute("data-proj") || null)));
  }

  _renderSbar() {
    this.root.querySelector("#pb-sse").textContent = this._sseLive ? "LIVE" : "…";
    this.root.querySelector("#pb-head").textContent = this._head || "—";
    this.root.querySelector("#pb-ready").textContent = this._readyCount ?? "—";
  }

  /* --- layout presets --- */
  _renderLayoutBtns() {
    const box = this.root.querySelector("#pb-layouts");
    box.innerHTML = LAYOUTS.map(([id, icon], i) =>
      `<button class="pb-proj ${i === this._layoutIdx ? "active" : ""}" data-layout="${id}" title="${id}">${icon}</button>`).join("");
    box.querySelectorAll("[data-layout]").forEach(b =>
      b.addEventListener("click", () => this.setLayout(b.getAttribute("data-layout"))));
  }

  _wireLayoutBtns() {
    // (кнопки пересоздаются в _renderLayoutBtns)
  }

  setLayout(layout) {
    this.workspace.setLayout(layout);
    this._layoutIdx = LAYOUTS.findIndex(l => l[0] === layout);
    this._renderLayoutBtns();
    this.eventBus.emit("toast", "layout: " + layout);
  }

  _cycleLayout() {
    this._layoutIdx = (this._layoutIdx + 1) % LAYOUTS.length;
    this.setLayout(LAYOUTS[this._layoutIdx][0]);
  }

  /* --- ntfy push --- */
  async notify(message) {
    const d = await this.actionRaw("notify", { message: message || "Pip-Boy: проверка связи" });
    this.eventBus.emit("toast", d.ok ? "push → ntfy:" + d.topic : "✗ " + (d.error || ""));
  }

  async actionRaw(op, params = {}) {
    const q = new URLSearchParams({ op, ...params });
    try {
      const r = await fetch("/action?" + q, { cache: "no-store" });
      return await r.json();
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  _initMobile() {
    const apply = () => {
      const mobile = window.innerWidth < 700;
      document.body.classList.toggle("mobile", mobile);
      if (mobile && this.workspace.layout !== "rows") this.workspace.setLayout("rows");
    };
    window.addEventListener("resize", apply);
    apply();
  }

  _wireKeys() {
    document.addEventListener("keydown", e => {
      if (e.target.closest("input,textarea,select")) return;
      if (e.key === "?") this._toggleKmap();
      if (e.key === "r" || e.key === "R") this.refreshAll();
      if (e.key === "l" || e.key === "L") this._cycleLayout();
      if (e.altKey && e.key >= "1" && e.key <= "9") {
        e.preventDefault();
        const tiles = [...this.workspace.tiles.values()];
        const t = tiles[+e.key - 1];
        if (t) {
          this.workspace.removeTile(t.id);
          this.workspace.render();
        }
      }
      if (e.key === "Escape") this.root.querySelector("#pb-kmap").style.display = "none";
    });
    this.root.querySelector("#pb-notify").addEventListener("click", () => {
      const msg = prompt("push-сообщение (ntfy):", "Pip-Boy: проверка связи");
      if (msg !== null) this.notify(msg);
    });
    this.root.querySelector("#pb-refresh").addEventListener("click", () => this.refreshAll());
    this.root.querySelector("#pb-keys").addEventListener("click", () => this._toggleKmap());
  }

  _toggleKmap() {
    const km = this.root.querySelector("#pb-kmap");
    km.style.display = km.style.display === "none" ? "block" : "none";
    km.innerHTML = `<div class="kmap-box"><h3>КЛАВИШИ</h3>
      <div class="krow"><b>L</b><span>цикл лейаута (grid/columns/focus/rows)</span></div>
      <div class="krow"><b>Alt+1..9</b><span>закрыть тайл</span></div>
      <div class="krow"><b>R</b><span>обновить все модули</span></div>
      <div class="krow"><b>?</b><span>эта справка</span></div>
      <div class="krow"><b>Esc</b><span>закрыть</span></div>
      <div class="krow"><b>drag</b><span>перетащить тайл за шапку</span></div>
    </div>`;
  }

  async refreshAll() {
    for (const t of this.workspace.tiles.values()) {
      try { t.module.refresh(); } catch (e) { console.error(`[refresh:${t.id}]`, e); }
    }
    this._renderSbar();
  }

  _initSSE() {
    if (typeof EventSource === "undefined") return;
    const es = new EventSource("/event");
    this._sseLive = false;
    es.onopen = () => { this._sseLive = true; this._renderSbar(); };
    es.addEventListener("file.watcher.updated", e => {
      const d = JSON.parse(e.data || "{}");
      this.feed.unshift({ ts: new Date().toTimeString().slice(0, 8), text: "файлы изменились · digest " + (d.digest || "").slice(0, 8) });
      this.feed = this.feed.slice(0, 30);
      this.eventBus.emit("feed:new", this.feed[0]);
      this.refreshAll();
    });
    es.onerror = () => { this._sseLive = false; this._renderSbar(); };
  }

  _esc(s) { return String(s ?? "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
}
