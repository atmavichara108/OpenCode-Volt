/**
 * Module — базовый класс всех модулей Pip-Boy (ООП-ядро).
 *
 * Жизненный цикл: mount(container) → refresh() → unmount().
 * Каждый модуль инкапсулирует своё состояние, рендер и действия;
 * связь между модулями — через App.eventBus (publish/subscribe).
 */
export class Module {
  /**
   * @param {string} id   уникальный идентификатор (например "ecosystem")
   * @param {string} title заголовок для заголовка тайла
   * @param {object} opts опции модуля (per-project и пр.)
   */
  constructor(id, title, opts = {}) {
    if (new.target === Module) {
      throw new TypeError("Module — абстрактный класс, наследуйся");
    }
    this.id = id;
    this.title = title;
    this.opts = opts;
    this.container = null;
    this.mounted = false;
    this.app = null; // подставляется App при регистрации
  }

  /** Вызывается один раз после монтирования; реализуется в потомках. */
  mount(container) {
    this.container = container;
    this.mounted = true;
  }

  /** Перерисовка данных (может вызываться многократно). */
  refresh() {}

  /** Снятие: сброс DOM, таймеров, подписок. */
  unmount() {
    if (this.container) this.container.innerHTML = "";
    this.container = null;
    this.mounted = false;
  }

  /* --- утилиты для потомков --- */
  esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  emit(event, payload) {
    this.app && this.app.eventBus.emit(event, payload);
  }

  on(event, handler) {
    this.app && this.app.eventBus.on(event, handler);
  }

  async fetchJson(path) {
    const r = await fetch(path, { cache: "no-store" });
    return r.ok ? await r.json() : null;
  }

  async action(op, params = {}) {
    const q = new URLSearchParams({ op, ...params });
    try {
      const r = await fetch("/action?" + q, { cache: "no-store" });
      return await r.json();
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }
}
