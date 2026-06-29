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

## Агенты (.opencode/agents/ + opencode.json)
| Агент | Mode | Модель | Назначение | Зона |
|-------|------|--------|-----------|------|
| plan | primary | opencode-go/qwen3.7-max | ADR, спеки, read-only | docs/architecture, product-vision, roadmap |
| build | primary | opencode/deepseek-v4-flash | разработка | src/, migrations/, tests/, package.json |
| reviewer | subagent | opencode-go/deepseek-v4-pro | ревью diff | — |
| researcher | subagent | opencode-go/qwen3.6-plus | tech spike | docs/research/ |
| infra | primary | opencode-go/qwen3.7-max | DevOps Phase 0 | docs/infra-runbook, scripts/deploy, server configs |

> Модели разведены по ролям — реализация [[model-routing]] (static routing).

## Команды (.opencode/commands/) — 7
/morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task

> 7 дистиллированных команд — реализация [[distill-pattern]].

## Плагины (.opencode/plugins/)
compaction.ts · env-guard.ts · notify.ts

## Скрипты (package.json)
dev · build · build:server · start · dev:cf · deploy:cf · deploy:vps · db:init · db:migrate:local · db:seed · db:reset · context:init/sync/bump/status/log · task:sync · lint · test · ci

## Docs
architecture.md (ADR) · product-vision.md · roadmap.md · glossary.md · infra-runbook.md · backend-conventions.md · mirotalk-setup.md · known-issues.md

> docs/ + AGENTS.md + context/ submodule — реализация [[context-as-docs]] (🟡: контекст есть, формальный DoD для задач не прописан).

## Конвенции (из AGENTS.md)
- TS strict, без any (unknown + type guards). Commit: feat/fix/chore/refactor/docs/task(DV-XXX).
- D1 SQLite не поддерживает RETURNING * → INSERT затем SELECT.
- Workflow задач: задача в context/.../Kanban/Tasks/ → spec → build/infra → lint+test → commit.
- Submodule flow через `/sync-task`.

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | нет команды /loop, нет автономной петли |
| [[verifier-pattern]] | ❌ | нет отдельного агента-верификатора с PASS/FAIL |
| [[context-as-docs]] | 🟡 | docs/ + AGENTS.md + context/ есть, формальный DoD не прописан |
| [[distill-pattern]] | ✅ | 7 команд в .opencode/commands/ |
| [[memory-management]] | 🟡 | compaction.ts есть, flush-протокол не реализован |
| [[model-routing]] | ✅ | 5 агентов на 4 моделях (qwen3.7-max / deepseek-v4-flash / deepseek-v4-pro / qwen3.6-plus) |

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-27: убрано упоминание claude-mem; статус memory-management обновлён
- 2026-06-29: добавлены статусы всех 6 методов
- 2026-06-30: ревью — исправлены статусы (distill ✅, model-routing ✅, context-as-docs 🟡, memory-mgmt 🟡), infra mode primary, модели агентов добавлены, docs дополнены, команды 7
