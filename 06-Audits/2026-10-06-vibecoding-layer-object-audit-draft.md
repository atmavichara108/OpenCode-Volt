---
type: audit-draft
status: draft
timestamp: 2026-10-06
source: coordinator mandate via librarian
provenance: автор «внедрение» передал отчёт линии librarian по решению Рудры 2026-10-06; владение принято librarian; статус остаётся draft
---

# Draft-отчёт объектного аудита вайбкодинг-слоя

Read-only срез на 2026-10-06. Каждый ряд — один объект. `✅` означает только
наличие проверяемого артефакта, а не полную готовность; `[проверить]` оставлено
там, где нужна отдельная runtime-проверка.

## 1. Объекты

| Имя | Категория | Owner | Path | Статус now | История | Evidence |
|---|---|---|---|---|---|---|

Переходы статусов:

| Статус | Допустимый переход |
|---|---|
| ✅ | остаётся ✅ после проверки; при проблеме → ⚠️/defect-open |
| 🟡 | → ✅ после закрытия acceptance; при блокере → BLOCKED |
| BLOCKED | → 🟡 после снятия блокера; → retired по отдельному решению |
| retired | остаётся retired; возврат возможен только новым решением |
| ⚠️/defect-open | → ✅ после исправления и проверки; иначе остаётся ⚠️ |
| OKF v0.1 | архитектура | librarian | `AGENTS.md`, `00-INDEX.md` | ✅ draft | 2026-10-05 readiness | `06-Audits/2026-10-05-pae-phase1-readiness-audit.md` §§1–4 (2026-10-05) |
| librarian | агент | Vault | `AGENTS.md` | ✅ primary | active 2026-10-06 | `/home/rudra/Projects/OpenCode-Vault/AGENTS.md` (2026-10-06) |
| tree-cop | агент | global | `~/.config/opencode/agent/tree-cop.md` | ✅ subagent | git isolation | `/home/rudra/dotfiles/opencode-global/.config/opencode/agent/tree-cop.md`, `tools/tree-cop/tree-cop.py` (2026-10-06) |
| researcher | агент | global | `~/.config/opencode/agent/researcher.md` | ✅ read-only | bash permission fix 2026-10-05 | `/home/rudra/dotfiles/opencode-global/.config/opencode/agent/researcher.md`, git `c13ecbf` |
| reviewer | агент | global | `~/.config/opencode/agent/reviewer.md` | ✅ read-only | bash permission fix 2026-10-05 | `/home/rudra/dotfiles/opencode-global/.config/opencode/agent/reviewer.md`, git `c13ecbf` |
| verifier | агент | global | `~/.config/opencode/agent/verifier.md` | ✅ acceptance | bash permission fix 2026-10-05 | `/home/rudra/dotfiles/opencode-global/.config/opencode/agent/verifier.md`, git `4c7d132` |
| capability-routing | skill/method | global | `~/.config/opencode/AGENTS.md`, `02-Methods/capability-routing.md` | ✅ | schema fixed 2026-10-06 | `04-Memory/idea-graph/nodes.jsonl`: узел `proto-capability-routing` (2026-10-06) |
| decision-queue | skill/plugin | global | `~/.config/opencode/plugins/decision-queue-hook.ts`, `~/.config/opencode/lib/decision-queue-helpers.js` | 🟡 | hook exists; acceptance remains [проверить] | `06-Audits/2026-10-05-pae-phase1-readiness-audit.md` §2.3 (2026-10-05) |
| spec-write-routing | plugin | global | `~/.config/opencode/plugins/spec-write-routing.ts` | ✅ | global routing | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/spec-write-routing.ts` (2026-10-06) |
| branch-auto | plugin | global | `~/.config/opencode/plugins/branch-auto.ts` | ✅ | branch policy | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/branch-auto.ts` (2026-10-06) |
| main-protector | plugin | global | `~/.config/opencode/plugins/main-protector.ts` | ✅ | moved to global dotfiles | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/main-protector.ts`, git history (2026-10-06) |
| replay-budget | plugin | global | `~/.config/opencode/plugins/replay-budget.ts` | ⚠️ дефект открыт | in-place mutation/task prompts | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/replay-budget.ts`, `TASKS.md` (2026-10-06) |
| input-security | plugin | global | `~/.config/opencode/plugins/input-security.ts` | ✅ | smoke 14/14 [проверить] | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/input-security.ts` (2026-10-06) |
| session-flush | plugin | global | `~/.config/opencode/plugins/session-flush.ts` | ✅ exists | проверка работы [проверить] | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/session-flush.ts` (2026-10-06) |
| tree-hygiene | plugin | global | `~/.config/opencode/plugins/tree-hygiene.ts` | ✅ exists | проверка работы [проверить] | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/tree-hygiene.ts` (2026-10-06) |
| telemetry | plugin | global | `~/.config/opencode/plugins/telemetry.ts` | ✅ exists | T-124 PASS | `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/telemetry.ts`, git `bb85f0f` |
| telegram-capture | tool | Vault | `tools/telegram-capture/` | ✅ exists | tests/config present | `tools/telegram-capture/README.md`, `tools/telegram-capture/capture.py` (2026-10-06) |
| ecosystem-map | tool/UI | Vault | `tools/ecosystem-map/` | ✅ exists | registry + UI; live Pip-Boy real-time не заявляется | `tools/ecosystem-map/registry.json`, `index.html`, `pipboy.py` (2026-10-06) |
| idea-graph | tool | Vault | `04-Memory/idea-graph/`, `tools/idea-graph/` | ✅ | validator PASS 2026-10-06 | `tools/idea-graph/validate.mjs`, `04-Memory/idea-graph/nodes.jsonl` (2026-10-06) |
| peers | tool | Vault | `tools/peers/` | ✅ method/prototype | live protocol [проверить] | `tools/peers/peer_role.py`, `peer_lease.py` (2026-10-06) |
| tree-cop | tool | Vault | `tools/tree-cop/tree-cop.py` | ✅ | implementation 2026-09 | `tools/tree-cop/README.md`, `tools/tree-cop/tree-cop.py` (2026-10-06) |
| mem-index | tool | Vault | `tools/mem-index/` | ✅ exists | index present | `tools/mem-index/index.py`, `index.json` (2026-10-06) |
| key-rotator | tool | Vault | `tools/key-rotator/` | ✅ exists | gateway layer 2026-09-28 | `tools/key-rotator/README.md`, `rotate.py` (2026-10-06) |
| mcp-readonly | tool | Vault | `tools/mcp-readonly/server.py` | BLOCKED/frozen | no active acceptance | `tools/mcp-readonly/server.py` (2026-10-06); runtime [проверить] |
| git-freed | tool/agent | Vault | `tools/git-agent/freed.py`, `.opencode/agents/git-freed.md` | ✅ | first circuit 2026-10-06 | `04-Memory/session-log/2026-10-06.md` строки 29–40 (2026-10-06), git `092f81a` |
| version-oracle | tool | Vault | `tools/version-oracle/` | ✅ exists | panel added 2026-10-06 | `tools/version-oracle/README.md`, git `9b305d4` |
| vibeos-vitrina | tool/UI | Vault | `tools/vibeos-vitrina/` | ✅ exists | vitrina 2026-10-06 | `tools/vibeos-vitrina/charts.py`, git `8d46e3f` |
| TradingMind | candidate project | Rudra | external repo/card path [проверить] | BLOCKED | только типизированные связи (typed-edge); первоначальная настройка не подтверждена | `04-Memory/idea-graph/nodes.jsonl` `tech-tradingmind`, `stream-misfit-tradingmind-stalled` (2026-10-05) |
| SERPlux | project | project owner | `03-Projects/SERPlux.md` | ✅ active | 21 commits/3 weeks | `03-Projects/SERPlux.md`, `06-Audits/2026-10-05-pae-phase1-readiness-audit.md` §2.1 (2026-10-05) |
| dv-hub | project | project owner | `03-Projects/dv-hub.md` | 🟡 активно, есть незакоммиченные изменения (dirty) | verifier closed-loop ❌ | `03-Projects/dv-hub.md`, readiness audit §2.1 (2026-10-05) |
| dotfiles | project/infra | sysop | `/home/rudra/dotfiles/opencode-global/` | ✅ v3 | global kernel commits 2026-10-05/06 | `03-Projects/dotfiles.md`, git history (2026-10-06) |
| recruiting-hr | project | project owner | `03-Projects/recruiting-hr.md` | 🟡 первоначальная настройка | git not initialized [проверить] | `03-Projects/recruiting-hr.md`, readiness audit §2.1 (2026-10-05) |
| ChaT | project | project owner | `03-Projects/ChaT.md` | BLOCKED/parked | 0 commits, 20 dirty | `03-Projects/ChaT.md`, readiness audit §2.1 (2026-10-05) |
| noop-guard | archived plugin | — | historical only | ❌ retired | removed 2026-09-23 after restart loop | `04-Memory/session-log/2026-09-23.md` (2026-09-23) |
| claude-mem | archived tool | — | historical only | ❌ retired | replaced by file memory 2026-07-02 | `04-Memory/session-log/2026-07-02.md` (2026-07-02) |
| Aider | archived tool | — | historical only | ❌ retired | retired; no live path | `06-Audits/2026-10-05-pae-phase1-readiness-audit.md` §3 (2026-10-05) |

## 2. Противоречия и честные границы

- ecosystem-map и UI существуют, но live Pip-Boy real-time не утверждается.
- decision-queue hook существует, но acceptance-гейт [проверить], полностью
  работающим его считать нельзя.
- `✅` у tools означает наличие файла/теста/evidence, не гарантию runtime.
- TradingMind, mcp-readonly и архивные объекты явно BLOCKED/retired; резервный путь (fallback)
  к «работает» запрещён.

## 3. Ranked минимальные изменения

1. Закрыть acceptance decision-queue: одно живое срабатывание hook (hook-fire) и verifier PASS.
2. Провести быструю проверку работы (runtime-smoke) global plugins и tools с пометкой [проверить].
3. Для Maya-lint дождаться verifier; до этого сохранять status candidate.
4. Зафиксировать для ecosystem-map границу: snapshot/UI, без real-time обещания.
5. Решить судьбу TradingMind и ChaT отдельным решением Рудры; не строить на них
   новые зависимости.
6. Для mcp-readonly либо назначить новый мандат, либо оставить frozen.

Отчёт остаётся **draft**, не канон; независимый quality-review/verifier впереди.

## 4. BLOCKED / [проверить]

**BLOCKED:** TradingMind (нет подтверждённого repo/card evidence),
mcp-readonly (frozen), ChaT (parked/заброшен, deadwood), архивные noop-guard,
claude-mem и Aider (неживые). **[проверить]:** проверка работы global plugins,
decision-queue acceptance, peers live-протокол, recruiting-hr git и внешние
репозитории, которые не входят в read-only доступ этого прохода.

---
---
## Приложение A v2 (2026-10-06, владение: librarian, мандат B12)

Переписано по reviewer-находкам (4 major). Все старые наблюдения отчёта
сохранены append-only; этот append — замещающий статусный справочник
с явным маппингом старого на новое. Никаких канонизаций: файл остаётся draft.

### A.1 Статусная машина v2 и маппинг старых кодов

Машина v2 (6 кодов + 1 допуск):

| Код | Значение | Переход | Evidence |
|---|---|---|---|
| stable | артефакт и проверка прямые: файл/коммит/валидатор/прогон с датой | → defect-open при сбое | путь+дата/коммит |
| prototype | реализовано; живое применение [проверить] или acceptance не закрыт | → stable после runtime-проверки | файл+дата |
| planned | спека/концепт записаны, артефакта на диске нет | → prototype после артефакта | спека+дата |
| live | непрерывно работает | → defect-open при сбое | runtime-журнал/метрики |
| blocked | есть блокер с причиной | → prototype после снятия блокера | причина+дата |
| retired | выведено по решению Рудры | новый старт = новое решение | решение Рудры |

Допуск: status **candidate/unknown** — вне машинного словаря условий,
используется только для TradingMind (см. A.4): репо существует, контур
не стартовал.

Маппинг старых кодов §1 → новых:
- ✅ + «exists / проверка [проверить]» → **prototype** (не stable);
- ✅ + прямая проверка с датой (коммит/валидатор/прогон) → **stable**;
- 🟡 → **prototype**; ⚠️/defect → **defect-open**;
- BLOCKED → **blocked**; ❌/retired → **retired**.

Пометка замещения (append): таблица переходов старой машины (строки 22–28
исходного отчёта) и колонка «Статус now» §1 — **superseded** этой машиной;
старые строки сохранены выше и читаются через маппинг, а не напротив.
Пустая заголовочная строка таблицы объектов (§1) и «примонтированная»
к ней таблица переходов — признаны структурным дефектом исходного
отображения; правка по месту невозможна без переписывания старого текста,
поэтому статусы собраны здесь, а §1 остаётся исходным read-only срезом.

### A.2 Объекты по машине v2 (полный список; строки §1 не правлю)

| Объект | Код v2 | Обоснование |
|---|---|---|
| OKF v0.1 | stable | структура подтверждена файлами (Architecture.md, 00-INDEX.md) |
| librarian | stable | живой агент, конфиг на диске |
| verifier / reviewer / researcher / tree-cop | stable | файлы в `~/.config/opencode/agent/` — прямая проверка сессии |
| main-protector / branch-auto / spec-write-routing | stable | файлы плагинов; живые pre-commit прогоны этой сессии |
| replay-budget | defect-open | открытый дефект T-143 (мутация tool-input; см. TASKS.md P0) |
| input-security | prototype | smoke 14/14 есть; live hook-fire [проверить] |
| session-flush / tree-hygiene | prototype | реализованы; живое применение [проверить] |
| decision-queue | prototype | hook есть; acceptance [проверить] |
| telemetry (T-124) | prototype | см. A.3: понижение T-124 PASS → prototype |
| telegram-capture | prototype | тесты/файлы есть; живое применение [проверить] |
| ecosystem-map | stable | registry+UI; read-only SSE acceptance PASS (T-141, 2026-09-06); real-time не обещается |
| idea-graph | stable | валидатор PASS exit 0 (вывод в A.3); append-only дисциплина |
| peers | prototype | метод/прототип; live-protocol [проверить] |
| mem-index / key-rotator / version-oracle / vibeos-vitrina | stable | артефакты с датой на диске |
| git-freed | prototype | первый контур + smoke (session-log 2026-10-06); реальная гонка [проверить] — запланированный шаг |
| mcp-readonly | blocked | frozen |
| SERPlux / dotfiles | stable | активные проекты; dotfiles v3 подтверждена |
| dv-hub / recruiting-hr | prototype | работы есть; acceptance не закрыт |
| ChaT | blocked | parked/deadwood |
| TradingMind | candidate/unknown | см. A.4 |
| Maya-lint v2 | prototype | автор igraphv2; пакет в дереве dotfiles, dry-run 8 репо, gate ждать digest |
| noop-guard / claude-mem / Aider | retired | исторические решения со ссылками |

### A.3 T-124 и validator PASS — точное evidence

**T-124 (ecosystem telemetry) — prototype, не PASS** (понижение
старого заявления честно):
- спецификации зафиксированы в `docs/specs/` (коммит `e9d0cbe`, 2026-09-24);
- runtime-артефакты: `control-plane/telemetry/provider-health.jsonl` —
  23 записи, первая 2026-09-27, формат entry = ts/provider_id/status/
  models_count (из спецификации);
- `control-plane/audit-log.jsonl` — 36 записей, append-only,
  metadata-only, живые записи этой сессии 2026-10-06;
- полный acceptance (2-недельный weekly-report цикл) — не прогонялся
  здесь → старая формулировка «T-124 PASS» superseded маппингом
  на prototype.

**Validator PASS (idea-graph) — stable.** Прямой прогон этой сессии
(`node tools/idea-graph/validate.mjs`, 2026-10-06):

=== idea-graph v2 validation ===
nodes: 165   edges: 198   protocol: 3
by graph:  {"stream":92,"proto":21,"world":14,"organ":7,"mech":8,"tech":8,"quest":7,"event":8}
by status: {"raw":16,"candidate":89,"accepted":56,"implemented":4}
PASS

exit 0, дата/время снятия: 2026-10-06 текущая сессия.

### A.4 TradingMind — candidate/unknown; BLOCKED-утверждения superseded

- Путь репо подтверждён: `/home/rudra/Projects/TradingMind`
  (ls: 00_Maps, 01_Daily, 02_Mentor, 03_Glossary — content-only проект).
- Карточки в 03-Projects нет (0 hits).
- Заметки: старые строки §1 (TradingMind BLOCKED / нет repo evidence)
  и §4 — superseded: репо подтверждён ls'ом, карточка отсутствует →
  candidate/unknown по машине A.1. Это не «не существует» и не
  «stopped»: репо содержит материалы, но в PAE-контур не собран;
  переход — через новый мандат (карточка + карта).
- Рекрутинг/TG — отдельный memory scope (согласовано со старшим),
  в знаменатель метрики полноты М3 не входят.

### A.5 Maya-lint v2 — реквизиты (уточнение A.2-строки)

Спека: `/home/rudra/dotfiles/docs/specs/maya-lint-v2.md` (kind: contract).
Словарь: `/home/rudra/dotfiles/tools/maya-lint/dictionary.json`
(v2: 15 терминов, phrase-only, whitelist[5] — сам spec-файл,
governor=librarian). Сканер: `scan.mjs` (report/--gate, zero-LLM).
Dry-run (200 коммитов/реп): Vault 40 (ожидаемо: внутри диегеза — язык мира разрешён),
dotfiles 1 (Pip-Boy в теле коммита), AndroidOS 3 (Pip-Boy в git-log),
serp/dv-hub/ChaT/recruiting-hr/TradingMind — 0. Гейт не вшит; report-mode
до digest (2 недели, FP < 1%) + решение Рудры.

Файл остаётся **draft**; независимая quality-review/verifier далее.
