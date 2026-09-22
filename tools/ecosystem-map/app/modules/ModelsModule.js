/**
 * ModelsModule — MODELS dashboard: переключение моделей агентов OpenCode.
 *
 * Таблица всех агентов (глобальные + проектные + встроенные из agent-блока
 * конфига): имя, scope, текущая модель, <select> доступных моделей.
 *
 * Источник истины: сами файлы агентов (`model:` фронтматтера) и
 * `agent.<n>.model` конфига. Карты «агент → модель» нет (решение Rudra).
 * Бэкенд: model-router.py через /action model-list | model-models | model-apply.
 *
 * Важно: переключение правит КОНФИГ. Эффект — после рестарта инструмента
 * или новой сессии (hot-reload модели в движке нет).
 */
import { Module } from "../core/Module.js";

const SCOPE_LABEL = { global: "GLOBAL", project: "PROJECT" };
const KIND_LABEL = { file: "агент .md", config: "встроенный" };

export class ModelsModule extends Module {
  constructor(id, title, opts) {
    super(id, title, opts);
    this.agents = [];
    this.models = [];
    this.providers = {};
    this._busy = false;
    this._filter = "";
  }

  async mount(container) {
    super.mount(container);
    await this.refresh();
  }

  async refresh() {
    if (!this.container) return;
    const [list, models] = await Promise.all([
      this.action("model-list", {}),
      this.action("model-models", {}),
    ]);
    this.agents = list?.ok ? (list.agents || []) : [];
    this.models = models?.ok ? (models.models || []) : [];
    this.providers = models?.ok ? (models.providers || {}) : {};
    if (!list?.ok && !models?.ok) {
      this.container.innerHTML = `<div class="eco-head">MODELS</div>
        <span class="dim">model-router недоступен: ${this.esc(list?.error || models?.error || "")}</span>`;
      return;
    }
    this.container.innerHTML = this._render();
    this._wire();
  }

  _modelOptions(current) {
    const ids = this.models.map(m => m.id);
    const known = new Set(ids);
    if (current && !known.has(current)) ids.unshift(current);
    return ids.map(id => {
      const prov = this.providers?.[id.split("/")[0]];
      const sources = (this.models.find(m => m.id === id)?.sources || []);
      const tags = [];
      if (sources.includes("in-use")) tags.push("in-use");
      if (sources.includes("live")) tags.push("live");
      if (prov?.status) tags.push(prov.status.replace(/[`✅❌]/g, "").trim());
      const label = tags.length ? `${id}  ·  ${tags.join(", ")}` : id;
      return `<option value="${this.esc(id)}"${id === current ? " selected" : ""}>${this.esc(label)}</option>`;
    }).join("");
  }

  _row(a) {
    const slug = `${a.scope}:${a.project || "-"}:${a.agent}`;
    const prov = a.model ? a.model.split("/")[0] : "";
    const pstatus = this.providers?.[prov]?.status || "";
    const warn = pstatus && /❌|BLOCKED|NO_MODELS/i.test(pstatus);
    return `<div class="mdl-row" data-slug="${this.esc(slug)}">
      <div class="mdl-name">
        <b>${this.esc(a.agent)}</b>
        <span class="mdl-scope ${a.scope}">${SCOPE_LABEL[a.scope] || a.scope}</span>
        ${a.project ? `<span class="mdl-proj">${this.esc(a.project)}</span>` : ""}
      </div>
      <div class="mdl-meta dim">
        <span class="mdl-kind">${KIND_LABEL[a.kind] || a.kind}</span>
        <span class="mdl-mode">${this.esc(a.mode || "")}</span>
      </div>
      <div class="mdl-cur ${warn ? "rot" : ""}">${this.esc(a.model || "— нет модели —")}</div>
      <select class="mdl-select" data-agent="${this.esc(a.agent)}"
              data-scope="${this.esc(a.scope)}" data-project="${this.esc(a.project || "")}"
              data-prev="${this.esc(a.model || "")}">
        ${this._modelOptions(a.model)}
      </select>
    </div>`;
  }

  _render() {
    const byScope = { global: [], project: [] };
    const q = this._filter.toLowerCase();
    for (const a of this.agents) {
      if (q && !(`${a.agent} ${a.model || ""} ${a.project || ""}`).toLowerCase().includes(q)) continue;
      (byScope[a.scope] ||= []).push(a);
    }
    const total = this.agents.length;
    const active = this.agents.filter(a => !/❌|BLOCKED|NO_MODELS/i.test(
      this.providers?.[(a.model || "").split("/")[0]]?.status || "")).length;
    const grp = (scope, label) => byScope[scope].length ? `
      <div class="csect">${label} · ${byScope[scope].length}</div>
      ${byScope[scope].map(a => this._row(a)).join("")}` : "";
    return `<div class="eco-head">MODELS · переключение моделей агентов</div>
      <div class="mdl-top">
        <input class="mdl-filter" placeholder="фильтр: агент / модель / проект…" value="${this.esc(this._filter)}">
        <span class="dim mdl-count">агентов <b>${total}</b> · моделей <b>${this.models.length}</b> · провайдеров <b>${Object.keys(this.providers).length}</b></span>
      </div>
      <div class="mdl-note dim">Выбор пишет <code>model:</code> в файл агента (или agent-блок конфига).
        Применяется после рестарта инструмента / новой сессии — hot-reload в движке нет.
        Бэкап и flock — на стороне model-router.</div>
      ${grp("global", "ГЛОБАЛЬНЫЕ")}
      ${grp("project", "ПРОЕКТНЫЕ")}
      <div class="mdl-providers">${Object.entries(this.providers).map(([id, p]) =>
        `<span class="mdl-chip ${/❌|BLOCKED|NO_MODELS/i.test(p.status || "") ? "rot" : ""}"
          title="${this.esc((p.sources || []).join(', '))}">${this.esc(id)} <b>${p.models}</b>
          ${p.status ? `<i>${this.esc(p.status.replace(/[`]/g, ""))}</i>` : ""}</span>`).join("")}</div>`;
  }

  _wire() {
    const f = this.container.querySelector(".mdl-filter");
    if (f?.addEventListener) {
      f.addEventListener("input", () => {
        this._filter = f.value;
        const pos = f.selectionStart;
        this.container.innerHTML = this._render();
        this._wire();
        const nf = this.container.querySelector(".mdl-filter");
        if (nf) { nf.focus(); try { nf.setSelectionRange(pos, pos); } catch (e) {} }
      });
    }
    this.container.querySelectorAll(".mdl-select").forEach(sel =>
      sel.addEventListener("change", () => this._apply(sel)));
  }

  async _apply(sel) {
    if (this._busy) return;
    const agent = sel.getAttribute("data-agent");
    const scope = sel.getAttribute("data-scope");
    const project = sel.getAttribute("data-project");
    const model = sel.value;
    const previous = sel.getAttribute("data-prev");
    if (model === previous) return;

    this._busy = true;
    sel.disabled = true;
    const params = { agent, model, scope };
    if (project) params.project = project;
    const d = await this.action("model-apply", params);
    this._busy = false;
    sel.disabled = false;

    if (!d?.ok) {
      this.emit("toast", { text: `✗ ${agent}: ${d?.error || "ошибка"}`, err: true });
      sel.value = previous || "";   // откат визуального выбора
      return;
    }
    if (d.changed) {
      // Undo: вернуть предыдущую модель (предложение живёт 9 секунд в toast)
      const undo = d.old_model ? {
        label: "↩ отменить",
        run: async () => {
          const r = await this.action("model-apply", { ...params, model: d.old_model });
          if (r?.ok) {
            this.emit("toast", `↩ ${agent}: возвращено ${d.old_model}`);
            await this.refresh();
          } else {
            this.emit("toast", { text: `✗ откат не удался: ${r?.error || ""}`, err: true });
          }
        },
      } : null;
      this.emit("toast", {
        text: `${agent}: ${d.old_model || "—"} → ${d.model} · применится после рестарта`,
        action: undo,
      });
      sel.setAttribute("data-prev", d.model);
      sel.classList.add("mdl-dirty");
    } else {
      this.emit("toast", d.dry_run ? `${agent}: dry-run` : `${agent}: модель уже стоит`);
      sel.value = d.model;
    }
  }
}