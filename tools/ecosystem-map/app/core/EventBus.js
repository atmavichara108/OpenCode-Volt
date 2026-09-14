/**
 * EventBus — связь модулей (publish/subscribe, инкапсулированная).
 */
export class EventBus {
  constructor() {
    this.handlers = new Map(); // event -> Set<fn>
  }

  on(event, fn) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event).add(fn);
    return () => this.handlers.get(event)?.delete(fn);
  }

  emit(event, payload) {
    const set = this.handlers.get(event);
    if (!set) return;
    for (const fn of [...set]) {
      try { fn(payload); } catch (e) { console.error(`[EventBus:${event}]`, e); }
    }
  }
}
