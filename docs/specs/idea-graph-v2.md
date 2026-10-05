---
type: spec
title: idea-graph v2 — мультиграфовый кластер памяти
status: implemented-in-branch
date: 2026-10-05
layer: "Вельзевул Layer v1.2-alpha"
kind: task
---

# idea-graph v2 — мультиграфовый кластер памяти («Вельзевул Layer v1.2-alpha»)

Мандат пользователя (2026-10-05): написать спеку и **полностью исполнить** апгрейд
графа памяти до v2, затем валидировать/верифицировать. Исполнитель: librarian
(явное исключение из правила «только через субагентов», подтверждено пользователем:
«исполни сам и после исполнения запусти верификатора»).

## Контекст

v1 (2026-10-04, первая fork-сессия): `04-Memory/idea-graph/` — 47 узлов, 48 рёбер,
`protocol.jsonl`, README, index; JSONL append-only; не был закоммичен → архив
v1 сохранён в `archive/v1-2026-10-04/` как единственный provenance. Затем fork
добавил peer-comms (n-0048..n-0054, e-0049..e-0054) — сохранено и мигрировано.

## S1. Epoch-правило

Внутри эпохи файлы `nodes.jsonl` / `edges.jsonl` / `protocol.jsonl` — append-only.
Смена эпохи (v1→v2) — атомарная миграция: старое состояние копируется в
`archive/<epoch>-<date>/`, затем файлы переписываются. `README.md` и `index.md` —
проекции/документы, их переписывать можно.

## S2. Схема v2

- Узел: `id`, `graph`, `kind`, `label`, `status`, `provenance`, `projection`
  (+ опциональные доменные поля: `essence`, `resolution`, `emitted`,
  `announcement`, `render`, `external`).
- Ребро: `id`, `graph`, `from`, `to`, `type`, `status`, `provenance`, `projection`.
- `graph` — обязательный namespace: `world`, `organ`, `mech`, `tech`, `proto`,
  `event`, `quest`, `stream`.
- Старые n-0001..n-0054: ID не переименовываются; `graph` назначается по смыслу
  (атомы диалога → `stream`; peer-comms → `proto`).
- Новые ID: `<graph>-<kind>-<slug>`.

## S3. Canonical edge types (слияние с TradingMind-эпистемологией)

- структурные: `belongs_to`, `contains`, `depends_on`
- эпистемические: `refines`, `generalizes`, `follows_from`, `prerequisite_for`,
  `example_of`, `contradicts`, `related`
- эволюционные: `inspires`, `evolves_into`, `devours`, `synthesizes`, `names`
- событийные: `announces`, `gates`

Дисциплина (TradingMind): каждое ребро обязано иметь тип; `related` — только
когда точнее подобрать нельзя.

## S4. Миграция типов рёбер v1 → v2

| v1 | v2 |
|---|---|
| mentions | related |
| requests, requests-artifact | inspires |
| may-project-into | related |
| is-recorded-by | depends_on |
| constrains | refines |
| leaves-open | related |
| represents, receives, has-role | related |
| creates | contains |
| feeds (source→stream) | belongs_to |
| feeds (stream→sink) | related |
| may-classify | related |
| is-peer-example-of | example_of |
| uses-channel | depends_on |
| governed-by | follows_from |
| constrained-by | depends_on |
| correction | refines |
| refines, contradicts | без изменений |

## S5. Канон имён Мира Майя (world)

- `world-entity-rudra` — Рудра, оператор, главный герой; двойная прогрессия
  (способности получают и система, и оператор).
- `world-entity-allis-maya` — Allis Maya, Сила, дух-хранитель Рудры;
  сверхспособность: **Симуляция Мира**; пишет законы Мира; сверхкодировка;
  сюжетная загадка, раскрывается версиями.
- `world-entity-beelzebub` — Вельзевул, Великий мудрец: аппрайзал стимулов,
  декодировка игрового в операционное; **читает** законы Мира (пишет их Сила);
  линия Обжорства: devour → analyze → store → synthesize → gift.
- `world-entity-world-voice` — Голос Мира, канал объявлений.
- `world-entity-veldora-mcode` — Вельдора, дракон M Code (форк OpenCode от друга;
  изучение = feature-mining; именован; «распечатывание» = мост T-156).
- `world-entity-maya` — Майя, рождающийся мир.
- Категории: `bestiary` (технологии-существа, перманентное пополнение),
  `retinue` (свита/великие слуги; эволюция = релизная каденция), `kingdoms`
  (SDK/харнесы), `chronicles` (session-logs/аудиты/blogerAI),
  `kodex` (терминологический реестр, будущие tooltips).
- Квесты: `eco-linia` (мета-квест-ось), `security-quests` (аудиты/инциденты =
  бои и осады).

## S6. Органы Вельзевула (organ)

`perception`, `appraisal` (JEV/Laya-кандидат, unresolved), `independent-counsel`
(situational proposal + одно-действенное подтверждение оператора; cooldown,
триггеры выгода/риск), `emergency-defense` (bounded protective autonomy: цена +
cooldown; класс commit-guard), `information-is-power` (преданализ удешевляет
действия), `ability-lab` (Stomach, Analysis bench, Synthesize-Separate,
Alteration, Test chamber = evaluator+holdout+rollback, Skill Gift, Регистр),
`skill-ladder` (пассивы → экстра → уникальные [Именование] → высшие
[Harvest Festival]).

## S7. Механики (mech)

`naming-canonization` (имя = gate raw→canon), `sacrifice-evolution` (новый
орган = поглощение готового компонента + жертвование старого; пример:
Raphael ← Great Sage + Degenerate; признанная киллер-фича), `harvest-festival`
(крупный апгрейд под управлением control-plane; снимает рутинное
администрирование с оператора), `dual-progression`, `dialectic`
(тезис+антитезис=синтез → масштаб; divergence/convergence), `research-versions`
(v0→v5 на уровне узла-концепции), `release-is-evolution` (новые релизы
опенсорс-инструментов = события мира/эволюции свиты), `supercoding` (Делёз:
сверхкодировка реального в игровое; единый кодекс → нет расхождений между
Силой и Мудрецом).

## S8. Технологические референсы (tech)

`jev` (TypeSafe cloud; приватность/offline-риски), `laya` (open on-device
аналог, Jev-wire `/v1/systemone`), `openjev`, `open-alternative-jev`,
`gepa` (reflective mutation, Pareto, deploy gate), `obra-knowledge-graph`
(SQLite+graphology; «no LLM inside the tool»), `obsidian-stack` (Dataview /
Bases / Graph Explorer), `tradingmind` (typed-edge epistemology — 7 типов рёбер
и дисциплина «связь без типа не ставится»; королевство на bootstrap; первый
кейс idea-stream).

## S9. Протоколы (proto)

`draft-protocol`, `no-loss`, `typed-edges`, `world-matrix` (pending deliverable),
`cross-session-canon` (**RESERVED**: ведёт первый fork), `versioning`
(minor++ за принятую концептуальную дельту; alpha до спеки, beta — спека +
прототип, stable — после verifier PASS), `idea-stream-v2` (три входа: поток
Рудры / внешние события / системные сигналы; append-only; никогда не канон и
не действия).

## S10. События-гейты (event)

Именования и эволюции — объявления: `announcement: true`,
`render: ["pipboy-gate", "toast"]`. События: naming maya / allis-maya /
beelzebub / world-voice / veldora-mcode. Реализация UI — обязанность модуля
Pip-Boy (вне scope этой спеки).

## S11. Дистилляция интентов (stream)

Не саммари, а экстрагированная суть каждого интента: узел `stream-intent-NNN`
с полями `essence` (1–2 строки), `resolution` (accepted/deferred/implemented),
`emitted` (ID порождённых узлов). Первая cohort: 24 интента текущей сессии
(2026-10-04/05), включая отложенные темы (git-слой/гит-агент → quest-git-layer;
версионирование экосистемы и порядок README/VibeOS → quest-readme-versioning).

## Acceptance

1. `docs/specs/idea-graph-v2.md` записан полностью.
2. v1 заархивирован в `archive/v1-2026-10-04/`.
3. Узлов ≥ 90; рёбер ≥ 120; dangling = 0; все типы рёбер ∈ taxonomy.
4. `node tools/idea-graph/validate.mjs` exit 0.
5. Правки только в: `docs/specs/idea-graph-v2.md`, `04-Memory/idea-graph/**`,
   `tools/idea-graph/**`.
6. Коммит — отдельно, только после независимого verifier PASS.
