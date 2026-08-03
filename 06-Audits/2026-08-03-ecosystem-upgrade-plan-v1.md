---
type: Upgrade Plan
title: Ecosystem upgrade plan v1 — рабочий план апгрейдов вайбкодинг-слоя
date: 2026-08-03
status: draft
sources:
  - "[[06-Audits/2026-08-02-vibecoding-layer-audit]]"
  - "[[06-Audits/2026-08-02-upgrade-planning-seed]]"
  - "[[06-Audits/2026-08-03-serplux-phase-c-audit]]"
  - "[[06-Audits/2026-08-03-serplux-phase-c-addendum]]"
  - "[[06-Audits/2026-08-03-dv-hub-phase-d-audit]]"
  - "[[06-Audits/2026-08-03-dv-hub-phase-d-addendum]]"
tags: [upgrade-plan, draft, ecosystem, kernel-contracts, roadmap]
---
# Ecosystem upgrade plan v1 (2026-08-03)

> **Рабочий план v1, не отчёт и не список выполненных работ.** Здесь —
> roles of nodes, 5 kernel contracts к первоочередной реализации,
> целевые архитектурные решения/roles (не claims о текущем внедрении),
> методологические принципы, project-specific constraints, implementation
> order (candidate/planned sequence), инженерный контракт инженерного
> качества кода как planned artifact, decision gates. **Без ложных
> статусов «done» и без дат.** Everything below is candidate/planned unless
> stated as confirmed fact with source.

---

## roles of nodes

- **OpenCode-Vault** = coordination node and methodology carrier. Держит
  смысл, роли, контракты, методы, память экосистемы; librarian как
  primary agent; сюда же — `06-Audits/`, `02-Methods/`, `04-Memory/`,
  planning artifacts.
- **`dotfiles/opencode-global`** = hands + nerve primitives + local
  execution substrate. Глобальный физический контур (`~/.config/opencode/`
  versioned через GNU Stow из `dotfiles/opencode-global/`); nerve
  primitives (`/loop`, `/done`, `meta`, `verifier`, `session-flush`).
  Manjaro local tooling — исполнительная методология на машине.
- **SERPlux** = commercial proving ground for kernel contracts. Live
  Python-проект с acceptance-поверхностью (94 test definitions; 111
  documented), где контракты (plugin loader, reviewer/verifier split,
  runtime enforcement, memory model, test metrics) проверяются на
  боевом коде.
- **dv-hub** = recovery/stability case for isolated local-agent
  projects. TS/Hono волонтёрский проект; локально организован,
  экосистемно не сцеплен; acceptance-поверхность деградирована; recovery
  gate предшествует любому kernel-апгрейду (см.
  [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]]).

---

## kernel contracts to implement first

> Ровно 5 контрактов. Для каждого: зачем нужен, какой риск закрывает,
> что считается доказательством. **Без утверждения реализации** — это
> design contracts, not implemented artifacts.

### 1. plugin loader contract

- **Зачем:** зафиксировать loader-поведение OpenCode для
  `.opencode/plugins/*.{js,ts}` (default-only / named / both; обязан ли
  `export default`).
- **Риск:** guard-плагины (`commit-guard`, `env-guard`) и harness,
  опирающийся на guard-plugins (verifier runtime gate), садятся на
  недокументированное поведение. Mixed default/named exports в SERPlux
  (`commit-guard.js` ESM SyntaxError, `notify.js` catch-all `event`) и
  dv-hub (`env-guard.ts`, `notify.ts` named без default) не имеют
  устойчивого fix-пути без этого контракта.
- **Доказательство:** documented loader-контракт в `01-Reference/plugins`
  (или как часть plugin-policy) + экспериментальное подтверждение
  поведения loader'а (загружается ли named-export без default; валиден
  ли `event` catch-all ключ) ДО любых правок проектных плагинов.
  Источник: [[06-Audits/2026-08-03-serplux-phase-c-addendum]] findings #1/#2.

### 2. reviewer vs verifier contract

- **Зачем:** разделить `reviewer` (quality: стиль, безопасность,
  контракты, разрешения) и `verifier` (acceptance: DoD, тесты, PASS/FAIL,
  never edits, narrow bash allowlist) как global role kernel + local
  extensions.
- **Риск:** карточки/INDEX приписывают `verifier-pattern ✅` локальному
  `reviewer`, если `/loop` на шаге 2 вызывает глобального `@verifier`.
  Неявная подмена reviewer↔verifier ломает closed-loop и capability-routing
  слой C «когда reviewer / verifier».
- **Доказательство:** явная декларация в карточках, какой verifier
  закрывает closed-loop (глобальный через `/loop` или локальный);
  раздельные карточные статусы `reviewer-pattern` vs `verifier-pattern`;
  global kernel contract (принципы, формат PASS/FAIL) + local extensions
  per project. Source: addendum Phase C finding #4; audit G1.

### 3. runtime enforcement contract

- **Зачем:** зафиксировать, что значит «`verify=PASS → finalize`» на
  runtime-уровне: gated command протокол / plugin hook
  (`tool.execute.before`) / harness loop-артефакт.
- **Риск:** без runtime-mechanism `closed-loop`/`/done` — командная
  конвенция, а не неотвратимый runtime-gate. Любой harness садится на
  плагин, который может не загружаться (зависит от контракта #1).
- **Доказательство:** зафиксированный runtime-mechanism (plugin hook vs
  command-gate vs harness wrapper) с различением `/commit` pre-commit
  hook vs `/loop`→`/done` finalize; зависит от plugin loader contract.
  Source: addendum Phase C finding #5; audit G2/G5.

### 4. memory model compatibility contract

- **Зачем:** допустить сосуществование двух memory-моделей — **vault-based**
  (`04-Memory/`, `facts.md`, `active-context.md`, `session-log/`) и
  **docs-based** (`docs/decisions.md`, `docs/progress.md`, предметные docs/).
- **Риск:** глобальный `session-flush` (целит в `04-Memory/session-log/`)
  к docs-based проекту (SERPlux, dv-hub) создаёт stray-каталоги и
  конкурирующий flush; `/done` (vault-scoped чеклист) механически
  неприменим к docs-based.
- **Доказательство:** либо общая абстракция (`/done` + `/dream` для
  docs-based), либо явное разделение «волтовский `/done`» vs «проектный
  flush»; policy global vs local plugin (когда отключать global flush для
  docs-based / local override / унификация в event-log + sinks).
  Source: addendum Phase C findings #6/#11; audit G5.

### 5. test metrics normalization contract

- **Зачем:** различать источники и назначение метрик — НЕ называть числа
  из разных артефактов «реальным числом тестов»: test definitions
  (`grep def test_`), documented suite claims per artifact (карточка/
  `AGENTS.md`/`docs/verification.md`/`TASKS.md`), pytest total (не
  подтверждается без прогона: parametrize, skip).
- **Риск:** решения по upgrade принимаются на разошедшихся метриках
  (SERPlux: 94 / 111 / 224 / 172 / 95 в разных артефактах); в карточке
  `111/111` без единого источника правды — нестабильно.
- **Доказательство:** единый source-of-truth по тестовому покрытию в
  карточке/AGENTS/docs; явный агент/скрипт/CI, поддерживающий консистентность.
  Source: addendum Phase C finding #7; audit G7.

---

## global architecture decisions

> Зафиксированы как **целевые архитектурные решения/roles**, не claims о
> текущем внедрении. Внедрение — через implementation order ниже; здесь
> только целевые роли и их контуры.

- **librarian** = primary Volt agent. Координационный узел, маршрутизатор
  задач, держатель контекста всех проектов; сам не редактирует код
  проектов (через subagents/skills/pipelines).
- **meta** = global sub-agent / nerve editor. Агентная инфраструктура
  (`/.opencode/`, `~/.config/opencode/`, vault-агенты/команды/скилы);
  редактирует инфру через subagents; proactive algorithmic loop —
  candidate (hooks/периодические инспекции/diff/capture-signals).
- **sysop** = global system inspector, partner of meta, tied to Manjaro
  reality. Executorская среда: пакеты, сервисы, порты, system state;
  усилитель OpenCode-апгрейдов (OpenCode живёт на машине).
- **guardian** = philosophy/policy keeper, **non-editing audit role**.
  Сверка с философией/конвенциями; инварианты, ограничители; gate после
  `prompt-engineer` spec (candidate); reviewer of capability-routing
  слой A.
- **researcher** = global scout for repo/system reality checks. Внутрь
  артефактов (код, git, docs, конфиги, история, связи); два луча сенсорного
  слоя: `researcher` (внутрь артефактов) ↔ `sysop` (наружу на машину).
- **reviewer** = quality/style/domain reviewer. Оценивает артефакт
  (стиль, безопасность, соответствие конвенциям, конфиг/разрешения);
  global kernel contract + local extensions; ≠ verifier.
- **verifier** = acceptance gate only. DoD, тесты, PASS/FAIL, never edits,
  narrow bash allowlist; global kernel contract + local extensions.
- **prompt-engineer / task-compiler** = layer compiling conversational
  tasks into strict agent prompts. Режим 1 — `prompt-normalizer`
  (свободная задача → цель/ограничения/контекст/DoD → spec); режим 2 —
  `task-compiler` (знает roster/routing/порядок/артефакты → pipeline).
  Цепочка: пользователь свободно → `prompt-engineer` spec → `guardian`
  проверка → `meta`/project planner execution.

---

## methodological principles

> Коротко, без философии. Дистилляция принципов; здесь — рабочие
> принципы плана, не канон.

1. **Local tooling as agents' limbs.** Локальная машина и серверы —
   исполнительные конечности; детерминированные операции (`grep`, `git`,
   `stow`, `shellcheck`, `py_compile`, `notify`, `systemctl`, `sqlite`,
   конвертации, графы, индексация, diff-анализ) разгружают LLM.
2. **Global role kernel + local specializations.** Глобальное ядро роли
   (общий контракт) + локальные расширения/предметная точность; контракт
   глобален, реализация/доопределение — локальны; роль ≠ файлу в каждом
   репо.
3. **Capability-routing.** Решение «кто исполняет» по типу операции/
   инструменту/риск-profile, не только по выбору модели: 3 слоя (A общие
   инженерные конвенции → B language/runtime conventions → C routing
   policy по модели/роли/языку/риску/типу операции).
4. **Event-log-first / low-token memory.** Append-only event-log как
   первичный источник; raw machine events без токенов; поверх — periodic
   semantic distillation (LLM периодически дистиллирует event log в
   facts/active-context/decisions/session summary). Hybrid: raw +
   distilled; `active-context` = summary + последние события.
5. **Capture chain:** `signal → classification → relevance → project
   mapping → upgrade path → backlog`. Capture (intake-слой) не просто
   сбор ссылок, а первый этап апгрейда проекта; привязка сигналов к
   узлам ecosystem-map.
6. **Ecosystem-map as operational planning UI.** Карта экосистемы как
   карта апгрейдов: узлы = кандидаты, связи = зависимости; capture-сигналы
   привязаны к узлам. Planning-роль карты; runtime-контракт — отдельный
   open question.
7. **Declarations vs reality reconciliation as permanent meta mechanic.**
   Сверка декларации (карточка/INDEX/VibeOS) ↔ факта (репо/инфра) —
   постоянный meta-механизм, не разовый аудит; `meta` proactive loop
   (diff-based drift audit) — candidate infra.
8. **Commands do not execute by magic; execution only via skills/hooks/
   pipelines/loops/allowed tool/task contours.** Произвольный shell по
   инициативе агента — `ask` или `deny`, не default; `prompt-engineer`
   компилирует не «идеальный текст», а OpenCode-compatible pipeline;
   `meta`-proactivity опирается на hooks/plugins/skills, а не на надежду.

---

## project-specific constraints

### SERPlux

- Live proving ground: kernel contracts (plugin loader, runtime
  enforcement, memory model, test metrics) проверяются на боевом коде
  первым.
- **Plugin/runtime/memory contracts first.** Стабилизация `commit-guard.js`
  (ESM SyntaxError) и `env-guard.js` (named-export) — после loader
  contract (T-084).
- **Reviewer/verifier split mandatory.** Локальный `reviewer` ≠ глобальный
  `verifier`; `/loop` на шаге 2 вызывает глобального `@verifier`.
- **Docs-based memory respected.** `docs/decisions.md`, `progress.md`,
  `techdebt.md`; global `session-flush` к SERPlux неприменим без адаптации.

### dv-hub

- **Not first kernel-upgrade target.** Recovery gate first.
- **Recovery gate:** (a) acceptance surface (минимальный test-gate; `tests/`
  пуст, `npm test` exit 1 — восстановить поверхность), (b) runtime health
  (Telegram auth 404 — G-D-RUN-1; D1 migration incomplete — G-D-RUN-2),
  (c) docs reconciliation (ADR Zomro↔Fornex; README 5 vs 7; VibeOS 6 vs 5
  агентов).
- **Wording must be:** «operational integration with global nerve is not
  confirmed». Не «не подключён», не «не используется».
- Capability-routing / engineering-style-contract / reviewer/verifier split
  применяются **только после** recovery gate; их отсутствие в проекте —
  ecosystem prerequisite, не project defect (см.
  [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]]).

### dotfiles

- **Global contour physically lives there** (`dotfiles/opencode-global/` →
  GNU Stow → `~/.config/opencode/`) but serves ecosystem, not self.
- **Manjaro local tooling is execution methodology.** `sysop`/`builder`/
  `planner` — ролейный яд; детерминированные инструменты (`stow`,
  `shellcheck`, `systemctl`) — исполнительная поверхность.
- Глобальные nerve primitives (`/loop`, `/done`, `meta`, `verifier`,
  `session-flush`) **physically root here**, но ownership — экосистемный;
  правки через meta sub-agents, не напрямую.

---

## implementation order

> Строго зафиксированная candidate/planned sequence. **Без Done, без дат.**
> Marked as candidate/planned; переход между phases — после evidentiary
> gate соответствующего phase.

### Phase 1 — kernel stabilization

- **Plugin policy** (plugin loader contract #1): documented loader-контракт;
  design contract, не правка кода проектов.
- **Reviewer/verifier split** (contract #2): разделить контракты
  `reviewer` (quality) vs `verifier` (acceptance); global kernel + local
  extensions; явная декларация в карточках.
- **`/done` adaptation by project memory model** (contract #4):
  vault-based vs docs-based адаптация scope.
- **Runtime gate enforcement** (contract #3): зафиксировать
  runtime-mechanism `verify=PASS → finalize` (plugin hook / command-gate /
  harness wrapper).
- **Test metrics normalization** (contract #5): единый source-of-truth по
  тестовому покрытию; различение test definitions vs documented claims vs
  pytest total.

### Phase 2 — global role extraction

- **Global sysop** (Manjaro/system inspecting).
- **Global researcher** (repo/system reality scout).
- **Global reviewer** (quality role kernel).
- **Guardian** (philosophy/policy non-editing audit).
- **Prompt-engineer / task-compiler** (conversational → strict pipeline).

### Phase 3 — memory and signals

- **Event-log-first memory redesign:** append-only event-ledger
  (SQLite/JSONL candidate) + distilled projection (facts/active-context/
  decisions) + локальная дистилляция (rg/jq/awk/python) + watchers / git
  metadata / cron/systemd timers.
- **Capture→upgrade chain:** intake → classify map node → relevance →
  project mapping → upgrade path → execution/backlog.
- **Notify redesign incl. voice:** global notify kernel + local transport
  sinks; voice candidate (global notify сейчас отсутствует — confirmed
  fact Phase A; candidate, не факт).
- **Ecosystem-map as planning UI:** превратить tools/ecosystem-map/ из
  визуализатора в интерфейс планирования апгрейдов; planning-роль карты;
  runtime-контракт — отдельный open question.

### Phase 4 — project adoption

- **SERPlux first** (приоритет kernel-proving): plugin stabilization,
  reviewer/verifier split, runtime gate, memory/docs adaptations.
- **dv-hub only after acceptance restoration** (recovery gate precedes
  kernel overlay): runtime health, acceptance surface, docs reconciliation;
  затем — kernel-конракты по аналогии с SERPlux.
- **dotfiles/global contour evolves in parallel** (Phase 1–3): физический
  контур global nerve правится синхронно с kernel contracts; Manjaro local
  tooling — execution methodology.

---

## engineering-style-contract

> **Planned artifact, не готовый method.** Это **не** файл в `02-Methods/`;
> здесь — развёрнутая техническая секция плана как кандидат на будущий
> design/approval. Цель — превратить общий лозунг «пиши хорошо» в
> enforceable инженерный объект с профилями и gate-проверкой.

### purpose

Превратить «code quality / code style conventions» из лозунга в
объектный контракт: короткое общее ядро + language-specific профили +
anti-shitcode паттерны + routing по языку/типу задачи/риску + reviewer/
verifier integration (минимальный расход токенов: детерминированные
checks/linter/DoD-чек-лист предпочтительнее свободного LLM-разбора).

### global rules

- Один файл = одна ответственность; no hidden side effects; explicit
  dependencies; deterministic entry points; no premature abstraction.
- Forbid: dead code, placeholder wrappers, speculative layers, duplicate
  configs, silent fallbacks without logs.
- Composition over inheritance; explicit schemas; minimize mutation;
  isolate side effects at edges.
- Docs reflect real commands/models/files; model IDs no drift; memory
  model explicit docs-based vs `04-Memory/`.
- Routing выбирает subagent по языку/типу задачи, опираясь на профиль;
  `reviewer`/`verifier` проверяют контракт детерминированно.

### 2. Конвенции качества кода

> Подробно, технически, без лозунгов.

#### 2.1 General code quality rules

- **Boring/readable/grep-friendly:** явные имена, без clever трюков;
  имена грепаются (no obfuscated metaprogramming).
- **One file = one responsibility:** модуль не делает «всё»; разделение
  по домену/слою.
- **No hidden side effects:** функция не молча изменяет глобальное
  состояние, не пишет в файл, не дёргает сеть без явной сигнатуры.
- **Explicit dependencies:** импорты/входы видимы; нет магического DI
  через строки/глобалы.
- **Deterministic entry points:** одна точка входа; no scattered CLI/
  server bootstrap.
- **No premature abstraction:** не плодить базовые классы/интерфейсы
  под гипотетическое будущее; YAGNI для speculative layers.
- **Forbidden:** dead code, placeholder wrappers (функции-пустышки для
  «будущей логики»), duplicate configs (та же настройка в 3 местах),
  silent fallbacks без logs (`try: ... except: pass`, `?? defaultValue`
  без log).

#### 2.2 OOP vs functional

- **OOP only when:** durable state / lifecycle / polymorphism / boundary
  object (сущность с долгоживущим состоянием, несколькими операциями над
  ним, полиморфной заменой реализации).
- **Functional default for:** transformations, validation, parsing,
  mapping, formatting, reducers, CLI glue, чистые функции ввода-вывода
  форматов.
- **Forbidden:** fake-OOP (classes-as-namespaces без состояния),
  god-services (один класс-«сервис» делает всё), inheritance-for-reuse
  (наследование чтобы переиспользовать 2 метода — использовать composition).
- **Composition over inheritance; explicit schemas; minimize mutation;
  isolate side effects at edges.**

#### 2.3 TypeScript / JavaScript

- **Strict typing** (`strict: true` в `tsconfig`); no `any` без
  justification comment.
- **Narrow interfaces:** интерфейсы по потребительскому контракту, не
  god-interface «все поля сущности».
- **No giant service files:** один файл ≤ ~300–400 строк по домену;
  разделение на domain/infra/adapters/UI.
- **Domain / infra / adapters / UI split:** бизнес-логика не зависит от
  infra (DB, HTTP, FS); adapters изолируют внешние API; UI — отдельный
  слой.
- **One plugin export contract:** один канонический export-формат плагина
  (default vs named) — см. plugin loader contract #1; no mixed без
  policy reason.
- **No mixed named/default exports** unless explicitly allowed
  (policy-reason documented).
- **Explicit async errors:** `try/catch` на async-границах; no
  `.catch(() => null)` swallow.
- **Boundary runtime checks:** validate внешнего ввода на границе
  (zod/io-ts/runtime guards); внутренний код работает с типизированным.
- **Centralized config:** один источник конфигурации (env + schema +
  defaults); no scattered `process.env` reads.
- **Typed routing schemas вместо stringly routing:** `app.get("/users/:id",
  { id: z.string() })` vs `req.params.id` без типа.

#### 2.4 Python

- **Typed functions** (`def f(x: int) -> str: ...`); type hints обязательны
  для public API.
- **Small modules:** один модуль = одна доменная область; no
  `utils.py` god-module.
- **CLI separate from library:** `cli.py` (argparse/click entry) →
  library functions; library не парсит argv.
- **dataclasses / pydantic structured data:** явные схемы вместо
  неформальных dict; валидация на границе (pydantic).
- **Explicit exceptions:** кастомные классы исключений домена; no
  bare `except Exception` без re-raise/log.
- **Pure core and side effects at edges:** ядро логики — чистые функции;
  IO (DB/HTTP/FS) — на периметре adapters.

#### 2.5 Shell

- **Glue/ops only:** shell — связующий клей и ops; не доменная логика.
- **`set -euo pipefail`** в начале каждого executable script.
- **No hidden cd/state:** `cd` в скобках `(cd dir && cmd)` или absolute
  paths; не изменять cwd вызывающего.
- **Idempotence:** повторный запуск не ломает состояние; destructive
  операции guarded (`rm -rf` только с explicit guard).
- **Log destructive commands:** `rm -rf`, `drop`, `truncate` — с ech перед
  выполнением.
- **Quote vars:** `"$VAR"`, not `$VAR`; especially in paths/args.
- **Split functions:** скрипт > ~80 строк — разбить на функции.
- **shellcheck mandatory:** CI/local pre-commit; no shellcheck warnings
  without justification.

#### 2.6 Config / docs

- **Minimal configs:** один источник конфигурации; no duplicate в 3
  местах (wrangler.toml + wrangler.jsonc + wrangler.example.toml —
  anti-pattern; cleanup).
- **Docs reflect real commands/models/files:** README/AGENTS/VibeOS не
  расходятся с фактическими файлами (G-D-DOC-2, G-D-DOC-3 example).
- **Model IDs no drift:** канонический namespace (`opencode-go/...`)
  везде; пер-проектная аномалия (`opencode/deepseek-v4-flash` без `-go/`)
  документируется или нормализуется.
- **Memory model explicit docs-based vs `04-Memory/`:** карточка/AGENTS
  явно указывают тип memory-модели; global `session-flush` не
  применяется к docs-based без адаптации.
- **Commands name real agent and acceptance path:** команда ссылается на
  существующего агента и реальный verifier/acceptance; no «команда на
  гипотетического агента».

#### 2.7 Anti-low-quality (anti-shitcode patterns)

- **No silently drifting copy-paste prompts:** один и тот же промпт,
  копипастенный в 5 команд → diverge; единая точка правки (skill/shared
  template).
- **No duplicate global/local agents without override policy:** локальный
  `reviewer` + глобальный `reviewer` без явного override = конфликт;
  policy override-or-merge обязательна.
- **No unverifiable active status:** «✅ active» без evidence (no tests,
  broken runtime) — нестабильно; статус reconciliation обязательна.
- **No fake test numbers:** `111/111 passed` без единого источника правды
  и без прогона — candidate, не факт.
- **No loop without verifier:** `/loop` без `@verifier` PASS/FAIL —
  half-pipeline; либо verifier, либо явно «no loop».
- **No plugin without loader proof:** плагин с named-export без default
  в loader-risk state → не claim «работает» без loader proof.
- **No upgrade of stale project before health checks:** dv-hub kernel
  overlay до recovery gate = наложение контрактов на неработающий проект.

#### 2.8 Routing table

> Routing по типу задачи → preferred language-style / agent-subagent /
> reviewer type / verifier-gate. Использует **target roles as planned
> architecture**; не claim existing implementation.

| Task type | Preferred language-style | Preferred agent-subagent | Reviewer type | Verifier-gate |
|---|---|---|---|---|
| UI tweak (web/Sheets/Apps Script) | TS/JS functional, small modules | ui-dev / build (UI specialization) | reviewer (UI/style/a11y) | visual/snapshot or manual DoD; runtime gate optional |
| Infra/config (YAML/TOML/JSON/env) | shell glue + config-as-data; `set -euo pipefail` | infra-dev / sysop | reviewer (infra/config/security) | infra apply dry-run + linter (shellcheck/yamllint) |
| Bash automation | shell glue/ops only; shellcheck mandatory | bash-dev / builder (shell specialization) | reviewer (shell/style/quote) | shellcheck + dry-run; idempotence check |
| Parser/transform (data ETL) | functional pure core + edge IO (Python/TS) | build / collector-dev (domain) | reviewer (data/schema/pure) | unit tests + golden fixtures; DoD check |
| Plugin (OpenCode `.opencode/plugins/`) | TS/JS plugin export contract (loader #1) | build (plugin) / meta (infra) | reviewer (plugin/loader/security) | loader proof + harness smoke; runtime gate |
| Migration (schema/data) | SQL + migration script (idempotent) | build (migration) / infra (deploy) | reviewer (SQL/migration/idempotence) | migrate test→prod dry-run; checksum/diff verify |
| Auth/runtime bug | strict typing + boundary checks (TS/Python) | build (bugfix) / researcher (spike) | reviewer (security/runtime) | runtime test + integration; PASS/FAIL |
| Audit/recon (read-only) | shell glue + grep/rg/awk + python analysis | researcher / sysop / guardian | guardian (philosophy/policy) | verifier PASS/FAIL on findings; no edits |
| Documentation sync (README/AGENTS/VibeOS) | markdown/docs (minimal, reflect reality) | meta / build (docs) | reviewer (docs/reality check) | pre-commit wikilink + empty-file check; drift reconciliation |

> Reviewer type column — `reviewer` global kernel + local UI/infra/shell/
> data/security/docs specializations. Verifier-gate column — `verifier`
> global kernel (acceptance PASS/FAIL) + project-local acceptance surface
> (test framework, linter, dry-run). Без подмены reviewer↔verifier.

### reviewer integration

- `reviewer` (quality) проверяет контракт **минимальным расходом токенов**:
  детерминированные checks/linter (`tsc --noEmit`, `ruff check`,
  `shellcheck`, `yamllint`) предпочтительнее свободного LLM-разбора.
- Anti-shitcode patterns (2.7) — чек-лист для `reviewer`: detect dead code,
  placeholder wrappers, god-services, duplicate configs, stringly routing,
  silent fallbacks.
- LLM-reviewer подключается только там, где детерминированный check
  невозможен (semantic checks, domain-logic consistency, doc reality).

### verifier integration

- `verifier` (acceptance) исполняет детерминированную проверку: билд/
  тесты/линтер/DoD; PASS/FAIL; never edits; narrow bash allowlist
  (`git status/diff/log`, test runner, linter, build).
- Runtime enforcement contract #3 определяет механизм: `verify=PASS →
  finalize` через plugin hook `tool.execute.before` (gate) / command-gate /
  harness wrapper; без runtime-gate closed-loop = конвенция.
- Engineering-style-contract gates (2.7 anti-shitcode, 2.8 routing
  verifier-gate) — это verifier-checklist, не LLM-judgement.

---

## decision gates

> Коротко, жёстко.

- **No project-level execution until kernel contracts have evidence.**
  Plugin loader (T-084), reviewer/verifier split (T-085), runtime gate
  (T-089), memory model compatibility (T-086), test metrics normalization
  (T-087) — design contracts с доказательством (documented + experimental
  для loader) до любого project-level overlay.
- **No dv-hub adoption until recovery gates.** Runtime health (auth 404,
  D1 migration), acceptance surface (минимальный test-gate), docs
  reconciliation (ADR/README/VibeOS) — предшествуют любому kernel-контракту
  overlay на dv-hub. dv-hub — recovery-case, не showcase-case.
- **No security stable fact without exact evidence.** Package name,
  version range, advisory ID/GHSA, impact, exploitability assessment,
  source/date, fix availability — без этого формулировка = candidate/
  unverified security finding, не stable fact (см.
  [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]]).
- **Every candidate has acceptance criteria and rollback/stop condition.**
  Каждый kernel contract / role extraction / project adoption имеет
  явные acceptance criteria (что считается доказательством) и
  rollback/stop condition (когда остановиться и пересмотреть plan).