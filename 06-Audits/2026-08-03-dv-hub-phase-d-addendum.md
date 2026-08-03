---
type: Audit Addendum
title: dv-hub — Phase D audit addendum (классификация findings, контрактные implications)
date: 2026-08-03
status: open
source:
  - "[[06-Audits/2026-08-03-dv-hub-phase-d-audit]]"
tags: [audit, addendum, phase-d, dv-hub, classification, contracts]
---
# dv-hub — Phase D audit addendum (2026-08-03)

> Addendum к [[06-Audits/2026-08-03-dv-hub-phase-d-audit]]: корректура
> формулировок, переклассификация gaps по High/Medium/Low с типами
> (runtime/methodology/drift/ecosystem), ecosystem implications, и явный
> перечень того, что **не должно** фиксироваться как стабильный факт.
> Основной аудит **не переписывается**; здесь — исправления и ужесточения.
> Read-only в части репо `dv-hub` и global nerve; правок кода/инфры нет.

---

## corrected verdict

**Уточнённый вывод взамен краткой формулировки основного аудита:**

dv-hub — **локально организованный, но экосистемно не сцепленный проект с
деградировавшей acceptance-поверхностью**. 5 агентов, 7 команд, 3 плагина
есть и работают локально (agent-files, commands, ts-плагины на месте);
но:

- **операционная интеграция с global nerve не подтверждена** — ноль
  evidence-type ссылок на `/loop`, `/done`, `@verifier`, `@meta`,
  `session-flush` в `dv-hub/{AGENTS.md, .opencode/, docs/}`;
- acceptance-поверхность деградирована: `tests/` пуст, `npm test` exit 1,
  CI = `lint+build` без тестов, `.github/` отсутствует → verifier-loop
  внедрять не во что;
- dv-hub — **recovery-case**, не showcase-case: первично восстановление
  runtime-здоровья (Telegram auth 404, D1-миграция incomplete) и
  acceptance-поверхности, а не наложение kernel contracts поверх
  неработающего проекта.

Старая формулировка «глобальный nerve не подключён» заменяется на строгую:
**«операционная интеграция с global nerve не подтверждена»**. Это не bug,
а наблюдаемый факт отсутствия coupling; статус проекта относительно
global kernel — открытый policy-вопрос, не автоматическое «adopt».

---

## wording corrections

| Было (в основном аудите) | Стало (строгая формулировка) | Основание |
|---|---|---|
| «Глобальный nerve к dv-hub фактически не подключён» | «Операционная интеграция с global nerve не подтверждена» | zero evidence-type references; наблюдаемое отсутствие ≠ утверждение о «неподключённости» как defect |
| «`engineering-style-contract` / `capability-routing` применимы к dv-hub» (implication) | `engineering-style-contract` и `capability-routing` — **ecosystem prerequisites / future kernel artifacts**, не defects dv-hub | они контрактны к экосистеме, не к конкретному проекту; их отсутствие в проекте — не дефект проекта |
| «high-severity Hono vulnerability» (как стабильный факт) | **candidate/unverified security finding** — пока нет доказательной спецификации (см. ниже) | ниже недостаточный spec для stable fact |
| «dv-hub — showcase-case для capability-routing» (импликация) | dv-hub — **recovery-case**, не showcase-case | acceptance surface деградирована, runtime incidents открыты |
| «global nerve isolation — zero coupling» (как HIGH gap) | фиксируется как наблюдаемый факт экосистемной изоляции, тип `ecosystem`, severity уточняется ниже | не дефект проекта, а состояние экосистемного сцепления |

---

## reclassified gaps: High / Medium / Low

> Переклассификация gaps основного аудита по severity с явным типом
> (`runtime` / `methodology` / `drift` / `ecosystem`). Без завышения
> дефектности проекта: «открытый runtime-incident» ≠ «дефект агентной
> инфры»; «отсутствие kernel contract» ≠ «дефект проекта».

### HIGH

| ID (audit) | Тип | Суть (строго) |
|---|---|---|
| G-D-RUN-1 | runtime | Primary auth broken at runtime: Telegram Bot API `getMe` 404, документировано в `docs/known-issues.md`. Рабочий инцидент, не агентно-инфраструктурный дефект. |
| G-D-RUN-2 | runtime | D1 migration data-incomplete: `/api/dashboard` возвращает только старые данные. Рабочий инцидент Phase 0. |
| G-D-RUN-3 | methodology | 0 acceptance tests / no verifier-loop: `tests/` пуст, `npm test` exit 1, CI без тестов. Acceptance-поверхности нет → verifier-pattern применить не к чему. Это recovery-gate, не showstopper kernel-апгрейда. |

> **G-D-METH-1 / G-D-METH-2** (verifier ❌ confirmed; reviewer без verifier)
> понижены до **MEDIUM**: карточка честно декларирует `verifier-pattern ❌`;
> half-pipeline (reviewer без verifier) — следствие отсутствия acceptance
> surface, не самостоятельный дефект.

### MEDIUM

| ID (audit) | Тип | Суть (строго) |
|---|---|---|
| G-D-RUN-4 | runtime | **candidate/unverified security finding**: `hono 4.12.10` ≤ 4.12.26, GHSA-458j-xx4x-4375 (HTML Injection в `hono/jsx` SSR). Релевантно (`src/index.tsx`), но до stable fact требуется exact spec (см. ниже). |
| G-D-RUN-5 | runtime | `@hono/node-server` moderate vulns (path traversal, WS memory-leak DoS), no fix available. Релевантно для target VPS-runtime. |
| G-D-RUN-6 | methodology | CI excludes tests + `.github/` absent: CI = `lint+build`, без GitHub Actions. Любой push проходит без test-gate. |
| G-D-RUN-7 | drift | Dependency drift растёт на простое (snap от 2026-07-21 уже фиксирует разрывы). |
| G-D-METH-1 | methodology | verifier-pattern ❌ (declared = observed, карточка честна). |
| G-D-METH-2 | methodology | reviewer без verifier-loop = half-pipeline (следствие G-D-RUN-3). |
| G-D-METH-3 | methodology | memory-management 🟡 — только compaction injection, event-log/replay нет (карточка честна). |
| G-D-METH-4 | methodology | context-as-docs 🟡 — формальный DoD не прописан (карточка честна). |
| G-D-DOC-1 | drift | ADR drift: `compaction.ts` PERSISTENT_CONTEXT «Zomro Poland» vs `docs/architecture.md` «Fornex Germany». Stable memory-drift. |
| G-D-DOC-2 | drift | README command table удалена на 2 команды (5 vs 7). |
| G-D-DOC-3 | drift | `VibeOS.md:232` «6 агентов» vs фактические 5. |
| G-D-ECO-1 | ecosystem | Операционная интеграция с global nerve не подтверждена (zero references). Наблюдаемый факт, не bug. |
| G-D-ECO-2 | ecosystem | No local/global `/commit` — `/done` (глобальный) «без якоря» до adapter/adopt. |

> **G-D-ECO-1** понижено с HIGH до MEDIUM: это структурный факт
> экосистемной изоляции, а не дефект проекта; фиксируется как ecosystem
> state, не как project defect.

### LOW

| ID (audit) | Тип | Суть (строго) |
|---|---|---|
| G-D-RUN-4-spec | runtime | Spec-неполнота security finding — до stable fact требуется exact package/version/advisory/impact/source-date (см. ниже). |
| G-D-METH-5 | methodology | model-routing ✅ — спорадичный model-id namespace drift (`opencode/` vs `opencode-go/`). Наблюдаемая аномалия, не bug карточки. |
| G-D-DOC-4 | drift | Card log stale с 2026-06-30. |
| G-D-DOC-5 | drift | Wrangler leftovers (3 файла, плейсхолдеры в `wrangler.toml`). |
| G-D-DOC-6 | drift | ecosystem-map node для dv-hub absent (не искался досконально, `[проверить]`). |
| G-D-ECO-3 | ecosystem | notify.ts — extension candidate to global notify kernel (mixed named-export → loader risk `[проверить]`). |
| G-D-ECO-4 | ecosystem | runtime-neutral plugin behaviour unverifiable без loader proof (loader risk, не доказанный bug). |
| G-D-ECO-5 | ecosystem | `commands/` vs `command/` naming variance dv-hub vs SERPlux. |

### Severity cross-reference (reclassified)

| Severity | Runtime | Methodology | Drift | Ecosystem | Total |
|---|---|---|---|---|---|
| HIGH | 2 | 1 | — | — | 3 |
| MEDIUM | 2 | 4 | 3 | 2 | 11 |
| LOW | 1 | 1 | 3 | 3 | 8 |

---

## ecosystem implications

1. **Recovery gate.** dv-hub — не первая цель kernel-апгрейда. До любого
   overlay (verifier/closed-loop/capability-routing/engineering-style-contract)
   должны быть закрыты: (a) runtime-инциденты (auth 404, D1-миграция),
   (b) acceptance-поверхность (минимальный test-gate), (c) docs
   reconciliation (ADR/README/VibeOS). Без этого kernel contracts
   накладываются на неработающий проект.

2. **Global kernel readiness.** Операционная интеграция с global nerve
   не подтверждена → нельзя считать `/loop`/`/done`/`@verifier`/`@meta`/
   `session-flush` «all-projects апгрейдом». Требуется explicit policy
   adoption: какие проекты подключают global nerve, какие остаются
   local-only island. dv-hub — кандидат на recovery-first path, не на
   auto-adopt.

3. **Docs-based memory.** dv-hub не имеет `04-Memory/`; память — в
   `docs/` + `context/` submodule. Глобальный `session-flush` (целит в
   `04-Memory/session-log/`) к docs-based проекту механически не применим
   без адаптации; `memory model compatibility contract` (planning seed)
   должен учитывать docs-based vs vault-based явно. `/done` (vault-scoped
   чеклист) требуется адаптировать либо ограничить применимость.

4. **Local extensions.** `notify.ts` (TS, `notify-send`, `session.idle`)
   — extension candidate на «global notify kernel + local transport
   sinks». `compaction.ts` (default export) — корректная форма; `env-guard.ts`
   и `notify.ts` (named без default) — loader risk, требует plugin loader
   contract до any harness, опирающегося на guard-plugins.

### main implication

> Главный вывод addendum: **dv-hub — локально организованный, но
> экосистемно не сцепленный проект с деградировавшей acceptance-поверхностью.**
> Это recovery-case, не showcase-case. KERNEL contracts
> (`engineering-style-contract`, `capability-routing`, `reviewer/verifier
> split`, plugin loader, runtime enforcement, memory model compatibility,
> test metrics normalization) — ecosystem prerequisites / future kernel
> artifacts, не defects dv-hub; их отсутствие в проекте — не дефект проекта,
> а состояние экосистемного сцепления.

---

## what must NOT be written as stable facts yet

> Явный перечень утверждений, которые **не должны** фиксироваться как
> стабильные факты в `04-Memory/facts.md`, карточке, INDEX, VibeOS до
> получения доказательной спецификации. Любое из них — кандидат/unverified
> до evidence.

- **«global nerve не используется dv-hub»** — нестабильно. Стабильная
  формулировка: «операционная интеграция с global nerve не подтверждена»
  (из evidence-absence не следует утвердительное «не используется»).
- **`capability-routing` / `engineering-style-contract` как дефекты
  dv-hub** — нет. Они ecosystem prerequisites / future kernel artifacts;
  их отсутствие в проекте — не дефект проекта.
- **«high-severity Hono vulnerability» как стабильный факт security**
  — недостаточно без точной спецификации. До stable fact требуется:
  exact package (`hono`), version range (`<=4.12.26`, resolved `4.12.10`),
  advisory ID (`GHSA-458j-xx4x-4375`), impact description (HTML Injection
  в `hono/jsx` SSR), exploitability assessment для dv-hub codepath
  (`src/index.tsx`), source/date (`npm audit` + GHSA), fix availability.
  Текущая формулировка — **candidate/unverified security finding**.
- **Runtime loader claims** («плагины не загружаются», «named-export
  без default = bug») — без loader proof (`[проверить]`) не фиксируются.
  Loader risk ≠ доказанный runtime bug.
- **«6 агентов» в VibeOS** — нестабильно; фактические 5 (+ inline-dublicate
  в `opencode.json` тех же 5). Дрейф подлежит reconciliation, не факту.
- **«CI/тесты в порядке»** — нестабильно; `tests/` пуст, `npm test` exit 1,
  CI без тестов.
- **Статус `verifier-pattern` / `closed-loop` «✅» для dv-hub** —
  нестабильно; карточка честно декларирует ❌, не ревизировать вверх без
  acceptance-поверхности.
- **«dv-hub showcase для capability-routing»** — нестабильно; dv-hub
  recovery-case, showcase — SERPlux (после стабилизации).

---

## closing note — read-only / no edits

Addendum — read-only в части `dv-hub`/global nerve; правок кода/инфры нет.
Основной аудит **не переписывается**. Никакое утверждение здесь не
выдаётся за выполненное; неподтверждённые runtime claims помечены
`[проверить]` либо candidate/unverified. Совместимо с
[[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]].