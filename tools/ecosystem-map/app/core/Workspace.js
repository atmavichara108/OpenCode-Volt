/**
 * Workspace - tiled multiplexer: module registration, lazy mounting and
 * per-project Pip-Boy profiles.
 *
 * A tile is kept alive while it is hidden. This is important for terminals,
 * browsers and any module which owns subscriptions or an iframe.
 */

const SKELETON = `<div class="skel">
  <span class="sk sk-1"></span><span class="sk sk-2"></span><span class="sk sk-3"></span>
  <span class="sk sk-4"></span>
</div>`;

/** Public profile registry. `modules: "*"` means every registered tile. */
export const PROFILES = Object.freeze({
  overview: Object.freeze({ label: "Overview", modules: ["launcher", "ecosystem", "projects", "health", "next", "kanban", "matrix"], layout: "columns" }),
  build: Object.freeze({ label: "Build", modules: ["ecosystem", "terminal", "browser", "dependency", "upgrade", "next"], layout: "monad3" }),
  control: Object.freeze({ label: "Control", modules: ["launcher", "terminal", "browser", "acceptance", "proposal", "agent"], layout: "slice" }),
  models: Object.freeze({ label: "Models", modules: ["models", "skills", "matrix", "link"], layout: "plasma" }),
  capture: Object.freeze({ label: "Capture", modules: ["search", "link", "projects", "proposal", "acceptance"], layout: "treetab" }),
  all: Object.freeze({ label: "All", modules: "*", layout: "plasma" }),
});

const PROFILE_IDS = new Set(Object.keys(PROFILES));
const STORAGE_KEY = "pipboy-layout-v10";
const MODULE_ROLES = Object.freeze({
  launcher: ["utility", "side-left"], projects: ["utility", "side-left"], search: ["utility", "side-left"],
  link: ["utility"], health: ["utility"], next: ["utility"],
  ecosystem: ["main"], terminal: ["main"], browser: ["main"], models: ["main"], matrix: ["main"], kanban: ["main"],
  acceptance: ["side-right"], proposal: ["side-right"], dependency: ["side-right"], upgrade: ["side-right"], agent: ["side-right"], skills: ["side-right"],
});

export class Workspace {
  constructor(root, layoutConfig = {}) {
    this.root = root;
    this.tiles = new Map();
    this.projectTiles = new Map();
    this.closedTiles = new Map();
    this.activeProject = null;
    this.layout = layoutConfig.layout || "columns";
    this.layouts = {};
    this.order = [];
    this.orders = {};
    this.sizes = {};
    this.profiles = {};
    this.focuses = {};
    this.ratios = {};
    this.compacts = {};
    this._profile = layoutConfig.profile || null;
    this._ratio = 1;
    this._loadLayout();
    if (typeof layoutConfig.compact === "boolean") this.compacts[this._projectOrderKey()] = layoutConfig.compact;
    this._profile = this._profileFor("__all__") || this._profile || "overview";
    if (layoutConfig.profile && PROFILES[layoutConfig.profile]) this._profile = layoutConfig.profile;
    this._applyRootState();
  }

  /* --- persistence (localStorage) --- */
  _loadLayout() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        this.compacts.__all__ = localStorage.getItem("pipboy-compact") === "1";
        return;
      }
      const s = JSON.parse(raw);
      if (s.layout) this.layout = s.layout;
      if (s.layouts) this.layouts = s.layouts;
      if (Array.isArray(s.order)) this.order = s.order;
      if (s.orders) this.orders = s.orders;
      if (s.sizes) this.sizes = s.sizes;
      if (s.profiles) this.profiles = s.profiles;
      if (s.focuses || s.focus) this.focuses = s.focuses || s.focus;
      if (s.ratios || s.ratio) this.ratios = s.ratios || s.ratio;
      if (s.compacts || typeof s.compact === "boolean") this.compacts = s.compacts || { __all__: s.compact };
      if (!Object.keys(this.compacts).length) this.compacts.__all__ = localStorage.getItem("pipboy-compact") === "1";
    } catch (e) { /* corrupt/private storage is non-fatal */ }
  }

  _saveLayout() {
    try {
      const currentOrder = [...this.tiles.keys()];
      const savedOrder = [...this.order, ...currentOrder.filter(id => !this.order.includes(id))];
      this.order = savedOrder;
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        layout: this.layout,
        layouts: this.layouts,
        order: savedOrder,
        orders: this.orders,
        sizes: this.sizes,
        profiles: this.profiles,
        focuses: this.focuses,
        ratios: this.ratios,
        compacts: this.compacts,
      }));
      localStorage.setItem("pipboy-compact", this.compact ? "1" : "0");
    } catch (e) { /* quota/private mode */ }
  }

  _layoutKey() { return this.activeProject || "__all__"; }
  _projectOrderKey(projectId = this.activeProject) { return projectId || "__all__"; }

  _profileFor(projectId = this.activeProject) {
    return this.profiles[this._projectOrderKey(projectId)] || null;
  }

  _profileModules() {
    const profile = PROFILES[this._profile];
    return profile ? profile.modules : "*";
  }

  _isAllowed(tile) {
    if (!this._profile || this._profile === "all") return true;
    if (tile.revealed) return true;
    const modules = this._profileModules();
    return modules === "*" || modules.includes(tile.module.id) || modules.includes(tile.id);
  }

  _isProjectVisible(tile) {
    return !this.activeProject || tile.projectId === "—" || tile.projectId === this.activeProject;
  }

  _isVisible(tile) { return this._isProjectVisible(tile) && this._isAllowed(tile); }

  _orderedTiles(projectId = this.activeProject) {
    const key = this._projectOrderKey(projectId);
    const saved = this.orders[key] || (key === "__all__" ? this.order : []);
    const known = new Set(saved);
    const result = [];
    for (const id of saved) {
      const tile = this.tiles.get(id);
      if (tile && (!projectId || tile.projectId === projectId || tile.projectId === "—")) result.push(tile);
    }
    for (const tile of this.tiles.values()) {
      if (!known.has(tile.id) && (!projectId || tile.projectId === projectId || tile.projectId === "—")) result.push(tile);
    }
    return result;
  }

  setLayout(layout) {
    if (!layout) return;
    this.layout = layout;
    this.layouts[this._layoutKey()] = layout;
    this._applyRootState();
    this._saveLayout();
    this._applyLayoutMode();
  }

  layoutFor(projectId) {
    return this.layouts[projectId || "__all__"] || this.layouts.__all__ || this.layout || "columns";
  }

  /** Current profile id, or null when an old/custom layout is active. */
  get profile() { return this._profile; }

  setProfile(id) {
    if (!PROFILE_IDS.has(id)) return false;
    this.exitFull();
    this._profile = id;
    this.profiles[this._projectOrderKey()] = id;
    this.layout = PROFILES[id].layout;
    this.layouts[this._layoutKey()] = this.layout;
    this._applyRootState();
    this._saveLayout();
    this.render();
    return true;
  }

  get compact() { return Boolean(this.compacts[this._projectOrderKey()]); }

  setCompact(value) {
    this.compacts[this._projectOrderKey()] = Boolean(value);
    this._applyRootState();
    this._saveLayout();
    return this.compact;
  }

  toggleCompact() { return this.setCompact(!this.compact); }

  get ratio() { return this.ratios[this._projectOrderKey()] ?? 1; }

  adjustRatio(delta = 0) {
    const n = Number(delta);
    if (!Number.isFinite(n)) return this.ratio;
    this.ratios[this._projectOrderKey()] = Math.max(0.5, Math.min(2.5, this.ratio + n));
    this._applyRootState();
    this._saveLayout();
    return this.ratio;
  }

  resetRatios() {
    delete this.ratios[this._projectOrderKey()];
    this._applyRootState();
    this._saveLayout();
    return this.ratio;
  }

  _applyRootState() {
    if (!this.root) return;
    this.root.dataset.layout = this.layout;
    if (this._profile) this.root.dataset.profile = this._profile;
    else delete this.root.dataset.profile;
    this.root.classList?.toggle("compact", this.compact);
    this.root.style?.setProperty("--workspace-ratio", String(this.ratio));
    this.root.style?.setProperty("--workspace-main-ratio", String(Math.max(1, this.ratio * 2)));
    this.root.dataset.columns = this.layout === "columns" ? "2" : "auto";
  }

  /** Register a module instance. */
  addTile(projectId, moduleInstance, { size = "normal", role = null } = {}) {
    const tileId = `${projectId}:${moduleInstance.id}`;
    if (this.tiles.has(tileId) || this.closedTiles.has(tileId)) return tileId;
    const tile = { id: tileId, projectId, module: moduleInstance, size: this.sizes[tileId] || size, role, el: null, mounted: false, revealed: false };
    this.tiles.set(tileId, tile);
    if (!this.projectTiles.has(projectId)) this.projectTiles.set(projectId, new Set());
    this.projectTiles.get(projectId).add(tileId);
    return tileId;
  }

  removeTile(tileId) {
    const tile = this.tiles.get(tileId);
    if (!tile) return;
    if (tile.mounted) tile.module.unmount?.();
    tile.mounted = false;
    this._io?.unobserve(tile.el);
    tile.el?.remove();
    tile.el = null;
    this.tiles.delete(tileId);
    this.projectTiles.get(tile.projectId)?.delete(tileId);
    this.closedTiles.set(tileId, tile);
    if (this._fullId === tileId) this.exitFull();
    this._saveLayout();
  }

  _tileClasses(tile) {
    const roles = tile.role ? (Array.isArray(tile.role) ? tile.role : [tile.role]) : (MODULE_ROLES[tile.module.id] || []);
    return ["tile", `tile-${tile.size}`, `tile-module-${String(tile.module.id).replace(/[^\w-]/g, "-")}`, ...roles.map(r => `tile-${r}`)].join(" ");
  }

  _createTileElement(tile) {
    const el = document.createElement("section");
    el.className = this._tileClasses(tile);
    el.dataset.tile = tile.id;
    el.dataset.module = tile.module.id;
    el.dataset.project = tile.projectId;
    el.innerHTML = `<header class="tile-head">
      <span class="tdot"></span><span class="t">${this._esc(tile.module.title)}</span>
      <span class="tp">${this._esc(tile.projectId)}</span>
      <button class="ts" data-size="${tile.id}" title="размер тайла">↔</button>
      <button class="tf" data-full="${tile.id}" title="на весь экран (f)">⤢</button>
      <button class="tx" data-close="${tile.id}">✕</button>
    </header><div class="tile-body">${SKELETON}</div>`;
    el.querySelector("[data-close]")?.addEventListener("click", e => { e.stopPropagation(); this.removeTile(tile.id); this.render(); });
    el.querySelector("[data-full]")?.addEventListener("click", e => { e.stopPropagation(); this.toggleFull(tile.id); });
    el.querySelector("[data-size]")?.addEventListener("click", e => { e.stopPropagation(); this.toggleSize(tile.id); });
    return el;
  }

  /** Render visibility/order without unmounting existing module instances. */
  render() {
    this.exitFull();
    this._io?.disconnect();
    this._io = null;
    this._applyRootState();
    // Keep inactive-project elements in the DOM, only hide them. This lets a
    // terminal/browser retain its DOM and module state across project switches.
    const activeTiles = this._orderedTiles(this.activeProject);
    const activeIds = new Set(activeTiles.map(tile => tile.id));
    const tiles = [...activeTiles, ...this._orderedTiles(null).filter(tile => !activeIds.has(tile.id))];
    for (const tile of tiles) {
      if (!tile.el) tile.el = this._createTileElement(tile);
      tile.el.className = this._tileClasses(tile);
      tile.el.dataset.size = tile.size;
      tile.el.hidden = !this._isVisible(tile);
      tile.el.style.display = tile.el.hidden ? "none" : "";
      this.root.appendChild(tile.el);
      if (this._isVisible(tile) && !tile.mounted) this._mountWhenVisible(tile);
    }
    this._wireDrag();
    this._applyLayoutMode();
    this._applyFocus2();
  }

  toggleSize(tileId) {
    const tile = this.tiles.get(tileId);
    if (!tile) return null;
    tile.size = tile.size === "wide" ? "normal" : "wide";
    this.sizes[tile.id] = tile.size;
    tile.el?.classList.toggle("tile-wide", tile.size === "wide");
    tile.el?.classList.toggle("tile-normal", tile.size !== "wide");
    this._saveLayout();
    return tile.size;
  }

  _applyLayoutMode() {
    if (!this.root) return;
    const tabbed = this.layout === "treetab" || this.layout === "focus2";
    const focusedId = this.focuses[this._projectOrderKey()] || this.root.querySelector(".tile-focused")?.dataset.tile;
    let focused = focusedId && this.tiles.get(focusedId);
    if (!focused || !this._isVisible(focused)) focused = this._orderedTiles().find(t => this._isVisible(t));
    this.root.querySelectorAll(".tile").forEach(el => {
      const active = !tabbed || el === focused?.el;
      el.classList.toggle("tile-focused", el === focused?.el);
      el.classList.toggle("tile-collapsed", tabbed && !active);
      const body = el.querySelector(".tile-body");
      if (body) body.style.display = tabbed && !active ? "none" : "";
    });
    if (focused?.el) focused.el.classList.add("tile-focused");
  }

  _applyFocus2() {
    const tabbed = this.layout === "treetab" || this.layout === "focus2";
    this.root.querySelectorAll(".tile").forEach(el => {
      el.classList.toggle("tile-focused", tabbed && el.dataset.tile === this.focuses[this._projectOrderKey()]);
      const head = el.querySelector(".tile-head");
      if (!head || head.dataset.focusWired) return;
      head.dataset.focusWired = "1";
      head.addEventListener("click", e => {
        if (e.target.closest("[data-close],[data-full],[data-size]")) return;
        this.focusTile(el);
      });
    });
    this._applyLayoutMode();
  }

  _ensureObserver() {
    if (this._io) return this._io;
    if (typeof IntersectionObserver === "undefined") return null;
    this._io = new IntersectionObserver(entries => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const tile = this.tiles.get(e.target.dataset.tile);
        if (tile && !tile.mounted && this._isVisible(tile)) this._mountTile(tile);
        this._io?.unobserve(e.target);
      }
    }, { root: this.root, rootMargin: "400px 0px" });
    return this._io;
  }

  _mountTile(tile) {
    if (tile.mounted || !tile.el || !this._isVisible(tile)) return;
    tile.mounted = true;
    const token = (tile.mountToken || 0) + 1;
    tile.mountToken = token;
    try {
      const result = tile.module.mount(tile.el.querySelector(".tile-body"));
      const ready = () => { if (tile.mountToken === token) this.onTileReady?.(tile); };
      const failed = err => {
        if (tile.mountToken !== token) return;
        tile.mounted = false;
        this._renderTileError(tile, err?.message || String(err));
        this.onTileReady?.(tile);
      };
      if (result && typeof result.then === "function") result.then(ready, failed);
      else ready();
    } catch (err) {
      tile.mounted = false;
      this._renderTileError(tile, err?.message || String(err));
      this.onTileReady?.(tile);
    }
  }

  _renderTileError(tile, msg) {
    const body = tile.el?.querySelector(".tile-body");
    if (!body) return;
    body.innerHTML = `<div class="tile-err"><span class="rot">✕ не загружено</span><span class="dim mono">${this._esc(msg)}</span><button class="pb-mini" data-retry="1">⟳ повторить</button></div>`;
    body.querySelector("[data-retry]")?.addEventListener("click", () => {
      body.innerHTML = SKELETON;
      this._mountTile(tile);
    });
  }

  _mountWhenVisible(tile) {
    if (!tile.el || !this._isVisible(tile)) return;
    const io = this._ensureObserver();
    if (!io) this._mountTile(tile);
    else io.observe(tile.el);
  }

  mountVisible() {
    for (const tile of this.tiles.values()) if (tile.el && this._isVisible(tile) && !tile.mounted) this._mountTile(tile);
  }

  toggleFull(tileId) {
    const tile = this.tiles.get(tileId);
    if (!tile?.el || !this._isVisible(tile)) return;
    if (this._fullId === tileId) { this.exitFull(); return; }
    if (this._fullId) this.exitFull();
    this._fullId = tileId;
    tile.el.classList.add("tile-full");
    const btn = tile.el.querySelector("[data-full]");
    if (btn) { btn.textContent = "⤡"; btn.title = "вернуть в сетку (Esc)"; }
    document.body.classList.add("has-full");
    this._mountTile(tile);
    this.onFullChange?.(tile);
  }

  exitFull() {
    if (!this._fullId) return;
    const tile = this.tiles.get(this._fullId);
    this._fullId = null;
    if (tile?.el) {
      tile.el.classList.remove("tile-full");
      const btn = tile.el.querySelector("[data-full]");
      if (btn) { btn.textContent = "⤢"; btn.title = "на весь экран (f)"; }
    }
    document.body.classList.remove("has-full");
    this.onFullChange?.(null);
  }

  fullTileId() { return this._fullId; }

  setActiveProject(projectId) {
    if (this.activeProject === projectId) return;
    this.exitFull();
    this.activeProject = projectId;
    this._profile = this._profileFor(projectId) || this._profileFor("__all__") || "overview";
    this.layout = this.layoutFor(projectId);
    this._applyRootState();
    this.render();
  }

  /** Return/reopen a module tile, making it visible in the active profile. */
  revealModule(id) {
    const candidates = [`${this.activeProject || "—"}:${id}`, `—:${id}`, id];
    let tile = candidates.map(key => this.tiles.get(key) || this.closedTiles.get(key)).find(Boolean);
    if (!tile) tile = [...this.tiles.values(), ...this.closedTiles.values()].find(t => t.module.id === id && this._isProjectVisible(t));
    if (!tile) return null;
    if (!this.tiles.has(tile.id)) {
      this.closedTiles.delete(tile.id);
      this.tiles.set(tile.id, tile);
      if (!this.projectTiles.has(tile.projectId)) this.projectTiles.set(tile.projectId, new Set());
      this.projectTiles.get(tile.projectId).add(tile.id);
    }
    tile.revealed = true;
    this.render();
    return tile.el;
  }

  focusTile(el) {
    if (!el) return null;
    this.root.querySelectorAll(".tile-focused").forEach(t => t.classList.remove("tile-focused"));
    el.classList.add("tile-focused");
    const tile = this.tiles.get(el.dataset.tile);
    if (tile) this.focuses[this._projectOrderKey()] = tile.id;
    this._applyLayoutMode();
    this._saveLayout();
    el.scrollIntoView?.({ block: "nearest", behavior: "smooth" });
    if (tile && !tile.mounted) this._mountTile(tile);
    return el;
  }

  /** Move focus by geometry where possible, otherwise by persisted linear order. */
  moveFocused(dir = "right") {
    const visible = this._orderedTiles().filter(t => this._isVisible(t) && t.el);
    if (!visible.length) return null;
    const currentEl = this.root.querySelector(".tile-focused") || visible[0].el;
    const current = this.tiles.get(currentEl?.dataset.tile);
    if (!current) return null;
    const index = visible.indexOf(current);
    let targetIndex = index + (["left", "up", "ArrowLeft", "ArrowUp"].includes(dir) ? -1 : 1);
    if (["up", "down", "ArrowUp", "ArrowDown"].includes(dir)) {
      const rect = current.el.getBoundingClientRect?.();
      if (rect) {
        const candidates = visible.filter(t => t !== current).map(t => ({ tile: t, rect: t.el.getBoundingClientRect() })).filter(x =>
          dir === "up" || dir === "ArrowUp" ? x.rect.bottom <= rect.top + 2 : x.rect.top >= rect.bottom - 2);
        if (candidates.length) targetIndex = visible.indexOf(candidates.reduce((a, b) => Math.abs(a.rect.left - rect.left) < Math.abs(b.rect.left - rect.left) ? a : b).tile);
      }
    }
    if (targetIndex < 0 || targetIndex >= visible.length) return null;
    const target = visible[targetIndex];
    return this.focusTile(target.el);
  }

  _wireDrag() {
    let drag = null;
    this.root.querySelectorAll(".tile-head").forEach(head => {
      if (head.dataset.dragWired) return;
      head.dataset.dragWired = "1";
      head.setAttribute("draggable", "true");
      head.addEventListener("dragstart", () => { drag = head.parentElement; drag.classList.add("dragging"); });
      head.addEventListener("dragend", () => {
        drag?.classList.remove("dragging");
        const key = this._projectOrderKey();
        const visible = [...this.root.querySelectorAll(".tile")].filter(el => !el.hidden).map(el => el.dataset.tile);
        const old = this.orders[key] || (key === "__all__" ? this.order : []);
        this.orders[key] = [...visible, ...old.filter(id => !visible.includes(id))];
        if (key === "__all__") this.order = this.orders[key];
        drag = null;
        this._saveLayout();
      });
      head.parentElement.addEventListener("dragover", e => {
        e.preventDefault();
        if (drag && drag !== head.parentElement) {
          const children = [...this.root.children];
          const after = children.indexOf(head.parentElement) > children.indexOf(drag);
          this.root.insertBefore(drag, after ? head.parentElement.nextSibling : head.parentElement);
        }
      });
    });
  }

  _esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
}
