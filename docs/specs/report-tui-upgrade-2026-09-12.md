# Отчёт: «Апгрейд системы» применительно к OpenCode TUI / Pip-Boy — состояние на 2026-09-12

Репозиторий: `/home/rudra/Projects/OpenCode-Vault`, текущая ветка `pipboy-v8-rethink`
(main = c8a7209 «pip-boy v4–v7 утверждён», далее 5 коммитов v8/v9 на ветке).
Read-only исследование; ничего не менялось.

---

## ВЫВОД (сначала главное)

1. **Апгрейд TUI в этом волте — это два взаимосвязанных трека:**
   - **Pip-Boy** (`tools/ecosystem-map/`) — браузерный read-only дашборд/планинг-UI
     экосистемы, прошедший путь v1→v9. Работает **прямо сейчас**: сервер жив
     на `http://127.0.0.1:8123/` (pid 2043283, idle 30 мин).
   - **Порт органов M Code Desktop в TUI-стек** (roadmap P6, карточки
     ECO-029..035, задачи T-131..T-143): плагины replay-budget, noop-guard,
     input-security, playwright-браузер, peers-реестр, verify-cache и т.д.
2. **Что работает фактически** (не «заявлено», а подтверждено смоками/live):
   - pip-boy host (`pipboy.py up/down/status/open`) + SSE `/event` +
     actions `/action` (workspace-open/status, link-open) — PASS, live.
   - Capture pipeline ECO-035: `watch.py` (демон Telegram), `inbox_queue.py`,
     `pipeline.py` → signals; полный круг 2026-09-07 дал 517 постов / 11 тем.
   - Плагины TUI: replay-budget (live hook-fire подтверждён 2026-09-08),
     noop-guard smoke 9/9, input-security smoke 14/14.
3. **Фронтенд сейчас в точке ветвления**: v8-BIS «КОМАНДНЫЙ ЦЕНТР» (task-deck)
   → v8-HITECH (стеклянный shell, уже в index.html) → v9 «TERRARIUM»
   (гибрид A+B+C, мокап terrarium.html) — **терраrium пока мокап, ожидает
   утверждения Rudra**, index.html и v8bis.html не тронуты.
4. **Самые горячие открытые задачи**: **T-143 (P0)** — мутация живых tool-input
   в replay-budget (инцидент пустых task-промптов); **T-135 остаток** — live
   hook-fire закрыт, остался T-143; **T-136/137/132/134 residuals** — live
   hook-fire после рестарта TUI `[проверить]`; **roadmap P6 #35, #38, #39, #41** ❌.

---

## 1. Хронология апгрейда Pip-Boy (v1 → v9)

Git-история (git log --all | grep pip-boy, от старого к новому):

| Этап | Коммит | Дата | Что сделано |
|------|--------|------|-------------|
| **v1** | `dc6368d` | 2026-07-13 | Первая интерактивная карта `tools/ecosystem-map`: 468 постов → 36 навыков → 326 инструментов, 4 вкладки (T-069). Чисто визуализатор capture-данных. |
| **v2 (план)** | `e32a51a` | 2026-08-31 | Ecosystem upgrade plan v2: Layers × Facets, canonical registry, observer, Pip-Boy multi-view, MCP spec. |
| **v3** | `d17dd7f` | 2026-08-31 | Kanban control plane: registry 28 карточек ECO-001..028, multi-view (MATRIX/KANBAN/PROJECTS/AGENTS/BLOCKERS/WORKSPACE), runbook (T-129, verifier PASS). |
| **v4** | `c8a7209` | 2026-09-06 | view **PROPOSALS** (очередь предложений, движок buildProposals), **AGENT COCKPIT**, **ACCEPTANCE DASHBOARD** (T-139). |
| **v5** | `900d31d` + `c8a7209` | 2026-09-06 | Действия + UI: `/action` (whitelist: workspace-open/workspace-status/link-open), tmux workspace launcher (`pb-<проект>`: main/files/tests/logs/local), localhost/Docker panel, link resolver, **Ctrl+K palette**, full-screen inspector (Shift+клик), compact mode, экспорт в MD/JSON (T-140). |
| **host** | `900d31d` | 2026-09-10 (код от 09-06) | `pipboy.py` — on-demand host: up/down/restart/status/open/serve, фиксированный URL `http://127.0.0.1:8123/`, авто-гашение по простою (PIPBOY_IDLE, 30 мин), read-only GET/HEAD, /healthz (T-137). |
| **rofi** | (T-138) | 2026-09-06 | `~/.local/bin/pipboy-rofi` — меню из rofi: Open/NEXT/DEPS/KANBAN/…/DOWN/TOGGLE. |
| **v6** | `c8a7209` | 2026-09-06 | SSE/live (T-128/ECO-018, verifier PASS): `watch_files()` sha256 registry+snapshot каждые 2 с, endpoint `GET /event` (event: file.watcher.updated + heartbeat :ping), фронт EventSource + polling-fallback, бейдж SSE LIVE. |
| **v7** | `e480d6c` + `c8a7209` | 2026-09-06 | Custom tools `ecosystem_*` (T-142/ECO-015): 7 read-only инструментов агента поверх `actions.py` — snapshot/next/blockers/query/dependencies/open-workspace(единственный не-read-only)/summary. NEXT-вью (readiness-движок READY/IN FLIGHT/AWAIT VERIFIER/BLOCKED) — это v3-наследование, но в v7 зеркальный Python-движок в actions.py. |
| **v8 spec** | `9c556ea` | 2026-09-10 | Spec `pipboy-v8-rethink.md`: 3 варианта визуального геймплея — **A «ВОКЗАЛ»** (пространственная canvas-карта), **B «БОРТОВАЯ ПАНЕЛЬ»** (HUD-виджеты), **C «ХРОНИКА»** (event-sourced таймлайн, → ECO-017). Рекомендация: B быстро → A поверх → C в фоне. |
| **v8/B** | `04f328c` | 2026-09-12 | Реализация варианта B: HUD widget grid M1–M3 в index.html (readiness-стакан, карта сигналов, спарклайны, cockpit, мини-канбан, live-фид). |
| **v8-BIS** | `1b5aa96` | 2026-09-12 | Обратная связь Rudra (HUD «красив, но пассивен») → `pipboy-v8bis-ux.md` + прототип `v8bis.html` **«КОМАНДНЫЙ ЦЕНТР»**: один экран = одна работа, task-deck (карточка в центре, actions/deps/blocks/tasks/evidence вокруг), deep-path навигация. |
| **v8-HITECH** | `3c4c3fd` + `1fa5f9a` | 2026-09-12 | Редирект §10: CRT-минимал → **стеклянный shell** (тёмное стекло, свет-данные, ambient-canvas); `v8bis.html` перерисован, `index.html` переосмыслен — стеклянный shell + вкладка **CENTRE** (task-deck). Порядок работ: P1 прототип (готово) → P2 вкладка CENTRE → P3 index-v8 + `/action op=summary` + events.jsonl. |
| **v9** | `b30f239` | 2026-09-12 | **TERRARIUM** (`pipboy-v9-terrarium.md` + мокап `terrarium.html`, ветка pipboy-v8-rethink): гибрид A+B+C — центральный WORLD CANVAS (карточки = растения, зависимости = лианы, capture-сигналы = капли, BLOCKED = гниль), режимы MAP/FOCUS/FEED, панель ЛАБОРАТОРИЯ (сервисы/порты/tmux/логи), биодок слева. Эстетика соларпанк×киберпанк. Backend не переписывается: добавляются `/action op=summary`, `generated/events.jsonl`, `/action op=logs`, capture read-state. Milestones: M1 мокап (готов) → M2 FEED+events.jsonl+капли → M3 scrub по истории → M4 agent live-sessions (после TUI hooks). |

## 2. Что реализовано и работает сейчас

### 2.1 Демоны/серверы/порты

| Компонент | Файл | Порт/состояние | Проверка |
|---|---|---|---|
| Pip-Boy host | `tools/ecosystem-map/pipboy.py` | `127.0.0.1:8123`, **RUNNING pid=2043283** на момент отчёта; idle 1800 с; состояние в `/tmp/mcode/pipboy-8123.{pid,log}` вне git | `pipboy.py status` → OK; /healthz OK; POST→501 |
| SSE | `GET /event` (в pipboy.py) | event: file.watcher.updated, heartbeat :ping 2 с, digest = sha256(registry.json + generated/snapshot.json), интервал опроса 2 с | verifier PASS 2026-09-06 (T-141) |
| Actions backend | `tools/ecosystem-map/actions.py` через `GET /action?op=…` | whitelist: `workspace-open`, `workspace-status`, `link-open`; незнакомый op → 400; GUI-запуски fire-and-forget Popen | node-обвязка 20/20 + playwright e2e (T-140) |
| tmux workspaces | actions.py | сессии `pb-<проект>` (main/files/tests/logs/local); известные порты: SERPlux 8000 API / 5173 preview, vault 8123 pip-boy | — |
| Capture watch-демон | `tools/telegram-capture/watch.py` | userbot Telethon: NewMessage → `inbox_queue.append`; `--once` = pull-режим; smoke-gated (без `--smoke`/credentials реальная подписка не стартует); systemd --user timer как fallback (pull) | полный круг 2026-09-07: 517 постов, 11 тем, 99-Inbox, маркировка 516/517 (коммит 8471030) |
| Inbox queue | `tools/telegram-capture/inbox_queue.py` | JSONL + flock; дедуп по message_id; команды count/ls/append/remove | тесты test_queue.py |
| Intake pipeline | `tools/telegram-capture/pipeline.py` | flatten → classify → score → map project (dotfiles/serplux/dv-hub/vault/new) → upgrade path → signals JSON с input_digest; read-only, no network | test_pipeline.py |
| TUI-плагины (dotfiles, symlink `~/.config/opencode/plugins/`) | `replay-budget.ts` (+helpers), `noop-guard.ts`, `input-security.ts`, `decision-queue-hook.ts` (глобальный `~/.config/.../decision-queue-hook.ts`) | хуки `experimental.chat.messages.transform`, `chat.message`, `event session.idle` | replay-budget live подтверждён; noop 9/9; input-security 14/14; DQ smoke 25/25 |
| Портированные TUI-инструменты | `tools/peers/peer_role.py` (claim/list/holds/release, append-only `generated/claims.jsonl`), `tools/verify-cache/verify.py` (tree-hash кэш гейтов), `tools/playwright-browser/browser.py` (goto/eval/click/fill/state-save/load, aria-ref) | stdlib/Playwright 1.62 | live smoke PASS |

### 2.2 Данные фронта

- `tools/ecosystem-map/registry.json` — canonical, 35 карточек ECO-001..035.
- `tools/ecosystem-map/generated/snapshot.json` — детерминированный snapshot
  (`observer.py`, перед открытием Pip-Boy: `python3 tools/ecosystem-map/observer.py`).
- `tools/ecosystem-map/data.json` — capture-данные; `signals-2026-07-12.json`
  в telegram-capture — 468 сигналов.
- HTML: `index.html` (v8-HITECH shell + CENTRE), `v8bis.html` (КОМАНДНЫЙ ЦЕНТР),
  `terrarium.html` (v9 мокап), `d3.v7.min.js`.

## 3. Как этим пользоваться

```bash
# Snapshot → поднять дашборд
python3 tools/ecosystem-map/observer.py
python3 tools/ecosystem-map/pipboy.py up          # или open — up + браузер
python3 tools/ecosystem-map/pipboy.py status|restart|down
PIPBOY_PORT/PIPBOY_HOST/PIPBOY_IDLE/PIPBOY_PYTHON/PIPBOY_DOCKER — env-переопределения

# Страницы (все через один host http://127.0.0.1:8123/)
/index.html       — v8-HITECH shell + CENTRE (текущая морда)
/v8bis.html       — прототип «КОМАНДНЫЙ ЦЕНТР» (task-deck)
/terrarium.html   — v9 TERRARIUM мокап (живые данные через тот же host)

# Из rofi
pipboy-rofi       # меню: Open/NEXT/DEPS/KANBAN/ACCEPTANCE/TASKS/BLOCKERS/AGENTS/MATRIX/WORKSPACE/SKILLS/REFRESH/STATUS/DOWN/TOGGLE

# Действия (SSE/action контракт)
GET /event                          — SSE-сигнал об изменении registry+snapshot
GET /action?op=workspace-open&project=X   — tmux pb-X (main/files/tests/logs/local)
GET /action?op=workspace-status&project=X — JSON: tmux/docker/порты
GET /action?op=link-open&target=…         — nvim/browser/tmux по викилинку/пути/URL

# Горячие клавиши UI
Ctrl+K — command palette; R — refresh; P — AUTO-polling (держит сервер живым);
Shift+клик — full-screen inspector; Esc — закрыть; #view — deep-link в hash.

# Агентский доступ (read-only custom tools, .opencode/tools/)
ecosystem_snapshot / ecosystem_next / ecosystem_blockers / ecosystem_query /
ecosystem_dependencies / ecosystem_summary (read-only) /
ecosystem-open-workspace (единственный не-read-only, требует подтверждения)

# Capture
python tools/telegram-capture/capture.py --topic <T>   # pull по теме
python tools/telegram-capture/watch.py                 # демон real-time
python tools/telegram-capture/watch.py --once          # разово слить непрочитанные
python tools/telegram-capture/inbox_queue.py count|ls|append|remove
python tools/telegram-capture/pipeline.py --input captures_all.json --output signals.json
# (нужен tools/telegram-capture/.env c TELEGRAM_API_ID/HASH; .venv + direnv)

# Peers / verify-cache
python3 tools/peers/peer_role.py claim --role "…" --scope "…"   # / list / release
python3 tools/verify-cache/verify.py [--force] [--json]
```

## 4. tools/* — что это и запускаются ли

- **`tools/peers`** — `peer_role.py` (stdlib): файл-реестр ролей параллельных
  сессий, порт P6 #31 из M Code. claim не блокирует (сигнализация), release по
  claim_id, реестр `generated/claims.jsonl` (gitignored, сейчас пуст). Письма/wake
  остаются M Code-only. **Запускается** (python3, без зависимостей).
- **`tools/ecosystem-map`** — фронт+бэкенд Pip-Boy (см. выше). **Работает, сервер жив.**
- **`tools/telegram-capture`** — capture-стек (README внутри): capture.py
  (Telethon pull), mark.py (реакции-маркеры), classify.py, inbox_queue.py,
  watch.py (демон), pipeline.py (signals), 8 тестовых файлов, conftest.
  **Запускается** при наличии `.env` (credentials) + venv; smoke-gated.
- **`tools/playwright-browser`** — browser.py, Playwright 1.62 + chromium 1234,
  read-only default. Live smoke PASS (T-134). Нюанс: под GUI M Code —
  `PYTHONPATH=.venv/lib/python3.14/site-packages`.
- **`tools/verify-cache`** — verify.py, tree-hash кэш гейтов. PASS.

## 5. Decision Queue (control-plane/decision-queue/)

- **Что это**: persistent machine-readable хранилище «карточек дилемм» —
  одна JSON-карточка на файл `YYYY-MM-DD-<slug>.json` (status pending/approved/
  rejected/deferred/resolved; risk low..critical; dilemma с options A/B/C,
  recommendation, resolution с approved_by/at). Схема — `SCHEMA.md`.
- **Карточки**: 4 ручных от 2026-09-05 — git-push-permission (recommendation A
  = push → ask), verifier-mutation, meta-agent-creation, decision-queue-storage.
- **`runtime-events.jsonl`** (106 записей): append-only лог runtime-событий
  permission.asked/replied от глобального плагина `decision-queue-hook.ts`
  (T-132; smoke 25/25). Metadata-only: нет shell/git/network, карточки не
  резолвит; graceful fallback при неизвестной сигнатуре permission.ask.
- **`decision-queue-smoke-test.mjs`** — pure-хелперы без живого рантайма.
- **Стадия**: инфраструктура готова и принята (T-131 verifier PASS 2026-09-05,
  T-132 smoke 25/25), **но**: карточки из JSONL не проецируются в `/decisions`
  (открыто в SCHEMA.md «future work»), live hook-fire после рестарта TUI —
  residual `[проверить]`; roadmap P6 #35 (сверить permission.ask payload и
  включить live hook fire) — ❌ не выполнено.

## 6. Открытые задачи (с приоритетом)

### P0 — блокеры
| ID | Суть | Комментарий |
|---|---|---|
| **T-143** (ECO-029 остаток) | Мутация живых tool-input в `applyReplayBudget` (prune без границы «текущего хода» + in-place) → инцидент пустых task-промптов субагентов 2026-09-07. Сначала контролируемый эксперимент, потом фикс (3 варианта в карточке) + дополнение smoke-теста | Единственный настоящий P0 в Active |
| T-136 | Doom-loop/no-op guard: `doom_loop: deny` в canonical jsonc — **red-line, вносит Rudra вручную**; live hook-fire после рестарта TUI `[проверить]` | Плагин готов, smoke 9/9 |

### P1
| ID/№ | Суть |
|---|---|
| T-123 | Verifier acceptance для v2-артефактов T-118..T-122 (перевод ECO-006/007 VERIFY→LIVE) |
| T-124 / ECO-002 | Telemetry P0: custom tools token-budget + audit-log → weekly report |
| T-134 (закрыта, но venv-нюанс) | Playwright в TUI — готова |
| T-132/P6 #35 | Decision queue live hook: сверить permission.ask payload, включить live hook fire, JSONL-проекция в /decisions |
| T-109/T-108/T-110 | AndroidOS bridge — **FROZEN BY USER, не активировать** |
| P6 #38 | session-flush runtime: подтвердить session.idle/compaction события |
| P6 #39 | Медиа-канал отчётов в TUI (файл + xdg-open) |

### P2
| ID/№ | Суть |
|---|---|
| T-125 / ECO-003 | Agent Workspace manifest pilot (после T-124) |
| T-127 | ecosystem-snapshot runtime smoke в live-сессии `[проверить]` |
| T-137/140/141 residuals | OSC8/tmux-линки `[проверить]` |
| ECO-030 | Doom-loop + no-op guard (карточка T-136) |
| ECO-033 | Peer-семантика TUI — claim-часть готова, письма/wake не переносятся |

### P3
| ID | Суть |
|---|---|
| T-128 | полностью закрыт v6 (SSE PASS); осталась строка OSC8 `[проверить]` |
| ECO-017 | Route-log / event-sourced memory (фонда для «ХРОНИКИ»/FEED v9) |
| ECO-035 | Capture → intake-сигналы: pipeline готов (полный круг 2026-09-07); осталось — панель CAPTURE в Pip-Boy, capture read-state, software-upgrade агент (T-079) |
| T-126/ECO-016 | Registry schema validation в pre-commit |
| T-080/T-083 | ecosystem-map как planning interface (v9 и есть этот шаг) |

### Roadmap P6 — не начато (❌)
| № | Задача |
|---|---|
| 35 | Decision queue live hook (см. T-132) |
| 38 | session-flush runtime |
| 39 | Медиа-канал отчётов |
| 41 | Майнинг релизов M Code (периодическая) |

### Решения-ожидания (нужен Rudra)
- Выбор/утверждение **v9 TERRARIUM** (мокап готов; index.html/v8bis.html
  заморожены до решения) и его milestones M2–M4.
- Внесение `doom_loop: deny` в canonical jsonc (red-line).
- Разрешение 4 дилемм decision-queue от 2026-09-05.

## 7. Ключевые файлы

- Спеки Pip-Boy: `docs/specs/pipboy-v8-rethink.md`, `pipboy-v8bis-ux.md`,
  `pipboy-v9-terrarium.md`
- Runbook: `07-Runbooks/ecosystem-kanban-runbook.md` (323 строки — свод по
  пользованию v3–v7 + custom tools + capture)
- Registry: `tools/ecosystem-map/registry.json` (35 карточек ECO)
- Backend: `tools/ecosystem-map/{pipboy,actions,observer}.py`
- Фронт: `index.html` / `v8bis.html` / `terrarium.html`
- Decision queue: `control-plane/decision-queue/{SCHEMA.md, runtime-events.jsonl,
  decision-queue-smoke-test.mjs, 4 карточки}`
- Capture: `tools/telegram-capture/{README.md, watch.py, inbox_queue.py, pipeline.py,
  classify.py, capture.py, mark.py}`
- Roadmap: `DEVELOPMENT-ROADMAP.md` § P6 (строки 100–127)
- Задачи: `TASKS.md` (Active: T-143, T-136, T-137, T-134, T-132, T-130…; Done:
  T-118..T-142)
