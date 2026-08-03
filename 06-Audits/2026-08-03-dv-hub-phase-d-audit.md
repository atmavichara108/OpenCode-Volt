---
type: Audit
title: dv-hub — Phase D read-only audit (волонтёрский TS/Hono проект)
date: 2026-08-03
status: open
scope: Сверка декларации волта (карточка, INDEX, VibeOS) с фактической агентной
  инфраструктурой `/home/rudra/Projects/dv-hub` и его изоляцией от глобального
  nerve (`~/.config/opencode/`). Только чтение. Факт отделён от интерпретации.
sources:
  - 03-Projects/dv-hub.md
  - 00-INDEX.md
  - VibeOS.md
  - /home/rudra/Projects/dv-hub/.opencode/**, opencode.json, AGENTS.md, README.md, package.json, wrangler.*, docs/**, migrations/**, tests/
  - /home/rudra/.config/opencode/** (global nerve, только для проверки изоляции)
  - 06-Audits/2026-08-02-upgrade-planning-seed.md
  - 06-Audits/2026-08-03-serplux-phase-c-audit.md
  - TASKS.md
tags: [audit, phase-d, dv-hub, read-only, agent-infra, global-nerve, isolation]
---
# dv-hub — Phase D audit (2026-08-03)

> Фаза D — повторно-читающая сверка проекта `dv-hub` после Фазы C по SERPlux.
> Read-only: репозиторий `dv-hub` и глобальный nerve не правились, существующие
> файлы волта не тронуты (кроме создания этого нового файла), коммита нет. Факт
> отделён от интерпретации: `declared` — только волт; `observed` — только чтение
> файлов; `confirmed gaps` — подтверждённые расхождения и неподтверждённые области
> (`[проверить]`); `what this changes` / `what must be fixed` — интерпретации для
> плана, без code-fix и без выдавания чего-либо за выполненное. Карточка проекта:
> [[03-Projects/dv-hub]]. Смежные аудиты:
> [[06-Audits/2026-08-03-serplux-phase-c-audit]],
> [[06-Audits/2026-08-02-upgrade-planning-seed]],
> [[06-Audits/2026-08-02-vibecoding-layer-audit]].

---

## short verdict

dv-hub — **изолированный локальный agent-island**: 5 агентов, 7 команд, 3 плагина,
static routing в `opencode.json`. Глобальный nerve (`/loop`, `/done`, `@verifier`,
`@meta`, `session-flush.ts`) к нему **не подключён** — ноль evidence-type ссылок в
конфиге, командах, AGENTS.md, docs/. Это подтверждает тезис upgrade-planning-seed
о «global kernel + local extensions» и явно относит dv-hub к «local-only» полке.
Карточка в основном точна, но расходится с фактом по `verifier-pattern ❌`,
`/loop`-изоляции, числу команд в README, ADR-дрейфу (Zomro↔Fornex) и нескольким
runtime-дефектам (primary auth 404, неполная D1-миграция, high-severity Hono CVE).
Acceptance/test-поверхности нет (`tests/` пуст, `npm test` exit 1, CI без тестов,
`.github/` отсутствует) → verifier-loop внедрять не во что.

---

## declared

### Слой 1 — что заявлено в волте про dv-hub

Источники: `03-Projects/dv-hub.md` (лог актуализирован 2026-06-30), `00-INDEX.md`,
`VibeOS.md`, а также связанные артефакты волта
(`06-Audits/2026-08-02-upgrade-planning-seed.md`,
`06-Audits/2026-08-03-serplux-phase-c-audit.md`, `TASKS.md:59` T-072).

#### Архитектурная роль

- **Платформа сообщества** re-search.wiki, волонтёрский проект (`dv-hub.md:3-4`).
- **Phase 0:** миграция Cloudflare Pages → own VPS (Fornex) (`dv-hub.md:9`).
- **Стек:** TS strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
  (`dv-hub.md:4`);
  Node 20/22, без venv, dev `npm run dev`, CI `npm run ci` (=lint+build)
  (`dv-hub.md:11-13`).
- **Status:** ✅ active в `00-INDEX.md:28`, `VibeOS.md:232` (там же ошибочно
  «✅ (6 агентов)» — см. D-1 below).
- `context/` — git submodule на dv-project (Obsidian-волт: vision, задачи,
  kanban) (`dv-hub.md:15`).

#### Агенты (заявлено, `dv-hub.md:33-41`) — 5

| Агент | Mode | Модель | Назначение |
|---|---|---|---|
| plan | primary | opencode-go/qwen3.7-max | ADR, спеки, read-only |
| build | primary | opencode/deepseek-v4-flash | разработка |
| reviewer | subagent | opencode-go/deepseek-v4-pro | ревью diff |
| researcher | subagent | opencode-go/qwen3.6-plus | tech spike |
| infra | primary | opencode-go/qwen3.7-max | DevOps Phase 0 |

> Модели разведены по ролям — реализация `[[model-routing]]` (static routing)
> (`dv-hub.md:42`).

#### Команды (заявлено, `dv-hub.md:44-47`) — 7

`/morning · /spec · /review · /hygiene · /sync-context · /sync-context-self ·
/sync-task` — реализация `[[distill-pattern]]`.

#### Плагины (заявлено, `dv-hub.md:49-50`) — 3

`compaction.ts · env-guard.ts · notify.ts`.

#### Методы (заявлено, `dv-hub.md:66-74`)

| Метод | Статус | Основание |
|---|---|---|
| `[[closed-loop]]` | ❌ | нет команды `/loop`, нет автономной петли |
| `[[verifier-pattern]]` | ❌ | нет отдельного агента-верификатора с PASS/FAIL |
| `[[context-as-docs]]` | 🟡 | docs/+AGENTS+context/ есть, формальный DoD не прописан |
| `[[distill-pattern]]` | ✅ | 7 команд в `.opencode/commands/` |
| `[[memory-management]]` | 🟡 | `compaction.ts` есть, flush-протокол не реализован |
| `[[model-routing]]` | ✅ | 5 агентов на 4 моделях |

#### Прочее заявленное

- Зоны ответственности build (`src/`, `migrations/`, `tests/`, `package.json`),
  plan (`docs/architecture`, `product-vision`, `roadmap`), infra
  (`docs/infra-runbook`, `scripts/deploy`, server configs) (`dv-hub.md:34-40`).
- Workflow задач: kanban → spec → build/infra → lint+test → commit; submodule flow
  через `/sync-task` (`dv-hub.md:62-64`).
- VibeOS (`VibeOS.md:141-200`) подтверждает: distill ✅, context-as-docs 🟡,
  model-routing ✅, memory-management 🟡; closed-loop/verifier — для dv-hub
  отмечены отсутствующими; строки 232 и 289-308 повторяют 5-агентную раскладку.
- `00-INDEX.md:50` — метод-таблица помещает dv-hub рядом с SERPlux/dotfiles/vault.

---

## observed

### Слой 2 — фактическое чтение `/home/rudra/Projects/dv-hub` (read-only)

#### `.opencode/` структура

- `ls .opencode/`: `agents/`, **`commands/`** (не `command/`), `plugins/`,
  `package.json`, `package-lock.json`, `node_modules/`. Каталога `subagent/` нет,
  `memory/` нет. `package.json` внутри не досматривался.
- Каталог **`commands/`** (множ. число) — у dv-hub именно так; в SERP — `command/`.
  Это локальная вариативность имени каталога команд — **`[проверить]`** как
  OpenCode дискалудизированно открывает оба имени.

#### `opencode.json` (140 строк, не `.jsonc`)

- `$schema`, `model: "opencode-go/deepseek-v4-flash"` (default), `lsp: true`.
- `instructions[]`: 10 путей — `docs/*` (5) + `context/DV/**` (5, globs). Это
  реализация context-as-docs — docs/ tether загрузки через `instructions`.
- `permission`: edit `ask`; bash `*`=ask + allowlist (ls/find/cat docs/src/tests/
  migrations/context/package.json/opencode.json/AGENTS.md/README, git status/diff/
  log/branch, `npm run lint|test|build`, `npm run context:status|log`,
  `npx tsc *`); deny — `cat .env*`, `cat **/.env*`, `cat **/auth.json`,
  `cat **/.ssh/*`, `cat **/keys-passwords*`, `cat /etc/**`, `cat /root/**`,
  `rm *`, `rm -rf *`, `sudo *`; `webfetch: allow`.
- **Все 5 агентов объявлены inline в `opencode.json`** (блок `agent.*`),
  отдельного `.opencode/agents/*.md`-discovery там не требуется — но
  **физически файлы `.opencode/agents/{plan,build,reviewer,researcher,infra}.md`
  тоже есть** и содержат согласованные `mode`/`description`/`steps`-семантику
  (см. ниже). Это дубль-источник правды agent-config: права/модели — в
  `opencode.json`, описание/зоны — в `.md`. **`[проверить]`** — конфликтует ли
  inline-блок с auto-discovered md-файлами (override-or-merge контракт) на
  runtime-уровне.
- Модели в `opencode.json` vs карточке — **совпадают полностью**:
  plan=qwen3.7-max, **build=opencode/deepseek-v4-flash** (именно **`opencode/`**,
  без `-go/` суффикса, в отличие от остальных 4 моделей `opencode-go/...`),
  reviewer=deepseek-v4-pro, researcher=qwen3.6-plus, infra=qwen3.7-max
  (`opencode.json:73-128`).
- **MCP:** блок `mcp.github` (`local`, `npx @modelcontextprotocol/server-github`,
  `${env:GITHUB_TOKEN}`, `enabled: true`). GitHub MCP явно подключён.

#### `.opencode/agents/*.md` (5 файлов, `mode` совпадает с карточкой)

- `build.md`: mode `primary` (frontmatter), описание, зоны `src/**, migrations/**,
  tests/**, package.json, .opencode/plugins/**`, anti-zones `docs/**, context/**,
  opencode.json`. Рассуждай по-русски. После изменений — `npm run lint && npm run
  test (если есть)`.
- `plan.md`: `primary`, стратег, read-only, пишет ADR/спеки в `docs/architecture.md`,
  `context/DV/Operations/Specs/DV-XXX-spec.md`, делегирует build.
- `reviewer.md`: `subagent`, ревью кода/документации; блок-лист проверок
  (соответствие спеке, утечки секретов, идемпотентность, зоны ответственности, TS
  strict); выдаёт список замечаний с приоритетами (blocker/major/minor). edit deny,
  bash allowlist (`git diff*`, `git log*`, `grep*`, `cat*`, `ls*`) — это **quality
  reviewer**, не acceptance verifier.
- `researcher.md`: `subagent`, tech spike, пишет в `docs/research/**`, read-доступ
  ко всем файлам через Read/Glob/Grep.
- `infra.md`: `primary`, DevOps, зоны `docs/infra-runbook.md`, `scripts/deploy/**`,
  nginx/pm2/.env.example; не трогает `src/`, `migrations/`, `product-vision.md`,
  `roadmap.md`.
- Подтверждено: **5 агентов** + inline-блок в `opencode.json`. Plan→build→reviewer
  split фактически есть. **Verifier отсутствует.**

#### `.opencode/commands/` (7 файлов; в README указано только 5)

| Файл | agent | subtask | Что делает |
|---|---|---|---|
| `morning.md` | plan | — | `git log --oneline -10`, Kanban Board → статус дня |
| `spec.md` | plan | — | Сгенерировать ТЗ для `$ARGUMENTS` (цель, риски, DoD, первый коммит) |
| `review.md` | reviewer | true | `git diff` → ревью blocker/major/minor/nit |
| `hygiene.md` | plan | true | Еженедельный аудит: устаревшие ADR, задачи без DoD, дрейф docs/ |
| `sync-context.md` | build | — | `npm run context:status/sync`, `git diff context`, bump с push |
| `sync-context-self.md` | — | — | Только статус + pull submodule, без explanation блок-инструкции как у sync-context |
| `sync-task.md` | — | — | `bash scripts/sync-task.sh "$ARGUMENTS"` — bump-коммит в submodule + pointer |

- Подтверждено: **7 команд** физически, как в карточке (`dv-hub.md:45`).
- **`README.md:151-155` перечисляет только 5** (`/morning`, `/spec`, `/review`,
  `/sync-context`, `/hygiene`) — **`/sync-context-self` и `/sync-task` опущены**.
  Это документационный дрейф README vs `.opencode/commands/` vs карточки.
- Содержательно `sync-context-self.md` и `sync-task.md` — близкие по смыслу
  «вспомогательные sync»-команды; их опущение в README похоже на осознанный отсев
  «внутренних» команд, но **`[проверить]`** — намеренное это или устаревание.

#### `.opencode/plugins/` (3 файла, `.ts`)

| Файл | export | обработчики |
|---|---|---|
| `compaction.ts` | `export default plugin` | `session.compact` (инжектит PERSISTENT_CONTEXT), `session.idle` (no-op placeholder) |
| `env-guard.ts` | `export const EnvGuard` (**named, no default**) | `tool.execute.before` (read/edit/write/bash → refuse защищённых путей) |
| `notify.ts` | `export const Notify` (**named, no default**) | **`event` catch-all** + фильтр `if (event.type === "session.idle")` → `notify-send` |

Примечания по плагинам (факт):
- **Mixed default/named exports**: `compaction.ts` — `export default`; `env-guard.ts`
  и `notify.ts` — `export const <<Name>>` без `export default`. Глобальный
  `~/.config/opencode/plugins/session-flush.ts` — `export default`. Совместим ли
  loader OpenCode с named-exports при отсутствии default — **`[проверить]`**
  (та же открытая область, что в SERP Phase C, G3). Не подтверждено, что это bug;
  это **loader risk**, не доказанный runtime-дефект.
- **`notify.ts` использует generic catch-all `event`** с внутренней фильтрацией
  `event.type === "session.idle"`, тогда как `compaction.ts` использует точечный
  ключ `session.idle`, а глобальный `session-flush.ts` — точечные `file.edited` /
  `session.idle`. Валидность `event` как catch-all ключа OpenCode Plugin API —
  **`[проверить]`** (тот же вопрос, что SERP Phase C G4).
- **`compaction.ts` PERSISTENT_CONTEXT** содержит «ADR-001: VPS **Zomro Poland**
  + Nginx + PM2» — противоречит `docs/architecture.md:4` («ADR-001: Self-hosted
  infrastructure on **Fornex VPS**, Germany, Ubuntu 24.04») и `infra-runbook.md`
  (Fornix упоминается свыше 8 раз, «Провайдер: Fornex»). Подтверждённый ADR-дрейф
  между инжектируемым при компакции контекстом и актуальной docs/. Аналог SERP
  Phase C G6 (устаревший persistent-context), но здесь дрейф конкретной ADR-ссылки.

#### `AGENTS.md` (проектный, `dv-hub/AGENTS.md`, 9.4 KB)

- Закрепляет стек (TS strict, без any), workflow (kanban → spec → build →
  lint+test → commit), submodule flow, commit-префиксы (`feat/fix/chore/refactor/
  docs/task(DV-XXX)`), D1-СПецифика (`INSERT затем SELECT` — нет `RETURNING *`).
- Содержательно согласуется с карточкой и с фактическими agent-файлами.

#### `docs/`

- `ls docs/`: `architecture.md`, `audit/`, `backend-conventions.md`, `glossary.md`,
  `infra-runbook.md`, `known-issues.md`, `mirotalk-setup.md`, `product-vision.md`,
  `roadmap.md`. Карточка (`dv-hub.md:56`) дополнительно заявляет `known-issues.md`
  и `mirotalk-setup.md` — все совпадают.
- `docs/architecture.md`: 8 ADR (ADR-001 «Self-hosted infrastructure on Fornex VPS»
  … ADR-008 «Authentication — Telegram + magic-link»). Содержание ADR-001 —
  **Fornex Germany**, что противоречит `compaction.ts` PERSISTENT_CONTEXT.
- `docs/known-issues.md` — два открытых пункта:
  - **#1: Telegram авторизация не работает.** Симптом: Telegram Bot API `getMe`
    возвращает `{"ok":false,"error_code":404,"description":"Not Found"}`.
    Webhook `/webhook/telegram` отвечает 200, домен в @BotFather зарегистрирован.
    Статус: «Токен обновлён несколько раз, проблема не решена». Временное решение:
    email magic-link работает. → **Primary auth broken at runtime.**
  - **#2: Неполная миграция данных из Cloudflare D1.** Симптом: отсутствуют
    последние темы/материалы после начального экспорта; API `/api/dashboard`
    возвращает только старые данные. Статус: «Миграция выполнена частично».
    Следующий шаг: повторный `wrangler d1 export`. → **D1 migration incomplete.**
- `docs/audit/audit-2026-07-21.md` — локальный аудиторский снимок от 2026-07-21:
  ветка main, последний коммит `c66d2ed` (23 дня stale на момент аудита), список
  modified/untracked, dependency drift report (@hono/node-server 2.0.4→2.0.11,
  @hono/vite-dev-server 0.18.3→0.26.1, @types/jest →30.0.0 и др.). Это
  evidence-источник про drift.
- Каталога `.opencode/memory/` нет; memory адресуется в docs/ + context/
  submodule.

#### `tests/`, `npm test`, CI

- `ls tests/`: **пуст** (каталог существует, `test_*.ts`/`test_*.js` файлов нет,
  `jest.config.js` в корне — есть).
- `npm test` → `jest: No tests found, exiting with code 1`. **`npm test` exit 1**
  подтверждено.
- `package.json` scripts: `ci: "npm run lint && npm run build"` — тестов в CI нет.
- `.github/` — **отсутствует** (нет GitHub Actions, нет PR-templates). CI =
  локально вручную `npm run ci`.

#### Wrangler — placeholders / leftovers

- `wrangler.toml` (старый, Cloudflare Pages): `account_id = "your-account-id"`,
  `id = "your-kv-namespace-id"`, `database_id = "your-d1-database-id"`,
  `JWT_SECRET = "your-jwt-secret-key"` — все плейсхолдеры.
- `wrangler.jsonc` (новее, `compatibility_date 2026-04-01`): `database_id =
  "cba35793-..."` — реальный ID; `pages_build_output_dir: ./dist`.
- `wrangler.example.toml` итого в корне → **3 wrangler-файла** при target VPS
  deploy. `deploy:cf` ещё в `package.json` (`dv-hub.md:14` отмечает both). Это
  leftovers от Phase 0 migration; `.wrangler/` каталог есть.

#### Зависимости и security

- `hono` resolved на `4.12.10` (devdeps + deduped).
- `npm audit`: **14 vulnerabilities (2 low, 2 moderate, 10 high)**.
  - **`hono <=4.12.26` — high** «Improperly Handles JSX Attribute Names Allows
    HTML Injection in hono/jsx SSR» (GHSA-458j-xx4x-4375) — релевантно для
    SSR-приложения с `src/index.tsx`.
  - **`@hono/node-server <=2.0.9` — moderate** Path traversal via `%5C` +
    Unauth memory-leak DoS via aborted WS-handshake (no fix available). Для
    VPS-runtime (target) — прямой риск.
  - `@babel/core` arbitrary file read; `brace-expansion` multiple DoS — devDep
    chains (eslint/jest), runtime-критичности ниже.
  - Dependency drift (по `docs/audit/audit-2026-07-21.md`): `@hono/node-server`
    2.0.4→2.0.11, `@hono/vite-dev-server` 0.18.3→0.26.1, `@types/jest` →30 —
    devDep-date-lag.

#### Активность и признаки деградации от простоя

- `git log -1 --format=%ci` = **2026-07-25 10:20:44 +0300** — последняя
  активность 9 дней назад (на дату аудита 2026-08-03). Между двумя
  аудиторскими снимками (`docs/audit/audit-2026-07-21.md` → 23-дня stale на
  2026-07-21) и последним коммитом 2026-07-25 — четыре коммита в один день
  (`b30727d`, `196565e`, `6df09d5`, `7e8b73e`). С тех пор — простой.
- Признаки деградации от простоя: незакрытые `known-issues` (Telegram auth 404
  с «токен обновлён несколько раз, не решён»), dependency drift растёт
  (snap от 2026-07-21 уже фиксирует разрывы), `tests/` остаётся пустым с
  момента инициализации.

### Слой 2 — фактическое чтение global nerve (для проверки изоляции)

- `~/.config/opencode/agent/`: `meta.md`, `verifier.md` (оба `mode: subagent`,
  см. SERP Phase C).
- `~/.config/opencode/command/`: `done.md`, `loop.md`.
- `~/.config/opencode/plugins/`: `session-flush.ts`.
- **`grep` по `/loop`, `/done`, `@verifier`, `@meta`, `verifier.md`, `meta.md`,
  `session-flush` в `dv-hub/{AGENTS.md, .opencode/, docs/}` — совпадений нет**
  (matches только в `node_modules/effect/**` — false positives по слову «done»).
  → **Глобальный nerve к dv-hub фактически не подключён.** Это не «declared ❌» —
  это **observed absence**: ни в проектном конфиге, ни в командах, ни в docs/
  ссылок на global nerve entities нет.
- **`/done` в контексте dv-hub не используется** (чеклист `/done` целит в
  волт-TASKS/VibeOS/active-context/`/commit`; у dv-hub локальная memory в
  `docs/`+context/ submodule, и глобального `/commit` нет, локального `/commit`
  тоже нет — только `/review` + `agent.instructions` workflow).
- **`/loop` в контексте dv-hub не используется** (карточка `closed-loop ❌`
  подтверждена).
- **`session-flush.ts`** целит в `<directory>/04-Memory/session-log/<date>.md`.
  Применяется ли он auto-ко всем проектам — **`[проверить]`** (та же открытая
  область, что SERP Phase C G5). В `dv-hub` нет `04-Memory/`; если применился бы
  auto — создавал бы stray-каталог в TS-проекте, конфликтуя с docs/-model.

---

## confirmed gaps by severity

> Только подтверждённые расхождения между `declared` и `observed` + неподтверждённые
> области (`[проверить]`). Runtime claims, которые сам аудитор не исполнял, помечены
> явно. Loader-risk НЕ называется доказанным bug.

### Runtime gaps

#### HIGH

- **G-D-RUN-1: Primary auth broken at runtime.** Telegram Bot API `getMe`
  возвращает 404 (документировано в `docs/known-issues.md:1`). Код в `src/lib/auth.ts`
  имеет ветки telegram (`createTelegramAuthToken`, `getTelegramAuthToken`, etc.),
  что формально подтверждает активную поверхность auth — но первичный auth-путь
  не работает; временное решение — email magic-link. Источник:
  `docs/known-issues.md:1-39`.
- **G-D-RUN-2: D1 migration incomplete.** API `/api/dashboard` возвращает только
  старые данные (после 2026-04-03 новыми записями нет в локальной SQLite).
  Документировано: `docs/known-issues.md:41-66`. Phase 0 migration фактически
  data-incomplete.
- **G-D-RUN-3: 0 acceptance tests / no verifier-loop.** `tests/` пуст, `npm test`
  exit 1, `ci: lint+build` (без тестов). **Нет поверхности, на которую может
  опереться `/loop`→`@verifier`→`VERDICT PASS/FAIL`** — верификатору нечего
  верифицировать. Подтверждено read-only.

#### MEDIUM

- **G-D-RUN-4: high-severity Hono vulnerability.** `hono 4.12.10` ≤ 4.12.26,
  GHSA-458j-xx4x-4375 (HTML Injection in `hono/jsx` SSR). Релевантно: кодовая база
  использует `src/index.tsx`. Источник: `npm audit`.
- **G-D-RUN-5: @hono/node-server moderate vulns (no fix available).** Path
  traversal `%5C` + unauth WS memory-leak DoS. Релевантно для target VPS-runtime.
- **G-D-RUN-6: CI excludes tests + `.github/` absent.** CI = `npm run lint &&
  npm run build`; нет GitHub Actions, нет PR-template. Любой push может пройти без
  тестов (которых нет) и без CI-gate. Подтверждено.
- **G-D-RUN-7: Dependency drift.** `@hono/node-server` 2.0.4 → 2.0.11,
  `@hono/vite-dev-server` 0.18.3 → 0.26.1, `@types/jest` → 30.0.0 и др. (по
  `docs/audit/audit-2026-07-21.md`). Drift растёт на простое.

### Methodology gaps

#### HIGH

- **G-D-METH-1: No verifier-pattern / closed-loop (✓ declared as ❌, confirmed).**
  Локального `verifier.md` нет; `/loop` нет; глобальные `verifier.md`/`/loop` не
  подключены (см. ecosystem integration). Карточка прямо заявляет ❌ (`dv-hub.md:69-
  70`) — **declared = observed**, gap зафиксирован в карточке честно. Это не
  «карточка врёт», это «метод не внедрён».
- **G-D-METH-2: reviewer without verifier — quality без acceptance.** Локальный
  `reviewer.md` — это code-review (blocker/major/minor/nit), edit deny, bash
  allowlist `git diff/log/grep/cat/ls`. Карточка различает `reviewer` (есть) vs
  `verifier` (нет) — это корректнее карточки SERPlux (где они смешаны). Но
  методологически это **«reviewer без verifier-loop»** = half-pipeline.

#### MEDIUM

- **G-D-METH-3: memory-management 🟡 — только compaction injection.** `compaction.ts`
  инжектит PERSISTENT_CONTEXT в `session.compact`. Event-log/replay нет
  (`session.idle` — no-op placeholder). В карточке помечено 🟡 (`dv-hub.md:73`) —
  соответствует факту.
- **G-D-METH-4: context-as-docs 🟡 — формальный DoD не прописан.** `instructions[]`
  в `opencode.json` подгружает 10 docs/context-путей; `/hygiene` прямо делает
  аудит DoD-пустоты. Сам DoD на задачу не формализован. Совпадает с карточкой 🟡.

#### LOW

- **G-D-METH-5: model-routing ✅ — спорадичный model-id namespace drift.** `build`
  использует `opencode/deepseek-v4-flash` (без `-go/`), остальные — `opencode-go/...`.
  Карточка и `opencode.json` согласованы — это **наблюдаемая аномалия**, не bug
  в карточке. Релевантно для capability-routing (T-073 «canonical builder
  name»).

### Documentation / drift gaps

#### MEDIUM

- **G-D-DOC-1: ADR drift Zomro ↔ Fornex.** `compaction.ts` PERSISTENT_CONTEXT
  говорит «ADR-001: VPS **Zomro Poland** + Nginx + PM2». `docs/architecture.md:4`
  говорит «ADR-001: **Fornex VPS**, Germany, Ubuntu 24.04». `infra-runbook.md` 8+
  раз ссылается на Fornex. Это рассинхронизация между инжектируемым при компакции
  persistent-context и каноническим docs/. После compaction агент «помнит» ADR
  Zomro вопреки архитектуре.
- **G-D-DOC-2: README command table удалена на 2 команды.** `README.md:151-155`
  перечисляет 5 (`/morning /spec /review /sync-context /hygiene`), файловая система
  и карточка — 7 (нет `/sync-context-self`, `/sync-task`). Дрейф README vs
  `.opencode/commands/` vs карточки.
- **G-D-DOC-3: VibeOS agent count mismatch.** `VibeOS.md:232` пишет про dv-hub
  «✅ (6 агентов)»; карточка (`dv-hub.md:33`) и фактические файлы — **5 агентов**
  (+ inline-блок в `opencode.json` дублирует те же 5). Одно место волта
  переоценивает.

#### LOW

- **G-D-DOC-4: Card log stale; card touched последний раз 2026-06-30.** `dv-hub.md:76-80`
  лог заканчивается 2026-06-30; после этого — 7 коммитов в репо до 2026-07-25,
  включая `6df09d5 chore(agents): add OKF v0.1 support and switch build model` —
  что фактически меняло agent-infra, но в карточке не отражено. Карточка drift
  от репо со скоростью коммита.
- **G-D-DOC-5: Wrangler leftovers (3 файла).** `wrangler.toml`, `wrangler.jsonc`,
  `wrangler.example.toml` все в корне; `wrangler.toml` содержит только плейсхолдеры
  (`your-account-id`, `your-kv-namespace-id`, `JWT_SECRET = "your-jwt-secret-key"`),
  `wrangler.jsonc` — production-ready ID. При target VPS-runtime (Phase 0) —
  смешанный state, потенциальный риск деплоя `deploy:cf`.
- **G-D-DOC-6: ecosystem-map node для dv-hub absent в волте.** Среди
  `tools/ecosystem-map/` экосистемных узлов (см. upgrade-planning-seed §290
  «ecosystem-map as planning UI») формальный dv-hub-узел с превью текущего
  состояния (vulns/auth/tests/agents) не обнаружен. Не подтверждено наличие
  актуальной карты-узла. **`[проверить]`** (не искал досконально — за границами
  read-only audit scope).

### Ecosystem integration gaps

#### HIGH

- **G-D-ECO-1: Global nerve isolation — zero coupling.** В `dv-hub/AGENTS.md`,
  `.opencode/`, `docs/` нет ни одной ссылки на `/loop`, `/done`, `@verifier`,
  `@meta`, `verifier.md`, `meta.md`, `session-flush.ts`. Глобальные global-nerve
  entities **фактически не подключены к проекту**. Это подтверждает ядро
  upgrade-planning-seed §176 («global kernel + local extensions»): часть проектов
  реально живёт как local-only islands. Это **не bug** — это структурный факт,
  который должен учитываться в upgrade-plan (глобальный `/done`, `/loop`,
  `verifier` неявно предполагают adoption, которой нет).

- **G-D-ECO-2: No local `/commit`, no global `/commit`.** У dv-hub нет
  `/commit`-команды (в SERP — есть локальная; в волте — глобальная, см. Phase C
  G2). Workflow задаётся через `agent.instructions` + `/review` + ручной commit
  через `AGENTS.md` commit-prefixes. `/done` (глобальный) ссылается на `/commit` —
  это связь «без якоря», пока локальный `/commit` не появится или `/done` не
  адаптируется.

#### MEDIUM

- **G-D-ECO-3: Local `notify.ts` — extension candidate to global notify.** В
  Phase A установлено, что глобального notify нет. dv-hub имеет **локальный TS-
  плагин** `notify.ts` (Linux `notify-send` на `session.idle`). Это прямой
  extension-candidate на «global notify kernel + local transport sinks» (по
  аналогии с `session-flush`). Mixed named-export без default → loader risk
  **`[проверить]`** (G-D-ECO-4).

- **G-D-ECO-4: runtime-neutral plugin behaviour unverifiable без loader proof.**
  `compaction.ts` (default export) — корректен по форме. `env-guard.ts`,
  `notify.ts` (named export без default) — форма расходится с `compaction.ts` и
  глобальным `session-flush.ts`. Загружаются ли они реально в runtime —
  **`[проверить]`**. Это **loader risk**, не доказанный runtime bug. Симптомы
  «плагин не работает» в логах/AGENTS не зафиксированы (а logs и нет — memory
  без event-log/replay, см. G-D-METH-3).

#### LOW

- **G-D-ECO-5: `commands/` vs `command/` naming variance.** dv-hub использует
  `.opencode/commands/` (множ.), SERPlux — `.opencode/command/`. Обе работают
  (или предполагаются работающими). Это локальная вариативность, **`[проверить]`**
  как OpenCode дискалудизированно открывает оба имени — релевантно для
  engineering-style-contract (стандартизация имени каталога команд).

### Severity cross-reference

| Severity | Count | IDs |
|---|---|---|
| HIGH | 7 | G-D-RUN-1 (auth 404), G-D-RUN-2 (D1 migration incomplete), G-D-RUN-3 (0 acc-tests/no verifier), G-D-METH-1 (verifier ❌ confirmed), G-D-METH-2 (reviewer w/o verifier), G-D-ECO-1 (global nerve isolation), G-D-ECO-2 (no /commit) |
| MEDIUM | 11 | G-D-RUN-4 (hono CVE), G-D-RUN-5 (node-server vuln no-fix), G-D-RUN-6 (CI no tests), G-D-RUN-7 (dep drift), G-D-METH-3 (memory compaction only), G-D-METH-4 (context-as-docs DoD), G-D-DOC-1 (ADR Zomro/Fornex), G-D-DOC-2 (README cmds), G-D-DOC-3 (VibeOS 6 ag.), G-D-ECO-3 (notify ext), G-D-ECO-4 (loader risk) |
| LOW | 5 | G-D-METH-5 (model-id namespace), G-D-DOC-4 (card log stale), G-D-DOC-5 (wrangler leftovers), G-D-DOC-6 (ecosystem-map absent), G-D-ECO-5 (commands/ naming) |

---

## what this changes in ecosystem plan

> Интерпретации для планирования апгрейдов волта. Без code-fix и без
> выдавания чего-либо за выполненное.

1. **dv-hub = isolated local-agent island; подтверждает pattern global kernel + local extensions.** Раньше isolation dv-hub от global nerve был гипотезой (карточка: closed-loop/verifier ❌, без упоминания `/loop`/`/done`). Теперь это **наблюдаемый факт** (zero references). Это подтверждает upgrade-planning-seed §176: часть проектов намеренно local-only, global `/done`/`/loop`/`verifier` нельзя считать «all-projects апгрейдом» — adoption-путь отдельный.

2. **T-072 получает evidence.** Задача `TASKS.md:59` «Глобальные researcher/reviewer — вынести из dv-hub в глобаль» подтверждается: dv-hub содержит локальные `reviewer.md` + `researcher.md` и не использует global `verifier.md`/`meta.md`. T-072 теперь обоснована наблюдаемой локальной реализацией ролей, не только логикой «kernel+extensions».

3. **`/done` must adapt docs-based memory.** Globальный `/done` (см. Phase C G2, `/done`→`/commit`, чеклист TASKS+VibeOS+active-context+`04-Memory/`) к dv-hub механически не применим: docs-based memory, нет локального `/commit`, нет TASKS.md формата волта. Это подкрепляет T-074 (redesign `/done` scope) — нужны либо явные preconditions «когда применимо», либо project-type-specific ветки `/done`.

4. **Acceptance surface precedes capability-routing / engineering-style-contract.** dv-hub — первый по road-map проект, кандидат на capability-routing (T-072 локальное→глобальное, model-routing есть). Но пока `tests/` пуст и verifier-loop не внедрён → **0 acceptance surface**. capability-routing и engineering-style-contract (Слой C: «когда reviewer / verifier») **не имеют объекта применения**. План апгрейда должен зафиксировать: построить acceptance/test surface **до** capability-routing, иначе router не к чему применять.

5. **Local `notify.ts` — extension candidate to global notify kernel.** Phase A установил, что глобального notify нет; Phase C показал, что локальные `notify.js` (SERP) и `notify.ts` (dv-hub) самостоятельны. dv-hub-вариант (TS, Linux `notify-send`, фильтр по `session.idle`) — конкретный extension-candidate для паттерна «global notify kernel + local transport sinks». Mixed named-export без default → loader risk **`[проверить]`** (G-D-ECO-4 blocker for proof-of-pattern).

6. **`meta` diff-based drift audit and ecosystem-map node — становятся релевантны.** Дрейф ADR (`compaction.ts` Zomro vs `architecture.md` Fornex, G-D-DOC-1), README-таблица (G-D-DOC-2), VibeOS agent-count (G-D-DOC-3), карточный лог (G-D-DOC-4) — это рассинхронизация 4 артефактов о dv-hub, ни одна из которых не пересекается с другими. Именно это обосновывает proposal meta-diff-based drift audit (auto-сверка `card ↔ repo ↔ AGENTS ↔ VibeOS`) и ecosystem-map-узел с фактическим состоянием (auth/tests/vulns/agents). Без такой инфраструктуры дрейф накапливается на простое.

---

## what must be fixed before any dv-hub upgrade

> Это **blockers / ordering constraints**, а не выполненные задачи. Code-fix
> предложений здесь нет; задачи не выданы за выполненные.

1. **Runtime health первой очереди.** Primary auth broken (G-D-RUN-1, Telegram
   `getMe` 404) и D1-миграция data-incomplete (G-D-RUN-2) — это рабочий, а не
   агентно-инфраструктурный долг, но весь agent-infra-upgrade-план
   (verifier/closed-loop/capability-routing) базируется на «проект живёт». Audio:
   сначала закрыть runtime-incident, потом overlay acceptance-loop. Security:
   high-severity Hono GHSA-458j-xx4x-4375 (HTML Injection `hono/jsx` SSR) +
   `@hono/node-server` path-traversal → перед переходом к PM2/Nginx VPS-runtime
   (target) dep upgrade & patch — blocking для Phase 0.

2. **Acceptance / test surface.** Ноль тестов ⇒ ноль acceptance-loop ⇒ verifier-
   pattern невозможно внедрить. Blocker для: closed-loop (`/loop` → `@verifier`
   → PASS/FAIL имеет `Nothing to verifier`), для engineering-style-contract Слой
   C «когда reviewer / verifier», для capability-routing по «типу операции».
   Должно предшествовать любой verifier-injection.

3. **Loader proof (plugin export contract).** Mixed default/named exports в
   `.opencode/plugins/` (`compaction.ts` default; `env-guard.ts`, `notify.ts`
   named без default) — без явного loader-contract (default-only? named? both?)
   невозможно утверждать, что env-guard и notify реально загружаются. **Не bug
   пока не доказано;** `[проверить]` — но без ответа verifier/closed-loop не
   построить: env-guard критически относится к security-gate. Blocker:
   зафиксировать loader-контракт как artifact перед любым plugin-harness.

4. **Docs reconciliation.** ADR drift Zomro↔Fornex (G-D-DOC-1) — это stable
   memory-drift (persistent-context противоречит canon). README-таблица команд
   (G-D-DOC-2), VibeOS 6-агентов (G-D-DOC-3), карточный лог stalled с 2026-06-30
   (G-D-DOC-4). Это blocker **не для code**, а для **source-of-truth**: любая
   upgrade-задача базируется на карточке/INDEX/VibeOS — продолжать на дрейфе —
   умножать дрейф. Должно быть сделано одним проходом reconcile (отдельная
   задача волта, не mix with agent-infra-apgрейдом).

5. **Reviewer / verifier decision.** Есть локальный `reviewer` (quality); нет
   `verifier` (acceptance); global `verifier.md` существует, но не подключён.
   Перед closed-loop-апгрейдом нужно **explicit decision**: (a) ввести локальный
   `verifier.md` в dv-hub по образцу global, (b) принудительно подключить global
   `verifier` через `/loop` (т.е. нарушить isolation), (c) держать hybrid (local
   reviewer + global verifier через global `/loop`). Без explicit выбора
   closed-loop внедряется неопределённо.

6. **Explicit global nerve adoption decision.** `G-D-ECO-1` (isolation) — это
   структурный факт, не bug, но upgrade-plan обязан зафиксировать explicit
   policy: какие проектам подключают global nerve (`/loop`, `/done`, `verifier`,
   `meta`, `session-flush`), какие остаются local-only island. Без этого решения
   «T-060s/T-059 global verbalizer adoption» применительно к dv-hub
   автоматически — а его runtime не приспособлен (memory-docs-based, `/commit`
   нет, `/done` чеклист не applicable).

---

## inspected paths (read-only)

**Vault (Layer 1):** `03-Projects/dv-hub.md`, `00-INDEX.md`, `VibeOS.md`,
`TASKS.md:59-61` (T-072, T-073, T-074 references), `06-Audits/2026-08-02-upgrade-
planning-seed.md`, `06-Audits/2026-08-03-serplux-phase-c-audit.md`,
`06-Audits/2026-08-02-vibecoding-layer-audit.md` (по ссылке).

**dv-hub repo (Layer 2):**
- `/home/rudra/Projects/dv-hub/opencode.json` (140 строк, не `.jsonc`)
- `/home/rudra/Projects/dv-hub/AGENTS.md` (9.4 KB)
- `/home/rudra/Projects/dv-hub/README.md` (13 KB)
- `/home/rudra/Projects/dv-hub/package.json`, `tsconfig.json`, `vite.config.ts`,
  `jest.config.js`, `wrangler.toml`, `wrangler.jsonc`, `wrangler.example.toml`,
  `ecosystem.config.cjs`, `.env.example`, `.gitignore`, `.gitmodules`
- `/home/rudra/Projects/dv-hub/.opencode/`: `agents/{plan,build,reviewer,researcher,infra}.md`,
  `commands/{morning,spec,review,hygiene,sync-context,sync-context-self,sync-task}.md`,
  `plugins/{compaction,env-guard,notify}.ts`, `package.json`, `node_modules/`
- `/home/rudra/Projects/dv-hub/docs/`: `architecture.md`, `infra-runbook.md`,
  `known-issues.md`, `product-vision.md`, `roadmap.md`, `glossary.md`,
  `backend-conventions.md`, `mirotalk-setup.md`, `audit/audit-2026-07-21.md`
- `/home/rudra/Projects/dv-hub/migrations/`: `0001_initial_schema.sql` …
  `0006_simplify_roles.sql` (6 файлов)
- `/home/rudra/Projects/dv-hub/tests/` (**пуст**)
- `/home/rudra/Projects/dv-hub/src/lib/auth.ts`, `src/routes/api.ts` — только
  выборочный grep по релевантным ключевым словам (`telegram`, `404`, `dashboard`)
- `/home/rudra/Projects/dv-hub/.github/` — **отсутствует** (подтверждено)
- `git log --oneline -10`, `git log -1 --format=%ci` (последняя активность
  2026-07-25)

**Global nerve (Layer 2, для проверки изоляции):**
`/home/rudra/.config/opencode/agent/{meta,verifier}.md`,
`/home/rudra/.config/opencode/command/{done,loop}.md`,
`/home/rudra/.config/opencode/plugins/session-flush.ts`. Каталога `subagent/` нет
(см. Phase C).

**Команды, исполненные read-only:** `ls`, `find`, `head`, `grep`/`rg`, `git log`,
`npm test` (для подтверждения exit-1), `npm audit` (для подтверждения CVE). Ни
один файл в `dv-hub` или global nerve не правлен. Ничего не закоммичено.

---

## closing note — read-only / no edits

Этот аудит — **исключительно read-only**: единственный изменённый/созданный файл —
сам `2026-08-03-dv-hub-phase-d-audit.md`. `VibeOS.md`, `02-Methods/`, `04-Memory/`,
`TASKS.md`, `00-INDEX.md`, карточка `03-Projects/dv-hub.md`, остальные `06-Audits/*`,
репозиторий `dv-hub`, и global nerve `~/.config/opencode/` — **не тронуты**.
Коммита нет. Code-fix предложений нет; ничего не выдано за выполненное.
Неподтверждённые runtime claims помечены `[проверить]`; loader-risk **не** назван
доказанным bug.