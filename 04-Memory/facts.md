---
type: Fact Registry
title: Реестр фактов
description: Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения [проверить].
tags: [memory]
timestamp: 2026-08-04
---
# Реестр фактов

> Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения `[проверить]`.

## Профиль пользователя
- **Полное имя:** Max Rudra
- **Сокращения:** Rudra (внутренние контексты), mr (аббревиатура)
- **Роль:** вайбкодер, системный инженер, минималист, пермакультурщик
- **Язык:** русский (основной), терминал-нативный стек
- **GitHub:** [max-ai](https://github.com/max-ai)

## OpenCode

### Агенты
- **librarian** — агент командного центра. Режим: primary (default в opencode.json). Запускается без `/agent`. Области: мониторинг проектов, аудит, управление знаниями.
- Дочерние агенты не поддерживаются в агентской архитектуре OpenCode (только subagent в командах/скриптах).

### Конфигурация
- `opencode.json` — корневой конфиг: `default_agent: librarian`, `lsp: true`, `$schema`, модель `opencode-go/deepseek-v4-flash-free` (дефолт для субагентов).
- Модель librarian: `opencode-go/qwen3.7-plus` (сильная модель Go-подписки для дирижёра).
- Субагенты general/build/explore явно зафиксированы на Go-моделях (не наследуют от вызывающего).
- `steps` в агенте = число шагов агента (действий). `steps: 15` достаточно для задач командного центра.
- `doom_loop: allow` — разрешает recovery-промпты при повторах.
- `budgetTokens` — не включён в конфиг волта (не требуется для командного центра).

### Папки агентов и плагины
- Папки агентов: глобальные = `~/.config/opencode/agent/` (ед.ч.), SERPlux = `.opencode/agents/` (мн.ч.). Verifier и meta — глобальные субагенты, видны в проектах через мёрж (OpenCode свежей версии).
- `commit-guard` плагин = неотвратимый гейт на `tool.execute.before`.
- `session-flush` плагин (глобальный, `~/.config/opencode/plugins/`) — копит `file.edited`, при `session.idle` дописывает в `04-Memory/session-log/YYYY-MM-DD.md`. Детерминированный, агентов не вызывает.

### Права и система плагинов
- `permissions` в opencode.json — права доступа для агента (external_directory, bash, edit и т.д.).
- **Skills** — плагины-помощники (SKILL.md), подгружаемые при совпадении задачи; есть белый список путей.
- **Doom loop** — механизм обнаружения зацикливания: агент повторяет одни и те же действия → recovery-промпт.
- **Plugin SDK** (`@opencode-ai/plugin`) — Node.js SDK для создания плагинов с событиями и кастомными инструментами.
- **tool.execute.before** — штатный механизм OpenCode для перехвата инструментов ДО выполнения. Плагин может блокировать вызов (пример: commit-guard блокирует git commit если тесты падают). Это неотвратимый гейт на уровне рантайма.

### Методы (02-Methods/)
Документированы 7 приёмов вайбкодинга:
| Метод | Суть |
|-------|------|
| [[closed-loop]] | Итеративный цикл: план → действие → проверка |
| [[verifier-pattern]] | Проверка через отдельный скрипт/воркфлоу |
| [[context-as-docs]] | Контекстные файлы как документация для ИИ |
| [[distill-pattern]] | Сжатие/структурирование знаний в заметки |
| [[memory-management]] | Управление памятью сессии + файловая память |
| [[model-routing]] | Разные модели для разных шагов (дешёвая/fast → дорогая/точная) |
| [[multi-agent-pipeline]] | Специализированные агенты в цепочках с проверкой |
| [[tool-integration-pattern]] | Внешние API как детерминированные инструменты; «LLM думает, API делает» |

### Границы /loop (closed-loop)
- **Применим:** задачи с быстрой автоматической проверкой (тесты секунды-минуты) и чётким DoD
- **Не применим:** UI-задачи без автопроверки (Apps Script/Sheets), дорогая/долгая проверка, размытые критерии
- **SERPlux:** 111 pytest-тестов → /loop идеален для core-модулей; для Apps Script UI — не сработает, нужен другой механизм

### Внешние инструменты (tools/)
- **tools/telegram-capture/** — первый инструмент VibeOS (T-062, 2026-07-08). Telethon-скрипт для capture постов из @inbox_tools, классификация, маркировка реакциями. 39 pytest-тестов, Tor SOCKS5 proxy.
- **tools/ecosystem-map/** — второй инструмент VibeOS (T-069, 2026-07-13). Интерактивная карта развития экосистемы в стиле Pip-Boy Fallout. 468 постов → 36 навыков → 326 инструментов. 4 вкладки: НАВЫКИ/СПОСОБНОСТИ/ИНСТРУМЕНТЫ/ПРОЕКТЫ. CRT-эффекты, vanilla JS, фильтры. Запуск: `python3 -m http.server 8000` в tools/ecosystem-map/.
- **Telethon 1.44.0** — единственный живой MTProto-клиент для Python. Pyrogram архивирован (Dec 2024), не поддерживается. Telethon переехал на Codeberg (Feb 2026), 12k stars, MIT license. Выбор для tools/telegram-capture/.
- **Группа @inbox_tools** — открытая Telegram-группа Rudra для сбора постов с интересным софтом. Темы (topics): Приложения, Софт, Вайб, #General, Смарт, Графика, красота, сайтостроение (старое), Обучалки (старое), ИИ, Питонизм (очень старое).
- **Схема маркировки реакциями** (двухуровневая): 👍 ingested (обработан), 🤔 ошибка. Категории: 👨‍💻 dotfiles/Linux UX, 🔥 SERPlux, 🤝 dv-hub, 🏆 VibeOS/метод, 🎉 новый проект. Default для без категории: 👍.
- **EMOJI_MAP (ограничения Telegram)** — Telegram ограничивает доступные реакции (73 шт.). Старые эмодзи (📥⚠️🐧🤖🌐🧠🎯) НЕ доступны → заменены на 👍🤔👨‍💻🔥🤝🏆🎉. Перед использованием нового эмодзи проверять через `client.get_available_reactions()`.
- **tool-integration-pattern** — седьмой метод VibeOS (с 2026-07-07). «LLM думает, API делает». Реализация: tools/ директория, первый инструмент telegram-capture (T-062, внедрён ✅ 2026-07-08).
- **Имя Telegram-приложения** — DesktopWorkspaceManager (short name: manager). Имена «VibeOS Capture»/«vibeos» не прошли валидацию при создании: Telegram требует определённого формата имени приложения.
- **Telethon сам определяет серверы подключения**. Test config (149.154.167.40:443) и Production config (149.154.167.50:443) — дефолтные, явно указывать ip/hash не нужно.
- **Tor SOCKS5 proxy** (127.0.0.1:9050) — обход блокировки Telegram в регионе. Без proxy все DC timeout. Настроен в `.env` (`PROXY_HOST`/`PROXY_PORT`), передаётся в Telethon через python-socks. Критическая инфраструктура для capture.
- **Raw API Telethon** — высокоуровневый метод `send_reaction` НЕ существует в Telethon 1.44.0. Используется raw API: `SendReactionRequest` (из `telethon.tl.functions.messages`) + `ReactionEmoji(emoticon=...)` (из `telethon.tl.types`). Паттерн для будущих интеграций.
- **GetForumTopicsRequest** — импорт из `telethon.tl.functions.messages` (НЕ `channels`). Список тем форума форума получаемый через `client(GetForumTopicsRequest(...))`.
- **peer через get_input_entity** — для запросов raw API нужен `InputPeer`, не entity. Получение: `await client.get_input_entity(peer)` → `InputPeerChannel`/`InputPeerUser`. Передача entity напрямую вызывает ошибки.
- **Массовая маркировка → FloodWaitpenalty:** попытка поставить 584 реакции за один запуск привела к FloodWaitpenalty на ~4 часа от Telegram. 117/120 помечено в первых 4 батчах, далее процесс застопорился. Урок: НЕ маркировать больше ~30-50 постов за запуск. В будущем /capture берёт только новые посты (10-20), mark.py маркирует порциями. Старые посты добиваются постепенно.

### Окружение (direnv + venv)
- **direnv** (v2.37.1) — shell extension для автоматической активации окружения при входе в каталог проекта. Установлен системно (`/usr/bin/direnv`).
- **Паттерн:** в корне каждого Python-проекта — `.envrc` с `source .venv/bin/activate` (или `venv/bin/activate`). После создания/изменения .envrc — один раз `direnv allow`.
- **venv** — Python виртуальное окружение (`.venv/` в корне проекта). Изолирует зависимости. В .gitignore.
- **SERPlux** — эталон: `.envrc` + `venv/`, работает.
- **vault** — внедрено 2026-07-08: `.envrc` + `.venv/` в корне. Зависимости: telethon, python-dotenv, pytest.
- **Конвенция:** каждый новый Python-проект создаёт `.envrc` + `.venv/`, `direnv allow`, зависимости в venv. НЕ глобально.

## Проекты

### SERPlux — Phase C confirmed facts (2026-08-03)

> Подтверждённые факты по итогам read-only аудита
> ([[06-Audits/2026-08-03-serplux-phase-c-audit]],
> [[06-Audits/2026-08-03-serplux-phase-c-addendum]]). Только факты о
> состоянии проверки/инфры, без предложений и кандидатов.

- SERPlux использует docs-based memory (`docs/decisions.md`, `progress.md`,
  `techdebt.md` и др.), не `04-Memory/`; каталога `.opencode/memory/` и
  `04-Memory/` в репо нет.
- `build` определён inline в `opencode.json` (mode primary, model
  kimi-k2.7-code, `permission.task: { "*": "allow" }`); файла
  `.opencode/agents/build.md` нет. Остальные 5 агентов — auto-discovery
  `.md` файлы.
- Локальный `reviewer` (`.opencode/agents/reviewer.md`, quality-роль,
  edit deny, bash allowlist `git diff/grep/cat`) ≠ глобальный `verifier`
  (`~/.config/opencode/agent/verifier.md`, acceptance, VERDICT PASS/FAIL);
  `/loop` на шаге 2 вызывает глобального `@verifier`.
- `commit-guard.js` имеет подтверждённую ESM SyntaxError: `const output = ...`
  переобъявляет параметр `output` функции-обработчика `tool.execute.before`
  (`async (input, output) =>`); ESM-загрузка бросает
  `SyntaxError: Identifier 'output' has already been declared`. `node --check`
  в CommonJS-режиме ошибку не показывает.
- `notify.js` catch-all обработчик `event: async (input) => ...` —
  валидность ключа `event` как catch-all в Plugin API **остаётся
  непроверенной** (это стабильный факт о состоянии проверки, не утверждение
  runtime bug).
- `/commit` и `/dream` физически существуют в `.opencode/command/` и в
  карточке, но отсутствуют в таблице команд `serp/AGENTS.md:90-97`
  (перечислены только `/interface`, `/container`, `/deploy`).
- Число тестов расходится между артефактами и требует нормализации: test
  definitions (`grep def test_` по `tests/*.py`) = 94; documented suite
  claims: карточка 111, `serp/AGENTS.md` 224, `docs/verification.md` CI 172,
  `serp/TASKS.md` (T-001) 95; pytest total без прогона не подтверждается
  (parametrize, skip). Источники и назначение метрик различаются.

### Phase 1 / T-084 — plugin loader / compaction contract (2026-08-03)

> Стабильные факты по итогам gate Phase 1 (T-084). Только
> подтверждённое состояние, без предложений.

- Loader contract подтверждён по официальным docs/Plugin SDK: local plugin
  module (`plugins/*.{js,ts}`) допускает **named exports**; `export default`
  **не обязателен**; named plugin function как доля набора экспортов
  валидна.
- `event` catch-all — **канонический** hook key в Plugin API (catch-all
  обработчик событий); подтверждено по официальным docs/SDK.
- `session.compact` — **невалидный** hook key (не документирован в Plugin
  API). Документированный injection hook для compaction —
  `experimental.session.compacting` с сигнатурой `(input, output)` и
  доступом к `output.context`. `compaction.js` в SERPlux исправлен на
  документированный hook.
- В SERPlux исправлена ESM `SyntaxError` в `commit-guard.js`: локальная
  переменная `const output = ...` переобъявляла параметр `output`
  обработчика `tool.execute.before`. Статическая проверка загрузки
  проходит.
- Добавлен `scripts/check-plugins.mjs` в SERPlux: динамически импортирует
  JS/TS plugins, проверяет наличие named/default plugin function.
  Static (discovery) и runtime discovery checks проходят для актуального
  набора плагинов.
- `opencode debug config` проходит без plugin loading errors; headless
  `opencode serve` поднимается без plugin loading errors.
- **Live Bun import + hook fire в реальной agent session НЕ подтверждён**
  `[проверить]` — поэтому Phase 1/T-084 не считается полностью завершённой.

### Phase 1 / T-084 — live Bun smoke residuals (2026-08-03)

> Подтверждённые факты после live Bun import/registration smoke. Только
> подтверждённое состояние + explicit `[проверить]`.

- T-084 loader contract подтверждён docs/Plugin SDK + live Bun
  import/registration всех 4 SERPlux plugins (`env-guard`,
  `notify`, `commit-guard`, `compaction`).
- `experimental.session.compacting` зарегистрирован; function-level
  fire подтверждён (hook вызывается). Реальный compaction event
  session-dispatch остаётся `[проверить]`.
- `tool.execute.before` registration/fire подтверждены. env-guard
  исторически срабатывал в session-dispatch.
- Бывший gap `tool.execute.before.webfetch` был **неканоничен**
  (несуществующий hook key); исправлен в SERPlux: webfetch check
  перенесён внутрь catch-all `tool.execute.before`. Smoke
  allow/block прошёл.
- Commit-guard на реальном `git commit` и compaction на реальной
  compaction-сессии остаются **безопасно непротестированными**
  `[проверить]`.
- SERPlux changes в working tree, **uncommitted**.

### Модели субагентов — временно на бесплатных Zen (2026-08-04)

> Подтверждённые факты после смены моделей. Временно: экономим Go-кредиты.
> Возврат — по решению пользователя (связь T-048/T-049).

- По запросу пользователя все субагенты временно переведены с платных
  Go-моделей (`opencode-go/*`) на бесплатные модели OpenCode Zen
  (`opencode/*-free`).
- `~/.config/opencode/agent/meta.md`: `opencode-go/glm-5.2` →
  `opencode/ling-3.0-flash-free` (средняя free, инфра-правки).
- `~/.config/opencode/agent/verifier.md`: `opencode-go/glm-5.2` →
  `opencode/deepseek-v4-flash-free` (дешёвая быстрая, детерминированные
  проверки).
- vault `opencode.json` → `agent.general`: `opencode-go/glm-5.2` →
  `opencode/nemotron-3-ultra-free` (самая сильная из free, сложные задачи).
- explore/build уже были на `opencode/deepseek-v4-flash-free` — не тронуты.
- Доступные бесплатные Zen-модели (проверено `opencode models` 2026-08-04):
  `deepseek-v4-flash-free`, `ling-3.0-flash-free`, `nemotron-3-ultra-free`,
  `laguna-s-2.1-free`, `mimo-v2.5-free`, `north-mini-code-free`.

### Phase 1 / T-087 — test-metrics normalization progress (2026-08-04)

> Стабильные факты по T-087 progress (test-metrics normalization
> contract). Только подтверждённое состояние, explicit WIP vs HEAD и
> open items, без предложений.

- **Clean canonical HEAD SERPlux `ee28637`** (verified measurement
  this gate, isolated worktree): `pytest` executed = **248 collected,
  248 passed, 0 failed, 0 skipped, 0 errors, exit 0**.
  `rg 'def test_'` по `tests/` definitions = **204** (separate metric,
  не executed suite size).
- **Working tree WIP (uncommitted):** collected = **254**;
  254/254 remains **unverified/not canonical** (executed run на WIP не
  проводился this gate). WIP **not canonical** (uncommitted).
- **`docs/test-metrics.md` exists** as canonical contract artifact,
  но its executed section is **stale** (не отражает 248/248 executed
  measurement this gate). Live docs claims — 224 (`serp/AGENTS.md`),
  172 (`docs/verification.md` CI), 95 (`serp/TASKS.md` T-001), 111
  (карточка SERPlux) — **намеренно не переписаны**, остаются
  stale/untyped; separate docs-sync required after WIP merge.
- **Test definitions — отдельный metric** от executed suite; old
  grep=94 source (запись Phase C выше) **остаётся untraceable** (не
  воспроизведён this gate, не подтверждён против текущего HEAD).
- **T-087 contract evidence достаточен для executed metric**
  (248/248 на canonical HEAD). Task остаётся **Active** до
  docs-sync / source-of-truth update (sync `docs/test-metrics.md` ↔
  artifact claims после WIP merge). **T-087 НЕ Done.**

### Phase 1 / T-085 — reviewer/verifier split contract (2026-08-03)

> Стабильные факты по выполнению Phase 1/T-085 (reviewer/verifier split)
> в SERPlux. Только подтверждённое состояние, без предложений; merge
> behavior permissions allowlist — наблюдение `[проверить]`, не strict
> isolation.

- В SERPlux создан project-local `.opencode/agents/verifier.md` как
  local extension/override глобального `verifier`
  (`~/.config/opencode/agent/verifier.md`).
- Роли разделены: `reviewer` (project-local
  `.opencode/agents/reviewer.md`, mode subagent) остаётся
  quality/style/domain reviewer; `verifier` — acceptance-only
  VERDICT `PASS`/`FAIL`, edit deny, webfetch deny, read-only allowlist и
  `python -m pytest -v`.
- Глобальная команда `/loop` `@verifier` теперь в SERPlux резолвится
  проектным verifier; `opencode debug config` видит reviewer+verifier;
  routing конфликтов не обнаружено.
- **Merge behavior permissions allowlist** (local override global
  для permissions/tools) остаётся наблюдением `[проверить]` — strict
  isolation НЕ объявляется.
- SERPlux changes uncommitted; **Phase 1 НЕ завершена** (T-084/T-085
  residuals совместно с T-097).

### Phase 1 / T-089 — runtime gate enforcement (2026-08-03)

> Стабильные факты по итогам design decision T-089. Только
> подтверждённое состояние, без проектных предложений; explicit
> `[проверить]`.

- `commit-guard` через `tool.execute.before` повторно запускает
  acceptance command (pytest) и **блокирует** `git commit` при FAIL —
  подтверждённый runtime gate для testable DoD в working tree.
- Полный gate на отдельный `verifier PASS` marker/state **не
  реализован**: payload capture для subagent/task в
  `tool.execute.after` не подтверждён `[проверить]`; `verifier` остаётся
  read-only (edit/webfetch deny, read-only allowlist).
- `/done` docs-based adaptation (T-086) нужна раньше полного
  finalize-chain для SERPlux.
- Real `git commit` smoke для `commit-guard` остаётся `[проверить]`.
- T-089 **не** объявляется done.

### Phase 1 / T-086 — `/done` memory-model adaptation progress (2026-08-03)

> Стабильные факты по T-086 progress (адаптация глобальной `/done` под
> docs-based vs vault-based memory-модели). Только подтверждённое
> состояние working tree, без предложений; explicit uncommitted status.

- Глобальная команда `/done` (source
  `~/dotfiles/opencode-global/.config/opencode/command/done.md`) получила
  generic memory-model branches: **vault-based** (признак — `04-Memory/`
  в корне или сам vault-репо с `00-INDEX.md`/`02-Methods/`/`03-Projects/`;
  чеклист: TASKS → 01-Reference/02-Methods/03-Projects → VibeOS →
  active-context → /commit), **docs-based** (признак — `docs/` с
  `decisions.md`/`progress.md`/`techdebt.md` + локальный
  `TASKS.md`/`AGENTS.md`, без `04-Memory/`; чеклист: TASKS/CHANGELOG →
  docs/progress → docs/decisions (ADR) → docs/techdebt → /commit), и
  **fallback** (нет ни того, ни другого — локальный TASKS/README/CHANGELOG,
  vault/docs-спец шаги пропускаются).
- Неоднозначная модель — явный вопрос пользователю, не угадывание.
- `/commit` dependency зафиксирована explicit: `/done` делегирует
  финальный коммит проектной команде `/commit` (`.opencode/command/commit.md`
  project-level) или глобальной; перед вызовом проверяется доступность
  `/commit` в текущем проекте; если нет — остановка с сообщением о
  ручном коммите. **Global `/commit` НЕ assumed.**
- **`/done` НЕ гарантирует T-089 verifier PASS/runtime gate:** текст
  команды явно фиксирует, что gate `verify=PASS → finalize` — отдельный
  unresolved контракт (T-089); `commit-guard`/verifier не предполагается
  уже отработавшим.
- **Source и resolved stow path идентичны:**
  `~/.config/opencode/command/done.md` (resolved) → symlink →
  `~/dotfiles/opencode-global/.config/opencode/command/done.md` (source);
  содержимое совпадает, stow-расхождения нет.
- **Implementation uncommitted:** `done.md` modified в working tree
  dotfiles (`git status`: modified, не staged). В той же working tree
  modified ещё ряд dotfiles-файлов (qtile keys, screenlayout, scripts,
  docs/decisions, docs/deferred, `.opencode/memory/todo.json`) — не
  относятся к T-086.
- **Vault refs update (04-Memory/facts.md, active-context.md, TASKS.md,
  session-log) — отдельный follow-up, не часть T-086 implementation.**
  T-086 **не** объявляется Done: dotfiles working tree uncommitted + vault
  refs follow-up + T-089 verifier/runtime gate не закрыт.

### SERPlux
- Репо: `/home/rudra/Projects/serp`
- GitHub remote: `atmavichara108/SERPlux`
- Стек: Python 3.11+ / requests / gspread / FastAPI / DeepSeek (labeler) / SQLite / Docker
- OpenCode-агенты (Go-подписка, 2026-07-02): 6 агентов — build (kimi-k2.7-code, primary, в opencode.json), plan (glm-5.2, primary), collector-dev (kimi-k2.7-code, subagent), reviewer (glm-5.2, subagent), ui-dev (kimi-k2.7-code, subagent, активен), infra-dev (qwen3.7-plus, subagent)
- Команды OpenCode (5): `/commit` (build, deepseek-v4-flash, subtask), `/interface` (ui-dev), `/container` (infra-dev), `/deploy` (infra-dev), `/dream` (build, memory-flush). Глобально: `/loop` (build)
- Плагины (4): env-guard.js, notify.js, commit-guard.js, compaction.js
- Статус: Core ✅, Docker ✅, Deploy ✅, Web UI ⏸ (ADR: только Sheets). Мультиклиентность ✅ (clients/positions/labels, client_id, domains mode). 111/111 тестов.
- Статус методов: context-as-docs ✅, model-routing ✅, multi-agent-pipeline ✅, distill-pattern ✅, verifier-pattern ✅, closed-loop ✅, memory-management 🟡

### dv-hub
- Репо: `/home/rudra/Projects/dv-hub`
- GitHub remote: `atmavichara108/dv-hub`
- Стек: TypeScript strict / Hono / better-sqlite3 / Vanilla JS + Tailwind / Vite
- 5 OpenCode-агентов: plan (qwen3.7-max), build (deepseek-v4-flash), reviewer (deepseek-v4-pro, subagent), researcher (qwen3.6-plus, subagent), infra (qwen3.7-max)
- 7 команд: /morning · /spec · /review · /hygiene · /sync-context · /sync-context-self · /sync-task
- 3 плагина: compaction.ts · env-guard.ts · notify.ts
- Статус методов: distill-pattern ✅, model-routing ✅, context-as-docs 🟡, memory-management 🟡, closed-loop ❌, verifier-pattern ❌
- Git submodule: context/ → dv-project
- Docs: 8 файлов (architecture, product-vision, roadmap, glossary, infra-runbook, backend-conventions, mirotalk-setup, known-issues)

### Глобальный слой OpenCode (2026-08-03)
- Глобальный слой OpenCode versioned через `~/dotfiles/opencode-global/.config/opencode/` и GNU Stow синхронизируется в `~/.config/opencode/`.
- В глобальном слое существуют: `meta` (субагент), `verifier` (субагент), команды `/done`, `/loop`, `session-flush` (плагин).
- Глобальная команда `/loop` использует `agent: build`; каноническое имя dotfiles-агента строителя — `builder` (имя `build` в `/loop` — legacy/алиас, требует фиксации совместимости).
- T-069 / `tools/ecosystem-map/` стал отдельным артефактом планирования апгрейдов вайбкодинг-слоя (не только инструмент-визуализатор).
- `capture` (tools/telegram-capture/ + скилл /capture) — intake-слой апгрейдов вайбкодинг-слоя, не просто сбор заметок.

### dotfiles
- Репо: `/home/rudra/dotfiles`
- GitHub remote: `atmavichara108/dotfiles`
- Стек: shell / GNU Stow / 23 пакета конфигов / OpenCode multi-agent
- OpenCode: мульти-агент v3 + verifier + closed-loop + flush-протокол (T-059, T-060, T-061, 2026-07-04)
- 3 primary агента: sysop (инспектор), planner (архитектор), builder (строитель)
- 5 subagent: reviewer, verifier, qtile-dev, bash-dev, util-dev
- 10 команд-пайплайнов: /sysaudit, /script, /qtile, /util, /prompt, /notify, /macro, /plugin, /loop, /flush
- Память: .opencode/memory/ (user-profile.md + decisions.md) + формализованный /flush-протокол
- Все агенты на deepseek-v4-flash-free (тестовый период)
- Статус методов: context-as-docs ✅, distill-pattern ✅, closed-loop ✅, verifier-pattern ✅, memory-management ✅

### vault (OpenCode-Vault)
- Репо: `/home/rudra/Projects/OpenCode-Vault`
- Это командный центр знаний, не код проекта
- 1 агент: librarian (opencode-go/qwen3.7-plus, primary)
- 9 команд: /ask · /capture · /inbox · /project · /commit · /project-add · /audit · /done (глобальная) · /distill-pipeline
- Pre-commit hook: проверка пустых файлов + валидация викилинков
- 7 методов заполнены в 02-Methods/ (+tool-integration-pattern с 2026-07-07)
- Статус методов (собственные): context-as-docs ✅, distill-pattern ✅, memory-management ✅, model-routing ➖, closed-loop ✅, verifier-pattern ✅, tool-integration-pattern ✅ (T-062 внедрён 2026-07-08)

### Documentation status (2026-08-03)

> Только стабильные факты/статус документации (не планы как текущая
> реализация). Источник:
> [[06-Audits/2026-08-03-dv-hub-phase-d-audit]],
> [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]],
> [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]].

- dv-hub классифицирован в аудите как **recovery-case**, не showcase-case
  (acceptance-поверхность деградирована: `tests/` пуст, `npm test` exit 1,
  CI без тестов; runtime-инциденты открыты: Telegram auth 404, D1 migration
  incomplete).
- **Операционная интеграция с global nerve не подтверждена** для dv-hub
  (zero evidence-type references на `/loop`, `/done`, `@verifier`,
  `@meta`, `session-flush` в проектных артефактах). Это наблюдаемый факт,
  не bug и не утвердительное «не используется».
- **Ecosystem prerequisites не являются project defects.**
  `engineering-style-contract`, `capability-routing`,
  `reviewer/verifier split`, plugin loader contract, runtime enforcement
  contract, memory model compatibility contract, test metrics
  normalization contract — ecosystem-level / future kernel artifacts;
  их отсутствие в конкретном проекте — состояние экосистемного сцепления,
  не дефект проекта.
- **Security findings требуют точной доказательной спецификации** до
  stable fact: exact package, version range, advisory ID (GHSA/CVE),
  impact, exploitability assessment for project codepath, source/date,
  fix availability. Текущая формулировка «high-severity Hono vulnerability»
  для dv-hub — **candidate/unverified security finding**, не stable fact.
- **Ecosystem upgrade plan v1 создан**
  (`06-Audits/2026-08-03-ecosystem-upgrade-plan-v1.md`, status: draft):
  roles of nodes, 5 kernel contracts to implement first, global
  architecture decisions (target roles, not current implementation),
  methodological principles, project-specific constraints, implementation
  order (candidate/planned sequence, без Done/дат), engineering-style-
  contract as planned artifact, decision gates.
- **Engineering-style-contract развёрнут как planned core artifact**
  (explicitly **не** implemented method; **не** в `02-Methods/`):
  общие правила + language profiles (TS/JS, Python, Shell, Config/docs) +
  anti-shitcode patterns + routing table + reviewer/verifier integration.
  Существование — в рамках ecosystem upgrade plan v1, не как внедрённый
  канон.

### Phase 1 / T-098 — test-metrics executed на новом HEAD (2026-08-04)

> Подтверждённые факты после merge WIP и повторного прогона. Только
> подтверждённое состояние + explicit техдолг.

- WIP SERPlux смёржен: HEAD теперь `f7ccd3e`
  (`fix(storage): simplify geo normalization to strip+lowercase, remove GEO_DISPLAY mapping`),
  ветка `fix/labeling-cache-and-quality`.
- **Executed run на новом HEAD `f7ccd3e`:** `./venv/bin/python -m pytest -q --tb=short`
  → **256 collected, 256 passed, 0 failed, 0 skipped, 0 errors, exit 0** (3.52s).
  Test definitions (rg `def test_`) = **212**.
- `docs/test-metrics.md` актуализирован до канона: executed 256/256 на
  HEAD `f7ccd3e`, definitions 212; реестр stale claims (224/172/95/111)
  перечислен, grep=94 признан UNTRACEABLE и исключён.
- **Sync claims → техдолг** (решение пользователя, НЕ правка claims
  librarian'ом): в `serp/docs/techdebt.md` добавлена запись
  «2026-08-04 — Test-metrics claims не синхронизированы с каноном
  (T-087/T-098)» — идемпотентная (заголовок-маркер), централизованная,
  реализация за пользователем при проектной работе в serp.
- Ранее WIP-запись «254/254 passed» была UNVERIFIED; после merge
  superseded фактическим executed 256/256.

### Phase 1 / closure — residuals (2026-08-04)

> Честно открытые residuals Phase 1. Не закрыты — требуют живой сессии
> в serp или наблюдения. Не объявляются закрытыми.

- **Commit-guard на реальном `git commit`** `[проверить]` — real commit
  smoke безопасно не проводился (нужна живая agent-сессия с cwd=serp,
  где загружается плагин; из vault-сессии плагины serp не грузятся).
- **Реальный compaction event session-dispatch** `[проверить]` —
  подтверждён только function-level fire хука
  `experimental.session.compacting`, не полный event-цикл сессии.
- **Payload capture для subagent/task в `tool.execute.after`** `[проверить]`
  — полный gate `verifier PASS` marker/state не реализован, verifier
  остаётся read-only (T-089 unresolved часть).
- **Merge behavior permissions allowlist** (local override global для
  permissions/tools) — наблюдение `[проверить]`, strict isolation не
  объявляется (T-085).

### Phase 1 / T-086 — `/done` memory-model adaptation done (2026-08-04)

> Подтверждённые факты после коммита done.md в dotfiles. Ранее (2026-08-03)
> branches были в working tree uncommitted; теперь закоммичено.

- Глобальная `/done` (`~/dotfiles/opencode-global/.config/opencode/command/done.md`,
  stow-resolved `~/.config/opencode/command/done.md`) имеет generic
  memory-model branches: vault-based / docs-based / fallback; неоднозначная
  модель → явный вопрос пользователю; `/commit` dependency explicit
  (project-resolved, global `/commit` НЕ assumed); `/done` НЕ гарантирует
  T-089 verifier PASS/runtime gate.
- `done.md` закоммичен в dotfiles 2026-08-04 (вместе с T-086 vault refs:
  `01-Reference/commands.md` обновлён).
