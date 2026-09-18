---
type: Method
status: stable
tags: [method, git, concurrency, worktree, isolation]
---

# Git Worktree Isolation — многопоток без спутанных коммитов

## Проблема

Несколько сессий (M Code + OpenCode TUI + субагенты) пишут в **одно** рабочее
дерево `main` одновременно. Итог: грязное дерево, где работы трёх несвязанных
сюжетов лежат кучей, один агент затирает другого, `main` divergence (локально
37 коммитов вперёд, 2 позади origin — среди них два почти одинаковых
«capture живой слив» с разными хэшами).

Конвенции это не лечат — лечат машины: каждый поток в своей ветке, общая точка
сборки живёт мержем, а не прямыми коммитами.

## Правила (обязательные, держит pre-commit hook)

1. **Один поток = одна ветка `task/<slug>`** (или `feat/<slug>`). Коммит прямо
   в `main`/`master` запрещён хуком `05-Templates/pre-commit-check.sh` — только
   merge или явный `ALLOW_MAIN=1`.
2. **Стартуй не с `main`, а с task-ветки**: `git switch task/<slug>`; если её
   нет — `git switch -c task/<slug> origin/main`.
3. **Горячие файлы** (`TASKS.md`, `04-Memory/active-context.md`,
   `tools/ecosystem-map/registry.json`, `00-INDEX.md`) — править только через
   жёсткий flock-lease: `tools/peers/peer_lease.py run --file F --timeout 10 -- <cmd>`.
   Не взял лок за таймаут → НЕ пишешь.
4. **Перед слиянием в main** — `tools/verify-cache/verify.py --git` (грязное
   дерево + защищённая ветка) и разрешённые конфликты.

## Признаки, что ты в грязном дереве (стоп-сигналы)

- `git status` на `main` показывает `M`-файлы, которых ты не делал → не
  коммить их вместе со своими, они принадлежат чужому потоку.
- Merge-конфликт-маркеры `<<<<<<<` в staged → разреши, не коммить как есть.
- `git branch -vv` видит `main` «впереди N, позади M» → divergence, не
  force-push, не rollback; сначала сверить с человеком.

## Карта текущих веток (создано 2026-09-18, всё сверх `a4c9df4`)

| Ветка | Сюжет |
|-------|-------|
| `task/agent-infra` | git-гигиена: pre-commit gate, `peer_lease.py`, `verify.py --git` |
| `task/promo-provider` | promo-provider protocol + карточки linaliapi/justwoker |
| `task/dotfiles-agent-v3` | dotfiles v3 агентная консолидация (ADR-010) |
| `task/vault-runtime` | decision-queue runtime, pip-boy v10 runbook |
| `snapshot/2026-09-18-worktree` | полный слепок всех 25 файлов (ничего не потеряно) |

## Восстановление / спасение

- Всё грязное дерево застраховано: `/tmp/mcode/vault-backup-20260918-154920/`
  (rsync 294 файла + `vault-full.bundle` всей истории).
- Забрать свою ветку на любом узле: `git fetch origin && git switch task/<slug>`.

## Связанные

- Механизмы: [[05-Templates/pre-commit-check]], `tools/peers/peer_lease.py`,
  `tools/verify-cache/verify.py`.
- Питает: [[multi-agent-pipeline]] (изоляция потока = изоляция агента).