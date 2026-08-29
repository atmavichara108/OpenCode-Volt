---
type: Active Context
title: Активный контекст
description: Phase 1 (kernel stabilization) ЗАВЕРШЕНА 2026-08-04. Текущая модельная политика Luna + DeepSeek Go сохранена; capability-routing design gate пройден, runtime extraction partial и evidence-gated.
tags: [memory]
timestamp: 2026-08-29
---

# Активный контекст

> Автоматически обновляется librarian. Читается при старте каждой сессии.

## Текущий фокус
- **Runbook layer (2026-08-17):** создан `07-Runbooks/` как отдельный operational
  use layer; handbook фиксирует текущее применение, changelog — подтверждённые
  shifts. Следить за freshness только по реальным изменениям практики.
- **Модельная политика (2026-08-25):** Luna + DeepSeek Go сохранена без
  изменений; capability-routing не меняет model-routing.
- **Текущий фокус:** capability-routing paused after v0.1 checkpoint. Exact
  smokes для researcher, reviewer, sysop и orchestration подтверждены;
  следующий шаг после возобновления — negative permission smoke и
  local-extension merge, затем дальнейшая adoption. Automatic router,
  prompt-normalizer и task-compiler не реализованы. Параллельно выполняется
  T-109, docs-only bootstrap Coordination Bridge;
  bridge создан в AndroidOS и остаётся uncommitted/untracked, structural smoke записан, independent
  reviewer/verifier gates для T-109 pending. Baseline SHA не является provenance bridge.
  Capability-routing имеет частичный rollout: named researcher и reviewer smoke
  подтверждены только scoped evidence, sysop — только exact global primary
  smoke. AndroidOS environment prep/sysop report и `/android-plan`
  следуют после bridge acceptance.
- **Coordination Bridge:** выбран единый canonical Git-backed file
  protocol/contract, не отдельный bridge-agent. Будущие agent facade/command и
  MCP facade только optional, без реализации и без зависимости телефона.
  Пользовательский operator guide добавлен в
  [[07-Runbooks/coordination-bridge-operator-guide]]. Реализация
  T-109 находится в `Blocked` и удерживается там до named
   reviewer/verifier verdict; optional MCP T-110 остаётся `Planned`.
- Глобальная `/bridge` добавлена в dotfiles source
  `opencode-global/.config/opencode/command/bridge.md`; после Stow требует
  restart OpenCode. Команда не фиксирует agent, не создаёт копию bridge и
  останавливается с `UNROUTABLE` при недоказуемом named route.
- **Текущий blocker T-109:** reviewer smoke подтверждён только для exact global
  smoke; это не acceptance Coordination Bridge. Поэтому T-109 remains
  `BLOCKED`; не симулировать `PASS` и не менять статус на Done.
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
- **Следующий фокус после bridge bootstrap:** закрыть named reviewer/verifier
  gates Coordination Bridge по spec T-109; затем перейти к AndroidOS
  environment prep/sysop report и `/android-plan`.
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
- **Dotfiles-local `system-ops` (2026-08-25):** agent skeleton создан, но
  runtime/root execution не подтверждены. `sysop` остаётся read-only; маршрут
  high-risk apply: `sysop` audit → `planner` plan → `system-ops` apply →
  `verifier`/post-check. Root apply только через explicit approval; edit/task
  deny, dangerous operations deny-safe. T-108 открыт до live evidence.
- **Следующий порядок:** T-107 controlled probe → T-108 permission/root
  smoke-test → reviewer/sysop extraction. Не объявлять задачи Done без
  acceptance.
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
- **Текущий шаг:** sysop primary smoke PASS зафиксирован независимым verifier
  только в exact global primary scope. T-109 bridge bootstrap создан в
  `AndroidOS/coordination/bridge/`; read-only structural smoke записан.
  Текущий статус — `BLOCKED`; следующий шаг — named reviewer и verifier. При отсутствии named role
  фиксировать `UNROUTABLE`, без silent general fallback. Runtime/root execution
  для `system-ops` не подтверждены.
- После отдельной сессии T-109 — sysop environment prep и `/android-plan`;
  T-110 не начинать до завершения bridge и отдельного decision gate.
- Capability-routing paused after v0.1 checkpoint; подтверждены exact smokes
  researcher, reviewer, sysop и orchestration. После возобновления: negative
  permission smoke → local-extension merge → дальнейшая adoption. Automatic
  router, prompt-normalizer и task-compiler не реализованы.
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
- AndroidOS T-101 возвращён в Planned с пометкой paused by routing rollout.

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
