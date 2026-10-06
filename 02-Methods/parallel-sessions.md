---
type: Method
status: proposed
tags: [method, concurrency, handshake, handoff, worktree, parallel-sessions]
---

# Parallel Sessions — протокол параллельной работы (глобальный)

Объединяет три выработанных сценария: `git-worktree-isolation` (Vault,
изоляция потоков), ADR-014 dotfiles (claim, общий worktree, раппорт/рапорт),
Coordination Bridge + host-peer практику mcode в AndroidOS (владение,
handoff, append-only evidence). Действует в opencode v2 и mcode во всех
проектах; per-project enforcement остаётся в репо-владельце.

## Проблема

Несколько сессий (M Code + OpenCode TUI + субагенты) пишут в общие чекауты
одновременно: грязные деревья из чужих сюжетов, перезапись чужой работы,
`main` уезжает из-под ног, коммиты уходят не в ту ветку. Конвенции не лечат —
лечат проверяемые шаги и артефакты.

## Слои (от обязательного к сильному)

### L1. Claim через ветки (всегда)

- Один поток = одна ветка `task/<slug>`; старт не с `main`.
- Перед работой: `fetch` + список активных task-веток. Пересечение scope
  с чужой веткой → вопрос пользователю, не молчаливая параллель.
- Чужие ветки — read-only. Чужое в свой коммит — никогда молча
  (перед коммитом `diff --stat` vs чужая ветка).
- `main` — только merge; push `main` — только по approval.

### L2. Handshake-раппорт (общий чекаут)

- Старт сессии: файл `<repo>/.opencode/memory/session-reports/active/<слаг>.md`
  (кто, ветка, scope, старт, heartbeat). mcode-сессии без `.opencode` —
  запись в локальный memory-стор проекта тем же составом.
- Чужие handshake-файлы — read-only. Heartbeat старше 24ч — мёртв, может
  быть убран с пометкой.
- Конец сессии: файл-отчёт `<дата>-<слаг>.md` по шаблону + удаление своего
  handshake. Мультипроект — строка-указатель в Vault `04-Memory/session-log`.

### L3. Handoff-владение (shared contract / cross-repo)

- У активного сюжета один владелец. Смена владельца — явный handoff
  (from/to/scope/inputs/ожидаемый выход), неявной передачи нет.
- Правка чужого владения без передачи — только как proposal с ожиданием
  согласия владельца (host-peer практика mcode: shared UI/state-контракт
  правит только сессия-владелец; правка без пира — с прозрачной пометкой
  «показать пиру при активности»).
- Наблюдения и проверки — append-only evidence; исправления — новым
  артефактом, без перезаписи provenance.
- Маршрут только по именованным ролям; нет capability — `UNROUTABLE`,
  silent fallback на `general` запрещён.
- Кросс-репо ссылки: `repo=` + полный SHA + `path=`; без SHA — `planned`.

## Stale / blocked

- Обновление/heartbeat старше 7 календарных дней — `stale` до продления
  владельцем с причиной.
- Конфликт владения — `blocked`, не silent merge. Divergence `main`
  (впереди N, позади M) — не force-push/rollback; сначала сверить с человеком.

## Per-project enforcement (не дублировать, ссылаться)

- Vault: `peer_lease.py` на hot-files, pre-commit gate, `verify.py --git`.
- dotfiles: tree-hygiene гейты, skip-worktree на model-пины (ADR-012).
- AndroidOS Bridge: task/handoff/evidence/decision артефакты как канон
  владения (`coordination/bridge/`).

## Worktree-per-session (сильнейшая форма, где возможна)

Изолированный checkout на первичный поток (`task { worktree: true }` в mcode
для субагентов; вручную для первичных сессий). Исключение: dotfiles —
stow-симлинки живут в одном чекауте, там только L1–L3.

## Handoff (librarian, по вызову /spec)

- Интегрировать как Method: связи в 00-INDEX / TASKS / session-log,
  перекрёстные ссылки с [[git-worktree-isolation]] и Bridge README.
- Ревью объединённого протокола; статус `proposed` → `stable` только после ревью.
- Коммит одним пакетом со своими правками: автор спеку отдельно не коммитит.

## Связанные

- Методы: [[git-worktree-isolation]], [[multi-agent-pipeline]], [[memory-management]].
- Репо: ADR-014 dotfiles (claim/worktree/рапорт), Bridge README (владение/handoff/evidence).
