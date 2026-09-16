/**
 * Workspace — тайловый мультиплексор: регистрация модулей, сетка тайлов,
 * пер-проект состояние, параллельная работа в нескольких проектах.
 *
 * Каждый тайл = { id, moduleInstance, projectId, size, order }.
 * Проекты изолированы: у каждого свой набор модулей (docker, браузер, ...).
 *
 * Лейауты (пресеты):
 *   grid     — адаптивная сетка (auto-fit)
 *   columns  — 3 равные колонки
 *   rows     — стек в одну колонку (mobile/чтение)
 *   focus    — первый тайл на всю ширину, остальные в 2 колонки
 * Порядок и размеры тайлов сохраняются в localStorage (pipboy-layout-v10).
 */
export class Workspace {
  constructor(root, layoutConfig = {}) {
    this.root = root;
    this.tiles = new Map();      // tileId -> tile
    this.projectTiles = new Map(); // projectId -> Set<tileId>
    this.activeProject = null;
    this.layout = layoutConfig.layout || "grid";
    this.layouts = {};           // per-project layout: { "<projectId>"|"__all__": layout }
    this.order = [];             // tileId-порядок (восстанавливается из storage)
    this.sizes = {};             // tileId -> size
    this._loadLayout();
  }

  /* --- persistence (localStorage) --- */
  _loadLayout() {
    try {
      const raw = localStorage.getItem("pipboy-layout-v10");
      if (!raw) return;
      const s = JSON.parse(raw);
      if (s.layout) this.layout = s.layout;
      if (s.layouts) this.layouts = s.layouts;
      if (Array.isArray(s.order)) this.order = s.order;
      if (s.sizes) this.sizes = s.sizes;
    } catch (e) { /* повреждённый storage — игнорируем */ }
  }

  _saveLayout() {
    try {
      localStorage.setItem("pipboy-layout-v10", JSON.stringify({
        layout: this.layout,
        layouts: this.layouts,
        order: [...this.tiles.keys()],
        sizes: Object.fromEntries([...this.tiles.values()].map(t => [t.id, t.size])),
      }));
    } catch (e) { /* quota/private mode */ }
  }

  _layoutKey() { return this.activeProject || "__all__"; }

  setLayout(layout) {
    this.layout = layout;
    this.layouts[this._layoutKey()] = layout;
    this.root.dataset.layout = layout;
    this._saveLayout();
  }

  /** Вернуть сохранённый лейаут проекта или дефолт (не переключая). */
  layoutFor(projectId) {
    return this.layouts[projectId || "__all__"] || this.layouts["__all__"] || "grid";
  }

  /** Зарегистрировать тайл модуля в проекте. */
  addTile(projectId, moduleInstance, { size = "normal" } = {}) {
    const tileId = `${projectId}:${moduleInstance.id}`;
    if (this.tiles.has(tileId)) return tileId;
    const tile = {
      id: tileId,
      projectId,
      module: moduleInstance,
      size: this.sizes[tileId] || size,
      el: null,
    };
    this.tiles.set(tileId, tile);
    if (!this.projectTiles.has(projectId)) this.projectTiles.set(projectId, new Set());
    this.projectTiles.get(projectId).add(tileId);
    return tileId;
  }

  removeTile(tileId) {
    const tile = this.tiles.get(tileId);
    if (!tile) return;
    tile.module.unmount();
    tile.el?.remove();
    this.tiles.delete(tileId);
    this.projectTiles.get(tile.projectId)?.delete(tileId);
    this._saveLayout();
  }

  /** Порядок тайлов: сохранённый порядок + новые в конце. */
  _orderedTiles() {
    const known = new Set(this.order);
    const result = [];
    for (const id of this.order) {
      const t = this.tiles.get(id);
      if (t) result.push(t);
    }
    for (const [id, t] of this.tiles) if (!known.has(id)) result.push(t);
    return result;
  }

  /** Показать тайлы активного проекта (или всех, если activeProject=null). */
  render() {
    // снять все смонтированные тайлы (терминалы, подписки, DOM) перед пересборкой
    for (const tile of this.tiles.values()) {
      if (tile.el) tile.module.unmount();
    }
    this.root.innerHTML = "";
    this.root.dataset.layout = this.layout;
    const tiles = this._orderedTiles().filter(t => {
      if (!this.activeProject) return true;           // без фокуса — показать всё
      if (t.projectId === "—") return true;            // глобальные тайлы всегда видимы
      return t.projectId === this.activeProject;       // тайлы активного проекта
    });
    for (const tile of tiles) {
      const el = document.createElement("section");
      el.className = `tile tile-${tile.size}`;
      el.dataset.tile = tile.id;
      el.innerHTML = `<header class="tile-head">
        <span class="t">${this._esc(tile.module.title)}</span>
        <span class="tp">${this._esc(tile.projectId)}</span>
        <button class="tx" data-close="${tile.id}">✕</button>
      </header><div class="tile-body"></div>`;
      this.root.appendChild(el);
      tile.el = el;
      tile.module.mount(el.querySelector(".tile-body"));
      el.querySelector("[data-close]").addEventListener("click", () => {
        this.removeTile(tile.id);
        this.render();
      });
    }
    this._wireDrag();
  }

  setActiveProject(projectId) {
    this.activeProject = projectId;
    // переключить лейаут на сохранённый для этого проекта (per-project layout)
    this.layout = this.layoutFor(projectId);
    this.render();
  }

  _esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  /* drag-переупорядочивание: переставляет DOM + сохраняет порядок */
  _wireDrag() {
    let drag = null;
    this.root.querySelectorAll(".tile-head").forEach(head => {
      head.setAttribute("draggable", "true");
      head.addEventListener("dragstart", e => {
        drag = head.parentElement;
        head.parentElement.classList.add("dragging");
      });
      head.addEventListener("dragend", () => {
        head.parentElement.classList.remove("dragging");
        drag = null;
        this.order = [...this.root.querySelectorAll(".tile")].map(el => el.dataset.tile);
        this._saveLayout();
      });
      head.parentElement.addEventListener("dragover", e => {
        e.preventDefault();
        if (drag && drag !== head.parentElement) {
          const parent = this.root;
          const after = [...parent.children].indexOf(head.parentElement) >
            [...parent.children].indexOf(drag);
          parent.insertBefore(drag, after ? head.parentElement.nextSibling : head.parentElement);
        }
      });
    });
  }
}
