---
type: Runbook
title: Ecosystem Kanban Runbook — control plane для апгрейдов экосистемы
description: Как пользователю читать и вести Layers × Facets / Kanban control plane (canonical registry, Pip-Boy, TASKS, observer).
tags: [runbooks, operations, ecosystem, kanban, registry, pip-boy]
---
# Ecosystem Kanban Runbook

## Purpose

Как оператору (Max Rudra) пользоваться Kanban control plane экосистемы:
видеть всю картину апгрейдов, выбирать следующий шаг, управлять переходами
lifecycle через librarian/approval. Это runbook пользования, не дизайна:
архитектура, schema и gates — в [[06-Specs/Vault/ecosystem-registry]] и
[[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]; здесь на них только
ссылки.

## Карта источников правды (кто чем управляет)

| Слой | Файл | Роль | Кто мутирует |
|------|------|------|--------------|
| Canonical registry | `tools/ecosystem-map/registry.json` | единственный источник карточек ECO-NNN, слоёв/фасетов/агентов | только librarian-контур по approval |
| Operational queue | [[TASKS]] | оперативные задачи T-NNN по сессиям | librarian по ходу сессии |
| Pip-Boy | `tools/ecosystem-map/index.html` | read-only проекция (все views) | не мутируется как данные |
| Observer snapshot | `tools/ecosystem-map/generated/snapshot.json` | generated снимок (gitignored) | только `observer.py` |

Правило: **one source, multiple projections.** Pip-Boy и observer никогда
не редактируются как «данные»: правка карточки = правка registry.json,
правка задачи = правка TASKS.md. Дублирование карточек в других файлах
запрещено.

## Как читать Layers × Facets (view MATRIX)

- Слои (вертикаль): **L0 Kernel** (инварианты/контракты) → **L1 Control
  Plane** (маршрутизация/наблюдение/память) → **L2 Agent Workspace**
  (task contract/capsule/budget/verify) → **L3 Project Build** (проектные
  агенты/тесты) → **L4 Interface** (человек-читаемые поверхности).
- Фасеты (горизонталь, сквозные): memory · routing · telemetry ·
  verification · knowledge · interface.
- Ячейка = layer × primary facet; у карточки могут быть вторичные фасеты.
- Вопросы, на которые отвечает матрица: где пусто (пробел покрытия), где
  скопление (затор слоя), где VERIFY без движения (нужен runtime smoke).

## Как пользоваться Kanban (view KANBAN)

- **Master Kanban** — все карточки по lifecycle
  IDEA→RESEARCH→DESIGN→APPROVED→BUILD→REVIEW→VERIFY→LIVE→OBSERVE→IMPROVE→RETIRED.
- **Facet/project Kanban** — тот же board с включённым фильтром FACET
  (primary или secondary) или PROJECT: доска показывает только этот срез.
- Фильтры **LAYER / OWNER / PRIORITY / STAGE** и **SEARCH** (по
  id/title/owner/status_note) работают во всех registry-views; STAGE в
  Kanban прячет колонки — фокус на нужных стадиях.
- Пустые колонки (сейчас REVIEW/LIVE/OBSERVE/IMPROVE) — честный статус
  «пробел pipeline», не ошибка. RETIRED — история (Aider), не бэклог.
- С v3 (2026-09-06) каждая карточка несёт readiness-точку (● зелёная =
  READY к следующему шагу, жёлтая = IN FLIGHT, синяя = ждёт verifier,
  красная = BLOCKED, серая = DONE/LIVE) и сортируется внутри колонки по
  PRIORITY → id. Итог по карточке — в её detail-панели (секция Next step
  + EXPORT PROPOSAL) или в view NEXT.
- Клик по карточке → detail-панель: dependencies, blocks, acceptance,
  evidence (artifacts + tasks), rollback, status note.

## Как выбрать следующую карточку

1. Сверь [[04-Memory/active-context]] — текущий фокус и известные блокеры.
2. Открой view **NEXT** (v3, 2026-09-06): он сам считает readiness и
   показывает READY / IN FLIGHT / AWAIT VERIFIER / BLOCKED с причиной
   (deps, frozen-задачи, implementation BLOCKED) и ranked critical
   blockers. Кнопка `⧉ PROPOSAL` копирует текст перехода (например
   `Move ECO-NNN: DESIGN → APPROVED / Reason: dependencies satisfied /
   Approval required`) в буфер — read-only, применение через librarian.
3. Если NEXT недоступен — вручную: KANBAN, колонки BUILD/VERIFY, затем
   DESIGN/APPROVED; фильтр PRIORITY P0/P1; DEPS на незакрытые
   `depends_on`; BLOCKERS на ⛔ TASKS + drift + BLOCKED в status_note.
4. Прими решение и озвучь его librarian'у (свободный запрос или
   slash-команда). Librarian маршрутизирует исполнение; изменения
   canonical registry — только после твоего approval.

Readiness-семантика (движок NEXT, read-only): READY =deps закрыты и нет
блокеров; ⛔ BLOCKED = незакрытая зависимость / задача карточки в
Blocked/Frozen TASKS / implementation BLOCKED в status_note; по blocked-
карточке показывается цепочка «по цепочке: ECO-xxx (stage) ← …».
Критический blocker ранжируется числом транзитивно зависимых карточек
(«держит N»). Карточки DONE/LIVE из очереди исключаются.

## Живой observer: Refresh + polling (v3) + SSE live (v6)

- Кнопка `⟳ REFRESH` (клавиша `R`) перечитывает `registry.json` +
  `generated/snapshot.json` без перезагрузки страницы; бейдж `READ
  HH:MM:SS · HEAD <sha> · DRIFT n` показывает время чтения, HEAD снимка и
  число drift signals.
- Кнопка `AUTO: OFF/60s` (клавиша `P`) включает polling раз в 60 с —
  обычный re-fetch. Это **fallback**: с v6 (T-128/ECO-018) при живом хосте
  `pipboy.py` фронт подключается по **SSE** (`GET /event`, EventSource) и
  бейдж становится `… SSE LIVE · reconnects:N`.
- **SSE live**: серверный `watch_files()` хеширует `registry.json` +
  `generated/snapshot.json` каждые 2 с; при изменении digest толкает
  `event: file.watcher.updated` с seq+digest, клиент делает
  `refreshData()` сам. Heartbeat `:ping` каждые 2 с держит соединение и
  idle-активность (сервер не гасится по простою при открытой вкладке).
  Это не real-time по данным (по-прежнему детерминированный snapshot),
  а live-сигнал «файлы изменились — пора обновить».
- Типовой цикл обновления: правка TASKS.md/registry → `python3
  tools/ecosystem-map/observer.py` → Pip-Boy сам подтянет (SSE) или `R`.
- Deep-link на view: `index.html#next`, `#deps`, `#kanban`, …
  (location.hash).

## Переходы lifecycle (кто двигает карточки)

- Переход инициирует **librarian** (исполнение через субагентов) по
  подтверждению пользователя; самоперевод статусов агентом запрещён.
- **VERIFY→LIVE** — только с runtime evidence + независимым verifier
  acceptance (plan v2 gates). Сейчас LIVE/OBSERVE пустые — это честно.
- Откат назад — явным decision-note в `status_note` карточки (пример:
  ECO-006 VERIFY→BUILD 2026-08-31 при расширении scope).
- **RETIRED** — окончательно, карточка остаётся в registry для истории
  (пример: Aider, ECO-026).

## Как интерпретировать blockers / dependencies / acceptance

- **BLOCKERS** (view BLOCKERS) = TASKS ⛔/frozen + observer drift signals
  (`repo_missing`, `artifact_missing`, `task_ref_missing`,
  `registry_schema`, `task_blocked`) + implementation BLOCKED в
  status_note карточек. Registry оперативные блокеры не дублирует.
- **DEPENDENCIES** (view DEPS) = `depends_on` — структурные предусловия;
  «blocks» — обратные зависимости (кто ждёт эту карточку). Зависимость в
  DESIGN не блокирует research, но блокирует BUILD. С v3 сверху таблицы:
  критический путь («держит N» = транзитивно зависимые карточки) и
  целостность графа — cycles (depends_on должен быть DAG), orphans, no
  owner, no acceptance, frozen-блокеры; битые/RETIRED-зависимости
  помечены ⛔.
- **ACCEPTANCE** (view ACCEPT) = доказательство перехода lifecycle;
  evidence = artifacts + tasks + verifier-записи. Self-declared маркеры
  («PASS» от самого агента) — не evidence. С v4 (2026-09-06) dashboard
  даёт verdict на карточку (VERIFIER PASS / SELF-PASS / PARTIAL / NO
  EVIDENCE) и для VERIFY-карточек **LIVE gate** — что именно запрещает
  переход в LIVE (нет runtime evidence, frozen-задача, BLOCKED notice,
  verifier pending).
- **PROPOSALS** (view PROPOSALS, v4) = очередь предложений системы, не
  применяется молча: [APPROVE] переход lifecycle, [REVIEW] проверить
  drift signal, [BLOCKED] ждёт внешнего решения, [RUN] открыть workspace
  (tmux launcher — later gate). ⧉ копирует текст; подтверждение — только
  через librarian/approval.
- **AGENTS** (view AGENTS, v4) = cockpit: доступность (registry.agents.
  status), роль/scope, workload по `owner=` карточкам (всего/in-flight/
  ready/blocked), список карточек агента с ⛔-пометками. Производная от
  registry, не live-нагрузка.

## Как обновлять canonical registry / TASKS

- Новая карточка или переход: попроси librarian'а → proposal (diff
  registry.json) → твоё approval → правка → `python3
  tools/ecosystem-map/observer.py` → Pip-Boy отражает.
- Новая задача: строка T-NNN в TASKS.md; связка с карточкой — через поле
  `tasks` карточки (и Related в TASKS). TASKS — оперативный трекер,
  registry — структурное состояние; описания не дублируются.
- Не создавать вторых редактируемых копий карточек; проекции (Pip-Boy,
  snapshot) руками не править.
- После любой правки registry перегенерируй snapshot observer'ом —
  детерминированный, безопасно перезапускать.

## Static vs generated vs future live

- **STATIC** (committed, git): `registry.json`, `data.json` (skills-граф
  T-069), `index.html`.
- **GENERATED** (gitignored): `generated/snapshot.json` — обновляется
  запуском observer; отражает TASKS/проекты/git на момент снимка.
- **LIVE**: не заявляется. SSE `/event` ingestion — отдельный later gate
  (T-128 / ECO-018); до его реализации и подтверждения словами
  «real-time» никто не пользуется.

## Rollback и запрет silent mutation

- Rollback каждой карточки — в её поле `rollback` (view ACCEPT /
  detail-панель); общий rollback — git: registry/index — committed файлы,
  snapshot — простая перегенерация.
- Pip-Boy — **read-only projection**: никаких edit-кнопок; единственный
  localStorage — прогресс skills-графа T-069 (пользовательские отметки,
  не canonical-данные).
- **No silent mutation**: любое изменение канона — через librarian-контур
  с approval; локальные permission-overrides не ослабляют этот контракт.

## Хостинг Pip-Boy: pipboy.py (on-demand, v3)

Pip-Boy — статика, но `fetch()` не работает с `file://`, поэтому нужен
локальный HTTP-хост. `tools/ecosystem-map/pipboy.py` — постоянный
on-demand механизм (stdlib, без зависимостей):

- **Универсальный контракт**: Pip-Boy всегда живёт на
  `http://127.0.0.1:8123/` — один и тот же URL во встроенном браузере
  M Code GUI, в будущем браузере TUI и в любом внешнем браузере.
- `python3 tools/ecosystem-map/pipboy.py up` — поднять в фоне
  (idempotent: повторный вызов сообщит, что уже запущен); `down` —
  погасить; `restart`; `status`; `open [--view next]` — поднять и открыть
  ($PIPBOY_OPEN > $BROWSER > xdg-open); `serve` — foreground.
- **Авто-гашение**: без запросов N секунд сервер гасит сам себя
  (по умолчанию 1800 с = 30 мин; `--idle 0` — никогда). AUTO-polling
  Pip-Boy считается активностью: вкладка с AUTO держит сервер живым,
  закрытая вкладка → сервер сам погаснет.
- Read-only хост: только GET/HEAD (остальное → 501), bind 127.0.0.1;
  состояние — `/tmp/mcode/pipboy-<port>.pid|.log`; `GET /healthz` —
  JSON-статус (используется `status`/`down`, годится для будущих
  custom tools/TUI).
- Переопределения через env: `PIPBOY_PORT`, `PIPBOY_IDLE`,
  `PIPBOY_HOST`, `PIPBOY_OPEN`, `PIPBOY_PYTHON`.
- Если Pip-Boy открыт, а хост погашен — бейдж refresh покажет
  `DOWN · pipboy.py up`.

## Действия: workspace / link resolver / localhost-panel (v5)

Сервер пробрасывает безопасный `/action` endpoint (GET, whitelist операций
в `pipboy.py`, исполнение — `tools/ecosystem-map/actions.py`). Браузер сам
tmux/nvim/xdg-open не запускает, поэтому действия идут через сервер:

- **Workspace launcher** (WORKSPACE view + карточная панель): ⚡ WORKSPACE
  поднимает tmux-сессию `pb-<проект>` с окнами `main/files/tests/logs/
  local` (files — nvim) и attach'ит в терминал; ☑ STATUS тянет порты/docker
  системы; ▤ DIR открывает карточку проекта в Neovim. Внешний tmux, не
  форк OpenCode.
- **Localhost/Docker panel** — в WORKSPACE: порты из `KNOWN_PORTS`/registry
  (health через connect), docker — если `PIPBOY_DOCKER=1` (иначе отключено
  и помечено). Пулл статуса — автоматический при входе во view.
- **Link resolver** — кликабельные `wikilinks` и пути в полях карточки
  (acceptance/review/risk/rollback/status_note/artifacts): действия `nvim`
  (alacritty -e nvim), `browser` (xdg-open), `tmux` (окно в pb-vault).
- GUI-запуски — fire-and-forget (`Popen`): не блокируют сервер, иначе open
  виснет, пока открыто окно. Whitelist: `workspace-open / workspace-status
  / link-open / capture-scan`; на всё прочее — 400.
- **Capture / intake-сигналы** (CAPTURE view): `⟳ REGEN` прогоняет
  `tools/telegram-capture/pipeline.py --dry-run` (детерминированный intake:
  capture → classify → relevance → project → upgrade path), `☰ СКАНИРОВАТЬ`
  читает существующий `signals.json`. Read-only: regen не трогает входы
  `captures_all.json` и не проставляет реакции. Сигналы группируются по
  проектам (dotfiles/SERPlux/dv-hub/vault/new); `error`/дубли исключены.

## Живой слив @inbox_tools (не копить группу)

Капчер — боевая лошадка Rudra: посты в `@inbox_tools` сыплются постоянно,
группа не должна накапливаться. Два слоя слива, оба пишут в staging-очередь
`tools/telegram-capture/inbox-queue.jsonl` (JSONL + flock, gitignored):

- **Демон (real-time, основной)** — `python3 tools/telegram-capture/watch.py
  --smoke`: Telethon `events.NewMessage` → append в очередь на каждый новый
  пост. Живёт постоянно (systemd --user), держит Tor/сессию.
- **Таймер (pull, fallback)** — `capture.py --topic <T>` идемпотентен (ставит
  👍, повторно не дёргает); для отставания: `capture.py` → `inbox_queue.append`
  → `pipeline.py --input inbox-queue.jsonl`. Под `systemd -user` timer.

Цикл записи: пост попал в очередь → классифицирован (`classify_batch`) →
помечен категорийной реакцией (`mark.py`) → удалён из очереди (remove).
`CAPTURE_QUEUE` (env) переопределяет путь очереди.

Боевое использование/тестирование слива — см. соседнюю сессию (live `@inbox_tools`,
не только софт); здесь — механика.

## Горячие клавиши и UI (v5)

- `Ctrl+K` — **command palette**: переход по views, поиск карточки (Enter →
  карточная панель), workspace-запуск, actions (refresh/toggle AUTO/export/
  compact). `Esc` — закрыть.
- `Shift+клик` по карточке — **full-screen inspector** (полный body карточки
  в модальном окне); `R` — refresh, `P` — AUTO-polling toggle.
- **Compact mode** — через palette; **Export** текущего view — Markdown
  (блок-цитата) или JSON (карточки + их `next` readyness) в буфер.

## Custom tools ecosystem_* (v7)

Агент видит ту же картину, что и пользователь, без открытия Pip-Boy:
`.opencode/tools/` — 7 read-only инструментов поверх `actions.py`
(Python-бэкенд, тот же readiness-движок, что и фронт):

- `ecosystem_snapshot` — детерминированный observer snapshot (существующий).
- `ecosystem_next` — READY/BLOCKED/AWAIT VERIFIER/IN-FLIGHT с причинами.
- `ecosystem_blockers` — blocked-карточки + drift + frozen TASKS.
- `ecosystem_query` — текстовый поиск по карточкам (+facet/project).
- `ecosystem_dependencies` — depends_on/blocks/critical path/orphans.
- `ecosystem_summary` — readiness + vault_head + drift одной строкой.
- `ecosystem_open_workspace` — единственный НЕ read-only: поднимает tmux
  `pb-<проект>`, требует подтверждения пользователя (side-effect вне vault).

Статус: код + `tsc --noEmit` + `py_compile` + Python-выводы проверены
2026-09-06 (T-142). **Runtime loading в live-сессии — `[проверить]`**
(по конвенции T-127/ECO-015 готовность не заявляется до smoke в новой
сессии; tools грузятся при старте, а не on-the-fly).

## Запуск из rofi (pipboy-rofi)

`~/.local/bin/pipboy-rofi` — фронтенд Pip-Boy для rofi, протокол
rofi-script(5):

- **Drun**: приложение «Pip-Boy» (`~/.local/share/applications/
  pipboy.desktop`) — поднимает хост и открывает браузер.
- **Custom modi**: `rofi -show pipboy` (или Tab в rofi) — меню
  действий: Open / NEXT / DEPS / KANBAN / ACCEPTANCE / TASKS /
  BLOCKERS / AGENTS / MATRIX / WORKSPACE / SKILLS / PROPOSALS /
  REFRESH (свежий snapshot через observer + открыть) / STATUS / DOWN /
  TOGGLE.
- Напрямую: `pipboy-rofi <action>` — те же действия из терминала или
  хоткея (например `Key([mod], "b", lazy.spawn("pipboy-rofi open"))`
  в qtile).
- Нюансы, учтённые в скрипте: `notify-send` ломается от AppImage-маунта
  в `LD_LIBRARY_PATH` (фильтруется перед вызовом); dunst — dbus-активация
  от `graphical-session.target` (в qtile target inactive — при сбое
  уведомлений поднять `systemctl --user start dunst.service`); `sys.executable`
  под M Code GUI указывает на AppImage — pipboy.py резолвит python сам.

## Типовой цикл (2 минуты)

1. `python3 tools/ecosystem-map/observer.py` — свежий snapshot (или
   REFRESH в rofi-меню Pip-Boy).
2. rofi → Apps → **Pip-Boy** (или `rofi -show pipboy` → NEXT; или
   `pipboy-rofi open --view next`).
3. NEXT → READY/BLOCKED → PROPOSAL → решение → librarian; `R`/AUTO —
   пересинхронизация после правок; `pipboy.py down` — или просто закрой
   вкладку и жди авто-гашения.

## Ссылки

- Schema/контракт: [[06-Specs/Vault/ecosystem-registry]] (canonical),
  [[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]] (план v2).
- Операционная модель: [[07-Runbooks/vibecoding-operator-handbook]];
  история практики: [[07-Runbooks/vibecoding-changelog]].
- MCP-политика: [[06-Specs/Vault/mcp-readonly]] (implementation BLOCKED).
