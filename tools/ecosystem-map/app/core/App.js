/**
 * PipBoyApp — главный класс приложения (фасад).
 *
 * Собирает всё воедино: eventBus, workspace, модули, топбар, статус-бар,
 * горячие клавиши, SSE-канал, command palette, card inspector.
 *
 * Клавиатура:
 *   Alt+1..9  переключить проект по номеру
 *   Alt+0     все проекты (ALL)
 *   Ctrl+K / p  command palette
 *   L         цикл лейаута · R обновить · ? клавиши · Esc закрыть оверлей
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
import { ProposalModule } from "../modules/ProposalModule.js";
import { AgentModule } from "../modules/AgentModule.js";
import { NextActionModule } from "../modules/NextActionModule.js";
import { SearchModule } from "../modules/SearchModule.js";
import { HealthModule } from "../modules/HealthModule.js";
import { KanbanModule } from "../modules/KanbanModule.js";
import { MatrixModule } from "../modules/MatrixModule.js";
import { SkillsModule } from "../modules/SkillsModule.js";

const LAYOUTS = [
  ["grid", "⊞"],
  ["columns", "▤"],
  ["focus", "▣"],
  ["rows", "≡"],
];

const APP_VERSION = "v10.3";

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
    this.registry = null;
    this._projectList = []; // [{id, ...}] только с repo
    this._overlay = null;
    this._prevLayout = null;
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
        <span class="pb-tag">${APP_VERSION} · tiling multiplexer</span>
        <nav class="pb-projects" id="pb-projects"></nav>
        <span class="spacer"></span>
        <span class="pb-layouts" id="pb-layouts" title="пресет лейаута (L)"></span>
        <button class="pb-btn" id="pb-cmd" title="command palette (Ctrl+K)">⌘</button>
        <button class="pb-btn" id="pb-keys" title="клавиши (?)">?</button>
        <button class="pb-btn" id="pb-refresh" title="обновить данные (R)">⟳</button>
      </header>
      <main class="pb-main" id="pb-main"></main>
      <footer class="pb-sbar" id="pb-sbar">
        <span>SSE <b id="pb-sse">…</b></span>
        <span>HEAD <b id="pb-head">—</b></span>
        <span>READY <b id="pb-ready">—</b></span>
        <span class="spacer"></span>
        <span><kbd>Alt+1..9</kbd> проекты · <kbd>Ctrl+K</kbd> команды · <kbd>?</kbd> клавиши</span>
      </footer>
      <div class="pb-kmap" id="pb-kmap" style="display:none"></div>
      <div class="pb-overlay" id="pb-overlay" style="display:none"></div>
    `;
    this.topbar = this.root.querySelector("#pb-projects");
    this.main = this.root.querySelector("#pb-main");
    this.overlayEl = this.root.querySelector("#pb-overlay");
    this.workspace = new Workspace(this.main);
    this._layoutIdx = LAYOUTS.findIndex(l => l[0] === this.workspace.layout);
    if (this._layoutIdx < 0) this._layoutIdx = 0;

    // 2. модули
    this.registerModule("ecosystem", EcosystemModule)
        .registerModule("projects", ProjectsModule)
        .registerModule("upgrade", UpgradeModule)
        .registerModule("terminal", TerminalModule)
        .registerModule("browser", BrowserModule)
        .registerModule("acceptance", AcceptanceModule)
        .registerModule("dependency", DependencyModule)
        .registerModule("link", LinkModule)
        .registerModule("launcher", LauncherModule)
        .registerModule("proposal", ProposalModule)
        .registerModule("agent", AgentModule)
        .registerModule("next", NextActionModule)
        .registerModule("search", SearchModule)
        .registerModule("health", HealthModule)
        .registerModule("kanban", KanbanModule)
        .registerModule("matrix", MatrixModule)
        .registerModule("skills", SkillsModule);

    // 3. проекты + глобальные тайлы
    await this._loadProjects();

    // 4. подсистемы
    this._wireKeys();
    this._initSSE();
    this._initMobile();
    this.eventBus.on("card:click", cid => this._openInspector(cid));

    // 5. первичная отрисовка
    this.workspace.render();
    this._renderProjectsBar();
    this._renderLayoutBtns();
    this._renderSbar();
  }

  instantiate(moduleId, projectId, opts = {}) {
    const M = this.modules.get(moduleId);
    if (!M) throw new Error(`модуль ${moduleId} не зарегистрирован`);
    const inst = new M(moduleId, moduleId, { projectId, ...opts });
    inst.app = this;
    return inst;
  }

  async _loadProjects() {
    const [snap, reg] = await Promise.all([
      fetch("generated/snapshot.json", { cache: "no-store" }).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch("registry.json", { cache: "no-store" }).then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    this.projects = (snap && snap.projects) || [];
    this.registry = reg;
    this._readyCount = (snap && snap.registry_cards) ? Object.values(snap.registry_cards).filter(c => c.lifecycle === "APPROVED").length : 0;
    this._head = (snap && snap.git && snap.git.head) ? (snap.git.head.slice(0, 8)) : null;
    this._projectList = this.projects.filter(p => p.repo);
    for (const p of this._projectList) {
      this.workspace.addTile(p.id, this.instantiate("launcher", p.id));
      this.workspace.addTile(p.id, this.instantiate("ecosystem", p.id), { size: "wide" });
      this.workspace.addTile(p.id, this.instantiate("terminal", p.id));
      this.workspace.addTile(p.id, this.instantiate("browser", p.id));
    }
    this.workspace.addTile("—", this.instantiate("upgrade", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("dependency", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("acceptance", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("proposal", "—"));
    this.workspace.addTile("—", this.instantiate("agent", "—"));
    this.workspace.addTile("—", this.instantiate("next", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("search", "—"));
    this.workspace.addTile("—", this.instantiate("health", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("kanban", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("matrix", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("skills", "—"), { size: "wide" });
    this.workspace.addTile("—", this.instantiate("link", "—"));
    if (this._projectList.length) this.setActiveProject(this._projectList[0].id);
  }

  setActiveProject(projectId) {
    this.activeProject = projectId;
    this.workspace.setActiveProject(projectId);
    this._layoutIdx = LAYOUTS.findIndex(l => l[0] === this.workspace.layout);
    if (this._layoutIdx < 0) this._layoutIdx = 0;
    this.eventBus.emit("project:change", { projectId });
    this._renderProjectsBar();
    this._renderLayoutBtns();
  }

  _renderProjectsBar() {
    const n = this._projectList.length;
    const all = `<button class="pb-proj ${!this.activeProject ? "active" : ""}" data-proj="" title="Alt+0">ALL</button>`;
    this.topbar.innerHTML = all + this._projectList.map((p, i) =>
      `<button class="pb-proj ${this.activeProject === p.id ? "active" : ""}" data-proj="${this._esc(p.id)}"
        title="Alt+${i + 1}"><b class="pn">${i + 1}</b>${this._esc(p.id)}</button>`).join("");
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

  async actionRaw(op, params = {}) {
    const q = new URLSearchParams({ op, ...params });
    try {
      const r = await fetch("/action?" + q, { cache: "no-store" });
      return await r.json();
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  /* --- mobile --- */
  _initMobile() {
    const apply = () => {
      const mobile = window.innerWidth < 700;
      document.body.classList.toggle("mobile", mobile);
      if (mobile && this.workspace.layout !== "rows") {
        this._prevLayout = this.workspace.layout;
        this.workspace.setLayout("rows");
      } else if (!mobile && this.workspace.layout === "rows" && this._prevLayout) {
        this.workspace.setLayout(this._prevLayout);
        this._prevLayout = null;
      }
    };
    window.addEventListener("resize", apply);
    apply();
  }

  /* --- keyboard --- */
  _wireKeys() {
    document.addEventListener("keydown", e => {
      if (this._overlay) {
        if (e.key === "Escape") this._closeOverlay();
        return;
      }
      if (e.target.closest("input,textarea,select")) return;
      if (e.key === "?" ) { this._toggleKmap(); return; }
      if (e.key === "r" || e.key === "R") { this.refreshAll(); return; }
      if (e.key === "l" || e.key === "L") { this._cycleLayout(); return; }
      if (e.key === "Escape") { this._clearTileFocus(); this.root.querySelector("#pb-kmap").style.display = "none"; return; }
      // Ctrl+K или p → command palette
      if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) { e.preventDefault(); this._openPalette(); return; }
      // Alt+1..9 → проект по номеру; Alt+0 → все проекты
      if (e.altKey) {
        if (e.key >= "1" && e.key <= "9") {
          e.preventDefault();
          const idx = +e.key - 1;
          const p = this._projectList[idx];
          if (p) this.setActiveProject(p.id);
        } else if (e.key === "0") {
          e.preventDefault();
          this.setActiveProject(null);
        }
        return;
      }
      // Keyboard-first навигация по тайлам: стрелки = фокус, Enter = активировать,
      // x = закрыть, f = focus-лейаут (первый тайл на всю ширину)
      if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
        e.preventDefault();
        this._navTile(e.key);
        return;
      }
      if (e.key === "x" || e.key === "X") { this._closeFocusedTile(); return; }
      if (e.key === "n" || e.key === "Tab") { e.preventDefault(); this._cycleTileFocus(); return; }
    });
    this.root.querySelector("#pb-cmd").addEventListener("click", () => this._openPalette());
    this.root.querySelector("#pb-refresh").addEventListener("click", () => this.refreshAll());
    this.root.querySelector("#pb-keys").addEventListener("click", () => this._toggleKmap());
    this.overlayEl.addEventListener("click", e => { if (e.target === this.overlayEl) this._closeOverlay(); });
  }

  _visibleTiles() {
    return [...this.main.querySelectorAll(".tile")].filter(t => t.offsetParent !== null || t.style.display !== "none");
  }

  _focusTile(el) {
    this._visibleTiles().forEach(t => t.classList.remove("tile-focused"));
    el?.classList.add("tile-focused");
    el?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  _focusedTile() {
    return this.main.querySelector(".tile.tile-focused");
  }

  _clearTileFocus() {
    this.main.querySelectorAll(".tile-focused").forEach(t => t.classList.remove("tile-focused"));
  }

  _cycleTileFocus() {
    const tiles = this._visibleTiles();
    if (!tiles.length) return;
    const idx = tiles.indexOf(this._focusedTile());
    this._focusTile(tiles[(idx + 1) % tiles.length]);
  }

  _navTile(dir) {
    // простой линейный обход + переход по стрелкам как по сетке (по колонкам)
    const tiles = this._visibleTiles();
    if (!tiles.length) return;
    const cur = this._focusedTile();
    if (!cur) { this._focusTile(tiles[0]); return; }
    const i = tiles.indexOf(cur);
    const step = (dir === "ArrowRight" || dir === "ArrowDown") ? 1 : -1;
    this._focusTile(tiles[(i + step + tiles.length) % tiles.length]);
  }

  _closeFocusedTile() {
    const t = this._focusedTile();
    if (!t) { this.eventBus.emit("toast", "нет фокуса: стрелки — выбрать тайл, x — закрыть"); return; }
    const tileId = t.dataset.tile;
    this.workspace.removeTile(tileId);
    this.workspace.render();
  }

  _toggleKmap() {
    const km = this.root.querySelector("#pb-kmap");
    km.style.display = km.style.display === "none" ? "block" : "none";
    km.innerHTML = `<div class="kmap-box"><h3>КЛАВИШИ</h3>
      <div class="krow"><b>Alt+1..9</b><span>переключить проект по номеру</span></div>
      <div class="krow"><b>Alt+0</b><span>все проекты (ALL)</span></div>
      <div class="krow"><b>Ctrl+K</b><span>command palette</span></div>
      <div class="krow"><b>L</b><span>цикл лейаута (grid/columns/focus/rows)</span></div>
      <div class="krow"><b>R</b><span>обновить все модули</span></div>
      <div class="krow"><b>← ↑ ↓ → / Tab</b><span>фокус тайла (следующий/предыдущий)</span></div>
      <div class="krow"><b>x</b><span>закрыть сфокусированный тайл</span></div>
      <div class="krow"><b>?</b><span>эта справка</span></div>
      <div class="krow"><b>Esc</b><span>снять фокус / закрыть оверлей</span></div>
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

  /* --- overlay (palette / inspector / prompt) --- */
  _openOverlay(html) {
    this.overlayEl.innerHTML = html;
    this.overlayEl.style.display = "grid";
    this._overlay = true;
  }

  _closeOverlay() {
    this.overlayEl.style.display = "none";
    this.overlayEl.innerHTML = "";
    this._overlay = null;
  }

  /* --- command palette --- */
  _openPalette() {
    const cmds = [];
    cmds.push({ id: "all", label: "Все проекты (ALL)", hint: "Alt+0", run: () => this.setActiveProject(null) });
    this._projectList.forEach((p, i) =>
      cmds.push({ id: "proj:" + p.id, label: "Проект: " + p.id, hint: "Alt+" + (i + 1), run: () => this.setActiveProject(p.id) }));
    LAYOUTS.forEach(([id]) => cmds.push({ id: "layout:" + id, label: "Лейаут: " + id, run: () => this.setLayout(id) }));
    cmds.push({ id: "refresh", label: "Обновить всё", hint: "R", run: () => this.refreshAll() });
    cmds.push({ id: "ws", label: "Открыть workspace активного проекта", run: () => this._openWorkspace() });
    cmds.push({ id: "notify", label: "Push на телефон (ntfy)", run: () => this._promptNotify() });
    cmds.push({ id: "help", label: "Клавиши", hint: "?", run: () => this._toggleKmap() });

    this._openOverlay(`<div class="palette">
      <div class="palette-head">COMMAND PALETTE <span class="dim">Ctrl+K</span></div>
      <input class="palette-input" placeholder="начни печатать…" autofocus>
      <div class="palette-list"></div>
    </div>`);
    const input = this.overlayEl.querySelector(".palette-input");
    const list = this.overlayEl.querySelector(".palette-list");
    let sel = 0;

    const render = (filter) => {
      const f = (filter || "").toLowerCase();
      const items = cmds.filter(c => c.label.toLowerCase().includes(f));
      if (!items.length) { list.innerHTML = '<div class="palette-empty">нет совпадений</div>'; return; }
      sel = Math.min(sel, items.length - 1);
      list.innerHTML = items.map((c, i) =>
        `<div class="palette-item ${i === sel ? "sel" : ""}" data-i="${i}">
          <span>${this._esc(c.label)}</span>${c.hint ? `<kbd>${this._esc(c.hint)}</kbd>` : ""}</div>`).join("");
      list.querySelectorAll("[data-i]").forEach(el =>
        el.addEventListener("click", () => { const it = items[+el.dataset.i]; this._closeOverlay(); it.run(); }));
    };
    const exec = () => {
      const f = input.value.toLowerCase();
      const items = cmds.filter(c => c.label.toLowerCase().includes(f));
      const it = items[sel];
      if (it) { this._closeOverlay(); it.run(); }
    };
    input.addEventListener("input", () => { sel = 0; render(input.value); });
    input.addEventListener("keydown", e => {
      if (e.key === "ArrowDown") { e.preventDefault(); sel++; render(input.value); }
      else if (e.key === "ArrowUp") { e.preventDefault(); sel--; render(input.value); }
      else if (e.key === "Enter") { e.preventDefault(); exec(); }
      else if (e.key === "Escape") this._closeOverlay();
    });
    render("");
    input.focus();
  }

  async _openWorkspace() {
    if (!this.activeProject) { this.eventBus.emit("toast", "выбери проект"); return; }
    const d = await this.actionRaw("workspace-open", { project: this.activeProject });
    this.eventBus.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
  }

  _promptNotify() {
    this._openOverlay(`<div class="prompt">
      <div class="prompt-head">PUSH (ntfy)</div>
      <input class="prompt-input" placeholder="сообщение (пусто = проверка связи)">
      <div class="prompt-actions">
        <button class="pb-mini" data-act="cancel">отмена</button>
        <button class="pb-mini up" data-act="send">▸ send</button>
      </div>
    </div>`);
    const input = this.overlayEl.querySelector(".prompt-input");
    input.focus();
    input.addEventListener("keydown", e => { if (e.key === "Enter") this._doNotify(input.value.trim()); });
    this.overlayEl.querySelector("[data-act=cancel]").addEventListener("click", () => this._closeOverlay());
    this.overlayEl.querySelector("[data-act=send]").addEventListener("click", () => this._doNotify(input.value.trim()));
  }

  async _doNotify(msg) {
    this._closeOverlay();
    const d = await this.actionRaw("notify", { message: msg || "Pip-Boy: проверка связи" });
    this.eventBus.emit("toast", d.ok ? "push → ntfy:" + d.topic : "✗ " + (d.error || ""));
  }

  /* --- card inspector --- */
  _openInspector(cid) {
    const c = this.registry?.cards?.[cid];
    if (!c) { this.eventBus.emit("toast", cid + " — нет в registry"); return; }
    const lc = c.lifecycle || "IDEA";
    const arts = (c.artifacts || []).map(a =>
      `<div class="insp-art"><a data-open="${this._esc(a)}">${this._esc(a.split("/").pop())}</a>
        <span class="dim mono">${this._esc(a)}</span></div>`).join("") || '<span class="dim">—</span>';
    const deps = (c.depends_on || []).length ? c.depends_on.join(", ") : "—";
    const tasks = (c.tasks || []).length ? c.tasks.join(", ") : "—";
    const proj = c.project || this.activeProject || "";
    this._openOverlay(`<div class="inspector">
      <div class="insp-head">
        <b class="mono leaf">${this._esc(cid)}</b>
        <span class="acc-stage">${this._esc(lc)}</span>
        <span class="dim grow">${this._esc(c.title || "")}</span>
        <button class="tx" data-act="close">✕</button>
      </div>
      <div class="insp-body">
        <div class="insp-grid">
          <div><span class="lbl">OWNER</span> ${c.owner ? this._esc(c.owner) : '<span class="warn">нет</span>'}</div>
          <div><span class="lbl">PRIORITY</span> ${this._esc(c.priority || "—")}</div>
          <div><span class="lbl">LAYER</span> ${this._esc(c.layer || "—")}</div>
          <div><span class="lbl">PROJECT</span> ${this._esc(proj || "—")}</div>
        </div>
        <div class="insp-sec"><span class="lbl">DEPS</span> ${this._esc(deps)}</div>
        <div class="insp-sec"><span class="lbl">TASKS</span> ${this._esc(tasks)}</div>
        ${c.acceptance ? `<div class="insp-sec"><span class="lbl">ACCEPT</span> ${this.linkify(c.acceptance)}</div>` : ""}
        ${c.status_note ? `<div class="insp-sec"><span class="lbl">NOTE</span> ${this.linkify(c.status_note)}</div>` : ""}
        ${c.rollback ? `<div class="insp-sec"><span class="lbl">ROLLBACK</span> ${this.linkify(c.rollback)}</div>` : ""}
        <div class="insp-sec"><span class="lbl">ARTIFACTS</span><div class="insp-arts">${arts}</div></div>
      </div>
      <div class="insp-actions">
        <button class="pb-mini" data-act="copy">⧉ copy id</button>
        ${proj ? `<button class="pb-mini up" data-act="ws">▸ workspace ${this._esc(proj)}</button>` : ""}
      </div>
    </div>`);
    this.overlayEl.querySelector("[data-act=close]").addEventListener("click", () => this._closeOverlay());
    this.overlayEl.querySelector("[data-act=copy]")?.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(cid); this.eventBus.emit("toast", cid + " в буфер"); }
      catch (e) { this.eventBus.emit("toast", "✗ " + e.message); }
    });
    this.overlayEl.querySelector("[data-act=ws]")?.addEventListener("click", async () => {
      const d = await this.actionRaw("workspace-open", { project: proj });
      this.eventBus.emit("toast", d.ok ? "tmux " + d.session : "✗ " + (d.error || ""));
      this._closeOverlay();
    });
    this.overlayEl.querySelectorAll("[data-open]").forEach(a =>
      a.addEventListener("click", async () => {
        const d = await this.actionRaw("link-open", { target: a.getAttribute("data-open"), mode: "browser" });
        this.eventBus.emit("toast", d.ok ? "открыто" : "✗ " + (d.error || ""));
      }));
    // кликабельные wikilinks внутри текста (note/accept/rollback)
    this.overlayEl.querySelectorAll(".wl[data-link]").forEach(a =>
      a.addEventListener("click", () => {
        this.eventBus.emit("link:resolve", a.getAttribute("data-link"));
        this._closeOverlay();
      }));
  }

  _esc(s) { return String(s ?? "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  _linkify(s) {
    return this._esc(s).replace(/\[\[([^\]]+)\]\]/g, (m, target) => {
      const t = target.split("|")[0].trim();
      return `<span class="wl" data-link="${this._esc(t)}" role="link">[[${this._esc(target)}]]</span>`;
    });
  }
  linkify(s) { return this._linkify(s); }
}
