---
type: Audit
title: SERPlux — Phase C read-only audit (боевой коммерческий проект)
date: 2026-08-03
status: open
scope: Сверка декларации волта (карточка, INDEX, VibeOS) с фактической агентной
  инфраструктурой `/home/rudra/Projects/serp` и глобальным nerve
  (`~/.config/opencode/`). Только чтение. Факт отделён от интерпретации.
sources:
  - 03-Projects/SERPlux.md
  - 00-INDEX.md
  - VibeOS.md
  - /home/rudra/Projects/serp/.opencode/**, opencode.json, AGENTS.md, docs/, TASKS.md, verify.sh, .github/workflows/ci.yml
  - /home/rudra/.config/opencode/** (global nerve)
  - 06-Audits/2026-08-02-vibecoding-layer-audit.md
tags: [audit, phase-c, serplux, read-only, agent-infra, global-nerve]
---
# SERPlux — Phase C audit (2026-08-03)

> Первая чистая Фаза C. Read-only: репозиторий SERPlux и глобальный nerve не
> правились, существующие файлы волта не тронуты, коммита нет. Факт отделён от
> интерпретации: `declared` — только волт; `observed` — только чтение файлов;
> `confirmed gaps` — подтверждённые расхождения и неподтверждённые области
> (`[проверить]`); `what this means for upgrade planning` — интерпретации для
> плана, без немедленных code-fix. Карточка проекта: [[03-Projects/SERPlux|SERPlux]].
> Смежный аудит: [[06-Audits/2026-08-02-vibecoding-layer-audit]].

---

## declared

### Слой 1 — что заявлено в волте про SERPlux

Источник: `03-Projects/SERPlux.md` (актуально на 2026-07-03), `00-INDEX.md`,
`VibeOS.md`.

#### Архитектурная роль проекта

- **Продукт SERP Factory** — первый продукт «производственной линии» развёртываемых
  продуктов по поисковой выдаче (`SERPlux.md:9-12`).
- **Стек:** Python 3.11+ / requests / gspread / FastAPI / DeepSeek (через Zen) /
  SQLite / Docker (`SERPlux.md:5`).
- **Статус:** Core ✅, Docker ✅, Deploy ✅; интерфейс = Google Sheets; Web UI
  ⏸ (ADR 2026-07-02); 111/111 тестов зелёные (`SERPlux.md:13,46`).
- **FLAT layout:** все `.py` в корне, `src/` нет и не будет (`SERPlux.md:16`).
- **Провайдер:** OpenCode Zen (primary) + DeepSeek (labeler); сервер с собственным
  доменом (`SERPlux.md:19-20`).
- В `00-INDEX.md:27` и `VibeOS.md:231,236` закреплён как «первый продукт SERP
  Factory», статус ✅ active.

#### Агенты (заявлено, `SERPlux.md:62-69`)

| Агент | Mode | Модель | Назначение | edit |
|---|---|---|---|---|
| build | primary | opencode-go/kimi-k2.7-code | Основная разработка, коммит через `/commit` | allow |
| plan | primary | opencode-go/glm-5.2 | Планирование, анализ, делегирование build (`task: build allow`) | deny |
| collector-dev | subagent | opencode-go/kimi-k2.7-code | topvisor.py, collector.py | allow |
| reviewer | subagent | opencode-go/glm-5.2 | PASS/FAIL верификация контрактов | deny |
| ui-dev | subagent | opencode-go/kimi-k2.7-code | Google Sheets UI (Apps Script) | allow |
| infra-dev | subagent | opencode-go/qwen3.7-plus | Docker, deploy, сервер | allow |

- ui-dev: bash `python*, curl*, cat*, ls*`; прочее — ask (`SERPlux.md:76`).
- infra-dev: bash `docker*, python*, nginx*, certbot*, systemctl*, cat*, ls*, curl*`;
  прочее — ask (`SERPlux.md:84`).
- Всего **6 агентов** (2 primary + 4 subagent).

#### Команды-пайплайны (заявлено, `SERPlux.md:92-98`)

| Команда | Агент | Что делает |
|---|---|---|
| `/commit` | build (deepseek-v4-flash, subtask) | Коммит с conventional message; тесты — через commit-guard |
| `/interface` | ui-dev | Google Sheets UI: Apps Script, лист «Настройки», webhook |
| `/container` | infra-dev | Dockerfile + docker-compose |
| `/deploy` | infra-dev | Деплой на сервер: проверка, обновление, proxy, SSL |
| `/dream` | build | Финальный memory-flush сессии в docs/ |

Всего **5 команд** (`VibeOS.md:349` подтверждает).

#### Методы (заявлено, `SERPlux.md:104-112`; `00-INDEX.md:50-58`)

| Метод | Статус | Основание (по волту) |
|---|---|---|
| closed-loop | ✅ | `/loop` создан (глобальный), зависит от `@verifier` |
| verifier-pattern | ✅ | `verifier.md` создан (GLM-5.2), PASS/FAIL верификация активна |
| context-as-docs | ✅ | docs/contracts.md, decisions.md, ui-spec.md, techdebt.md, progress.md |
| distill-pattern | ✅ | `/interface`, `/container`, `/deploy` — команды-пайплайны |
| memory-management | 🟡 | compaction.js: flush summary в docs/decisions.md + persistent-context; `/dream` |
| model-routing | ✅ | build/collector/ui = kimi-k2.7-code; plan/reviewer = glm-5.2; infra = qwen3.7-plus |
| multi-agent-pipeline | ✅ | 2 primary + 4 subagent, команды через `.opencode/command/` |

#### Плагины (заявлено, `SERPlux.md:117`)

`env-guard.js · notify.js · compaction.js · commit-guard.js` — 4 локальных плагина.

#### Прочее заявленное

- memory-management 🟡: flush-протокол в AGENTS.md + compaction.js + `/dream`
  (`SERPlux.md:110`, лог `2026-07-03`).
- VibeOS (`VibeOS.md:312-365`) подтверждает: 5 команд, plan→build делегирование
  через task-tool, FLAT layout, мультиклиентность, плагины env-guard/notify/
  compaction (SERP+dv-hub) и commit-guard (только SERP).

---

## observed

### Слой 2 — фактическое чтение `/home/rudra/Projects/serp` (read-only)

#### Структура `.opencode/`

- Каталог **`.opencode/agents/`** (множ. число) — НЕ `.opencode/agent/` и НЕ
  отдельный `subagent/`. Все агенты в одном каталоге; режим `subagent` задаётся в
  frontmatter каждого файла, не каталогом. Аналогично dotfiles-паттерну (где primary
  в `agent/`, subagents в `subagent/`) НЕ применяется — SERP уплощает.
- `ls .opencode/`: `agents/`, `command/`, `plugins/`, `package.json`, `node_modules/`,
  `package-lock.json`, `.gitignore`. **Каталога `subagent/` нет.** **Каталога
  `memory/` нет** (memory живёт в `docs/`).
- `package.json`: только `{ "dependencies": { "@opencode-ai/plugin": "1.15.7" } }`
  (без `"type": "module"`).

#### `opencode.json` (33 строки, не `.jsonc`)

- `$schema`, `lsp: true`, `default_agent: "build"`.
- `permission.edit: allow`, `permission.webfetch: allow`.
- `permission.bash`: `*` → ask; allow для `git status/diff/log`, `ls`, `cat`,
  `python -m pytest`, `python *`, `git push` → ask, `rm *` → ask.
- **`agent.build` объявлен inline** (`mode: primary`, `model: kimi-k2.7-code`,
  `temperature: 0.1`, `steps: 30`, `permission.task: { "*": "allow" }`). Файла
  `.opencode/agents/build.md` НЕТ — build живёт только в `opencode.json`.
- Никакие другие агенты в `opencode.json` не объявлены — все остальные в
  `.opencode/agents/*.md` (auto-discovery по имени файла).

#### Фактические агенты `.opencode/agents/*.md`

| Файл | mode | model | temp | steps | edit | bash | task | webfetch |
|---|---|---|---|---|---|---|---|---|
| `plan.md` | primary | glm-5.2 | 0.1 | 20 | deny | deny | `build: allow` (только build) | — |
| `collector-dev.md` | subagent | kimi-k2.7-code | 0.1 | — | allow | `*`=ask, `python*`/`cat*`=allow | — | allow |
| `reviewer.md` | subagent | glm-5.2 | 0.1 | — | deny | `*`=deny, `git diff*`/`grep*`/`cat*`=allow | — | — |
| `ui-dev.md` | subagent | kimi-k2.7-code | 0.2 | 25 | allow | `*`=ask, `python*`/`cat*`/`ls*`/`curl*`=allow | — | — |
| `infra-dev.md` | subagent | qwen3.7-plus | 0.1 | 15 | allow | `*`=ask, `docker*`/`docker compose*`/`python*`/`cat*`/`ls*`/`curl*`/`systemctl*`/`nginx*`/`certbot*`=allow | — | — |

Подтверждено: 5 файлов + inline `build` в `opencode.json` = **6 агентов**, как в
карточке. Модели и режимы совпадают с заявленным.

Особенности vs карточки:
- **`reviewer.md` имеет bash allowlist** (`git diff`, `grep`, `cat`, остальное deny).
  Карточка (`SERPlux.md:67`) указывает только `edit: deny` и «PASS/FAIL верификация»;
  фактический bash-permission в карточке не описан.
- **`plan.md`**: `task` разрешает **только** `build` (`build: allow`), никто другой
  не делегируется. Совпадает с заявленным.
- **`build`** определён inline в `opencode.json` (temperature 0.1, steps 30,
  `task: { "*": "allow" }`) — в карточке/AGENTS не отмечено, что build — inline, а
  не файл.

#### Фактические команды `.opencode/command/*.md`

| Файл | agent | model | subtask | Назначение |
|---|---|---|---|---|
| `commit.md` | build | deepseek-v4-flash | true | git status+diff → conventional msg → git add+commit; тесты — commit-guard |
| `interface.md` | ui-dev | — | — | Apps Script меню, лист «Настройки», POST /run, статус/история |
| `container.md` | infra-dev | — | — | Проверка/улучшение Dockerfile + docker-compose |
| `deploy.md` | infra-dev | — | — | Чек-лист деплоя; «агенты локально, деплой пользователем через SSH» |
| `dream.md` | build | — | — | Flush в docs/decisions.md, progress.md, techdebt.md; НЕ коммитит |

Подтверждено: **5 команд**, совпадает с заявленным. `/dream` существует (в AGENTS.md,
`serp/AGENTS.md:90-97`, перечислены только `/interface`, `/container`, `/deploy` —
`/commit` и `/dream` в AGENTS-таблице **НЕ указаны**, но в `.opencode/command/` они
есть, а карточка их перечисляет).

Команды используют `!cat docs/...` (template-include) для подгрузки прогресса/техдолга.

#### Фактические плагины `.opencode/plugins/`

| Файл | export | обработчики событий |
|---|---|---|
| `env-guard.js` | `export const EnvGuard` (**named, no default**) | `tool.execute.before`, `tool.execute.before.webfetch` |
| `commit-guard.js` | `export const CommitGuard` (**named, no default**) | `tool.execute.before` |
| `compaction.js` | `export default async ({ directory }) =>` | `session.compact` |
| `notify.js` | `export default async ({ $ }) =>` | **`event:` (generic catch-all)** `async (input) =>` |

Замечания по плагинам (факт):
- **`commit-guard.js` содержит Syntax-ошибку в режиме ESM:** строка
  `const output = (result.stdout?.toString() || "") + ...` **переобъявляет**
  параметр `output` функции-обработчика (`async (input, output) =>`). Эмпирически
  подтверждено: загрузка модуля как ESM бросает `SyntaxError: Identifier 'output'
  has already been declared` (проверено через `node` на подтверждённом паттерне в
  `/tmp/opencode`). `node --check` на `.js` (CommonJS-режим без `"type":"module"`)
  ошибку **не** показывает — поэтому `node --check` сам по себе не доказывает
  загружаемость плагина.
- **`env-guard.js` и `commit-guard.js` используют named export** (`export const
  EnvGuard` / `export const CommitGuard`) **без `export default`**. Глобальный
  `session-flush.ts` и локальные `compaction.js`/`notify.js` используют `export
  default`. Совместим ли loader OpenCode с named-exports при отсутствии default —
  **`[проверить]`** (см. confirmed gaps).
- **`notify.js` использует единый обработчик `event:`** (catch-all) вместо
  точечных ключей (`session.idle`, `task.done`…), как в `session-flush.ts`. Является
  ли `event` валидным ключом OpenCode Plugin API — **`[проверить]`**.

#### `AGENTS.md` (проектный, `serp/AGENTS.md`, 155 строк)

- Закрепляет стек, FLAT layout, контракты модулей, секреты только в `.env`, flush-
  протокол (дописывать в `docs/decisions.md`), язык (рус. для общения/комментариев,
  англ. для кода/коммитов).
- Команды разработки: `python -m pytest -v` (АС заявляет «все 224 теста»), `docker
  compose up -d`, `./verify.sh`, `./backup_db.sh`, `bash -n`.
- Таблица агентов (`AGENTS.md:81-88`) совпадает с карточкой и с фактическими файлами.
- **Таблица команд (`AGENTS.md:90-97`) перечисляет только `/interface`, `/container`,
  `/deploy`** — `/commit` и `/dream` в ней отсутствуют, хотя физически есть в
  `.opencode/command/`.

#### docs/ (read-only)

- `ls docs/`: 20 файлов, включая `contracts.md`, `decisions.md` (97 KB — активный
  ADR-лог с записями от 2026-07-02 до 2026-08-03), `progress.md` (96 KB),
  `techdebt.md` (30 KB), `ui-spec.md` (41 KB), `topvisor-api.md`,
  `deploy.md`, `infra-testing.md`, `verification.md`, `CANON.md`,
  `labeling_canon.md`, `onboarding-client.md`, `release-1.0.md`, `roadmap-2.0.md`,
  `report_layout.md`, `user-guide.md`, `user-guide-v1.md`, `audit_2026-07-10.md`,
  `review_2026-08-02_labeling-cache-and-quality.md`.
- **Отдельного файла `adr/` или `ADR-NNN` протокола нет** — ADR живут как `## ADR`
  секции внутри `docs/decisions.md` (подтверждено grep'ом: заголовки `## 2026-XX-XX
  — ADR: ...`).
- **`docs/verification.md`** описывает границу авто/ручной проверки: GitHub Actions
  CI (`pytest -v` — там заявлено «172 теста»), shellcheck, `verify.sh` на сервере.
- **Каталога `.opencode/memory/` нет** — memory адресуется в `docs/`, не в
  `.opencode/memory/`.

#### Прочее фактическое

- `verify.sh` (7.4 KB), `backup_db.sh`, `deploy.sh` — shell-скрипты в корне.
- `tests/`: 14 `test_*.py` файлов; `grep -rhoE "^(async )?def test_" tests/*.py` =
  **94 определения тестов**.
- `.github/workflows/ci.yml` существует (CI: pytest + shellcheck).
- `TASKS.md` в корне SERP (локальный трекер, не волтовский).
- Корень содержит БД `serplux.db` (9.4 MB) и 2 бэкапа (`.bak.*`) — БД в репо-дереве
  (но в `.gitignore`-статусе не проверялось read-only; **`[проверить]`**).
- `migrate.py` (36 KB), `labeler.py` (23 KB), `webhook.py` (33 KB), `reporter.py`
  (18 KB), `storage.py` (45 KB) — крупные модули; `apps_script.gs` (111 KB).

### Слой 2 — фактическое чтение global nerve `~/.config/opencode/`

- `agent/`: `meta.md` (`mode: subagent`, model glm-5.2, edit allow, bash
  ask+allowlist git*/cat/ls/grep, webfetch allow), `verifier.md` (`mode: subagent`,
  model glm-5.2, edit deny, webfetch deny, bash deny + allowlist `git diff/log`,
  `npm run ci`, `npm test*`, `./venv/bin/python -m pytest*`; возвращает `VERDICT:
  PASS/FAIL`).
- **Каталога `subagent/` в global nerve НЕТ** — оба глобальных агента живут в
  `agent/` с `mode: subagent` в frontmatter.
- `command/`: `done.md` (model deepseek-v4-flash, **без поля `agent`**; чеклист:
  TASKS → волт-описание → VibeOS → active-context → `/commit`), `loop.md`
  (`agent: build`, arg1=goal, arg2=ci command; шаги: implement → invoke @verifier →
  фиксить по списку → PASS → STOP; HARD STOP после 5 циклов).
- `plugins/`: `session-flush.ts` (`export default`; слушает `file.edited` и
  `session.idle`; копит Set изменённых путей; при idle дописывает в
  `<directory>/04-Memory/session-log/<date>.md` секцию `## HH:MM:SS — file.edited
  flush`; **Агентов НЕ вызывает** — дословно в комментарии).
- `opencode.jsonc`: только `$schema` (минимальный).
- `AGENTS.md`: 1 байт (пустой маркер).
- **Глобального `notify`-плагина или `notify`-команды НЕТ** (подтверждает Фаза A).
- **Глобальной `commit`-команды НЕТ** (только проектная в
  `OpenCode-Vault/.opencode/command/commit.md` — см. Фаза A). В SERP `/commit`
  определён **локально** (`serp/.opencode/command/commit.md`).

---

## confirmed gaps

> Только подтверждённые расхождения между `declared` и `observed`, либо
> **неподтверждённые области** (помечены `[проверить]`). Без додумывания.

### G1. `reviewer` (локальный) ≠ `verifier` (глобальный) — карточка их смешивает

- Карточка (`SERPlux.md:67`) и `00-INDEX.md` заявляют `verifier-pattern ✅` через
  локального **`reviewer`** («PASS/FAIL верификация контрактов»).
- Фактически **локального `verifier.md` в SERP нет** (`ls .opencode/agents/` — нет
  `verifier.md`). Локальный `reviewer.md` — это code-review (контракты, утечки
  ключей, идемпотентность, зоны ответственности), edit deny, bash allowlist
  (`git diff/grep/cat`).
- Глобальный `~/.config/opencode/agent/verifier.md` — это **acceptance verifier**
  (DoD, тест-команда, `VERDICT: PASS/FAIL`), edit/bash/webfetch deny с узким bash
  allowlist (`git diff/log`, `npm test`, `pytest`).
- `/loop` (`~/.config/opencode/command/loop.md`) на шаге 2 вызывает `@verifier` —
  то есть closed-loop в SERP опирается на **глобального verifier**, а не на
  локального `reviewer`. Карточка прямо пишет «`/loop` создан (глобальный),
  зависит от `@verifier`» — но неявно приписывает verifier-pattern **локальному
  `reviewer`**, что не подтверждается файлами: это разные роли (quality vs
  acceptance), и за closed-loop отвечает глобальный, а не локальный.
- Подтверждено: `verifier-pattern ✅` в карточке фактически означает «глобальный
  `verifier.md` + `/loop`», а `reviewer` — отдельная локальная роль, не та же
  сущность.

### G2. `/loop` и `/done` — глобальные; SERP не имеет собственных. Routing `build` resolves локально

- `/loop` и `/done` существуют **только в global nerve** (`~/.config/opencode/command/`),
  не в `serp/.opencode/command/`. Карточка заявляет closed-loop ✅ через «`/loop`
  создан (глобальный)» — подтверждено: команда глобальная.
- `/loop` указывает `agent: build`. В SERP `build` определён **inline в
  `opencode.json`** (`mode: primary`, `permission.task: { "*": "allow" }`) →
  команда резолвится к локальному build. На глобальном уровне файла
  `agent/build.md` нет (см. Фаза A, tension `build`↔`builder`) — но в контексте SERP
  это не проблема, т.к. локальный `build` есть.
- `/done` НЕ объявлен ни в карточке SERP, ни в `serp/AGENTS.md`, ни в локальном
  `.opencode/command/`. `/done` волт-заточен (TASKS.md, VibeOS, 04-Memory,
  `/commit`) и **ссылается на `/commit`**, который глобально отсутствует (Фаза A)
  — но в SERP `/commit` определён **локально**. Таким образом, в контексте SERP
  цикл `/done` формально не разорван (локальный `/commit` есть), но SERP не заявлен
  пользователем `/done`.
- **Routing-конфликта глобального/локального в SERP для `/loop`/`/done` не
  подтверждено** — наоборот, локальный `build` покрывает ссылку глобального
  `/loop`. Но неделимый контракт «loop → build → verifier → finalize»
  нигде не enforced на runtime-уровне (см. G7).

### G3. `commit-guard.js` — подтверждённая Syntax-ошибка (ESM) и не-`default` export

- Строка `const output = ...` переобъявляет параметр `output` функции
  `tool.execute.before` (`async (input, output) =>`). Эмпирически: ESM-загрузка
  бросает `SyntaxError: Identifier 'output' has already been declared`.
- Дополнительно `export const CommitGuard` — **named export без `export default`**
  (как и у `env-guard.js`), тогда как `compaction.js`/`notify.js`/глобальный
  `session-flush.ts` используют `export default`.
- Карточка (`SERPlux.md:117`) и AGENTS заявляют `commit-guard.js` как рабочий
  CI-гейт. Фактически: либо плагин не загружается (если loader требует default),
  либо загружается с ошибкой (ESM SyntaxError). **`[проверить]`** как именно
  OpenCode грузит `.opencode/plugins/*.js` (default-only или любой export) — но
  SyntaxError при ESM-оценке модуля подтверждён.
- `env-guard.js` той же схемой (`export const EnvGuard`, без default) — тот же
  вопрос совместимости; собственно синтакс-ошибки в нём не найдено.

### G4. `notify.js` — generic `event:` handler; валидность ключа `[проверить]`

- Глобальный `session-flush.ts` использует точечные ключи (`"file.edited"`,
  `"session.idle"`). `notify.js` возвращает `{ event: async (input) => ... }` —
  единый catch-all. Поддерживает ли OpenCode Plugin API ключ `event` как catch-all
  — **`[проверить]`**. Если нет — notify не сработает.

### G5. `session-flush` (глобальный) против SERP: целевой путь `04-Memory/` не существует в репо

- Глобальный `session-flush.ts` пишет в `<directory>/04-Memory/session-log/<date>.md`.
- В SERP **нет каталога `.opencode/memory/` и нет `04-Memory/`** — memory адресуется
  в `docs/` (`decisions.md`, `progress.md`). Если глобальные плагины применяются ко
  всем проектам автоматически, `session-flush` создал бы в репо SERP каталог
  `04-Memory/session-log/` (вне `docs/`), конфликтующий с SERP-паттерном memory.
- **`[проверить]`**: применяются ли глобальные плагины auto ко всем проектам, и
  создаются ли stray `04-Memory/` каталоги в SERP. Карточка `memory-management 🟡`
  описывает только локальный `compaction.js` (flush в `docs/decisions.md`), не
  упоминает глобальный `session-flush` — возможный двойной/конкурирующий flush.

### G6. `compaction.js` — устаревший persistent-context (`ui-dev ⏸ paused`)

- `compaction.js` PERSISTENT_CONTEXT содержит «ui-dev (⏸ paused)», что противоречит
  актуализированной карточке (`SERPlux.md:73`: «ui-dev — активен», Web UI паузится,
  а не сам агент) и `AGENTS.md`. Persistent-context, инжектируемый при каждой
  компакции, **разошёлся с карточкой**: риска дрейфа между «что агент помнит после
  компакции» и «актуальное состояние».
- Подтверждено чтением `compaction.js:53` vs `SERPlux.md:73`.

### G7. Число тестов: расхождение между артефактами (drift)

- Карточка (`SERPlux.md:46`): **111/111**.
- `serp/AGENTS.md:56`: «все **224** теста».
- `docs/verification.md`: CI pytest «**172** теста».
- `serp/TASKS.md` (T-001 результат): «Все **95** тестов зелёные».
- `grep def test_` по `tests/*.py`: **94 определения**.
- Реальное pytest-число без прогона не подтверждается (могут быть parametrize) —
  но **5 разных цифр в 5 разных артефактах** — подтверждённый дрейф, карточка устарела
  относительно фактического состояния тестов.

### G8. `infra-dev.md` / `container.md` ссылаются на несуществующие `templates/` и `static/`

- `infra-dev.md` anti-goals: «НЕ трогай код приложения: .py файлы, `templates/`,
  `static/`». `container.md` команда: «Убедись что `templates/` и `static/`
  копируются в образ».
- В корне SERP (read-only `ls`) **каталогов `templates/` и `static/` нет** — Web UI
  ⏸ (ADR 2026-07-02), FLAT layout. Ссылки устарели/заведомо неактуальны.

### G9. AGENTS-таблица команд неполна

- `serp/AGENTS.md:90-97` перечисляет только `/interface`, `/container`, `/deploy`.
  `/commit` и `/dream` физически есть в `.opencode/command/` и в карточке
  (`SERPlux.md:92-98`), но в AGENTS-таблице отсутствуют. Подтверждённый локальный
  дрейф документации.

### G10. Engineering-style-contract / capability-routing — не подтверждены

- В SERP нет файла/секции engineering-style-contract (общие инженерные конвенции),
  нет capability-routing policy. Есть `docs/contracts.md` (контракты модулей,
  сигнатуры) и `docs/CANON.md` (канон раскладки отчёта) — это предметные контракты,
  **не** кросс-языковой engineering-style contract из предложений Фазы A.
- Карточка/INDEX не заявляют capability-routing — его и нет. Готовность к нему —
  **не подтверждена**: model-routing есть (3 модели), но layer B/C capability-
  routing — отсутствует как артефакт.

### G11. Глобальные сущности, применимые к SERP — сводка confirmed vs `[проверить]`

| Сущность | exists globally | SERP ссылается/использует | статус |
|---|---|---|---|
| `agent/meta.md` | да | не упоминается в карточке/AGENTS | глобально доступен как @meta; фактическое использование SERP — не подтверждено |
| `agent/verifier.md` | да | `/loop` шаг 2 «invoke @verifier» — **косвенно, через глобальный `/loop`** | подтверждено (используется глобальным `/loop`, не локальным `reviewer`) |
| `command/loop.md` | да | карточка: «`/loop` создан (глобальный)» | подтверждено: команда глобальная |
| `command/done.md` | да | НЕ заявлен в SERP | `/done` не используется SERP (не подтверждено) |
| `plugins/session-flush.ts` | да | НЕ упоминается в карточке; SERP-эквивалент — `compaction.js` | **`[проверить]`** применяются ли глобальные плагины к SERP и создают ли stray `04-Memory/` (G5) |
| `notify` (команда/плагин) | **нет глобально** | SERP имеет локальный `notify.js` | подтверждено: глобального notify нет; локальный — `notify.js` (см. G4) |
| `/commit` | нет глобально | SERP имеет **локальный** `commit.md` | подтверждено; `/done` ссылается на `/commit`, который глобально отсутствует, но локально в SERP есть |

---

## what this means for upgrade planning

> Интерпретации для планирования апгрейдов. Без code-fix на этом шаге.

1. **Развести `reviewer` и `verifier` как раздельные роли в карточке/методах.**
   Сегодня `verifier-pattern ✅` приписывается локальному `reviewer`, но closed-loop
   (`/loop`) верифицирует через **глобального** `verifier`, а `reviewer` — локальная
   quality-роль. Планировать: либо локальный `verifier.md` (acceptance) в SERP, либо
   явная декларация, что closed-loop намеренно использует глобальный verifier. Это
   уточняет готовность к capability-routing (Слой C: «когда reviewer / verifier»).

2. **`commit-guard.js` и `env-guard.js`: формат экспорта и здравость loader-контракта
   — первичный кандидат на стабилизацию перед любым verifier/loop-harness.** Подтверждена
   Syntax-ошибка в `commit-guard.js` (переобъявление `output`) и универсальный паттерн
   named-export без default у двух плагинов. Пока неясно, как loader OpenCode грузит
   `.opencode/plugins/*.js` (default-only? named?), план должен зафиксировать
   loader-контракт раньше code-fix-ов — иначе «/commit тесты — через commit-guard»
   (карточка + `commit.md`) формально невыполнимо, а об этом не известно.

3. **`notify.js` catch-all `event` и `session-flush`-vs-`compaction` — кандидат на
   глобальную plugin-policy (Слой: global roles + local specializations).** Локальный
   `notify.js` расходится с точечным паттерном `session-flush.ts`; «глобальный notify
   отсутствует» (Фаза A) + «локальные notify везде свои» — повторяет тезис Фазы A о
   «глобальном vs локальном плагинах». Планировать унификацию catch-all vs точечных
   ключей и решение, что Maurщий flush (глобальный `session-flush`) делает в проекте,
   у которого собственная memory-модель (`docs/`, а не `04-Memory/`) (G5).

4. **`/done` не пригоден к SERP без адаптации.** Его чеклист целит в волт
   (`02-Methods/`, `04-Memory/active-context.md`), а SERP memory — в `docs/` и
   локальный `TASKS.md`. Если `/done` планируется к применению в SERP (или как часть
   Session🐚-loop), нужна либо общая абстракция (`/done` + `/dream` для docs-based
   проектов), либо явное разделение «волтовский `/done`» vs «проектный flush». Это
   связка с memory-management (Фаза A tension #4, #15).

5. **Routing между слоями для SERP фактически работает через локальный `build`, но
   contest-gate `verify=PASS → finalize` не enforced.** `/loop` → @verifier → STOP
   при PASS — это командный протокол, не runtime-gate. Планировать harness loop/done
   имеет смысл только после G2/G3 (loader-контракт) — иначе harness будет опираться на
   плагин, который может не загружаться.

6. **Drift артефактов (G6, G7, G8, G9) — Indicate карточного обновления, не code-fix.**
   `compaction.js` persistent-context (`ui-dev paused`), число тестов (111/224/172/95/94),
   `templates/static` в контейнере, AGENTS-таблица команд — это документационный дрейф.
   Планировать сверку карточки/AGENTS/docs с фактическим репо как отдельную задачу
   (после Фазы C); не путать с agent-infra-апгрейдом. Source-of-truth drift само по
   себе риск для upgrade planning (на卡片ке принимаются решения).

7. **Готовность SERP к capability-routing / engineering-style-contract — низкая, но
   есть основания.** Имеется: model-routing (3 модели), plan/build split, локальный
   `reviewer` (quality) + доступ к глобальному `verifier` (acceptance), предметные
   контракты в `docs/contracts.md` + `CANON.md`. Отсутствует: layer A (общие
   инженерные конвенции), layer B (языковые runtime-conventions), layer C (routing
   policy по риску/типу операции). Планировать — layered introduction; SERP как
   «боевой проект» — подходящий полигон, но без skip-step G2/G3.

8. **`session-flush` (глобальный) против `compaction.js` (локальный) — needs policy
   decision, не просто фикс.** Это частный случай proposals Фазы A (tension #17 «global
   vs local plugins»): глобальный event-skeleton (`session-flush`) + локальная
   семантика memory (`compaction.js` → `docs/decisions.md`). Возможные направления:
   (a) отключить глобальный flush для docs-based проектов, (b) дать SERP локальный
   override, (c) унифицировать в глобальный event-log + локальные sinks. Решение —
   в roadmap, не в этом аудите.

9. **`build` как inline в `opencode.json` vs другие агенты как `.md` — структурная
   аномалия.** Все остальные агенты SERP — markdown-файлы с	auto-discovery; `build`
   — JSON-конфиг. Это не баг (OpenCode допускает), но при harness/routing-контрактах
   способствует ошибкам «build vs builder» типа Фазы A tension #2. Планировать:
   каноническое определение primary-агента (inline vs md) как часть engineering-
   style-contract.

---

## inspected paths (read-only)

**Vault (Layer 1):** `03-Projects/SERPlux.md`, `00-INDEX.md`, `VibeOS.md`,
`06-Audits/2026-08-02-vibecoding-layer-audit.md`.

**SERPlux repo (Layer 2):**
- `/home/rudra/Projects/serp/opencode.json` (нет `opencode.jsonc`)
- `/home/rudra/Projects/serp/AGENTS.md`, `TASKS.md`
- `/home/rudra/Projects/serp/.opencode/agents/{plan,reviewer,collector-dev,ui-dev,infra-dev}.md` (5 файлов; `build` — inline в `opencode.json`)
- `/home/rudra/Projects/serp/.opencode/command/{commit,interface,container,deploy,dream}.md` (5)
- `/home/rudra/Projects/serp/.opencode/plugins/{env-guard,commit-guard,compaction,notify}.js` (4)
- `/home/rudra/Projects/serp/.opencode/package.json`, `.opencode/.gitignore`
- `/home/rudra/Projects/serp/docs/` (20 файлов: `contracts.md`, `decisions.md`,
  `progress.md`, `techdebt.md`, `ui-spec.md`, `topvisor-api.md`, `deploy.md`,
  `infra-testing.md`, `verification.md`, `CANON.md`, `labeling_canon.md`,
  `onboarding-client.md`, `release-1.0.md`, `roadmap-2.0.md`, `report_layout.md`,
  `user-guide.md`, `user-guide-v1.md`, `audit_2026-07-10.md`,
  `review_2026-08-02_labeling-cache-and-quality.md`)
- `/home/rudra/Projects/serp/tests/` (14 `test_*.py`), `/home/rudra/Projects/serp/.github/workflows/ci.yml`
- `/home/rudra/Projects/serp/verify.sh`, `backup_db.sh`, `deploy.sh`

**Global nerve (Layer 2):** `/home/rudra/.config/opencode/agent/{meta,verifier}.md`,
`/home/rudra/.config/opencode/command/{done,loop}.md`,
`/home/rudra/.config/opencode/plugins/session-flush.ts`, `opencode.jsonc`, `AGENTS.md`.
(Каталога `subagent/` в global nerve НЕТ.)

## diff summary

- **Создан:** `/home/rudra/Projects/OpenCode-Vault/06-Audits/2026-08-03-serplux-phase-c-audit.md` (новый).
- **Не изменено:** код/конфигурация SERPlux, существующие файлы волта (`00-INDEX.md`,
  `TASKS`, `04-Memory/`, `VibeOS.md`, карточка SERPlux, Фаза A audit).
- **Не закоммичено.**

## ключевые confirmed gaps (кратко)

1. **G1** — `reviewer` (локальный) ≠ `verifier` (глобальный); карточка смешивает под
   `verifier-pattern ✅`.
2. **G2** — `/loop`/`/done` — глобальные; `/loop` резолвится к локальному `build`
   (inline в `opencode.json`), но `verify=PASS → finalize` не enforced.
3. **G3** — `commit-guard.js`: подтверждённая ESM Syntax-ошибка (переобъявление
   `output`) и named-export без `default` (как и `env-guard.js`); loader-поведение
   OpenCode — `[проверить]`.
4. **G4** — `notify.js` generic `event:` handler; валидность ключа — `[проверить]`.
5. **G5** — глобальный `session-flush` целит в `04-Memory/session-log/`, которого в
   SERP нет; риск stray-каталогов и конкурирующего flush с `compaction.js` —
   `[проверить]`.
6. **G6** — `compaction.js` PERSISTENT_CONTEXT устарел (`ui-dev ⏸ paused` вопреки
   карточке).
7. **G7** — число тестов расходится: карточка=111, AGENTS=224, verification.md=172,
   TASKS.md=95, `grep def test_`=94.
8. **G8** — `infra-dev.md`/`container.md` ссылаются на несуществующие `templates/`,
   `static/`.
9. **G9** — AGENTS-таблица команд неполна (нет `/commit`, `/dream`).
10. **G10** — engineering-style-contract / capability-routing не подтверждены в SERP.