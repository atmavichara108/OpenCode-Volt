---
type: specification / session plan
project: AndroidOS
status: planned
date: 2026-08-28
scope: documentation-only; bridge implementation is not included
---
# AndroidOS Coordination Bridge: отдельная сессия

> Простая временная спецификация надёжного coordination-канала между Vault,
> AndroidOS, dotfiles/sysop и AndroidOS-агентами. Это не реализация bridge и не
> заявление о существующем runtime. Все пути/агенты, которых ещё нет, должны
> оставаться `planned` или `[проверить]`.

## 1. Problem, goals, non-goals

### Problem

Планирование живёт в Vault, код и acceptance должны жить в AndroidOS, фактическое
состояние Manjaro и Android toolchain проверяется в dotfiles/sysop, а работа
агентов должна передаваться без потери контекста. Сейчас нет одного маленького,
проверяемого формата task → handoff → evidence → decision с явными ссылками между
репозиториями.

### Goals

- Дать всем узлам один читаемый Git-backed coordination surface.
- Разделить authority: стратегия не смешивается с кодом, host facts и acceptance.
- Передавать задачи и результаты с owner, scope, статусом, DoD и provenance.
- Обеспечить повторяемый intake и read-only bootstrap перед любым изменением.
- Оставить transport заменяемым и не создавать runtime-зависимость от bridge.

### Non-goals

- Не реализовывать AndroidOS bridge, приложение, backend, API или daemon.
- Не делать MCP единственным хранилищем и не поднимать API server, event bus, CRDT,
  Telegram или cloud sync.
- Не решать phone↔laptop sync и не делать MCP заменой capability-routing.
- Не синхронизировать живые базы, SQLite-файлы, профили или raw audio.
- Не делать Vault source of truth для AndroidOS-кода или host facts.
- Не объявлять named-agent runtime/acceptance существующими без live evidence.

## 2. Узлы и роли

| Узел | Ответственность | Может утверждать |
|---|---|---|
| Vault | стратегия, roadmap, ADR, приоритеты, cross-repo links, task envelopes | направление и scope; не код/host acceptance |
| AndroidOS | продукт, application code, локальные агенты, тесты и acceptance | реализацию и product DoD |
| dotfiles/sysop | фактическое состояние Manjaro, ноутбука, SDK/ADB/toolchain и system risk | host/toolchain evidence; sysop read-only |
| AndroidOS agents | named research/plan/build/review/verify роли в локальном проекте | только свой declared output; project verifier закрывает DoD |

Vault librarian координирует и обновляет только Vault-документацию в scope. Он не
редактирует AndroidOS code или global agent runtime. `reviewer` оценивает качество,
`verifier` оценивает acceptance; один не подменяет другого.

## 3. Source of truth и запрет дублирования

| Данные | Канон | В bridge допустимо |
|---|---|---|
| Стратегия, roadmap, ADR и priority | Vault | ссылка, краткий rationale, decision id |
| AndroidOS code, tests, local agent config, product DoD | AndroidOS | task status, commit ссылкой, acceptance summary |
| Manjaro/ноутбук/SDK/ADB факты | dotfiles/sysop evidence | ссылка на audit/report, timestamp и checksum при необходимости |
| User profile facts | `/home/rudra/dotfiles/.opencode/memory/user-profile.md` согласно [[01-Reference/user-profile-contract]] | scope/reference, не копия профиля |
| Secrets, tokens, credentials | secret manager/local protected storage | никогда |
| Raw audio и приватные corpora | local device/lab storage с retention | только redacted result/metric |

Bridge хранит ссылки и operational metadata, а не копию authority. Derived summary
помечается как derived и содержит `source`/`observed_at`; конфликт фактов решается
в каноническом узле.

## 4. Минимальная архитектура и физическое расположение

**Выбор MVP:** один canonical bridge в AndroidOS, каталог
`AndroidOS/coordination/bridge/` в репозитории AndroidOS. В нём только Markdown
артефакты, коммиты и ссылки на внешние репозитории. Vault хранит эту спецификацию,
roadmap и ссылки; dotfiles хранит свои sysop reports. AndroidOS может быть ещё
планируемым репозиторием, поэтому до его создания каталог является target path,
а не существующим фактом.

### Принятое решение: два уровня

1. **Canonical bridge files** в Git-backed репозитории AndroidOS остаются source of
   truth: именно они содержат task envelopes, handoffs, evidence и decisions.
2. **Optional local MCP facade** может дать агентам узкий интерфейс к этим файлам,
   но не владеет данными и не становится отдельным canonical store. MCP читает и
   пишет через тот же файловый контракт, Git и provenance.

MCP MVP ограничен инструментами `get context/task`, `claim task`, `update status`,
`write handoff` и `append evidence`. Каждый вызов обязан проверять строгие
`scope` и `owner`; evidence остаётся append-only, а silent overwrite запрещён.
Facade не решает phone↔laptop sync, не заменяет capability-routing и не создаёт
новый runtime-контур: для него не требуются API, cloud, event bus или CRDT.

Порядок реализации: сначала файловый bridge и smoke test, затем тонкий локальный
MCP adapter, и только при доказанной необходимости расширение инструментов или
архитектуры. Телефон не зависит от запущенного OpenCode или MCP: его offline-first
контур должен работать независимо, а bridge остаётся coordination surface для
агентов и репозиториев.

```text
AndroidOS/coordination/bridge/
  README.md                 # contract, owner, status vocabulary
  tasks/<task-id>.md        # one mutable task envelope per task
  handoffs/<handoff-id>.md  # explicit transfer records
  evidence/<evidence-id>.md # append-only result pointers
  decisions/<decision-id>.md# approved/rejected decisions
```

Не делать копии в Vault/dotfiles. Пока AndroidOS repo не создан, bootstrap может
быть read-only и создать только proposed path/links в отдельной сессии; Vault не
становится временным вторым canonical bridge без отдельного decision.

## 5. Task envelope (Markdown + YAML frontmatter)

Выбран один формат: Markdown с YAML frontmatter. ID глобально уникален, например
`AOS-BRIDGE-001`; файл `tasks/AOS-BRIDGE-001.md`. Поля обязательны, пустые списки
допустимы, неизвестные поля запрещены до расширения spec.

```markdown
---
id: AOS-BRIDGE-001
title: Validate Android toolchain baseline
source: vault
owner: androidos-planner
scope: androidos
inputs:
  - ref: "[[06-Audits/2026-08-28-androidos-coordination-bridge-spec]]"
constraints:
  - docs-only bootstrap; no application code
acceptance:
  - named evidence file with commands, versions, exit codes and gaps
status: planned
artifacts:
  - ref: "coordination/bridge/evidence/E-001.md"
evidence: []
blockers: []
next_action: "Run read-only bootstrap"
timestamps:
  created: "2026-08-28T00:00:00Z"
  updated: "2026-08-28T00:00:00Z"
  closed: null
---

## Context
Why this task exists and what is explicitly out of scope.

## Links
- Vault: `https://example.invalid/vault-ref-or-commit`
- AndroidOS: `https://example.invalid/androidos-ref-or-commit`
- dotfiles: `https://example.invalid/dotfiles-ref-or-commit`
```

`source` и `scope` используют значения `vault|androidos|dotfiles|agent` и
`vault|androidos|dotfiles|cross-repo`. `owner` всегда named role/agent, не generic
`general`. `status`: `planned|ready|in_progress|blocked|review|verify|closed|stale`.
Каждое cross-repo ref должно указывать repo и commit/path; placeholder выше нельзя
выдавать за рабочую ссылку.

## 6. Handoff и evidence

Handoff передаёт ownership, а не только текстовый комментарий. Шаблон:

```markdown
---
id: H-001
task_id: AOS-BRIDGE-001
from: androidos-planner
to: dotfiles-sysop
reason: "Toolchain facts required before build"
scope: dotfiles
inputs: ["task ref", "required command list"]
expected_output: "E-001"
status: open
created: "2026-08-28T00:00:00Z"
---
## Boundary
Read-only; no sudo, package install, config edit or device mutation.
```

Evidence шаблон:

```markdown
---
id: E-001
task_id: AOS-BRIDGE-001
producer: dotfiles-sysop
kind: sysaudit
observed_at: "2026-08-28T00:00:00Z"
source_repo: dotfiles
source_commit: "<full-sha>"
status: pass|fail|partial
---
## Result
Команда/версия/exit code, redacted output, limitations and reproducibility.
## Links
- Handoff: `../handoffs/H-001.md`
```

Evidence append-only: новая проверка создаёт новый файл/commit, старое не
переписывается. Decisions ссылаются на envelope и evidence и фиксируют approver,
дату, rationale и rollback/next decision.

## 7. Жизненный цикл

`intake → plan → sysop/research → build → review → verify → report → close`

`intake`: Vault создаёт envelope и route. `plan`: AndroidOS planner уточняет scope
и DoD. `sysop/research`: named sysop или researcher собирает evidence read-only.
`build`: AndroidOS builder меняет только заявленный project scope. `review`:
reviewer выдаёт findings. `verify`: project verifier проверяет acceptance. `report`:
owner добавляет links, commit SHA и gaps. `close`: coordinator закрывает только при
полном DoD, иначе `blocked`/`stale`.

## 8. Минимальные вызовы и routing

1. Vault librarian читает envelope, ADR/roadmap и создаёт route/handoff.
2. AndroidOS `planner` формирует план; при отсутствии named роли задача `UNROUTABLE`.
3. dotfiles `sysop` выполняет `/sysaudit` read-only для host/toolchain facts.
4. Named `researcher` выполняет только заявленное read-only исследование.
5. AndroidOS `builder` реализует project change после plan/evidence.
6. Named `reviewer` делает quality review; project `verifier` делает DoD check.
7. Owner публикует report и просит librarian обновить Vault links/status.

Маршрут записывается в envelope: capability, named agent, mutability, acceptance,
fallback и rationale. `general` не является silent fallback. Fallback разрешён
только на заранее зарегистрированную совместимую local/global роль, явно записан
в handoff и журнале; иначе остановка `UNROUTABLE` с missing capability/agent.
Правило следует [[02-Methods/capability-routing]] и
[[06-Audits/2026-08-25-capability-routing-design-note]].

## 9. Обновления, конфликты и stale

- У каждой active task ровно один owner; остальные работают через handoff.
- Чужой active envelope не редактировать без принятого handoff.
- Status меняет owner/coordinator с timestamp и короткой причиной.
- Evidence и historical decisions append-only; corrections создают новый artifact.
- Cross-repo commits не cherry-pick автоматически: указывать repo, full SHA, path и статус проверки.
- При двух owners, divergent edits или missing SHA статус `blocked`, не merge silently.
- `in_progress` без update дольше 7 календарных дней становится `stale`; owner обязан продлить с причиной или вернуть `planned`.
- Deletion task/evidence требует decision и ссылки на replacement; не удалять provenance.

## 10. Безопасность и приватность

Bridge — public-to-repo-like text surface: считать любой commit потенциально
видимым. Запрещены secrets, tokens, private keys, profile copy, raw audio,
необезличенные transcripts, device identifiers сверх необходимого и полные
environment dumps. Sysop redacts usernames/paths/serials; команды не должны
печатать секреты. High-risk/root действия не входят в MVP; для них отдельный
explicit approval, dry-run, pre/post-check и rollback. Не запускать код/скрипты из
envelope автоматически. Retention для временных evidence задаётся owner; удаление
не должно ломать audit link, вместо этого оставляется redacted tombstone.

## 11. MVP implementation session: 8 шагов

1. **Read-only bootstrap:** прочитать эту spec, [[AndroidOS]], ADR, routing docs,
   [[user-profile-contract]] и [[TASKS]]; проверить наличие AndroidOS/dotfiles refs.
2. Создать route decision для реализации с `docs-only`/`project-edit` границами;
   named roles и explicit fallback, либо `UNROUTABLE`.
3. Провести smoke test структуры: required directories, YAML frontmatter, unique
   IDs, valid statuses и ссылки без placeholder claims.
4. Создать в AndroidOS только `coordination/bridge/README.md`; не создавать пустые
   каталоги/файлы: добавить первый real envelope или остановиться.
5. Выполнить read-only sysop/research smoke test и сохранить redacted evidence.
6. Передать handoff AndroidOS planner → sysop/researcher с одним owner и DoD.
7. Провести review/verifier smoke на документах; application code не трогать.
8. Обновить Vault links/status/report; implementation bridge остаётся отдельной
   будущей задачей, не коммитить в этой сессии.

## 12. Acceptance criteria и stop conditions

MVP принят для отдельной implementation-сессии, если:

- canonical location и ownership явно зафиксированы;
- canonical source of truth — Git-backed bridge files; MCP, если появится, только
  optional local facade;
- envelope, handoff, evidence, decision templates валидны и взаимно связаны;
- один read-only bootstrap и smoke test дают воспроизводимый report;
- нет secrets/profile/raw audio/живой БД и нет application-code changes;
- route использует named roles или явно logged `UNROUTABLE`, без silent `general`;
- conflict/stale/append-only правила проверены на одном примере;
- MCP MVP (если реализуется) ограничен пятью перечисленными инструментами, уважает
  scope/owner, не перезаписывает молча и не является обязательным для телефона;
- implementation order соблюдён: files/smoke test → thin local adapter → расширение
  только при доказанной необходимости;
- Vault links ведут на существующие документы или честно помечены planned.

Немедленно остановиться при неизвестном owner/capability, отсутствии acceptance
boundary, попытке root/install/device mutation, secret/private-data exposure,
двух canonical locations, stale evidence без provenance, пустом/невалидном
artifact или попытке закрыть задачу без verifier evidence.

## 13. Open questions и будущее

После MVP отдельно решить: создавать ли AndroidOS repo сейчас, нужны ли JSON export
или schema validation, как подписывать commits/evidence, как делать cross-repo
index, retention policy, encrypted transport и детали optional adapter. Расширять
MCP, API, event bus, CRDT, Telegram или service relay можно только при доказанном
ограничении Markdown/Git и через новый ADR, не молчаливо.

## 14. Рабочие ссылки

- [[AndroidOS]] — umbrella, roadmap и PA MVP boundaries.
- [[06-Audits/2026-08-22-androidos-pa-mvp-architecture-adr]] — provisional PA architecture, no live DB sync.
- [[DEVELOPMENT-ROADMAP]] — Vault strategy/roadmap.
- [[02-Methods/capability-routing]] — named routing, fallback and `UNROUTABLE`.
- [[06-Audits/2026-08-25-capability-routing-design-note]] — sequence and generic fallback correction.
- [[TASKS]] T-110 — planned optional thin local MCP facade после файлового bridge.
- [[01-Reference/user-profile-contract]] — canonical profile and no-copy policy.
- [[03-Projects/dotfiles]] — Manjaro/sysop/toolchain state and `system-ops` boundary.
- [[TASKS]] T-108 — dotfiles `system-ops` permission/root smoke-test, live evidence pending.
