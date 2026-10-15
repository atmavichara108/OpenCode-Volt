# Pip-Boy Rebuild — Phase 1: переподключение данных (2026-10-09)

kind: task · status: in-progress · owner: vault-librarian · branch: `task/pipboy-rebuild-20261009`

## Проблема

Pip-Boy v11 (сентябрь 2026) показывает картину мира на сентябрь: ECO-карточки,
registry, TASKS. С тех пор источники правды уползли, и Pip-Boy их не видит:

- `control-plane/decision-queue/cards/` — ~471 карточка решений (shell-разрешения и др.)
- `04-Memory/idea-graph/` — nodes.jsonl (213) + edges.jsonl (234), мультиграф stream/world
- `control-plane/model-catalog.json` — каталог моделей/провайдеров
- `00-WORLD.md`, граф 048-053, задачи T-171..178

Фронтенд при этом почти не читает `snapshot.json` напрямую — модули едят вывод
`actions.py` ops (`query/blockers/next/dependencies/proposals`). Значит
переподключение идёт через **observer + actions**, а не через перекраску тайлов.

## Scope Phase 1 (эта сессия)

1. `observer.py` — три новых reader'а, schema `ecosystem-snapshot/1.1`:
   - `read_decision_queue()` — counts by status/type, high-risk pending (топ-20)
   - `read_idea_graph()` — counts by status/graph/kind
   - `read_model_catalog()` — providers, total/free models
   - Детерминизм: DQ-хеш — один sha256 по отсортированным похешам файлов
     (471 запись в digest не тащим).
2. `actions.py` — два новых op: `dq`, `igraph` (сводка + списки).
3. `pipboy.py` — whitelist +2.
4. Регенерация snapshot, smoke-test обоих op, коммит ветки.

## Не scope

- Новые тайлы UI, перекраска, UX-концепция — Phase 2, после решения Рудры.
- Горячие файлы (TASKS.md, registry.json) — только чтение; правки через flock-lease.
- Чужие WIP-файлы в дереве (`.b11-staging/`, `.inv/`, `Без названия.base` и др.) — не трогать.

## Валидация

- `python3 observer.py --dry-run | python3 -c json.load` — schema 1.1, три новых ключа.
- `python3 actions.py dq`, `python3 actions.py igraph` — `{"ok": true, ...}`.
- Verifier: независимая проверка перед merge в main.
