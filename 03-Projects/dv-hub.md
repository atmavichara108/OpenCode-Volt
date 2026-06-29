---
type: project
repo: /home/rudra/Projects/dv-hub
kind: волонтёрский
stack: TypeScript strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
---
# dv-hub

Платформа сообщества. Phase 0: миграция с Cloudflare Pages на собственный VPS (re-search.wiki).

**Окружение:** Node 20/22, без venv. Разработка через localhost:3000.
**Запуск:** `npm run dev` (tsx watch) → localhost:3000
**CI / проверка:** `npm run ci` (= lint + build)
**Деплой:** `deploy:cf` (текущий, Cloudflare) / `deploy:vps` (target, DV-008)
**Особенность:** `context/` — git submodule на dv-project (Obsidian-волт: vision, задачи, kanban). Клон с `--recurse-submodules`.

## Стек: current vs target
- Current: Cloudflare Workers (Hono) + D1 (SQLite) + Pages
- Target (Phase 0): Node.js + PM2 + Nginx + SQLite (better-sqlite3) на Fornex VPS, Ubuntu 24.04
- Constant: TS strict, Vanilla JS ES-modules, Tailwind, Vite, Auth = Telegram Login + email magic-link (Resend)

## Архитектура
```
src/index.tsx        Hono app, HTML shell, OG meta
src/routes/api.ts    REST endpoints
src/lib/auth.ts      Telegram verify, magic-link, sessions
public/static/       app.js + modules/*.js — SPA (hash routing)
migrations/NNNN__.sql
```

Таблицы: cells, users, materials, topics, discussion_rooms, messages, publications, sessions.

## Агенты (.opencode/agents/)
| Агент | Mode | Назначение | Зона |
|-------|------|-----------|------|
| plan | primary | ADR, спеки, read-only | docs/architecture, product-vision, roadmap |
| build | primary | разработка | src/, migrations/, tests/, package.json |
| reviewer | subagent | ревью diff | — |
| researcher | subagent | tech spike | docs/research/ |
| infra | subagent | DevOps Phase 0 | docs/infra-runbook, scripts/deploy, server configs |

## Команды (.opencode/commands/)
/morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task

## Плагины (.opencode/plugins/)
compaction.ts · env-guard.ts · notify.ts

## Скрипты (package.json)
dev · build · build:server · start · dev:cf · deploy:cf · deploy:vps · db:init · db:migrate:local · db:seed · db:reset · context:init/sync/bump/status/log · task:sync · lint · test · ci

## Docs
architecture.md (ADR) · product-vision.md · roadmap.md · glossary.md · infra-runbook.md · backend-conventions.md

## Конвенции (из AGENTS.md)
- TS strict, без any (unknown + type guards). Commit: feat/fix/chore/refactor/docs/task(DV-XXX).
- D1 SQLite не поддерживает RETURNING * → INSERT затем SELECT.
- Workflow задач: задача в context/.../Kanban/Tasks/ → spec → build/infra → lint+test → commit.
- Submodule flow через `/sync-task`.

## Состояние внедрения методов
| Метод | Статус |
|-------|--------|
| [[closed-loop]] | ❌ |
| [[verifier-pattern]] | ❌ |
| [[context-as-docs]] | ❌ |
| [[distill-pattern]] | ❌ |
| [[memory-management]] | ❌ |
| [[model-routing]] | ❌ |

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-27: убрано упоминание claude-mem; статус memory-management обновлён
- 2026-06-29: добавлены статусы всех 6 методов
