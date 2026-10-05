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

Старые атомы `n-0001..n-0054` сохранены (темы, протоколы, ограничения,
peer-comms `n-0048..n-0053` → graph `proto`).

## Незакрытые вопросы

- `[проверить]` JEV vs Laya — выбор органа классификации (`n-0047`)
- `[проверить]` предметные смыслы за явным списком тем (`n-0017`)
- Матрица миров (`proto-world-matrix`) — deliverable не составлен
- Реализация гейтов/toast — за Pip-Boy-модулем
