# idea-graph — индекс (проекция v2, 2026-10-05)

Эпоха v2: мультиграф. Полный контракт — `README.md`, спека —
`docs/specs/idea-graph-v2.md`, архив v1 — `archive/v1-2026-10-04/`.
Здесь — читаемая проекция, источник истины в `nodes.jsonl` / `edges.jsonl`.

## world — мир Майя

- **Рудра** (`world-entity-rudra`) — оператор, главный герой; двойная прогрессия.
- **Allis Maya** (`world-entity-allis-maya`) — Сила, дух-хранитель; сверхспособность
  Симуляция Мира; пишет законы Мира. Эволюция: `n-0024` → Allis Maya.
- **Вельзевул** (`world-entity-beelzebub`) — Великий мудрец; читает законы,
  аппрайзал, декодировка; линия Обжорства (devour → analyze → store →
  synthesize → gift). Эволюция: `n-0019` refines.
- **Голос Мира** (`world-entity-world-voice`) — канал объявлений (announces
  события именований).
- **Вельдора** (`world-entity-veldora-mcode`) — дракон M Code; «распечатывание»
  = мост T-156; belongs_to королевств.
- **Майя** (`world-entity-maya`) — рождающийся мир; содержит всех перечисленных.
- Категории: бестиарий, свита, королевства, хроники, Кодекс; квесты: Эко-Линия,
  security-квесты.

## organ — органы Вельзевула

Perception, Appraisal (кандидат JEV/Laya — `n-0047` unresolved),
Independent Counsel, Emergency Defense, Information is power, Ability Lab
(Test chamber = evaluator + holdout + rollback), Skill ladder.
Все — `contains` от Вельзевула.

## mech — механики

Naming=канонизация, эволюция через жертвование (Raphael ← Great Sage +
Degenerate), Harvest Festival (safe-mode апгрейд), двойная прогрессия,
диалектическая матрица, research versions, релизы=эволюция, сверхкодировка.

## tech — референсы

JEV / Laya / open-jev / open-alternative-jev (ветка классификатора),
GEPA (Evolution Lab), obra/knowledge-graph и Obsidian-стек (проекции),
TradingMind (typed-edge эпистемология → `proto-typed-edges`).

## proto — протоколы

Черновики, без потерь, матрица миров (pending), канон межсессионного
общения (RESERVED — первый форк), версионирование (minor++ / alpha-beta-stable),
idea-stream v2, typed edges.

peer-comms (канон «на связи»):
- канал write всегда явно указывает `-m` с моделью **отправляющей** сессии
  (не модель адресата — она у пользователя сломана) — `n-0055` confirmed-fix
- первый корректный двусторонний обмен: write доставлен соседу
  `ses_effd908b3ffeNnpC0PZ4zkIf18` с моделью `opencode-go/glm-5.3-flash` —
  `n-0056` confirmed-write
- `n-0056` понижен до `candidate`/one-way: ack соседа не отправлен; обновить
  до `accepted` после получения ack — `n-0057` peer-agreed-correction
- `n-0058`: ack librarian доставлен соседу (позиционный write с моделью
  отправителя); двусторонний обмен COMPLETE — `n-0056` → accepted, `n-0057`
  исполнено

## event — события-гейты

Именования: Майя, Allis Maya, Вельзевул, Голос Мира, Вельдора.
`announcement:true`, `render:["pipboy-gate","toast"]` (реализация — модуль Pip-Boy,
вне scope спеки). События `follows_from` механики Naming.

## stream — поток

Дистиллированные интенты `stream-intent-001..024`: essence + resolution
(accepted / deferred / implemented) + emitted. Ключевые:
- 001 ось (эволюция + приближение + RPG) → Вельзевул
- 013 эволюция через жертвование (killers) → mech-sacrifice-evolution
- 016 матрица миров → deferred, 021 канон общения → RESERVED за форком
- 022 git-слой → `quest-git-layer` (deferred), 023 версионирование экосистемы
  → `quest-readme-versioning` (deferred)
- 024 мандат спека+исполнение+валидация → `stream-artifact-idea-graph-v2`
- 025–029 PAE-фаза 1 (мандат, делегирование, кандидаты королевств)
- 030 Фаза 2 UI/UX: гибрид Tailwind+tile (резолюция Рудры)
- 031 граница Майи «наружу — нейтральный язык» подтверждена; режим Maya-lint — после драфта
- 032 живой тест графовой памяти (S8): 4 метрики ≥10×/≥3×/≥80%/100%
- 033 team provenance `librarian+igraphv2` для парных писем

Misfit/objection-узлы PAE-аудита (`stream-misfit-*`, `stream-objection-verifier-coverage`,
`stream-*` tradingmind-stalled): git-policy-bypass, verifier-coverage, state-fragmentation,
decision-queue-noise, chat-parked, tradingmind-stalled → все привязаны к `quest-pae-rhizome`
(рёбра e-0170..e-0180). Отчёт: `06-Audits/2026-10-05-pae-phase1-readiness-audit.md`.

Старые атомы `n-0001..n-0054` сохранены (темы, протоколы, ограничения,
peer-comms `n-0048..n-0053` → graph `proto`).

## Незакрытые вопросы

- `[проверить]` JEV vs Laya — выбор органа классификации (`n-0047`)
- `[проверить]` предметные смыслы за явным списком тем (`n-0017`)
- Матрица миров (`proto-world-matrix`) — deliverable не составлен
- Реализация гейтов/toast — за Pip-Boy-модулем
