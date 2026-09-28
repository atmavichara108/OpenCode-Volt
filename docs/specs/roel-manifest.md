# ROEL

Манифест runtime-слоя OpenCode Vault. Источник: отчёт `report-tui-upgrade-2026-09-12.md`.

## 1. Слои

### Layer 1 — Runtime / Plugins
Плагины OpenCode (canonical: `~/dotfiles/opencode-global/.config/opencode/plugins/`, symlink `~/.config/opencode/plugins/`).

| Плагин | Файл | Хук | Evidence |
|---|---|---|---|
| replay-budget | `replay-budget.ts` + `replay-budget-helpers.js` | `experimental.chat.messages.transform` | smoke **15/15** (T-143 fixed), live hook-fire подтверждён 2026-09-08 |
| noop-guard | `noop-guard.ts` + `noop-guard-helpers.js` | `event session.idle` | smoke **9/9** (T-136) |
| input-security | `input-security.ts` + `input-security-helpers.js` | `chat.message` / `messages.transform` | smoke **14/14** (T-137) |
| decision-queue-hook | `decision-queue-hook.ts` (глобальный) | `permission.ask/replied` | smoke 25/25 (T-132) |
| main-protector | `main-protector.ts` (глобальный) | `tool.execute.before` | блок commit в main/master + edit hot-files в main; fail-open; обход `ALLOW_MAIN=1` |

### Layer 2 — Control-Plane
- Decision Queue: `control-plane/decision-queue/` — JSON-карточки (`YYYY-MM-DD-<slug>.json`) + `SCHEMA.md` + `runtime-events.jsonl` (append-only).
- Registry: `tools/ecosystem-map/registry.json` (35 карточек ECO-001..035) + `generated/snapshot.json` (observer.py).
- Custom tools (read-only): `ecosystem_snapshot/next/blockers/query/dependencies/summary`; `ecosystem-open-workspace` — единственный не-read-only.

### Layer 3 — Pip-Boy + Capture
- Pip-Boy host: `tools/ecosystem-map/pipboy.py` (`127.0.0.1:8123`, SSE `/event`, actions `/action`).
- Capture stack: `tools/telegram-capture/` — `watch.py` (демон), `inbox_queue.py`, `pipeline.py`, `capture.py`, `classify.py`, `mark.py`. Полный круг 2026-09-07: 517 постов / 11 тем.
- Skill: `.opencode/skills/capture/SKILL.md`.

## 2. Capture stack (кратко)
```
Telegram @inbox_tools ──watch.py (Telethon)──► inbox_queue.py (JSONL+flock, дедуп)
        └─ capture.py (pull, --topic/--limit/--dry-run) ─► classify.py ─► pipeline.py ─► signals.json
```
Темы: Приложения / Софт / Вайб / #General / Смарт / Графика.

## 3. Pip-Boy v10 — tiling multiplexer

- Entry point: `tools/ecosystem-map/index-v10.html`; layout presets: `grid`,
  `columns`, `focus`, `rows`.
- Modules: `ecosystem`, `projects`, `upgrade`, `terminal`, `browser`,
  `acceptance`, `dependency`, `link`, `launcher`, `proposal`, `agent`,
  `next`, `search`, `health`, `kanban`, `matrix`, `skills`, `models`.
- Per-project isolation: каждый проект получает собственные экземпляры модулей
  и workspace; переключение проекта не смешивает состояние тайлов.
- Terminal: `tools/ecosystem-map/termproxy.py` (pty→WebSocket→xterm.js),
  локальные vendor-ассеты в `tools/ecosystem-map/vendor/`;
  при недоступности termproxy отображается tmux-статус.
- Models: `tools/ecosystem-map/model-router.py` — переключение моделей агентов
  (list/models/apply); вкладка MODELS + `/agents` + rofi `models`. Точечная
  правка `model:` с flock+бэкапом; эффект после рестарта инструмента.

## 4. Pip-Boy usage
```bash
python3 tools/ecosystem-map/observer.py      # snapshot
python3 tools/ecosystem-map/pipboy.py up|status|restart|down|open
# /index-v10.html (v10 tiling multiplexer)
# /index.html (v8-HITECH shell) · /v8bis.html (КОМАНДНЫЙ ЦЕНТР)
# Ctrl+K palette · R refresh · P auto-poll · Shift+click inspector · #view deep-link
```
Actions: `workspace-open|workspace-status|link-open` через `GET /action?op=…`.

## 5. Карта 27 рекомендаций (отчёт 2026-09-12)

**P0 — блокеры (2):**
1. T-143 — фикс мутации tool-input в `applyReplayBudget` (инцидент пустых task-промптов 2026-09-07) → done, smoke 15/15.
2. T-136 — `doom_loop: deny` в canonical jsonc (red-line, Rudra вручную) + live hook-fire `[проверить]`.

**P1 (9):**
3. T-123 — verifier acceptance v2-артефактов T-118..122.
4. T-124/ECO-002 — telemetry: token-budget + audit-log → weekly report.
5. T-134 — playwright-browser (venv-нюанс).
6. T-132/P6#35 — decision-queue live hook: payload, hook-fire, JSONL→/decisions.
7. T-109 — AndroidOS bridge (**FROZEN**, не активировать).
8. T-108 — AndroidOS bridge (**FROZEN**).
9. T-110 — AndroidOS bridge (**FROZEN**).
10. P6#38 — session-flush runtime (session.idle/compaction).
11. P6#39 — медиа-канал отчётов в TUI.

**P2 (7):**
12. T-125/ECO-003 — workspace manifest pilot.
13. T-127 — ecosystem-snapshot runtime smoke `[проверить]`.
14. T-137 — OSC8/tmux-линки `[проверить]`.
15. T-140 — OSC8/tmux-линки `[проверить]`.
16. T-141 — OSC8/tmux-линки `[проверить]`.
17. ECO-030 — doom-loop + no-op guard карточка.
18. ECO-033 — peer-семантика TUI (claim готов, письма/wake не переносятся).

**P3 (5):**
19. T-128 — OSC8 residual `[проверить]`.
20. ECO-017 — route-log / event-sourced memory.
21. ECO-035 — capture: панель CAPTURE, read-state, upgrade-агент (T-079).
22. T-126/ECO-016 — registry schema validation pre-commit.
23. T-080/T-083 — ecosystem-map как planning interface.

**Roadmap P6 — не начато (4):**
24. #35 — decision queue live hook.
25. #38 — session-flush runtime.
26. #39 — медиа-канал отчётов.
27. #41 — майнинг релизов M Code (периодическая).

## 6. Runbook
- `07-Runbooks/ecosystem-kanban-runbook.md` — свод по v3–v7 + custom tools + capture.
- `07-Runbooks/vibecoding-operator-handbook.md` / `vibecoding-changelog.md`.
- `07-Runbooks/coordination-bridge-operator-guide.md`.
