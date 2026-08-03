---
type: Audit Addendum
title: SERPlux — Phase C addendum (классификация findings и контрактные implications)
date: 2026-08-03
status: open
source:
  - 06-Audits/2026-08-03-serplux-phase-c-audit.md
tags: [audit, addendum, phase-c, serplux, contracts]
---
# SERPlux — Phase C addendum (2026-08-03)

> Addendum к [[06-Audits/2026-08-03-serplux-phase-c-audit]]. Не переписывает
> основной аудит и не вводит новых observations — только классифицирует уже
> подтверждённые findings по типу (bug / contract risk / documentation drift /
> ecosystem implication) и извлекает контрактные implications для глобального
> upgrade plan. Факт отделён от интерпретации; непроверенные runtime-утверждения
> помечены `[проверить]`. Без code-fix поручений.

---

## short summary

Phase C audit выявил: один подтверждённый runtime bug (`commit-guard.js`,
ESM SyntaxError), один неподтверждённый contract risk (`notify.js` catch-all
`event` ключ vs точечные ключи), системный documentation drift (число тестов,
AGENTS-таблица команд, `templates/static` ссылки, `compaction.js` persistent-
context) и три architectural/ecosystem-level implications: локальный `reviewer`
≠ глобальный `verifier` (карточка смешивает); глобальный `session-flush` против
SERP docs-based memory (модель несовместима без policy); `verify=PASS →
finalize` не enforced runtime-wise (контур loop/done — командный протокол, не
runtime-gate). Совместимость loader OpenCode с named-exports без `default` —
`[проверить]`; валидность ключа `event` catch-all — `[проверить]`.

## severity matrix

| # | finding | категория | severity | evidence | consequence |
|---|---------|-----------|----------|----------|-------------|
| 1 | `commit-guard.js` ESM SyntaxError (переобъявление `output`) | confirmed bug | critical | `const output = ...` переобъявляет параметр `output` функции `tool.execute.before` (`async (input, output) =>`); эмпирически `node` ESM-загрузка бросает `SyntaxError: Identifier 'output' has already been declared` (audit G3). `node --check` в CommonJS-режиме ошибку НЕ показывает | если loader грузит плагин как ESM — guard падает при загрузке; `/commit` «тесты — через commit-guard» (карточка + `commit.md`) формально невыполним; CI-гейт silent-broken без runtime-evidence |
| 2 | named-export без `export default` у `env-guard.js` и `commit-guard.js` | confirmed contract risk | high | audit G3: `export const EnvGuard`/`export const CommitGuard` без default; `compaction.js`/`notify.js`/глобальный `session-flush.ts` используют `export default`. Поведение loader OpenCode с named-only — UNKNOWN | совместимость loader с named-exports без default — `[проверить]`; пока не зафиксировано, всё guardian/verifier/harness-планирование опирается на недокументированный loader-контракт |
| 3 | `notify.js` generic `event:` catch-all vs точечные ключи | confirmed contract risk | medium | audit G4: `notify.js` возвращает `{ event: async (input) => ... }`; глобальный `session-flush.ts` использует точечные `"file.edited"`, `"session.idle"`. Валидность ключа `event` как catch-all — UNKNOWN | notify может быть silent-dead, если key не поддерживается; риск undetected silent failure в локальном notify без runtime-evidence. **Не доказанный runtime bug — это contract risk о состоянии проверки.** |
| 4 | локальный `reviewer` ≠ глобальный `verifier`; карточка смешивает под `verifier-pattern ✅` | ecosystem-level implication | high | audit G1: нет локального `verifier.md` в SERP; `/loop` (`~/.config/opencode/`) на шаге 2 вызывает глобального `@verifier`; локальный `reviewer.md` — quality-роль (`git diff/grep/cat`, edit deny), не acceptance | `verifier-pattern ✅` в карточке приписывает closed-loop локальному `reviewer`, что не подтверждается; capability-routing слой C теряет однозначность «кто верифицирует». Требует design decision, а не правки файла |
| 5 | `verify=PASS → finalize` не enforced runtime-wise | ecosystem-level implication | medium | audit G2/G5 (what this means): `/loop` → @verifier → STOP — командный протокол (шаги команды), не runtime-gate; нет артефакта, enforcing PASS→commit/finalize на уровне runtime | closed-loop как enforced gate остается contractual aspiration; harness проектирование бесполезно до прояснения loader/runtime contract |
| 6 | глобальный `session-flush` против SERP docs-based memory (`docs/`, не `04-Memory/`) | ecosystem-level implication | high | audit G5: глобальный `session-flush.ts` пишет в `<directory>/04-Memory/session-log/<date>.md`; SERP использует `docs/decisions.md`, `04-Memory/` в репо нет. Применимость глобального плагина к docs-based проекту — UNKNOWN (`[проверить]`) | возможны stray `04-Memory/` каталоги в SERP, конкурирующий/дублирующий flush с локальным `compaction.js`; memory model mismatch без global policy. Это architectural mismatch (docs-based vs vault-based memory), не один баг |
| 7 | drift числа тестов между артефактами | documentation drift | medium | audit G7: **test definitions by grep** = 94 (`def test_`); **documented suite claims**: карточка 111, `serp/AGENTS.md` 224, `docs/verification.md` CI 172, `serp/TASKS.md` T-001 результат 95. Источники и назначение метрик различаются: карточка/AGENTS/docs/TASKS — человекочитаемые claims о suite; `grep def test_` — подсчёт определений, не assertion-уровень; pytest total без прогона не подтверждается (parametrize, skip) | решения по upgrade принимаются на устаревших/несогласованных метриках; источник правды о тестовом покрытии отсутствует |
| 8 | `compaction.js` PERSISTENT_CONTEXT устарел (`ui-dev ⏸ paused`) | documentation drift | low | audit G6: `compaction.js:53` vs `SERPlux.md:73` (ui-dev активен) и `AGENTS.md` | persistent-context инжектируемый при каждой компакции разошёлся с карточкой — риск «что агент помнит после компакции» vs «актуальное состояние» |
| 9 | `infra-dev.md`/`container.md` ссылаются на несуществующие `templates/`, `static/` | documentation drift | low | audit G8: anti-goals и команда контейнера упоминают `templates/`/`static/`; `ls` корня SERP их не имеет (Web UI ⏸, FLAT layout) | команды/anti-goals ссылаются на фантомные каталоги; low runtime-риск, drift обнаружения |
| 10 | AGENTS-таблица команд неполна (`/commit`, `/dream` отсутствуют) | documentation drift | low | audit G9: `serp/AGENTS.md:90-97` перечисляет только `/interface`/`/container`/`/deploy`; `/commit` и `/dream` физически есть в `.opencode/command/` и в карточке | локальный documentation drift; AGENTS как операционный документ неполон |
| 11 | `/done` не пригоден к SERP без адаптации (vault-спецфичный чеклист vs docs-based memory) | ecosystem-level implication | medium | audit G2 what-this-means #4: `/done` чеклист целит в `02-Methods/`, `04-Memory/active-context.md`; SERP memory — в `docs/` и локальном `TASKS.md`. `/done` не заявлен в SERP | `/done` как глобальный контур finalization требует общей абстракции под разные memory-модели; без неё применение к docs-based проекту формально не разорвено, но семантически бессмысленно |
| 12 | `build` inline в `opencode.json` vs другие агенты как `.md` | ecosystem-level implication (structural anomaly) | medium | audit G2 / what-this-means #9: build определён в JSON-конфиге; 5 других агентов — auto-discovery `.md` файлы | содействует `build`↔`builder` ambiguities (Фаза A tension #2); каноническое определение primary-агента не зафиксировано в engineering-style-contract |
| 13 | engineering-style-contract / capability-routing не подтверждены в SERP | ecosystem-level implication (readiness) | low | audit G10: нет общего инженерного контракта layer A, нет routing-policy layer C; есть только `docs/contracts.md` (предметные контракты) + `CANON.md` | layered introduction остаётся дизайном; SERP как «боевой полигон» — гипотеза, не подтверждённое обязательство |

---

## what must enter global upgrade plan

> Только глобальные contract/policy implications. Без немедленных code-fix
> поручений. Конкретные задачи — в [[TASKS]] через planning seed.

1. **Plugin loader contract (global, blocking).** Loader OpenCode для
   `.opencode/plugins/*.js` (и `.ts`): default-only / named / both?
   Обязан ли `export default`? Это блокирующий контракт перед любой
   stabilisation плагинов и перед verifier-harness/loop-gate.
   Без зафиксированного loader-контракта `commit-guard.js` SyntaxError (#
   1) и named-export ( # 2) не имеют устойчивого fix-пути — fixed плагин
   всё равно опирается на недокументированное поведение. Источник: audit
   G3.

2. **Reviewer vs verifier contract (global kernel + local extensions).**
   Разделить как два разных контракта: `reviewer` — quality-роль (стиль,
   безопасность, контракты); `verifier` — acceptance-роль (DoD, тесты,
   PASS/FAIL, never edits). Глобальный kernel (формат PASS/FAIL, never
   edits, edit/bash deny narrow allowlist) + local extensions
   (проектные проверки). Карточка `verifier-pattern ✅` должна явно
   указывать, какой verifier (глобальный через `/loop` или локальный) —
   иначе capability-routing слой C теряет однозначность. Источник: audit
   G1, G2.

3. **Runtime enforcement contract (verify=PASS → finalize).** Зафиксировать
   что значит «verify=PASS → finalize» на runtime-уровне: gated command
   протокол / плагин hook / harness. Без этого closed-loop — командная
   конвенция, не неотвратимый gate. Связано с `commit-guard` (loader
   contract #1) — harness бесполезен, если гейт не загружается.
   Источник: audit G2, G5 (`verify=PASS → finalize не enforced
   runtime-wise`).

4. **Memory model compatibility contract (docs-based vs vault-based).**
   Глобальный `session-flush` (vault-based, `04-Memory/`) и локальный
   `compaction.js` (docs-based, `docs/decisions.md`) — competing flush
   с разными memory-моделями. Политическое решение (design contract, не
   code-fix): отключить глобальный flush для docs-based проектов / дать
   локальный override / унифицировать в event-log + sinks. `/done`
   адаптация — частный случай (чеклист целит в vault-only сущности).
   Источник: audit G5, G2 (`/done` what-this-means #4).

5. **Test metrics normalization contract (source-of-truth по тестовому
   покрытию).** Различать источники и назначение: «test definitions»
   (grep `def test_` = 94), «documented suite claim per artifact»
   (карточка 111, AGENTS 224, verification.md CI 172, TASKS.md T-001 95),
   «pytest total» (не подтверждается без прогона — parametrize/skip).
   Не называть числа из разных артефактов «реальным числом тестов».
   Нормализация — в карточке/AGENTS/docs как единый source-of-truth, без
   комментирования самих claims в этом addendum. Источник: audit G7.

6. **Primary-agent definition canon (inline vs `.md`) как часть
   engineering-style-contract.** `build` в SERP inline в `opencode.json`;
   остальные — auto-discovery `.md`. Это не баг (OpenCode допускает), но
   без канонического правила плодит `build`↔`builder` ambiguities (Фаза
   A tension #2). Входит в engineering-style-contract design (не в этот
   addendum — готовит planning seed). Источник: audit what-this-means
   #9.

## what can wait

> Низкоприоритетные drift/косметика и вопросы, не блокирующие kernel
> contracts. Документационный дрейф карточек/AGENTS/docs — отдельная
> задача сверки после Phase C, а не agent-infra upgrade.

- `compaction.js` PERSISTENT_CONTEXT (`ui-dev ⏸ paused`) — синхронизация
  с карточкой/AGENTS; документационная правка (audit G6).
- `infra-dev.md`/`container.md` ссылки на `templates/`/`static/` —
  удаление фантомных каталогов из anti-goals/команды (audit G8).
- AGENTS-таблица команд: добавить `/commit` и `/dream` в `serp/AGENTS.md`
  (audit G9).
- Сверка числа тестов между артефактами как самостоятельная задача
  (метрики #7 separate от contract normalisation #5) — точки claims не
  комментировать до нормализации контракта.
- Capability-routing / engineering-style-contract full introduction в
  SERP — гипотеза, не подтверждённое обязательство (audit G10); ниже в
  приоритете, чем loader/reviewer-verifier/runtime/memory contracts.
- `notify.js` catch-all `event` ключ — `[проверить]` валидность через
  Plugin API docs/тест; без подтверждённого runtime bug это candidate для
  plugin-policy, не blocker.
- Voice notify глобальный слой, capture↔ecosystem-map runtime loop,
  software-upgrade контуры — остаются условными кандидатами из planning
  seed, не зависят от результатов Phase C как blockers.