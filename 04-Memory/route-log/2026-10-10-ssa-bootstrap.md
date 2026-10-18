---
type: Route Log
title: SSA bootstrap — control + seo-outreach cards/index/spec
date: 2026-10-10
status: ROUTED
tags: [routing, bootstrap, general-override, ssa, worktree]
---

# SSA Bootstrap — route decision / evidence

- **route_id:** `ssa-bootstrap->general:2026-10-10`
- **status:** `ROUTED`
- **scope:** `две карточки (SSA, seo-outreach) + 00-INDEX.md + execution-spec продукта`
- **mutability:** `mutable (запись карточек/index/spec), без commit/push`

## Факты маршрута

1. **Named `git-freed` нельзя вызвать как subagent.** Попытка dispatch вернула
   `Agent git-freed cannot run as a subagent`. Это ограничение рантайма, а не
   отказ пользователя.
2. **Пользователь одобрил явный general override** на bootstrap scope (разовая
   роль general, НЕ выдача за вызов git-freed).
3. **General запустил детерминированные проверки** перед любыми Vault-записями:
   `tools/git-agent/freed.py detect` и `tools/tree-cop/tree-cop.py status`
   (точный `--mine` scope) — GO только на чистом изолированном worktree.
4. **Изоляция:** текущий dirty worktree (`task/pipboy-rebuild-20261009`,
   ahead 3 / behind 7, 1482 foreign changes) не трогался. Создан отдельный
   worktree от `origin/main` на ветке `task/ssa-bootstrap-20261010`
   (`/home/rudra/Projects/OpenCode-Vault-tasks/ssa-bootstrap-20261010`).
5. **Scope ровно:** `03-Projects/SSA.md`, `03-Projects/seo-outreach.md`,
   `00-INDEX.md`, spec продукта
   `/home/rudra/Projects/SSA/products/seo-outreach/docs/specs/seo-outreach-mvp-v0.1.md`.
6. **Commits / push: none.** Все правки — рабочие, незакоммиченные.

## Итог

- worktree: `/home/rudra/Projects/OpenCode-Vault-tasks/ssa-bootstrap-20261010`
- ветка: `task/ssa-bootstrap-20261010` (трекает `origin/main`)
- `00-INDEX.md` правился только под flock-lease (`tools/peers/peer_lease.py run`).
- Другие memory-файлы не трогались.
