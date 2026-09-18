---
type: Method
status: stable
tags: [method, git, concurrency, worktree, isolation]
---

# Git Worktree Isolation — многопоток без спутанных коммитов

## Проблема

Несколько сессий (M Code + OpenCode TUI + субагенты) пишут в **одно** рабочее
дерево `main` одновременно. Итог: грязное дерево, где работы несвязанных
сюжетов лежат кучей, один агент затирает другого, `main` расходится с origin
(в Vault был дубль коммита с разными хэшами — следствие работы в двух
инструментах). Конвенции это не лечат — лечат машины: каждый поток в своей
ветке/worktree, сборка происходит мержем, а не прямыми коммитами.

## Правила (обязательные, держит pre-commit hook в Vault)

1. **Один поток = одна ветка `task/<slug>`** (или `feat/<slug>`). Коммит прямо
   в `main`/`master` запрещён хук-ом `05-Templates/pre-commit-check.sh` —
   только merge или явный `ALLOW_MAIN=1`.
2. **Стартуй не с `main`, а с task-ветки**: `git switch task/<slug>`; если её
   нет — `git switch -c task/<slug> origin/main`.
3. **Горячие файлы** (`TASKS.md`, `04-Memory/active-context.md`,
   `tools/ecosystem-map/registry.json`, `00-INDEX.md`) — править только через
   жёсткий flock-lease: `tools/peers/peer_lease.py run --file F --timeout 10 -- <cmd>`.
   Прямой `edit` на эти файлы гейтится в `ask` (см. [[#принуждение-edit-гейты]]).
   Не взял лок за таймаут → НЕ пишешь.
4. **Перед слиянием в main** — `tools/verify-cache/verify.py --git` (грязное
   дерево + защищённая ветка) и разрешённые конфликты.

## Признаки, что ты в грязном дереве (стоп-сигналы)

- `git status` на `main` показывает `M`-файлы, которых ты не делал → не
  коммить их вместе со своими, они принадлежат чужому потоку.
- Merge-конфликт-маркеры `<<<<<<<` в staged → разреши, не коммить как есть.
- `git branch -vv` видит `main` «впереди N, позади M» → divergence, не
  force-push, не rollback; сначала сверить с человеком.

## Worktree-per-session (сильнейшая форма)

Полная изоляция, когда у каждого первичного потока — свой checkout:

```bash
# создать изолированный worktree под новую ветку
git worktree add ../<project>-tasks/<slug> -b task/<slug>
# работать внутри него — сборка задач идёт в отдельной папке,
# чужие файлы физически недоступны и затирание невозможно
cd ../<project>-tasks/<slug>
# по завершении — закоммитить, вернуться, слить в main, убрать worktree
git switch main && git merge --no-ff task/<slug>
git worktree remove ../<project>-tasks/<slug>
```

M Code умеет это для субагентов нативно: `task { worktree: true }` запускает
каждого субагента в изолированном worktree. Для первичных сессий — запускать
их из отдельного worktree вручную (см. карту ниже).

## Карта текущих worktree-веток (создано 2026-09-18)

| Ветка | Сюжет |
|-------|-------|
| `review/pipboy-2026-09-18` | фикс 2 багов pip-boy (review) |
| `task/specs-migration-2026-09-18` | миграция 06-Specs/ → docs/specs/ + control-plane/ |
| `task/agent-infra` | git-гигиена: pre-commit gate, `peer_lease.py`, `verify.py --git` |
| `task/dotfiles-wip-2026-09-18` | dotfiles WIP (конфиги, плагины, агенты) |
| `task/serp-wip-2026-09-18` | serp WIP (агенты + opencode.json) |
| `task/androidos-wip-2026-09-18` | AndroidOS PA MVP skeleton (пуш — вручную изнутри) |
| `snapshot/2026-09-18-worktree` | полный слепок грязного Vault-дерева |

Все ветки выкачиваются на любом узле: `git fetch origin && git switch <ветка>`.

## Принуждение (edit-гейты)

Два активных слоя:

**1. edit-гейты в конфигах** — прямой `edit` на hot-files переведён в `ask`
(вносится вручную в глобальные конфиги):
```json
"edit": { "*": "allow", "**/TASKS.md": "ask", "**/00-INDEX.md": "ask",
          "**/active-context.md": "ask", "**/registry.json": "ask", "**/AGENTS.md": "ask" }
```

**2. Плагин `main-protector.ts`** (глобальный, `tool.execute.before`) —
неотвратимый runtime-гейт на уровне любого инструмента:
- блок `git commit` в защищённой ветке `main`/`master`, кроме merge;
- блок edit/write на hot-files находясь в `main`;
- fail-open на ошибках git-разведки (не ломает легитимную работу);
- аварийный обход `ALLOW_MAIN=1` для осознанных release.

Это закрывает «бегать за агентами»: правило живёт в рантайме, а не в памяти
модели. Расширение зоны защиты — список `HOT_FILES` в плагине.

## Восстановление / спасение

- Грязное дерево каждого проекта застраховано rsync-snapам в
  `/tmp/mcode/<project>-backup-<stamp>/tree/` + `git bundle` всей истории.

## Связанные

- Механизмы: [[05-Templates/pre-commit-check]], `tools/peers/peer_lease.py`,
  `tools/verify-cache/verify.py`.
- Питает: [[multi-agent-pipeline]] (изоляция потока = изоляция агента).