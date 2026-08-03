---
type: Upgrade Seed
date: 2026-08-02
status: seed
---
# Upgrade planning seed — 2026-08-02

> **Это НЕ финальный план апгрейда, а каркас будущего плана.** Здесь принципы,
> типы будущих артефактов, разделение глобального и локального и нерешённые
> вопросы. Нет поручений, нет статусов «готово», нет дат и сроков. Любой
> порядок внедрения — **кандидатный** и пересматривается после аудита и
> измерений. Конкретные задачи идут в [[TASKS]] / [[DEVELOPMENT-ROADMAP]]
> только после замеров и решений по дизайну. Источник находок —
> [[06-Audits/2026-08-02-vibecoding-layer-audit]] (разделы `confirmed tensions`,
> `what changes planning`).

## principles

> 10 принципов — **addendum-кандидат для стабилизации терминов, не внедрённый
> canon**. Дистилляция предложений research-источника; зафиксировать, что
> значит role / contract / override / route, до любых harness-контрактов.

1. **ecosystem-map / Pip-Boy как каркас планирования.** [[vault]] держится
   как операционная карта экосистемы: узлы проектов, роли, инструменты,
   связи. Планирование апгрейдов идёт поверх этой карты, а не как набор
   разрозненных задач. **Capture-сигналы привязываются к конкретным узлам
   карты; операторы (`guardian` / `meta` / `sysop` / `researcher`) читают и
   обновляют карту; `vault` как координационный узел хранит смысл, приоритеты
   и историю решений; каждый апгрейд отвечает на вопрос, какой узел карты он
   меняет и по каким рёбрам расползается дальше.** Роль T-069 как
   planning-интерфейса — proposal композиции; runtime-роль НЕ утверждать
   (см. unresolved: planning vs runtime contract).

2. **Локальные инструменты как руки агентов (`local-tooling-as-limbs`).**
   Локальная машина и серверы — исполнительные конечности агентной системы;
   детерминированные операции (`grep`, `git`, `stow`, `shellcheck`,
   `py_compile`, `notify`, `systemctl`, `sqlite`, конвертации, графы,
   индексация, diff-анализ) разгружают LLM от механики — экономия токенов /
   контекстного окна, рост автономности и достоверности. Custom Tools,
   плагины, проектные команды — исполнительная поверхность локальных агентов;
   глобальный слой не подменяет их, а даёт контракты и общую инфраструктуру.
   **Планируемый методологический блок (`02-Methods/`), не внедрённый canon.**

3. **capability-routing, а не только model-routing.** Решение «кто исполняет»
   строится по типу операции/инструменту/риск-profile, не только по выбору
   модели. **Три слоя:** A — общие инженерные конвенции (именование,
   идемпотентность, тестируемость, no hardcode, секреты, читаемость diff,
   критерии «готово»); B — language/runtime conventions (Bash, Python,
   TS/Node, Kotlin/Android, HTML/CSS/JS для утилит/дашбордов,
   YAML/JSON/TOML); C — routing policy: модель + роль + язык + риск + тип
   операции (когда `reviewer` / `verifier` / `sysop` / `researcher` / `meta`
   / `prompt-engineer` / `guardian`). См. [[model-routing]] как фон, но здесь
   — более широкий слой; design proposal, не действующая политика волта.

4. **global role kernel + local specializations/overrides.** Глобальное ядро
   роли (общий контракт — принципы, формат PASS/FAIL, never edits) +
   локальные расширения/предметная точность для `dotfiles` / `SERPlux` /
   `dv-hub` / `vault` / new. Применимо к `reviewer`, `researcher`, `sysop`,
   `guardian` и плагинам: «одна роль + локальные специализации», а не
   «один глобальный агент на всё». Контракт глобален, реализация/
   доопределение — локальны; роль ≠ файлу в каждом репо.

5. **meta + sysop + guardian как глобальная тройка (candidate).** Три
   ортогональных глобальных контура: **meta → агентная инфраструктура**
   (`/.opencode/`, `~/.config/opencode/`, vault-агенты/команды/скилы);
   **sysop → исполнительская среда / Manjaro** (пакеты, сервисы, порты,
   system state), усилитель OpenCode-апгрейдов, т.к. OpenCode живёт на
   машине; **guardian → сверка с философией / конвенциями** (инварианты,
   ограничители, `capability-routing` слой A). Роли не сливаются; их
   контракты раздельны. `researcher` (внутрь артефактов) и `sysop` (наружу на
   машину) — два луча сенсорного слоя, не дублё. **Систематизация как
   «глобальной тройки» — предложение, не внедрённое.**

6. **reviewer ≠ verifier.** Reviewer оценивает артефакт/решение (quality:
   стиль, безопасность, соответствие конвенциям, конфиг/разрешения);
   verifier исполняет детерминированную проверку (билд/тесты/линтер/DoD,
   PASS/FAIL, never edits). Разные слои и разные контракты; не подменять.
   **Общий global contract (принципы, формат PASS/FAIL) + local extensions**
   (пер-проектные проверки, permission-окружение); без подмены (см.
   [[verifier-pattern]], [[closed-loop]]; также `reviewer-pattern` как
   кандидат на оформление).

7. **prompt-engineer как prompt-normalizer + task-compiler (candidate).**
   Не «красивый переписыватель текста», а двухрежимная прослойка: **режим 1 —
   `prompt-normalizer`** (свободная задача → цель / ограничения / контекст /
   DoD → структурированный spec); **режим 2 — `task-compiler`** (знает
   roster/routing/порядок/артефакты → пайплайн исполнения). Цепочка:
   пользователь свободно → `prompt-engineer` собирает spec → `guardian`
   проверяет полноту/конфликты → `meta`/project planner запускает исполнение.
   Заявлен как «один из сильнейших кандидатов на апгрейд после аудита» —
   кандидат, не существующая роль.

8. **event-log-first memory + periodic distillation + hybrid memory.**
   Память — append-only event-log как первичный источник; raw machine events
   (`file.edited`, `command invoked`, `task start/finish`, verifier PASS/FAIL,
   `plugin fired`, `changed files`, `commit sha`) — дешёвая машинная хроника
   без токенов. Поверх — periodic semantic distillation (LLM периодически
   дистиллирует event log в facts / active-context / decisions / session
   summary). Hybrid: raw machine memory + distilled semantic memory;
   `active-context` = summary + последние события. Raw и дистиллированное слои
   не подменяют друг друга. **Реализационные опоры (candidate options, не
   решение):** SQLite/JSONL event store, `rg`/`jq`/`awk`/python локальная
   дистилляция, файловые watchers, git metadata, cron/systemd user timers.
   Минимизация участия LLM в механическом сохранении памяти. См.
   [[memory-management]], [[distill-pattern]].

9. **capture как intake-слой апгрейдов.** [[capture]] (скрапинг сигналов
   извне) — не просто сбор ссылок, а первый этап апгрейда проекта.
   **Цепочка intake→upgrade:** (1) signal intake (Telegram/др.) →
   (2) classification → узел карты; (3) relevance scoring; (4) project mapping
   (`dotfiles` / `SERPlux` / `dv-hub` / `vault` / new) → (5) upgrade path
   generation (какой agent / method / plugin / skill) → (6) execution or
   backlog. Для `dotfiles` — через «Linux UX Lab» / software-Manjaro upgrade
   loop (агент, принимающий предложения по софту/апгрейдам Manjaro). Не
   финальный roadmap, а источник кандидатов; ручная координация в `/inbox`
   остаётся фактом.

10. **Глобальные vs локальные плагины (boundary; global notify НЕ внедрён).**
    Тот же принцип, что у агентов: global role kernel + local specializations.
    **Глобальные плагины** = событийная инфраструктура экосистемы (notify,
    session/event log, guard plugins, infra/code boundary enforcement).
    **Локальные плагины** = проектно-специфичные (SERPlux commit-guard/CI,
    dv-hub notify/TS, dotfiles system-specific). Граница — по ownership и
    видимости, не по «удобно положить сюда». **Внимание:** global notify
    сейчас отсутствует (confirmed fact Phase A), поэтому само введение
    глобального event-слоя — candidate / open design, не факт. См.
    [[tool-integration-pattern]].

## future global artifacts

Кандидаты/типы будущих артефактов. Без статусов «готово» — это перечень того,
что может появиться; конкретные файлы/задачи — после решений по дизайну.

- **guardian** — глобальный слой ограничителей и инвариантов (сверка с
  философией / конвенциями; может выступать gate после `prompt-engineer` spec).
- **Глобальный sysop** — роль исследования/эксплуатации машины (Manjaro,
  сервисы, пакеты) как усилитель OpenCode-апгрейдов.
- **Глобальный researcher** — роль исследовательского поиска/синтеза внутрь
  артефактов (код, git, docs, конфиги, история, связи).
- **Глобальный reviewer** — роль оценки артефактов (≠ verifier), global
  contract + local extensions.
- **Глобальный verifier contract** — унификация global/dotfiles verifier
  (permissions, allowlist), чтобы runtime-gate `verify=PASS → finalize` стал
  enforceable, а не справочник.
- **prompt-engineer layer** — `prompt-normalizer` + `task-compiler` как
  отдельный слой перед routing/guardian.
- **meta proactive algorithmic loop** — событийный/периодический контур meta
  (hooks, периодические инспекции, diff-based проверки, signals from
  `capture`, signals from `ecosystem-map`) → точечное действие, не «подумай
  обо всём». Сегодня hook-скелета для meta-проактивности нет.
- **Переработанный notify (глобальный event-слой)** — notify-инфра поверх
  event-log, опц. голосовой канал `[проверить]`; candidate, т.к. global notify
  сейчас отсутствует.
- **Пересобранный memory/event-log слой** — append-only event-ledger (SQLite/
  JSONL) + distilled projection (facts/active-context/decisions) +
  локальная дистилляция (rg/jq/awk/python) + watchers / git metadata /
  timers.
- **Routing spec** — контракт `capability-routing` (3 слоя: инженерные
  конвенции → language/runtime → routing policy по модели/роли/языку/
  риску/типу операции).
- **Code quality / code style conventions** — глобальные конвенции качества
  кода как часть контрактов ролей (`capability-routing` слой A). Конкретизируется
  в `engineering-style-contract` (см. ниже) — общий лозунг «пиши хорошо»
  превращается в отдельный инженерный объект с профилями и gate-проверкой.
- **`engineering-style-contract` (контракт инженерного качества кода)** —
  отдельный инженерный объект, а не набор общих лозунгов про «чистый код».
  **Форма — короткий общий контракт + language-specific профили, НЕ монолитный
  трактат/файл на тысячи строк.** Ядро контракта фиксирует решения:
  когда ООП оправдано и когда оно лишнее; когда достаточно функционального
  стиля; когда нужен класс, модуль или plain script; как делить файлы;
  как оформлять конфиг-код; как писать shell; как проектировать утилиты;
  какие антипаттерны считаются anti-shitcode. Поверх ядра — **языко-
  специфичные профили** (Bash, Python, TS/Node, Kotlin/Android, HTML/CSS/JS
  для утилит/дашбордов, YAML/JSON/TOML), расширяющие и доопределяющие общее
  ядро под runtime. **Интеграционные ребра:** routing
  выбирает subagent по языку/типу задачи, опираясь на профиль;
  `reviewer`/`verifier` проверяют контракт с **минимальным расходом токенов**
  (детерминированные checks/linter/DoD-чек-лист предпочтительнее свободного
  LLM-разбора). Candidate / planned artifact, не готовый метод и не done;
  конкретные файлы/имя/задачи — после design decisions (см. unresolved).
  Разворачивает «Code quality / code style conventions» выше до enforceable
  формы; смежная task T-078 — gate в пайплайнах, T-082 — проектирование
  самого контракта.
- **`local-tooling-as-limbs` method block** — отдельный кандидат в
  `02-Methods/` с детерминированным tool-canon (`grep`/`git`/`stow`/
  `shellcheck`/`py_compile`/`notify`/`systemctl`/`sqlite`/…).
- **Интеграция capture с dotfiles/software-upgrade контуром** — связка
  intake-сигналов с узлами update-цикла (Linux UX Lab / software-Manjaro
  upgrade loop).
- **ecosystem-map как operational upgrade map** — карта экосистемы она же —
  карта апгрейдов: узлы = кандидаты, связи = зависимости; capture-сигналы
  привязаны к узлам.

## ecosystem-map as planning UI

> **Candidate / planning design, не утверждённый runtime-интерфейс.**
> Эволюция T-069 / `tools/ecosystem-map/` / Pip-Boy из визуального артефакта в
> рабочий интерфейс планирования апгрейдов (см. principle 1 и
> `ecosystem-map как operational upgrade map` выше). Здесь фиксируется только
> **какой набор сущностей/связей карта должна показывать** для планирования;
> runtime-контракт (живая карта, читаемая агентами в цикле) — отдельный
> unresolved вопрос, здесь НЕ утверждается.

Карта планирования апгрейдов должна показывать:

- **Узлы проектов** — `dotfiles` / `SERPlux` / `dv-hub` / `vault` / new; узел =
  кандидат апгрейда.
- **Глобальный слой** — vault + `~/.config/opencode/` (role contracts, routing
  spec, event infrastructure, code quality canon) как координационный контур
  поверх узлов.
- **Capture sources** — intake-сигналы (Telegram/др.), привязанные к конкретным
  узлам карты (см. principle 9, intake→upgrade).
- **Planned upgrades** — кандидатные апгрейды/задачи, размещённые по узлам и рёбрам
  зависимости (что блокирует что).
- **Tensions / tech debt** — подтверждённые натяжения и техдолг (из
  [[06-Audits/2026-08-02-vibecoding-layer-audit]] — confirmed tensions), с привязкой к
  узлам.
- **Status of methods and agents** — статус внедрения методов `02-Methods/`
  (❌ / 🟡 / ✅) и ролей/агентов по узлам; какой контракт готов, какой кандидат.

Связи/рёбра: capture → узел; узел → planned upgrade; planned upgrade →
зависимость (другой узел/метод/роль); tension → узел. **Это planning-роль карты;
runtime-роль остаётся отдельным open question** (см. unresolved: ecosystem-map
runtime vs planning).

## local vs global boundaries

Только границы и ownership. Не утверждение о внедрении — только разделение
«где живёт».

- **Глобальный слой (vault + `~/.config/opencode/`):** общий role contract,
  общие conventions (code quality/style — слой A `capability-routing`),
  event infrastructure (event-log schema, audit-log), routing spec,
  агентная инфраструктура ролей (meta/sysop/guardian/researcher/reviewer/
  prompt-engineer как контракты), **глобальная событийная инфраструктура
  плагинов** (если вводится — notify/event log/guards/boundary enforcement).
- **Локальный проектный слой (`<repo>/.opencode/`):** project-specific
  quality checks, project agents/специализации, project-specific
  plugins/tools/commands, per-project `opencode.json` overrides, локальные
  commit-guard/CI/TS/system-specific плагины.
- **`tools/ecosystem-map/` и [[capture]]** — координационный/global слой: карта
  узлов и intake-сигналов живёт глобально; **реализация project-specific
  upgrade остаётся локальной** (глобальный слой не исполняет апгрейд за
  проект, он координирует).
- **command/shell constraint (cross-cutting):** действия не выполняются
  произвольно «по желанию агента» — действие идёт через skills / hooks /
  plugins / loop pipeline / разрешённые tool/task контуры. Произвольный shell
  по инициативе агента — `ask` или `deny`, не default. Следствие:
  `prompt-engineer` компилирует не «идеальный текст», а OpenCode-совместимый
  pipeline; `meta`-проактивность опирается на hooks/plugins/skills, а не на
  надежду; `session-flush` и `notify` — событийные плагины, не агентные
  рассуждения. (Подтверждено Phase B фактом про `permission.bash` allowlists
  в глобальных `agent/*.md`.)
- **Override-зона `[проверить]`:** где именно живут global/local overrides
  (приоритет, мердж-политика) — открытый вопрос, не решение.

## unresolved design choices

Вопросы, а не решения. Спорное помечено `[проверить]`.

- **Стабилизация терминов/границ** предшествует harness-контрактам: что значит
  role / contract / override / route, какие replay/acceptance критерии. Без
  этого всё ниже не имеет критериев готовности. `[проверить]` baseline сейчас
  отсутствует.
- Какие роли поднимать первыми — одним батчем или по приоритету?
  `[проверить]` зависимость от routing spec.
- Как guardian связан с meta — подчинение, параллель, ортогональный контур?
  `[проверить]` договор о границах.
- Где живут global/local overrides — в `opencode.json`, в `.opencode/`, в
  vault? `[проверить]` priority/merge семантика.
- Как routing spec учитывает: язык проекта / risk-profile / тип операции /
  модель. Минимальный набор полей? `[проверить]` против [[model-routing]]
  warning про overhead; `model-routing` расширяется до capability-routing
  через hooks/plugins, или отдельная routing-policy подсистема?
- Как устроить voice-notify — отдельный плагин, событие event-log'а, опц.
  зависимости от среды? `[проверить]` окружение/расположение daemon.
- **Глобальные плагины — вводить ли глобальный event-слой (notify /
  session-event log / guard / infra-code boundary), при confirmed fact
  «глобального notify нет»?** Конфликт proposal ↔ факт остаётся открытым, не
  снимается авт. `[проверить]`.
- Event-log schema: набор полей одной записи, rotation, addressing. SQLite
  vs JSONL, watchers vs git metadata vs cron/systemd timers — выбор
  реализации. `[проверить]`.
- Raw vs distilled memory — что первично, что projection, где граница
  достоверности. `[проверить]` не плодить два источника правды; остаётся ли
  `facts.md` единственной проекцией.
- Как связать capture signals с map nodes и backlog — автоматическая
  классификация или ручная третья? `[проверить]` scope агента intake.
- **Ecosystem-map: runtime-роль** (живая карта, используемая агентами в
  цикле) vs **planning-роль** (карта для планирования апгрейдов)? И то и то?
  `[проверить]` разные контракты; runtime-контур не подтверждён, «будущий
  runtime не выдавать за существующий».
- Verifier/reviewer contract — общий шаблон и как project-local extensions
  доопределяют его. `[проверить]` без подмены (reviewer≠verifier);
  унификация global/dotfiles verifier permissions — отдельный вопрос.
- **`meta`-проактивность — алгоритмический контур** (hooks/периодические
  инспекции/diff-проверки/capture-signals/ecosystem-map-signals): сегодня
  hook-скелета нет. Реализовывать ли и через какие хуки? `[проверить]`.
- **`prompt-engineer`** — вводить ли, в каком объёме (только normalizer или
  сразу task-compiler), и в каком порядке с `guardian`/`meta`? `[проверить]`
  до addendum.
- **`local-tooling-as-limbs` как `02-Methods/` canon:** оформлять ли
  отдельным методом с детерминированным tool-canon? `[проверить]` сегодня —
  предложение.
- **`engineering-style-contract` — расположение/версионирование/gates
  (не финальный design, кандидат):** где живёт общий контракт и где language
  profiles — один файл `02-Methods/` + per-language профили, или дерево, или
  часть role contracts? Как версионировать и наследовать профили (базовый
  контракт → профиль языка → профиль проекта), чтобы переопределение не
  плодило два источника правды? Какие минимальные gates обязательны для
  enforce (deny/pass-fail), какие advisory? Как `reviewer`/`verifier` проверяют
  контракт без token-heavy LLM-review — детерминированные checks/linter/
  DoD-чек-лист вместо свободного разбора? `[проверить]` до addendum; design
  proposal, не решение.
- **phase gate «после addendum → Фаза C / SERPlux»** — рекомендация
  источника (planning proposal), не confirmed fact; SERPlux как «боевой
  коммерческий проект» — целевая проверка методологии, не подтверждённое
  обязательство. `[проверить]` до addendum.

## candidate implementation order

Только **условная** последовательность/группы зависимостей (addendum-кандидат
для стабилизации терминов). Не roadmap, не «сделать всё», без дат и сроков.
Порядок **пересматривается после аудита и измерений**; переход к Phase C /
SERPlux — только **как условная гипотеза после addendum**, не решение.

- **0) candidate — стабилизация терминов/границ + replay/acceptance критерии.**
  Зафиксировать, что значит role / contract / override / route и что вообще
  меряем (token/cycle count, pass rate, replay set, A/B); baseline сейчас
  отсутствует. Зафиксировать `local-tooling-as-limbs` как candidate-метод
  (не canon). Без этого всё ниже не имеет критериев готовности.
- **1) candidate — role contracts + routing spec.** Контракты ролей
  (meta/sysop/guardian/reviewer/researcher/prompt-engineer/verifier — global
  kernel + local extensions) + routing spec (`capability-routing` 3 слоя).
  Ничего не запускается, только описание границ; унификация `build`↔`builder`
  и подъём/декларация `/commit` для `/done` как предусловия harness'а.
- **2) candidate — memory/event-log и событийная notify-инфра.** Event-ledger
  schema (SQLite/JSONL candidate) + постоянные опоры (`session-flush`-like)
  + distilled projection (rg/jq/awk/python), watchers, git metadata,
  cron/systemd timers; notify как событие поверх event-log. Зависит от (0)
  по части терминов и от (1) по contracts; помнит, что global notify сейчас
  отсутствует → вводится как candidate/open.
- **3) candidate — global role candidates + local overrides.** Кандидатные
  минимальные реализации ролей (meta/sysop/guardian/reviewer/researcher/
  prompt-engineer) + механизм local overrides для `dotfiles`/`SERPlux`/
  `dv-hub`/`vault`. Зависит от (1) контрактов; `meta`-проактивность здесь
  только как алгоритмический контур (hooks/периодические инспекции/diff/
  capture-signals), не самовольное творчество.
- **4) candidate — capture ↔ ecosystem-map planning loop.** Связка intake
  (capture) → classify map node → relevance → project mapping → upgrade path
  → execution/backlog; capture-сигналы привязаны к узлам карты. Зависит от
  (1) контрактов и глобальной map-инфраструктуры; runtime-роль map отдельно
  решается (unresolved).
- **5) candidate — voice notify и project-specific software-upgrade loop.**
  Опц. голосовой notify; локальные software-upgrade циклы (dotfiles / Linux
  UX Lab / software-Manjaro upgrade loop). Самый «продуктовый» слой,
  ставится когда инфра (2,3) стабилизирована.
- **6) candidate — оценка и решение о следующем цикле.** Замеры против
  критериев (0); пересмотр порядка; решение, какие кандидаты становятся
  задачами в [[TASKS]] / [[DEVELOPMENT-ROADMAP]]. Переход к **Phase C /
  SERPlux** — только как условная гипотеза после addendum (целевая проверка
  методологии на боевом коммерческом проекте), не подтверждённое
  обязательство.