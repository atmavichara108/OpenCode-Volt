---
type: Active Context
title: Активный контекст
description: Ecosystem Upgrade Plan v2 MVP реализован и подтверждён независимым verifier PASS 2026-08-31 (T-118..T-122 Done). Phase 1 завершена 2026-08-04. Модельная политика Luna + DeepSeek Go сохранена.
tags: [memory]
timestamp: 2026-08-31
---

# Активный контекст

> Автоматически обновляется librarian. Читается при старте каждой сессии.

## Текущий фокус
- **Ecosystem Upgrade Plan v2 — MVP реализован и верифицирован
  2026-08-31 (независимый verifier acceptance — PASS; T-118..T-122 →
  Done):** созданы plan v2
  ([[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]), registry spec
  ([[06-Specs/Vault/ecosystem-registry]]) + canonical
  `tools/ecosystem-map/registry.json` (8 карточек ECO-001..008, Layers ×
  Facets, lifecycle IDEA→RETIRED), read-only детерминированный observer
  (`tools/ecosystem-map/observer.py` → gitignored
  `generated/snapshot.json`), Pip-Boy v3 multi-view (MATRIX/KANBAN/
  PROJECTS/AGENTS/BLOCKERS/WORKSPACE; static/generated метки, real-time
  не заявляется), MCP spec ([[06-Specs/Vault/mcp-readonly]],
  implementation BLOCKED) + custom tool `.opencode/tools/
  ecosystem-snapshot.ts` (runtime loading `[проверить]`). Research
  artifact получил append-only Addendum 2026-08-31 (OpenCode
  UI/UX/Workspace по докам; TUI widgets/OSC8/tmux `[проверить]`).
  Aider retired из roadmap; tree-sitter/ast-grep — independent tools.
  После verifier PASS 2026-08-31: ECO-006/007 → VERIFY (MVP
  acceptance), ECO-001 policy-артефакт покрыт; ECO-008 остаётся DESIGN
  (implementation BLOCKED). Residuals открыты: MCP runtime, custom tool
  runtime loading (T-127), live real-time (T-128), OSC8/tmux,
  telemetry/workspace (T-124/T-125). TASKS: T-118..T-122 Done
  (2026-08-31), T-123..T-128 (gates). Без commit/push.
- **Следующий actionable focus:** T-127 custom tool runtime smoke;
  T-124 telemetry P0. ECO-006/007 в LIVE не переводить до runtime
  evidence (live-режим — T-128 later gate); MCP runtime остаётся
  BLOCKED. (T-123 verifier acceptance — PASS зафиксирован 2026-08-31 в
  session-log; статус T-123 в TASKS не менялся — вне scope финализации.)
- **Global HITL + `/flush` + `/dream` (2026-08-30):** созданы/приняты global
  human-in-the-loop контракт (`~/.config/opencode/AGENTS.md`, ADR-009,
  runtime-гейты `task: ask`/`edit: ask`) и команды `/flush`/`/dream`.
  Acceptance HITL/`/flush` — verifier PASS (после reviewer evidence); live
  smoke выполняется в соседней сессии, его результат здесь не зафиксирован.
  Создан spec `06-Specs/Vault/risk-based-orchestration.md` (status:
  proposed); реализация отложена до отдельной сессии.
- **Следующий actionable focus (2026-08-30):** запустить отдельную сессию по
  `06-Specs/Vault/risk-based-orchestration.md` (review/decision по spec);
  реализацию spec не выполнять в текущей сессии.
- **SERPlux local-first release workflow (2026-08-30):** authoritative specs и
  workflow находятся в `/home/rudra/Projects/serp/docs/specs/`; Vault SERPlux
  specs archived/non-authoritative как approved exception. Единая точка входа
  — `/release v1.0.2: <описание>`: intake/normalization → local spec/plan →
  approval → build/tests/reviewer/verifier → до 5 fix loops. `/spec` только
  read-only для existing specs, `/prompt` optional diagnostic. После verifier
  PASS — `READY_FOR_USER_INTEGRATION`/`AWAITING_USER_REVIEW`; `/dream`/flush,
  commit, tag, push и deploy не запускаются автоматически.
- **Следующий actionable focus:** после подготовки и проверки clean state
  включить paid feature v1.0.2 через `/release`; release не считать Done до
  прохождения согласованных gates и пользовательского handoff.
- **Decision (2026-08-30):** Coordination Bridge заморожен пользователем. T-109,
  T-108/system-ops и T-110 не активировать; не выполнять permission experiments,
  root, MCP или bridge integration. AndroidOS возвращён к local-first работе:
  `AGENTS.md` → `/android-plan`/свободный запрос, status → plan → approval →
  implementation. Dotfiles открывать отдельно только для `/sysaudit`; Vault
  `/ask` даёт контекст без обязательного копипаста отчётов.
- **Runbook layer (2026-08-17):** создан `07-Runbooks/` как отдельный operational
  use layer; handbook фиксирует текущее применение, changelog — подтверждённые
  shifts. Следить за freshness только по реальным изменениям практики.
- **Модельная политика (2026-08-25):** Luna + DeepSeek Go сохранена без
  изменений; capability-routing не меняет model-routing.
- **Текущий фокус:** capability-routing paused after v0.1 checkpoint. Exact
  smokes для researcher, reviewer, sysop и orchestration подтверждены;
  дальнейшие permission/runtime experiments не продолжаются в текущем
  рабочем контексте. Automatic router,
  prompt-normalizer и task-compiler не реализованы. T-109 — historical
  docs-only bootstrap Coordination Bridge;
  bridge создан в AndroidOS и остаётся uncommitted/untracked, structural smoke записан, independent
  reviewer/verifier gates для T-109 pending. Baseline SHA не является provenance bridge.
  Capability-routing имеет частичный rollout: named researcher и reviewer smoke
  подтверждены только scoped evidence, sysop — только exact global primary
  smoke. AndroidOS environment prep/sysop report больше не являются
  предварительным шагом; следующий шаг — независимый `/android-plan`.
- **Coordination Bridge:** выбран единый canonical Git-backed file
  protocol/contract, не отдельный bridge-agent. Будущие agent facade/command и
  MCP facade только optional, без реализации и без зависимости телефона.
  Пользовательский operator guide добавлен в
  [[07-Runbooks/coordination-bridge-operator-guide]]. Реализация
  T-109 frozen by user и не активируется; optional MCP T-110 frozen/deferred.
- Глобальная `/bridge` остаётся historical frozen artifact в dotfiles source
  `opencode-global/.config/opencode/command/bridge.md`; не вызывать и не
  активировать после freeze.
- **Текущий blocker T-109:** reviewer smoke подтверждён только для exact global
  smoke; это не acceptance Coordination Bridge. T-109 frozen by user; не
  активировать, не симулировать `PASS` и не менять статус на Done.
- Телефон подтверждён через ADB: Redmi 2510ERA8BG/flourite, Android 16/API 36,
  SM7635, arm64-v8a, около 11.1 GiB RAM, 464G storage, ADB authorized.
- Подтверждён ноутбук sysop: Lenovo ThinkPad P51, Manjaro, i7-7820HQ, около
  15.3 GiB RAM, NVMe 500GB, Intel+NVIDIA.
- Capability-routing rollout продолжается отдельными evidence-gated шагами;
  предыдущие temporary general fallbacks отмечены как процессуальная ошибка.
- **Orchestration smoke PASS (2026-08-29):** independent verifier подтвердил
  exact `vault` read-only chain `librarian route selection -> researcher ->
  reviewer -> verifier`, sequential, без `general` fallback и self-marker.
  Runtime automation/router не внедрён; это не общий automatic router claim.
- **Предыдущий контекст:** design gate — `PASS`; researcher runtime extraction
  подтверждён только в scope named smoke evidence. Создан dotfiles-local
  `system-ops` skeleton, но runtime/root execution не подтверждены.
- **Incident symptom (2026-08-25):** при acceptance verification global
  `researcher` verifier task был отменён пользователем после зависания модели
  в бесконечном цикле. Это symptom/incident observation, root cause unknown;
  не считать доказательством дефекта `researcher`, `verifier`, модели, task
  runtime или routing. Повторный запуск тем же маршрутом отложен до
  investigation; researcher runtime extraction paused pending a controlled
  probe.
- **SERP Factory productization discovery (2026-08-21):** read-only аудит выявил
  мультиклиентный продукт-прототип, но не фабрику продуктов. Recommended next
  step — decision gate по модели поставки и tenancy/product/deployment boundaries;
  до подтверждения решения код не писать.
- **ChaT:** bootstrap завершён 2026-08-14. Интервью Макса остаётся следующим
  проектным шагом после capability-routing rollout.
- **Phase 1 (kernel stabilization) ЗАВЕРШЕНА 2026-08-04.** Все задачи
  T-084..T-089 + T-096..T-098 перенесены в Done с датой. Коммиты:
  vault (память), SERPlux (агентский слой), dotfiles (`done.md`).
- **Модель general (vault `opencode.json`):** `opencode-go/gpt-5.6-luna`.
  Историческая запись о временном переводе субагентов на бесплатные Zen
  сохранена в `facts.md`.
- **Следующий фокус:** T-101, AndroidOS PA MVP planning через
  `/android-plan <PA MVP intent>`; bridge acceptance не требуется.
- **Следующий gate:** Phase 2 (SERPlux first adoption по ecosystem upgrade
  plan v1) + dotfiles/global hardening (Phase 3). dv-hub — recovery case,
  не первая цель.
- **T-107:** исследовать symptom бесконечного цикла verifier task до root cause
  и исправления; forensic уточнение и безопасный probe protocol записаны в
  [[06-Audits/2026-08-25-capability-routing-design-note]] и
  [[04-Memory/session-log/2026-08-25]]. Feasibility check показал, что CLI
  `opencode run --agent researcher` не гарантирует запуск subagent, per-run
  запрет `task` не предоставляется, а shell `timeout` не гарантирует abort
  серверной сессии; controlled probe пока не выполнен, задача открыта.
- **Historical dotfiles-local `system-ops` (2026-08-25):** agent skeleton создан, но
  runtime/root execution не подтверждены. `sysop` остаётся read-only; маршрут
  high-risk apply: `sysop` audit → `planner` plan → `system-ops` apply →
  `verifier`/post-check. Root apply только через explicit approval; edit/task
  deny, dangerous operations deny-safe. T-108 frozen by user; live evidence не
  требуется для возобновления AndroidOS.
- **Frozen order:** T-107/T-108/T-109/T-110 не активировать в рамках bridge
  freeze. Не объявлять задачи Done без acceptance; T-101 остаётся следующим
  planning step и не считается Done.
- **T-108 intake (2026-08-29):** protocol report сохранён в canonical
  AndroidOS bridge как `AOS-T108-001`, `H-108-001`, `E-108-001`. Named `sysop`
  подтверждён только как read-only; system-ops route недоступен. Статус
  `BLOCKED/UNROUTABLE` до librarian decision о границе sysop vs system-ops;
   `general` не назначался. Bridge-файлы uncommitted/untracked и
   `unverified/planned`.
- **T-108 evidence persistence fix (2026-08-29):** в dotfiles `system-ops`
  получил только scoped edit/external-directory access к canonical
  `bridge/evidence/**`; global prompt требует новый append-only evidence с
  report, commands/results/exit codes/gaps/full SHA refs и `BLOCKED` при
  невозможности записи. Runtime write/live evidence ещё не подтверждены.
- **T-108 root cause (2026-08-30):** вероятная реальная причина runtime blocker
  установлена: canonical `system-ops.md` содержал более приоритетный scalar
  `edit: deny`, перекрывавший project scoped object. Policy приведена к
  object deny-default: edit allow только для нового evidence и external read
  allow только для `tasks/**`, `handoffs/**`, `evidence/**`; task deny и
  dangerous bash deny сохранены. Task owner передан `system-ops`, новый
  `H-108-002` ожидает `E-108-003`; fresh-session verification ещё pending,
  T-108 остаётся BLOCKED.
- **Residuals `[проверить]` (честно открыты, не закрыты):**
  - T-089/T-097: commit-guard на реальном `git commit` (real commit smoke)
    и реальный compaction event session-dispatch — безопасно
    непротестированы (нужна живая сессия в serp, не vault).
  - T-085: merge behavior permissions allowlist (local override global) —
    наблюдение, strict isolation не объявлена.
  - T-089: payload capture для subagent/task в `tool.execute.after`
    (полный `verifier PASS` marker gate) — не подтверждён.
  - T-084: реальный compaction session-dispatch.
- **Открытый техдолг (по решению пользователя, реализуется ИМ при
  проектной работе):** sync test-metrics claims в SERPlux
  (`serp/docs/techdebt.md`, запись 2026-08-04 «Test-metrics claims не
  синхронизированы с каноном»): README/AGENTS/CANON/verification/
  user-guide/TASKS содержат 224/172/95/111, канон = 256/256 executed на
  HEAD `f7ccd3e`, definitions 212. Записано идемпотентно и централизованно.
- **Working tree:** изменения документации и модельной конфигурации Vault
  незакоммичены. Отдельно сохраняются pre-existing bootstrap/WIP-изменения в
  ChaT, dotfiles и SERPlux; они не откатываются и не объявляются частью этой
  сессии.

## Активная задача
 - **Текущий шаг:** AndroidOS PA MVP planning через `/android-plan`; bridge и
   T-108/T-109/T-110 frozen by user, bridge не вызывается. Permission/runtime
   experiments не продолжаются. Historical bridge WIP и evidence не удаляются и
   не объявляются PASS.
 - Capability-routing paused after v0.1 checkpoint; дальнейшие permission/runtime
   experiments не являются текущим рабочим шагом. Automatic router,
   prompt-normalizer и task-compiler не реализованы.
- SERP Factory: сначала обсудить decision gate по модели поставки и границам,
  implementation не начинать до подтверждения.

### Capability-routing rollout (2026-08-29; partial, evidence-gated)
- Named `read-research -> researcher` smoke завершён с `PASS`; результат
  подтверждён verifier в route log.
- Runtime smoke подтверждён только в scope этого evidence; общий researcher
  rollout не заявлен.
- Named `quality-review -> reviewer` live smoke PASS подтверждён только в
  scope `global` этого evidence; reviewer quality verdict и verifier acceptance
  разделены. Max steps — minor, не failure.
- Exact global primary sysop smoke PASS подтверждён independent verifier;
  `system-audit -> sysop` имеет статус `runtime-smoke-confirmed` только в этом
  scope. Это не orchestration/general rollout; `system-ops` apply отдельно.
- Orchestration exact smoke PASS подтверждён independent verifier; общий
  automatic runtime router не внедрён.
- Gaps закрыты для R1/F1/F2/F3; остаются negative deny smoke, local extension
  merge, uncommitted artifacts и literal tool output limits.

### Capability-routing rollout design (2026-08-25)
- Созданы [[02-Methods/capability-routing]] и [[06-Audits/2026-08-25-capability-routing-design-note]].
- Design gate пройден: verifier после фикса ложного partial status в `00-INDEX` — `PASS`.
- Решён sequence: `researcher → reviewer → sysop → orchestration integration`;
  guardian и prompt-engineer/task-compiler идут после базового routing.
- Зафиксированы global kernel + local extensions, named dispatch, registry,
  fallback `UNROUTABLE`, mutability/risk gates и reviewer != verifier.
- T-092 описан как будущий prompt-normalizer/task-compiler interface без
  runtime; T-094 остаётся на approval gate и не стал Method.
- T-077/T-092/T-093/T-094 остаются active design/approval substeps; T-094 не
  закрыт до explicit approval.
- AndroidOS T-101 возвращён в Planned как следующий PA MVP planning step после
  freeze bridge; реализация не начата и Done не заявлен.

## Завершённые изменения (все сессии)
- [x] **Phase 1 kernel stabilization (2026-08-04, T-084..T-089, T-096..T-098):**
  plugin loader/compaction contract (named exports, `event` catch-all,
  `experimental.session.compacting`), SERPlux plugin stabilization
  (commit-guard ESM fix, env-guard webfetch gap), project-local
  `.opencode/agents/verifier.md` (acceptance-only, VERDICT PASS/FAIL),
  global `/done` memory-model branches (vault-based / docs-based / fallback),
  test-metrics канон `serp/docs/test-metrics.md` (executed 256/256 на
  HEAD f7ccd3e, definitions 212), техдолг-запись sync claims, execution
  sequence note (Phase 1→4). Коммиты во все 3 репо.
- [x] (T-098) WIP SERPlux смёржен в HEAD f7ccd3e; executed run = 256/256
  pass, exit 0; `docs/test-metrics.md` обновлён до канона; sync claims →
  техдолг (за пользователем).
- [x] (T-097) Live Bun import/registration всех 4 SERPlux плагинов +
  function-level hook fire подтверждены; residuals (real commit smoke,
  real compaction dispatch) открыты `[проверить]`.
- [x] (T-096) Execution sequence note: SERPlux first → dotfiles/global
  hardening → dv-hub recovery; global layer на полшага впереди.
- [x] README.md — визитка репозитория как VibeOS (для GitHub, основа для лендинга)
- [x] LICENSE — GPL-3.0 (copyleft + коммерция разрешена) + секция в README + упоминание фонда инженера
- [x] SERP Factory — SERPlux как продукт фабрики. Архитектура: ux-dev, infra-dev, команды /interface /container /deploy. multi-agent-pipeline: Factory variant.
- [x] Имя пользователя: Макс/Max → Max Rudra / Rudra / mr — обновлено во всех файлах волта + LICENSE + facts.md
- [x] distill-pipeline + multi-agent-pipeline метод — дистилляция пайплайнов
- [x] dotfiles v3: полная мульти-агентная архитектура (8 агентов, 10 команд, память, UX)
- [x] VibeOS v0.2.0–v0.2.3 — дашборд, ревью 17 багов, dotfiles, distill-pipeline
- [x] opencode.json, config.md, facts.md, 00-INDEX, Architecture.md — обновлены
- [x] Модель librarian: Claude Sonnet 4.6 → DeepSeek v4-flash-free
- [x] OKF v0.1 — полная архитектура волта, 6 методов, 4 карточки проектов, память, трекер
- [x] SERPlux: агенты ui-dev + infra-dev, команды /interface /container /deploy, карточка актуализирована
- [x] Централизованное удаление claude-mem из экосистемы (плагин, AGENTS.md, memory-management.md, бэкап)
- [x] Инфраструктурный техдолг Уровня 0 (T-056): модель librarian qwen3.7-plus, verifier whitelist, факты, /done, session-flush
- [x] Убрана привязка `agent: librarian` из /done — команда работает во всех проектах
- [x] Создан `01-Reference/global-config.md` — документация глобальной инфраструктуры (~/.config/opencode/)
- [x] Фикс commit-guard (T-057): pytest-вывод захвачен через `.quiet()`, TUI чист
- [x] (T-058) SERPlux plan-агент: создан `.opencode/agents/plan.md` с `task.build: allow`. plan делегирует исполнение build через task-tool, сам не редактирует (edit/bash deny). Inline-определение убрано из opencode.json.
- [x] SERPlux T-001: новая схема БД (clients/positions/labels) + migrate.py + тесты
- [x] SERPlux T-002: режим `domains` разметки + справочник `domain_labels` + `confidence` (без LLM)
- [x] SERPlux T-003: идемпотентность migrate.py (любое состояние БД)
- [x] SERPlux T-004: расширение POST /run (client_id, label_mode=domains default, force_relabel) + валидация. 111/111 тестов.
- [x] T-059: verifier-pattern в dotfiles — `.opencode/subagent/verifier.md`, builder whitelist
- [x] T-060: closed-loop в dotfiles — `.opencode/command/loop.md` (build → verify → fix, HARD STOP 5)
- [x] T-061: flush-протокол (dotfiles + vault) — pre-compaction flush, /flush команда, planner scoped edit, librarian flush перед compact
- [x] T-062: tools/telegram-capture/ — рабочий MVP. capture.py + mark.py + config.py, 39 pytest-тестов, Tor SOCKS5 proxy (обход блокировки Telegram), первый capture (тема «Софт», 3 поста). 3 captures в 99-Inbox (C-001..C-003). Скилл capture + команда /capture. /inbox восстановлена. direnv + .venv внедрены в волт. Коммит 768b786 запушен.
- [x] Полный capture 584 постов (11 тем), классификация, 10 паттернов зафиксировано (коммит 13ec706)
- [x] Создан гайд-карточка стороннего софта GTweak — 01-Reference/tools/GTweak.md. Полный гайд с риск-классами операций и чек-листом для использования на чужой машине. Добавлен в 00-INDEX раздел "Сторонний софт".
- [x] T-069: tools/ecosystem-map/ — интерактивная Pip-Boy карта экосистемы. 468 постов → 36 навыков → 326 инструментов. 4 вкладки (НАВЫКИ/СПОСОБНОСТИ/ИНСТРУМЕНТЫ/ПРОЕКТЫ). CRT-эффекты, фильтры, привязка к проектам. Второй инструмент VibeOS.

## Отложено (P5 будущее)
- T-015: Telegram-бот — эволюция T-062 (команда /capture первый шаг)
- T-016: /project-upgrade — автоматический апгрейд проектов
- T-017: Команда /project-upgrade
- T-046: R-005 — Project Orchestrator (оркестрация из волта всеми проектами + Android)
- **Напряжения:** память (flush-протокол), теория vs практика

## Открытые вопросы
- Когда возвращать Go-модели субагентам (T-048/T-049)?
- Как закрывать residuals Phase 1 (real commit smoke / compaction dispatch) — нужна живая сессия в serp?

## Последнее обновление
2026-08-31 — **Финализация Ecosystem Upgrade v2 (после независимого
verifier PASS):** T-118..T-122 → Done (2026-08-31; verifier acceptance —
PASS, evidence-раздел в [[04-Memory/session-log/2026-08-31]]).
registry.json: ECO-006/007 → VERIFY (MVP acceptance подтверждён),
ECO-001 policy-артефакт покрыт PASS, ECO-008 остаётся DESIGN
(implementation BLOCKED; MCP/custom-tool runtime готовностью не
объявляется). Plan v2 §6/§8 и registry-spec §9/§10 — краткие
статус-правки. Residuals честно открыты: MCP runtime, custom tool
runtime loading (T-127), live real-time (T-128), OSC8/tmux. facts.md не
тронут. Без commit/push.

2026-08-31 — **Ecosystem Upgrade Plan v2 MVP:** реализованы plan v2,
registry (spec + canonical json), observer (детерминированный read-only
snapshot), Pip-Boy v3 multi-view, MCP spec (BLOCKED) + custom tool
ecosystem-snapshot; research addendum UI/UX/Workspace. Все
implementation-статусы честные: verifier acceptance pending (T-123),
runtime-claims `[проверить]` (custom tool loading, OSC8, tmux). Без
commit/push. Детали: [[04-Memory/session-log/2026-08-31]].

2026-08-28 — **End-session flush: Coordination Bridge:** текущая сессия
завершена; создана спецификация
`06-Audits/2026-08-28-androidos-coordination-bridge-spec.md` и добавлена planned
T-109. Следующий фокус — отдельная реализация Coordination Bridge после
read-only bootstrap и smoke test. Capability-routing продолжается частичным
evidence-gated rollout; AndroidOS environment prep/sysop report и `/android-plan`
следуют после bridge bootstrap. Незакоммиченные изменения ожидают отдельного
commit/push.

2026-08-17 — **Временная модельная политика подтверждена**:
primary/сложные роли используют `opencode-go/gpt-5.6-luna`, дешёвые
read-only/research/reviewer/verifier — `opencode-go/deepseek-v4-flash`.
Доступность подтверждена `opencode models`, merged config debug проходит;
для применения нужен перезапуск OpenCode. Изменения незакоммичены; pre-existing
bootstrap/WIP в ChaT, dotfiles и SERPlux сохранены. Следующий фокус —
capability-routing rollout.

2026-08-17 — **Создан runbook operational layer**: `07-Runbooks/` отделён от
Methods, Audits и `AGENTS.md`; следующий фокус сохраняется за capability-routing
rollout, затем Phase 2/3 adoption и hardening. Residuals не изменены.

2026-08-14 — **Bootstrap ChaT завершён; модель general обновлена**:
синхронизированы проектная карточка
и память волта. `general` использует `opencode-go/gpt-5.6-luna`.
Следующий шаг — интервью Макса. Phase 1 ранее завершена
2026-08-04: T-084..T-089, T-096..T-098 Done.
Исторический перевод meta/verifier на бесплатные Zen-модели отмечен в facts.md.
SERPlux: executed 256/256 на HEAD f7ccd3e, канон test-metrics обновлён,
техдолг sync claims записан (за пользователем). Коммиты: vault (память),
SERPlux (агентский слой), dotfiles (done.md). Residuals `[проверить]`
открыты в facts.md. Следующий gate: Phase 2 (SERPlux adoption) / Phase 3
(dotfiles hardening) / residuals через живую сессию.

2026-08-29 — **Researcher smoke PASS:** named `read-research -> researcher`
завершён с normal completion, без general fallback; PASS подтверждён verifier.
Runtime dispatch подтверждён только для конкретного smoke в
`04-Memory/route-log/`; общий rollout не заявлен. Reviewer smoke подтверждён
отдельно и scoped; exact global primary sysop smoke PASS подтверждён
independent verifier. `system-audit -> sysop` имеет scoped
`runtime-smoke-confirmed`; orchestration не внедрена.

2026-08-29 — **Sysop primary smoke PASS:** exact global primary
`system-audit -> sysop` подтверждён независимым verifier; route scoped, без
general fallback. Gaps: negative deny smoke, local extension merge,
uncommitted artifacts, orchestration и literal tool output limits. T-109
остаётся `BLOCKED`.

2026-08-29 — **Reviewer smoke PASS:** named `quality-review -> reviewer`
подтверждён только для exact global smoke; reviewer дал quality verdict
`REVIEWER VERDICT: clear`, verifier отдельно подтвердил acceptance PASS.
Sysop primary smoke подтверждён отдельно и scoped; T-109 остаётся `BLOCKED`.

2026-08-29 — **Orchestration smoke PASS:** independent verifier подтвердил
  exact `vault` read-only chain `librarian -> researcher -> reviewer ->
  verifier`, sequential, без `general` fallback и self-marker. Runtime
  automation/router не внедрён. Evidence: [[04-Memory/route-log/2026-08-29-orchestration-smoke]],
  [[06-Specs/Vault/control-plane-smoke]]. R1/F1/F2/F3 закрыты документально;
  uncommitted/negative deny/local merge/literal output gaps остаются.

2026-08-29 — **Routing checkpoint pause:** capability-routing приостановлен
после v0.1 checkpoint; exact smokes researcher, reviewer, sysop и orchestration
подтверждены. Следующий шаг после возобновления — negative permission smoke и
local-extension merge, затем дальнейшая adoption. Automatic router,
 prompt-normalizer и task-compiler не реализованы.

2026-08-29 — **T-108 protocol report:** named `system-ops` session
`ses_fb0ee381fffeHfjxggBF0CXpm3/` не использовала fallback, но получила отказ
edit evidence path и отказ `external_directory` для task/handoff; host и WIP не
изменялись. E-108-002 записан librarian, не самим system-ops. Статический
merged config содержит scoped rules, но runtime application edit не доказан;
T-108 остаётся BLOCKED. Safe next step — fresh-session controlled smoke, без
broad allow.
