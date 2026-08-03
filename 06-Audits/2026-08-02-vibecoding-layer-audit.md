---
type: Audit
title: Vibe-coding layer audit — global nerve + dotfiles
date: 2026-08-02
status: open
scope: Слой вайбкодинга: global nerve (`~/.config/opencode/`), dotfiles-архитектура, T-069 ecosystem-map, capture/routing/memory (п. 19–21).
source: 99-Inbox/vault-upgrade-research-2026-08-02.md
tags: [audit, vibe-coding, global-nerve, dotfiles, ecosystem-map]
---
# Vibe-coding layer audit — 2026-08-02

> Аудит фиксирует **подтверждённые результаты** по глобальному нерву, dotfiles,
> T-069 и пунктам 19–21. Факт отделён от интерпретации: факты — в `confirmed
> facts`, выводы — в `confirmed tensions` / `what changes planning`, спорное —
> в `what remains open`. Не план; см. [[06-Audits/2026-08-02-upgrade-planning-seed]].
> Пути к компонентам и их типы даны буквально по дереву файлов; «командами»
> названы только `command/*.md`.

## confirmed facts

### Фаза A — global vibecoding layer / nerve

- **Реальный путь global nerve:** `~/dotfiles/opencode-global/.config/opencode/`
  → `stow` → `~/.config/opencode/`. Глобальная конфигурация не правится напрямую
  в `~/.config/`, а стасится из dotfiles. Подтверждено по дереву файлов.
- **Точные компоненты global nerve (по типам, не «все команды»):**
  - **agents** — `agent/meta.md` (meta-infra editor, `mode: subagent`), `agent/verifier.md` (acceptance verifier, `mode: subagent`, PASS/FAIL). Глобальных primary-агентов нет.
  - **commands** — `command/done.md`, `command/loop.md`.
  - **plugins** — `plugins/session-flush.ts` (плагин, не команда).
  - **config** — `opencode.jsonc` (минимальный: только `$schema`).
- **`/loop` ссылается на несуществующего глобально агента:** `command/loop.md`
  имеет `agent: build`, но файла `agent/build.md` в global nerve нет; в dotfiles
  `/loop` указывает `agent: builder` на реальный `agent/builder.md`. Нестыковка
  имени `build` ↔ `builder` подтверждена по файлам.
- **`/done` — чеклист-протокол завершения задачи:** `command/done.md` (без поля
  `agent`, только `model:`) опирается на `TASKS.md` (перенос в Done),
  `VibeOS` (актуализация принципов), `04-Memory/active-context.md` и `/commit`
  (финальный шаг). Заточен под волт-цикл, не под общий код-проект.
- **`/commit` — отсутствует в global nerve:** `commit.md` materialized только в
  проектном `OpenCode-Vault/.opencode/command/commit.md` (`agent: librarian`,
  `subtask: true`), не в `~/.config/opencode/command/`. Глобальный `/done`
  ссылается на `/commit`, которого в global nerve нет — цикл `/done` разрывается
  на глобальном уровне.
- **`session-flush` — детерминированный плагин, не команда и не агент:** `plugins/session-flush.ts`
  слушает `file.edited` события и `session.idle`, копит Set изменённых путей и
  при idle дописывает в `04-Memory/session-log/<date>.md` секцию
  `## <time> — file.edited flush` со списком файлов. Агентов НЕ вызывает;
  в заголовке файла прямо: «Детерминированный плагин… Агентов НЕ вызывает».
- **`notify` отсутствует глобально:** в global nerve нет ни notify-плагина, ни
  notify-команды. `command/notify.md` (пайплайн настройки уведомлений:
  builder → util-dev → reviewer) существует **только в dotfiles**;
  `notify.ts`/`notify.js` **локальны в проектах** (`serp/.opencode/plugins/`,
  `dv-hub/.opencode/plugins/`). Глобального notify-layer нет.
- **`opencode.jsonc` минимален:** только `$schema`; тяжёлой конфигурации нет,
  логика живёт в `agent/`, `command/`, `plugins/`.

### Фаза B — dotfiles

- **Зрелая архитектура primary/subagents (раздельные каталоги):**
  - **primary** (`agent/`, `mode: primary`): `planner.md` (архитектор, read-only),
    `builder.md` (строитель, пишет конфиги/скрипты/qtile/плагины),
    `sysop.md` (системный инспектор Manjaro).
  - **subagents** (`subagent/`): `reviewer.md`, `verifier.md`, `researcher.md`,
    `bash-dev.md`, `qtile-dev.md`, `util-dev.md`, `stow-ops.md` (и др. по
    доменам).
- **`researcher` vs `sysop` — разные домены:** `researcher` смотрит **внутрь**
  проектов/артефактов волта (читает карточки, методы, session-log, исходники);
  `sysop` смотрит **наружу на машину** — Manjaro, пакеты, конфиги системы,
  сервисы. Это разные субагенты, не синонимы.
- **`reviewer` vs `verifier` — разные роли, не синонимы:** `reviewer` = quality
  (стиль, безопасность, соответствие конвенциям, конфиг/разрешения); `verifier` =
  применимость/acceptance (DoD, тест-команда, PASS/FAIL, never edits). Разделены
  в dotfiles, в vault различение не отражено (только `verifier-pattern`).
- **Глобальный vs локальный verifier:** `agent/verifier.md` в global nerve —
  `mode: subagent`, edit=deny, webfetch=deny, bash-allowlist
  (`git diff/log`, `npm test`, `pytest`); возвращает PASS/FAIL. Роль та же
  (acceptance), но **permissions отличаются** от локального dotfiles verifier
  (там подчиняется общему permission-окружению dotfiles).
- **Единый командный паттерн (ровно):** frontmatter `agent: <primary>` задаёт
  исполнителя-дирижёра; тело команды —
  `анализ → делегирование специализированному агенту (task(agent=…)) →
   проверка (verifier/reviewer) → финализация`. Примеры: `stow.md` =
  builder → stow-ops → verifier; `notify.md` = builder → util-dev → reviewer;
  `fix.md` = util-dev → verifier.
- **Shell НЕ исполняется «по желанию агента»:** действие идёт через skills,
  hooks, plugins, loop и разрешённые permission-пайплайны. Глобально в
  `agent/*.md` заданы `permission.bash` allowlists (planner: `bash: deny`;
  builder: `bash: {"*": ask, "ls*|cat*|grep*": allow}`; sysop: `bash: deny` с
  allowlist; verifier: `bash: deny` кроме `git diff/log, npm test, pytest`).
  Произвольный shell по инициативе агента — `ask` или `deny`, а не default.
- **`user-profile` principles для подъёма:** в `dotfiles/.opencode/memory/user-profile.md`
  зафиксированы принципы пользовательского профиля, предназначенные для подъёма
  в global nerve. Подъём не выполнен.
- **Слой глубже волта:** dotfiles содержат больше исполнительной структуры
  (primary/subagents, мультиклиентные команды, hooks, tool-слой), чем vault,
  который остаётся преимущественно справочно-методическим.

### T-069 ecosystem-map / Pip-Boy

- **T-069 ecosystem-map = важный planning artifact:** воспринимается как
  «Pip-Boy» — будущий **интерфейс планирования апгрейдов**, навигации по
  capture-сигналам и связям проектов. Не runtime-модуль; не продукт. Аудит
  НЕ утверждает его runtime-статус.
- **Реальные файлы артефакта (по git/дереву):** `tools/ecosystem-map/`
  с `index.html` + `data.json`; коммит `dc6368d` «feat(tools/ecosystem-map):
  интерактивная Pip-Boy карта экосистемы (468 постов → 36 навыков → 326
  инструментов, 4 вкладки). docs(memory): T-069 done…». Воспринимается как
  **поворотный артефакт планирования**, не побочный визуал. Графовая модель
  (узлы, связи, зоны влияния, апгрейды) — заявленная цель артефакта, не
  подтверждённый runtime-контур (см. what remains open).

### capture / routing / memory (пункты 19–21)

- **Пункт 19 — capture = intake-слой апгрейдов проектов:** подтверждён как
  рабочий канал (`tools/telegram-capture/capture.py`, Telethon+Tor, скилл
  `capture` в `.opencode/skills/capture/SKILL.md`). Это **не просто сбор
  заметок**, а intake-слой апгрейдов: посты @inbox_tools → классификация →
  99-Inbox → карточки/методы. Ручная координация в `/inbox` остаётся.
- **Пункт 20 — routing:** librarian маршрутизирует задачи в `general` текстом;
  machine-readable task contract отсутствует.
- **Пункт 21 — memory:** OKF-память (`active-context`/`facts`/`session-log`)
  работает; provenance по времени не сохраняется (`facts.md` переписывается).

## confirmed tensions

1. **Global nerve управляется через stow, но `/done` ссылается на `/commit`,
   которого в global nerve нет** (`commit.md` — только в
   `OpenCode-Vault/.opencode/command/`). Цикл `/done` разрывается глобально —
   нужен либо подъём `/commit`, либо явная декларация зависимости.
2. **`build` vs `builder` — подтверждённая нестыковка имён:** global `/loop`
   указывает `agent: build` (файла нет), dotfiles `/loop` — `agent: builder`
   (файл есть). Требует фиксации **кому** loop направляется (поле контракта, не
   совпадение имён).
3. **Global verifier существует, но его role/permissions отличаются от
   локального dotfiles verifier** — оба `mode: subagent`, PASS/FAIL, never
   edits, но global имеет жёсткий `bash: deny` с коротким allowlist
   (`git diff/log`, `npm test`, `pytest`), а dotfiles подчиняется местному
   permission-окружению. Единый runtime-gate `verify=PASS → finalize` не
   enforced ни там, ни там — в vault только справочник `verifier-pattern`.
4. **`session-flush` — детерминированный flush-плагин (algorithmic, не агентный
   пересказ), но полноценная algorithmic/event-sourced memory как подсистема
   (JSONL per-task ledger, event-sourced facts projection, replay) НЕ
   внедрена.** Текущая проекция — простой список `file.edited` за сессию;
   provenance, bi-temporal claims, A/B-replay — design proposal (см.
   planning-seed / 99-Inbox research), не имущество волта.
5. **`reviewer` vs `verifier` разведены в dotfiles (quality vs acceptance),
   но в vault различение не отражено** — один `verifier-pattern` как справочник.
6. **dotfiles глубже волта, но подъём `user-profile` principles в global nerve
   не выполнен.** Принципы зафиксированы в `memory/user-profile.md`, но не
   стащены в `~/.config/opencode/`.
7. **T-069 ecosystem-map/Pip-Boy — артефакт планирования, не runtime-интерфейс
   harness.** Роль зафиксирована как planning artifact; остаётся открытым,
   становится ли он runtime-interface для агентов.
8. **`local-tooling-as-limbs` («локальные инструменты как руки агентов») —
   предложение нового методологического блока (не заметка на полях).** Тезис:
   локальная машина и серверы — исполнительные конечности агентной системы,
   разгружающие LLM от детерминированных операций (`grep`, `git`, `stow`,
   `shellcheck`, `py_compile`, `notify`, `systemctl`, `sqlite`, конвертации,
   графы, индексация, diff-анализ). Связка: экономия токенов / контекстного
   окна, рост автономности и достоверности. Кандидат на оформление как
   отдельный метод (`02-Methods/`); сегодня — предложение, не внедрённый canon.
9. **`capability-routing` вместо только `model-routing` — предложение
   трёхслойной routing-политики, не россыпи verifier-ов.** Слой A — общие
   инженерные конвенции (именование, идемпотентность, тестируемость, no
   hardcode, секреты, читаемость diff, критерии «готово»). Слой B —
   language/runtime conventions (Bash, Python, TS/Node, Kotlin/Android,
   HTML/CSS/JS для утилит/дашбордов, YAML/JSON/TOML). Слой C — routing policy:
   модель + роль + язык + риск + тип операции (когда reviewer / verifier /
   sysop / researcher / meta / prompt-engineer / guardian). Предложение, не
   действующая политика волта.
10. **`researcher` vs `sysop` vs `meta` vs `guardian` — два луча сенсорного
    слоя + два управителя (предложение по精进ению разделения).** `researcher`
    → артефакты проекта (код, git, docs, конфиги, история, связи); `sysop` →
    исполнительная среда (Manjaro, процессы, пакеты, сервисы, порты, system
    state) — два луча одного сенсорного слоя (внутрь / наружу), не дублё.
    `meta` → агентная инфраструктура; `guardian` → сверка с философией и
    конвенциями. `sysop` позиционируется как усилитель апгрейдов OpenCode
    (plugins / hooks / TTS/notify / локальные базы-индексы / CLI/MCP/tooling),
    т.к. OpenCode живёт на машине. Фактическое разделение в dotfiles
    подтверждено (см. Phase B); систематизация этого кадра как «глобальной
    тройки meta+sysop+guardian» — предложение.
11. **Global role kernel + local specializations/overrides — предложение
    вместо одного глобального verifier-а на всё.** Тезис: глобальное ядро
    роли (контракт verifier/reviewer: принципы, формат PASS/FAIL) +
    локальные расширения/предметная точность (dotfiles / SERPlux / dv-hub).
    Применимо к `reviewer`, `researcher`, `sysop`, `guardian` и плагинам:
    «одна роль + локальные специализации», а не «один агент на всё». Не
    противоречит confirmed fact #3 (различие global/dotfiles verifier
    permissions) — как раз его систематизация; в статусе предложения.
12. **`prompt-engineer` — предложение двухрежимной прослойки, не
    «красивого переписывателя текста».** Режим 1 — `prompt-normalizer`
    (свободная задача → цель/ограничения/контекст/DoD → структурированный
    spec). Режим 2 — `task-compiler` (знает roster/routing/порядок/артефакты
    → пайплайн исполнения). Цепочка: пользователь свободно → `prompt-engineer`
    собирает spec → `guardian` проверяет полноту/конфликты → `meta`/project
    planner запускает исполнение. Заявлен как «один из сильнейших кандидатов
    на апгрейд после аудита» — кандидат, не существующая роль.
13. **Проактивность `meta` — предложение алгоритмического контура, не
    самовольного творчества.** Тезис: регулярная/событийная/дешёвая сверка
    декларации и реальности → точечное действие. Каналы: hooks, периодические
    инспекции, diff-based проверки, signals from capture, signals from
    ecosystem-map. «Не подумай обо всём», а алгоритмический контур.
    Предложение; today Hook-скелета для meta-проактивности нет.
14. **Команды/shell constraint — уточнение дизайна (не новое предложение,
    усиление существующего факта Phase B #shell-stuborn).** Дальнейший
    дизайн должен исходить из того, что агент не исполняет произвольный
    shell по желанию: действие зашито в skills / hooks/plugins / loop
    pipeline / разрешённые tool/task контуры. Следствия: `prompt-engineer`
    компилирует не «идеальный текст», а OpenCode-совместимый pipeline;
    `meta`-проактивность опирается на hooks/plugins/skills, а не на надежду;
    `session-flush` и `notify` — событийные плагины, не агентные рассуждения.
15. **`session-flush` / memory — оценка текущей схемы как слабой + предложение
    центрального апгрейда (в дополнение к confirmed tension #4).** Текущее
    `/done`-подобное переписывание сессии агентом помечено в исходнике как
    «жрёт токены / перечитывает историю / грузит контекст / отрывает агента»
    — это **оценка источника**, помечена как tension, не как confirmed fact
    волта. Вектор: минимизировать участие LLM в механическом сохранении
    памяти. Кандидаты: A) event-log first (сырые события `file.edited`,
    `command invoked`, `task start/finish`, `verifier PASS/FAIL`,
    `plugin fired`, `changed files`, `commit sha` — дешёвая машинная
    хроника без токенов); B) periodic distillation (LLM периодически
    дистиллирует event log в facts / active-context / decisions / session
    summary); C) hybrid memory (raw machine memory + distilled semantic
    memory, `active-context` = summary + последние события). Реализационные
    опоры: SQLite/JSONL store, ripgrep/jq/awk/python локальная дистилляция,
    файловые watchers, git metadata, cron/systemd user timers. Заявлен как
    «один из центральных апгрейдов вайбкодинг-слоя» — кандидат, не
    действующая подсистема.
16. **Цепочка `capture` — предложение формализованной модели intake→upgrade
    (в дополнение к confirmed fact #19).** `capture` — не просто сбор ссылок,
    а первый этап апгрейда проекта: (1) signal intake — Telegram/др.;
    (2) classification → узел карты; (3) relevance scoring; (4) project
    mapping — dotfiles / SERPlux / dv-hub / vault / new; (5) upgrade path
    generation (какой агент/метод/плагин/скилл); (6) execution or backlog.
    Для dotfiles через «Linux UX Lab» частично описано в `99-Inbox`;
    предложение — агента, принимающего предложения по софту/апгрейдам
    Manjaro. Модель — предложение; ручная координация в `/inbox` остаётся
    фактом (см. #19).
17. **Глобальные vs локальные плагины — предложение по разделению,
    конфликтующее с confirmed fact «глобального notify нет».** Глобальные
    плагины = событийная инфраструктура экосистемы (notify, maybe
    session/event log, maybe guard plugins, maybe infra/code boundary
    enforcement). Локальные плагины = проектно-специфичные (SERPlux
    commit-guard/CI, dv-hub notify/TS, dotfiles system-specific). Тот же
    принцип, что у агентов: глобальное ядро роли + локальные специализации.
    **Открыто, не текущее состояние:** global notify отсутствует
    (confirmed fact Phase A); предложение ввести глобальные плагины —
    кандидат, не внедрённое.

## what changes planning

- **Подъём из dotfiles в global nerve становится отдельной задачей плана:**
  `user-profile` principles, зрелый командный паттерн
  (`анализ → делегирование → проверка → финализация`), разделение
  `researcher`/`sysop` и `reviewer`/`verifier` — кандидаты на stow-подъём.
- **Унификация имён агентов (`build`↔`builder`) предшествует любому
  harness-контракту:** без поля «кому направляется loop» контракт ложится на
  совпадение имён, которого нет. Решить, кто canonical-исполнитель `/loop`.
- **`/done` требует подъёма `/commit` либо декларации зависимости** — иначе
  волтовая заточенность `/done` (`TASKS.md → VibeOS → 04-Memory → /commit`)
  остаётся локальной, а global nerve её не поддерживает.
- **Algorithmic/event-sourced memory как подсистема попадает в план как
  design proposal (не «уже есть»):** `session-flush` сегодня — детерминированный
  flush-плагин; полную модель (event-sourced facts projection, JSONL per-task
  ledger, replay, provenance) планировать отдельной задачей после telemetry
  (см. planning-seed, [[memory-management]]).
- **T-069 ecosystem-map/Pip-Boy фиксируется как planning artifact/interface:**
  план не должен превращать его в runtime-модуль без отдельного решения.
- **Пункты 19–21 (capture/routing/memory) входят в roadmap как связанные, но
  раздельные задачи:** capture уточняется под intake-слой апгрейдов и ручную
  координацию в `/inbox`; routing — под отсутствие task contract; memory — под
  сохранение provenance (event-sourced projection).
- **Глобального `/notify` нет и подъём не планируется** — `notify-команда`
  остаётся в dotfiles, проектные `notify.ts/notify.js` локальны в
  SERP/dv-hub; поднимать ли что-то notify-подобное в global nerve — отдельный
  вопрос, не часть данного аудита.
- **T-069 ecosystem-map/Pip-Boy фиксируется как операционная карта
  планирования (предложение композиции, не текущий runtime):** артефакт
  становится **каркасом планирования апгрейдов** — `ecosystem-map` =
  операционная карта экосистемы; `capture` = источник новых сигналов;
  `guardian`/`meta`/`sysop`/`researcher` = операторы, которые читают и
  обновляют карту; `vault` = координационный узел, хранящий смысл, приоритеты
  и историю решений; **каждый апгрейд должен отвечать на вопрос, какой узел
  карты он меняет и по каким рёбрам расползается дальше**. Capture-идеи
  привязываются к конкретным узлам системы. Это проект композиции в план,
  не подтверждённое runtime-состояние (см. what remains open).
- **`local-tooling-as-limbs` входит в план как кандидат отдельного
  методологического блока** (`02-Methods/`), связывающего токены/контекст/
  автономность/достоверность через детерминированные локальные операции.
- **`capability-routing` (3 слоя) входит в план как design proposal вместо
  россыпи verifier-ов:** общие инженерные конвенции + language/runtime
  conventions + routing policy (модель/роль/язык/риск/тип операции).
- **`prompt-engineer` (prompt-normalizer + task-compiler) — кандидат на
  апгрейд после аудита** (после addendum); flow «свободно →
  prompt-engineer → guardian → meta/project planner».
- **`meta`-проактивность входит в план как алгоритмический контур**
  (hooks/периодические инспекции/diff-проверки/capture-signals/
  ecosystem-map-signals), не «подумай обо всём».
- **`session-flush`/memory — event-log-first + periodic distillation +
  hybrid memory входят в план как центральный апгрейд вайбкодинг-слоя**
  (см. confirmed tension #4, #15): SQLite/JSONL event store, локальная
  дистилляция (rg/jq/awk/python), watchers, git metadata, cron/systemd
  timers. Минимизация участия LLM в механическом сохранении памяти.
- **Глобальные vs локальные плагины — design proposal разделения по тому же
  принципу, что агенты** (global role kernel + local specializations).
  Конфликт с confirmed fact «глобального notify нет» сохраняется как
  открытый вопрос (см. what remains open), не снимается авт.
- **Фаза A/B концептуально закрыта, но требуется короткий Addendum перед
  Phase C — стабилизация терминов (10 принципов, см. ниже), чтобы Фаза C
  не размазалась.** Рекомендация «после addendum стартовать Фазу C / SERPlux»
  — **planning proposal источника, не confirmed fact волта**; SERPlux остаётся
  целевой проверкой методологии на боевом коммерческом проекте.
- **10 принципов будущего плана апгрейда (addendum-кандидат для стабилизации
  терминов, не внедрённый canon):** (1) ecosystem-map/Pip-Boy как каркас
  планирования; (2) локальные инструменты как руки агентов
  (`local-tooling-as-limbs`); (3) capability-routing вместо только
  model-routing; (4) global roles + local specializations; (5) meta + sysop
  + guardian как глобальная тройка; (6) reviewer ≠ verifier; (7)
  prompt-engineer как task compiler; (8) event-log memory + semantic
  distillation; (9) capture как intake-слой апгрейдов; (10) глобальные vs
  локальные плагины. Список — это дистилляция предложений temp-файла, не
  утверждённый roadmap; будущие артефакты addendum: `guardian`, global
  `sysop`, `prompt-engineer`, event-log memory, `notify`, routing spec; что
  глобальное / локальное / что внедрять первым — отдельный deliverable.

## what remains open

- **Runtime gate verifier в global nerve:** существует ли нативный OpenCode
  hook для enforcement `verify=PASS → finalize`? `[проверить]`. Глобальный
  `verifier.md` существует, но role/permissions отличаются от локального
  dotfiles verifier — унификация отдельный вопрос.
- **Подъём `notify` в global nerve:** нет ни плагина, ни команды глобально;
  `notify.md` — только dotfiles, `notify.ts/notify.js` — только SERP/dv-hub.
  Поднимать или оставить проектным? Открыто.
- **Превращается ли T-069 ecosystem-map/Pip-Boy в runtime-interface для
  агентов**, или остаётся planning artifact (интерфейс планирования апгрейдов,
  capture-сигналов и связей проектов)? Открыто до отдельного решения.
- **Становится ли `session-flush` structured-event источником** для полноценной
  algorithmic/event-sourced memory (JSONL per-task ledger / SQLite,
  event-sourced facts projection, replay), или `facts.md` остаётся единственной
  проекцией? Открыто; event-sourced facts — кандидат, не решение
  ([[04-Memory/facts]], [[memory-management]]).
- **Имя `build` vs `builder` — какой канонический?** Подтверждена нестыковка
  `command/loop.md` (`build`) ↔ `agent/builder.md` (dotfiles); канон не
  зафиксирован. Открыто.
- **Статус операционной карты ecosystem-map:** превращается ли T-069 в
  рабочую planning-интерфейс для операторов (`guardian`/`meta`/`sysop`/
  `researcher`), читающих/обновляющих карту, с привязкой capture-сигналов к
  узлам и правилом «каждый апгрейд отвечает, какой узел/рёбра меняет» — или
  остаётся статичным planning artifact? Открыто; runtime-контур не
  подтверждён, «будущий runtime не выдавать за существующий».
- **`local-tooling-as-limbs` как 02-Methods/canon:** оформлять ли отдельным
  методом с детерминированным tool-canon (`grep`/`git`/`stow`/`shellcheck`/
  `py_compile`/`notify`/`systemctl`/`sqlite`/…)? Открыто; сегодня —
  предложение.
- **`capability-routing` (3 слоя) — какой стек implementations?** Является
  ли `model-routing` расширяем до capability-routing через hooks/plugins,
  или отдельная routing-policy подсистема? Открыто.
- **`prompt-engineer` — вводить ли, в каком объёме (только normalizer или
  сразу task-compiler), и в каком порядке с `guardian`/`meta`?** Кандидат
  «после аудита»; открыто до addendum.
- **`meta`-проактивность — алгоритмический контур (hooks/периодические
  инспекции/diff-проверки/capture-signals/ecosystem-map-signals):** сегодня
  hook-скелета для meta-проактивности нет. Реализовывать ли и через какие
  хуки? Открыто.
- **`session-flush` → central upgrade (event-log first / periodic
  distillation / hybrid memory):** остаётся ли `facts.md` единственной
  проекцией, или внедряется event-log + distillation pipeline
  (SQLite/JSONL/rg/jq/awk/python/watchers/git metadata/cron-systemd)?
  Открыто; кандидат central upgrade, не решение (доп. к существующему open
  про event-sourced).
- **Глобальные плагины — вводить ли глобальный event-слой (notify /
  session-event log / guard / infra-code boundary), при confirmed fact
  «глобального notify нет»?** Конфликт proposal ↔ факт остаётся открытым
  (см. также open про подъём notify). Открыто.
- **Phase gate «после addendum → Фаза C / SERPlux» — подтверждать ли как
  roadmap-шаг?** Рекомендация — planning proposal источника;SERPlux как
  «боевой коммерческий проект» в проверке методологии — целевая проверка,
  не подтверждённое обязательство. Открыто до addendum.

## Источники

- Исследование: [[99-Inbox/vault-upgrade-research-2026-08-02]]
- Экстракция: `98-Temporary/ansver_genspark.md` (корректировка Genspark после
  пропуска T-069; экстрагировано и удалено 2026-08-03)
- Файлы: [[AGENTS]], [[Architecture]], [[02-Methods/verifier-pattern]],
  [[02-Methods/memory-management]], [[02-Methods/tool-integration-pattern]],
  [[02-Methods/closed-loop]], `03-Projects/` (T-069), [[04-Memory/facts]]
- Global nerve: `~/dotfiles/opencode-global/.config/opencode/` → `stow` →
  `~/.config/opencode/` — `agent/meta.md`, `agent/verifier.md`,
  `command/done.md`, `command/loop.md`, `plugins/session-flush.ts`,
  `opencode.jsonc`
- Dotfiles: `agent/{planner,builder,sysop}.md` (primary);
  `subagent/{reviewer,verifier,researcher,bash-dev,qtile-dev,util-dev,stow-ops}.md`;
  `command/{loop,flush,fix,stow,notify,…}.md`; `memory/user-profile.md`
- Capture: `tools/telegram-capture/capture.py` (Telethon+Tor),
  `.opencode/skills/capture/SKILL.md`
- T-069: `tools/ecosystem-map/index.html`, `tools/ecosystem-map/data.json`;
  commit `dc6368d`
- `/commit`: `OpenCode-Vault/.opencode/command/commit.md` (проектный, не global)