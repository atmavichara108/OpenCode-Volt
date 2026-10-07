# idea-graph — мультиграфовый кластер памяти (v2)

Атомы сессионного диалога, их смыслы и связи, переживающие compact, handoff и
смену агентов. Layer: **Вельзевул v1.2-alpha**. Эпоха: **v2** (2026-10-05).
Спека: `docs/specs/idea-graph-v2.md`. Архив v1: `archive/v1-2026-10-04/`.

## Epoch-правило (S1)

Внутри эпохи `nodes.jsonl` / `edges.jsonl` / `protocol.jsonl` — **append-only**.
Смена эпохи — атомарная миграция: старое состояние копируется в
`archive/<epoch>-<date>/`, затем файлы переписываются. `README.md` / `index.md` —
проекции и документы, их можно переписывать.

## Файлы

| Файл | Что это | Запись |
|---|---|---|
| `nodes.jsonl` | узлы: атомы диалога + канон мира | append-only в эпоху |
| `edges.jsonl` | типизированные связи | append-only в эпоху |
| `protocol.jsonl` | протоколы сессии (черновики, без потерь, epoch) | append-only |
| `index.md` | структурированная проекция для чтения | переписываем |
| `README.md` | контракт формата (этот файл) | переписываем |
| `archive/` | заархивированные эпохи | не трогаем |

## Схема узла (S2)

```json
{"id":"<graph>-<kind>-<slug>","graph":"world|organ|mech|tech|proto|event|quest|stream",
 "kind":"...","label":"...","status":"raw|candidate|accepted|implemented",
 "provenance":{"source":"...","observed_at":"YYYY-MM-DD","scope":"...","basis":"quoted|derived|unknown"},
 "projection":["index","compact","handoff"]}
```

Обязательные: `id`, `graph`, `kind`, `label`, `status`, `provenance`, `projection`.
Допустимые доменные поля: `essence`, `resolution`, `emitted`, `announcement`,
`render`, `external`. Старые ID `n-0001..n-0054` сохранены без переименования.

## Схема ребра (S3)

```json
{"id":"e-NNNN","graph":"...","from":"<node-id>","to":"<node-id>",
 "type":"<canonical>","status":"...","provenance":{...},"projection":[...]}
```

`graph` ребра обязан совпадать с `graph` узла `from`.

### Canonical edge types

- структурные: `belongs_to`, `contains`, `depends_on`
- эпистемические: `refines`, `generalizes`, `follows_from`, `prerequisite_for`,
  `example_of`, `contradicts`, `related`
- эволюционные: `inspires`, `evolves_into`, `devours`, `synthesizes`, `names`
- событийные: `announces`, `gates`

Дисциплина (TradingMind): тип обязателен; `related` — только когда точнее
подобрать нельзя. Таблица миграции типов v1→v2 — в спеке (S4).

## Графы (namespaces)

| graph | Что живёт |
|---|---|
| `world` | сущности и структура Майя: Рудра, Allis Maya, Вельзевул, Голос Мира, Вельдора, категории, квесты |
| `organ` | органы Вельзевула: Perception, Appraisal, Independent Counsel, Emergency Defense, Information is power, Ability Lab, Skill ladder |
| `mech` | механики: Naming=канонизация, эволюция через жертвование, Harvest Festival, двойная прогрессия, диалектика, research versions, сверхкодировка |
| `tech` | технологические референсы: JEV, Laya, open-jev, GEPA, knowledge-graph, Obsidian-стек, TradingMind |
| `proto` | протоколы: черновики, без потерь, typed edges, версионирование, idea-stream, peer-comms (RESERVED за первым форком) |
| `event` | события-гейты: именования → `announcement:true`, `render:["pipboy-gate","toast"]` |
| `quest` | отложенные темы: git-слой, версионирование экосистемы |
| `stream` | атомы диалога и дистиллированные интенты (`stream-intent-NNN`: `essence`, `resolution`, `emitted`) |

## Статусы

- `raw` — сырая идея, не оценена
- `candidate` — оценена, не принята
- `accepted` — принята в канон
- `implemented` — исполнена в артефакте

### Голос Мира (закон 2)

- `announcement:true` допустим только для **доказанного**: `status=accepted`.
  Валидатор выдаёт `WARN announce-on-unaccepted:<id>` иначе.
- Узел `graph=event` **без** `announcement` — не ошибка: молчание штатно,
  событие остаётся журналом.
- Пинги/статусы писем в этот слой не попадают: журнал и Голос — разные дома
  (переписка живёт в `tools/peer-comms/`).

## Канон

Принцип слоя: **Вельзевул читает законы Мира — Allis Maya их пишет.**
Именование = канонизация (gate raw→canon). Ответы ассистента — принимаемые
черновики; возражения адресные по номеру пункта/заголовку; ни одна идея не
теряется. Ничего не теряется — граф переживает compact и handoff.

## Валидация

```
node tools/idea-graph/validate.mjs
```

exit 0 = PASS: JSONL парсится, ID уникальны, dangling-ссылок нет, все типы рёбер
из taxonomy, обязательные поля на месте, ≥90 узлов, ≥120 рёбер, сводка по
графам и статусам.
