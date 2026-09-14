/**
 * Workspace — тайловый мультиплексор: регистрация модулей, сетка тайлов,
 * пер-проект состояние, параллельная работа в нескольких проектах.
 *
 * Каждый тайл = { id, moduleInstance, projectId, size, order }.
 * Проекты изолированы: у каждого свой набор модулей (docker, браузер, ...).
 */
export class Workspace {
  /**
   * @param {HTMLElement} root контейнер DOM для сетки тайлов
   * @param {object} layoutConfig пресет лейаута по умолчанию
   */
  constructor(root, layoutConfig = {}) {
    this.root = root;
    this.tiles = new Map();      // tileId -> tile
    this.projectTiles = new Map(); // projectId -> Set<tileId>
    this.activeProject = null;
    this.layout = layoutConfig.layout || "grid";
  }

  /** Зарегистрировать тайл модуля в проекте. */
  addTile(projectId, moduleInstance, { size = "normal" } = {}) {
    const tileId = `${projectId}:${moduleInstance.id}`;
    if (this.tiles.has(tileId)) return tileId;
    const tile = {
      id: tileId,
      projectId,
      module: moduleInstance,
      size,
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
  }

  /** Показать тайлы активного проекта (или всех, если activeProject=null). */
  render() {
    this.root.innerHTML = "";
    for (const tile of this.tiles.values()) {
      if (this.activeProject && tile.projectId !== this.activeProject) continue;
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
    this.render();
  }

  _esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  /* простой drag-переупорядочивание (CSS Grid order) */
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
