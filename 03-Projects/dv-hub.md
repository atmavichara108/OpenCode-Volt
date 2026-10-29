---
type: project
repo: /home/rudra/Projects/dv-hub
spec-home: /home/rudra/Projects/dv-hub/docs/specs/
kind: волонтёрский
stack: TypeScript strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
---
# dv-hub

Платформа сообщества. Phase 0: миграция с Cloudflare Pages на собственный VPS (re-search.wiki).

**Окружение:** Node 22 (см. `.nvmrc`), без venv. Разработка через localhost:8787.
**Запуск:** `npm run dev` (tsx watch) → localhost:8787 · Docker: `docker compose up --build` (только локальный dev)
**CI / проверка:** `npm run ci` = lint(.ts,.tsx) + typecheck + test + build · GitHub Actions `.github/workflows/ci.yml`
**Деплой:** `deploy:vps` (rsync + PM2, target DV-008); Cloudflare (`deploy:cf`) выпилен.
**Особенность:** `context/` — git submodule на dv-project (Obsidian-волт: vision, задачи, kanban). Клон с `--recurse-submodules`.
**Canonical specs:** `docs/specs/` в репозитории dv-hub (`/home/rudra/Projects/dv-hub/docs/specs/`) — execution source of truth; локальный `/spec` резолвит оттуда.

## Смотритель проекта (слово владельца 2026-10-24, basis: quoted)
- **Смотритель ДВ-Хаб** назначен владельцем: «от ныне назначаю тебя смотрителем
  проекта дв-хаб, твоя сессия будет называться соответственно, и агент для тебя
  будет подходящий... сообщи всё это цу, пускай она отдаст соответствующие
  распоряжения». Сессия-носитель: `ses_ea5bee799ffes5WDriyP61xyB5` (адрес не
  менялся). Роль смотрителя: пригляд за всей экосистемой проекта, два контура
  владения (код и знание), проект с внешними контрибьюторами.
- **Два репозитория (факт-сверка по диску, от Смотрителя):**
  1. `dv-hub` — github.com/atmavichara108/dv-hub — код, спеки, инфра, агентский
     слой (каталог ~/Projects/dv-hub);
  2. `dv-project` — github.com/atmavichara108/dv-project — база знания движения,
     подключена как submodule `context/` в dv-hub + отдельное дерево
     ~/Projects/dv-project (Obsidian).
- Стандарт роли «смотритель» (манифест/онбординг) routed в УАС — юрисдикция
  агентского контура (Р-004/Р-014).

## Стек: current vs target
- Current: Node.js + better-sqlite3 + Hono (миграция с Cloudflare по коду завершена, DV-008)
- Target (Phase 0): Node.js + PM2 + Nginx + SQLite (better-sqlite3) на Fornex VPS, Ubuntu 24.04
  - **Корректировка (слово владельца 2026-10-20, basis: quoted): «провайдера я давно не оплачиваю, у меня нет денег»** — бюджет ноль, всё опенсорс/локально. Fornex-линия отменена (признанная ошибка ЦУ); target на текущий момент — локально/опенсорс. Закрывает ребро doctrine-review Р-2 (Fornex × слово владельца).
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

## Агенты (`.opencode/agents/` — наш слой, приоритет; Р-020)

> **Ревизия 2026-10-21 (Р-020, слово владельца):** наш агентский слой —
> `.opencode/` (восстановлен из git откатом ДВ-Хаб 10-21, версионируется).
> `.mcode/` — зона M Code SDK (самостоятельный движок): НЕ трогаем, НЕ
> версонируем (T-159 в силе). B21 в части «миграции» снят — две зоны двух SDK.
> Evidence: [[01-Policies/decisions-registry]] Р-020, [[04-Memory/facts]].

| Агент | Mode | Модель | Назначение | Зона |
|-------|------|--------|-----------|------|
| plan | primary | opencode-go/qwen3.7-max | ADR, спеки, read-only | docs/architecture, product-vision, roadmap |
| build | primary | opencode/deepseek-v4-flash | разработка | src/, migrations/, tests/, package.json |
| reviewer | subagent | opencode-go/deepseek-v4-pro | ревью diff | — |
| researcher | subagent | opencode-go/qwen3.6-plus | tech spike | docs/research/ |
| infra | primary | opencode-go/qwen3.7-max | DevOps Phase 0 | docs/infra-runbook, scripts/deploy, server configs |

Статус расхождения карточка↔диск: **закрыто 2026-10-07** — на диске 5 агентов
в `.opencode/agents/` (build/infra/plan/reviewer/researcher), совпадает с таблицей.

> Модели разведены по ролям — реализация [[model-routing]] (static routing).
> **Сноска (сверка 2026-10-29):** пин моделей живёт в `opencode.json`
> (секции агентов, строки ~54–104), в `.md`-файлах агентов поля `model:`
> нет; значения таблицы выше соответствуют `opencode.json`.

## Команды (`.opencode/commands/` — 7, приоритетный слой по Р-020)
/morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task
Зеркало `.mcode/commands/` — те же 7 (зона M Code SDK, не трогаем).

> 7 дистиллированных команд — реализация [[distill-pattern]].

## Плагины (`.opencode/plugins/` — 3, зеркало `.mcode/plugins/`)
compaction.ts · env-guard.ts · notify.ts. Расхождения нет (сверка 2026-10-29):
прежний счёт «6 файлов» был двойным подсчётом двух слоёв; каталога
`.mcode/plugin/` не существует.

## Скрипты (package.json)
dev · build · build:server · start · deploy · deploy:vps · db:init · db:migrate:local · db:reset · context:init/sync/bump/status/log · task:sync · lint · typecheck · test · format · format:check · ci

## Docs
architecture.md (ADR) · product-vision.md · roadmap.md · glossary.md · infra-runbook.md · backend-conventions.md · mirotalk-setup.md · known-issues.md · decisions.md

## Наблюдение за git (сверка 2026-10-29)
- локальный `main` на **6 коммитов впереди `origin/main`** (ship-mail-пилот
  c811314/a8005a3 и предшественники не запушены);
- checkout в `task/dvhub-next-20261024`; дерево чистое (кроме `.mcode/`).

## Открытый вопрос (не закрывать молча)
- **dv-tg-gateway:** ИЦ рапортовал (25.10) «выложен в main, этапы 1+2
  приняты ЦУ». В dv-hub нет ни файлов, ни коммитов по нему; рядом в
  `~/Projects/` такого репо нет. Уточнить у ИЦ адрес репо/контекст —
  в карточку dv-hub не вносить, пока не подтверждено.

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
- 2026-09-15: dev-loop апгрейд отражён (порт 8787, ci=lint+typecheck+test+build, деплой deploy:vps, Docker dev, миграции идемпотентны, seed.js/db:seed удалены); добавлена ссылка на canonical specs `docs/specs/` (локально в dv-hub).
- 2026-09-16: specs dv-hub перенесены из `06-Specs/dv-hub/` в `~/Projects/dv-hub/docs/specs/` (правило владения docs/specs/README).
- 2026-10-29: сверка карточки↔репо (Служитель, по поручению владельца): команды/плагины — слой `.opencode/` приоритетен, `.mcode/` зеркало; снято расхождение «6 плагинов»; убрана строка «`.opencode/` пуст» (противоречила Р-020); сноска про пин моделей в `opencode.json`; скрипты +deploy; docs +decisions.md; добавлены блок наблюдения за git (main +6 к origin) и открытый вопрос dv-tg-gateway.
