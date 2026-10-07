---
type: Fact Registry
title: Реестр фактов
description: Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения [проверить].
tags: [memory]
timestamp: 2026-08-17
---
# Реестр фактов

> Подтверждённые факты об OpenCode и проектах. Факты попадают сюда после разрешения `[проверить]`.

## Профиль пользователя
- **Полное имя:** Max Rudra
- **Сокращения:** Rudra (внутренние контексты), mr (аббревиатура)
- **Роль:** вайбкодер, системный инженер, минималист, пермакультурщик
- **Язык:** русский (основной), терминал-нативный стек
- **GitHub:** [max-ai](https://github.com/max-ai)

## M Code ↔ OpenCode bridge (T-156, 2026-10-06)

- **Сервер v2 принимает только HTTP Basic `base64("opencode:<password>")`** —
  Bearer/пустой username/`?auth_token=` без префикса → 401. Подтверждено живым
  прогоном (dotfiles, T-156 Incident 1; librarian re-check → 200).
- **Порт моста `127.0.0.1:49374`** держит managed systemd user-unit
  `opencode-serve.service` (active+enabled, cgroup-ownership проверена по
  `/proc/<pid>/cgroup`). Орфан-режим `serve --service` от TUI больше не
  канон; `opencode-reload` при убийстве бэкенда трогает и managed unit —
  после релоада сервис надо поднимать через `systemctl --user restart`.
- **Обёртка `opencode-bridge`** (dotfiles `scripts/.local/bin/`): операции
  `prompt` (тело — ключ `text`), `read` (`content[]`, не `parts[]`),
  `handoff` (git-tree). Токен только из `service.json`.
- **Ротация пароля service.json гасит сервис** — делать в плановом окне,
  затем `systemctl --user restart opencode-serve.service` и re-pair M Code
  (подтверждено практикой 2026-10-06).
- **leak-guard** (глобальный плагин dotfiles): редакция известных
  секрет-литералов в выводе инструментов до транскрипта; инвалидация кэша
  секретов по mtime+size, debounce 5s.
- **M Code peer-взаимодействие:** sессии M Code работают на том же общем
  OpenCode-сервисе — после рестарта юнита они переподключаются сами.

## Replay budget (T-135, порт M Code)

- **2026-09-08: live hook-fire подтверждён в TUI.** Плагин `replay-budget.ts` (хук `experimental.chat.messages.transform`) работает в живых сессиях: маркеры `[N characters cleared]` (pruneToolInput, старые tool-входы) и `[mcode: replay budget — omitted N chars …]` (truncateToolOutput, старые tool-результаты) наблюдаются в контексте живой сессии; контент на диске при этом полный — резHistory режется только на реплее к модели, исполнение не трогается. Smoke 14/14 PASS. Бывший residual `[проверить]` закрыт.
- **2026-09-08 [проверить → T-143]:** побочный эффект — `applyReplayBudget` применяет `pruneToolInput` ко всем tool-частям без границы «текущего хода» + мутация in-place; при живых ссылках на store возможна мутация task-промптов субагентов (инцидент: 3 субагента получили `[N characters cleared]` вместо промпта 2026-09-07). Улика сильная, причинность не доказана — контролируемый эксперимент в T-143.
- **2026-09-17: doom_loop в волте зафиксирован как `ask` (решение Rudra).** Конфиг `opencode.json` и `.opencode/agent/librarian.md` frontmatter содержат `doom_loop: ask`.
- **2026-09-18: плагин `main-protector.ts` и worktree-изоляция внедрены.** Хук `tool.execute.before` блокирует коммиты в `main`/`master` и правки 5 hot-files на защищённых ветках. Метод: [[02-Methods/git-worktree-isolation]].
- **2026-09-19: живой evidence работы replay-budget.** В сессии 2026-09-19 при чтении файлов волта зафиксированы маркеры резки вывода `[mcode: replay budget — omitted N chars …]` в реальном времени; контент на диске полный.

## OpenCode

- **2026-10-07 JustDoWork (justwoker) DEGRADED (non-stream-only):** anthropic-путь
  `/v1/messages` работает **только без стрима** (HTTP 200, корректный JSON).
  Со `stream: true` шлюз отдаёт только `message_start/delta/stop` — события
  `content_block_*` с текстом отсутствуют (3/3). OpenAI-путь `/chat/completions`
  закрыт Cloudflare 403. OpenCode всегда стримит (AI SDK streamText), опции
  non-stream в конфиге OpenCode нет → прямой провайдер отвечает пустотой.
  Root cause: регрессия New API-шлюза justwoker (в памяти с 2026-10-03).
  Временный фикс (решение оператора): локальный стриминг-шим — форвардит
  non-stream upstream и сам генерирует корректный SSE. Целевое — канал New API
  ([[docs/specs/newapi-gateway-layer]]). Баланс $300+.

### Агенты
- **librarian** — агент командного центра. Режим: primary (default в opencode.json). Запускается без `/agent`. Области: мониторинг проектов, аудит, управление знаниями.
- Primary agents переключаются через `Tab` или настроенный keybind
  `switch_agent`; subagents вызываются через `@mention` или `task`.
- Самодекларированный acceptance marker агента не является evidence; verdict
  подтверждается независимым verifier по session/runtime artifacts.
- 2026-08-29 independent verifier подтвердил PASS для exact global primary
  sysop smoke: `system-audit -> sysop`, `mode=primary`,
  `opencode-go/deepseek-v4-flash`; только read-only audit commands, без
  `edit`/`task`/mutating `bash`, с `stow -n` simulation и без general fallback.
  Route scoped; это не orchestration/general rollout. `system-ops` apply
  отдельно.
- Официальная документация: https://opencode.ai/docs/agents/
- Предыдущая инструкция использовать `/agent` для переключения роли была
  ошибочной. Новый sysop PASS подтверждён только independent verifier и
  runtime artifacts, не self-declared marker.

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
  ~~`laguna-s-2.1-free`~~ (RETIRED 2026-09-05: зацикливания, удалена), `mimo-v2.5-free`, `north-mini-code-free`.

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

### ChaT
- Репо: `/home/rudra/Projects/ChaT`
- Добавлен bootstrap проекта.
- Тип: knowledge-operations
- Стек: Markdown / Obsidian / OpenCode
- Статус: planning
- Краткая ссылка: [[ChaT]]

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

### Временная модельная политика (2026-08-17)

> Подтверждённая временная политика для активных агентов Vault, ChaT,
> dotfiles и SERPlux. Политика действует до capability-routing.

- Для primary и сложных ролей используется `opencode-go/gpt-5.6-luna`.
- Для дешёвых read-only/research/reviewer/verifier ролей используется
  `opencode-go/deepseek-v4-flash`.
- Доступность обеих моделей подтверждена командой `opencode models`.
- Merged config debug проходит без ошибок разрешения конфигурации.
- Изменения требуют перезапуска OpenCode, чтобы новая модельная политика
  применялась в активных сессиях.
- Политика временная и будет заменена capability-routing после его rollout.

### 3 Режима выбора моделей (2026-09-01) — **[проверить]**

> Исследование провайдеров OpenCode с бесплатными лимитами. Созданы
> [[01-Reference/providers]] и [[01-Reference/config-modes]].

- **Всего 4 провайдера доступны в OpenCode:** `opencode` (Zen), `opencode-go` (Go), `openrouter`, `mistral`.
- **Истинные бесплатные лимиты только у 2 провайдеров:**
  - `opencode` (Zen): 7 бесплатных моделей (nemotron-3-ultra-free, deepseek-v4-flash-free, ling-3.0-flash-free, mimo-v2.5-free, nemotron-3.5-lightning-free, ling-3.0-flash-fin-free, muse-spark-1.2-contributor-free)
  - `openrouter`: 47+ бесплатных моделей (glm-5.2:free, minimax-m3:free, nemotron-3-ultra:free, ~~poolside laguna-s-2.1:free RETIRED 2026-09-05~~ и др.)
- **БЕЗ бесплатных лимитов:** `opencode-go` (только подписка), `mistral` (только платные).
- **OpenCode Go** — платная подписка, модели: gpt-5.6-luna, glm-5.2/5.3, qwen3.7-plus, kimi-k2.7-code, mimo-v2.5-pro и др.
- **Созданы 3 режима программного переключения:**
  - **FREE** — 100% бесплатные (Zen + OpenRouter free), primary: nemotron-3-ultra-free
  - **MEDIUM** — GPT-5.6 Luna (Go, сильная и дешёвая) + Zen free для рутины
  - **PREMIUM** — Топовые (Claude Opus 5, Sonnet 4.6, GPT Codex) на будущее
- Документация: [[providers]], [[config-modes]], [[model-routing]] обновлён

### Runbook operational layer (2026-08-17)

- В vault создан отдельный слой `07-Runbooks/` для live usage, usage patterns
  и operator workflows.
- Граница слоя подтверждена: `02-Methods/` хранит abstract reusable techniques,
  `06-Audits/` — dated findings, `AGENTS.md` — agent rules; runbooks не
  дублируют эти источники.
- [[07-Runbooks/vibecoding-operator-handbook]] — текущее рабочее состояние;
  [[07-Runbooks/vibecoding-changelog]] — append-only история подтверждённых
  practice shifts.

### Orchestration smoke (2026-08-29)

- Exact Vault orchestration smoke получил `PASS` по независимому verifier:
  `librarian` route selection → named `researcher` → `reviewer` → `verifier`,
  строго последовательно, без `general` fallback и без self-marker evidence.
- Scope ограничен `vault`, risk/mutability — `read-only`; researcher и reviewer
  не выполняли edits/task. Runtime dispatch подтверждён только для exact smoke;
  automatic runtime orchestration/router не внедрён.
- Evidence: [[04-Memory/route-log/2026-08-29-orchestration-smoke]],
  [[docs/specs/control-plane-smoke]].
- Capability-routing gaps R1/F1/F2/F3 закрыты документально/evidence-gated;
  остаются uncommitted artifacts, negative deny, local extension merge,
  literal tool output limits. T-109 и остальные проектные задачи не изменены.

### Кастомные провайдеры OpenCode / LinaliAPI (2026-09-06)

- `/connect` сохраняет **только ключ** в `~/.local/share/opencode/auth.json`;
  провайдера, отсутствующего в models.dev, нужно описывать в конфиге
  (`provider`: npm `@ai-sdk/openai-compatible`, `options.baseURL`, `models`) —
  подтверждено https://opencode.ai/docs/providers/. Без config-блока
  провайдер не появляется в `/models`.
- **ID провайдера в конфиге = ключу записи в auth.json** — тогда `apiKey`
  подтягивается автоматически, хардкод в options не нужен.
- Глобальный конфиг на этой машине — `~/.config/opencode/opencode.jsonc`
  (JSONC); файла `opencode.json` в каталоге нет (подтверждено субагентом
  2026-09-06; ранее в [[01-Reference/global-config]] уже был .jsonc).
- `external_directory` правила: побеждает **последнее совпавшее** правило;
  allow ставится после deny `*`, секретные deny (`**/.env*`, `*.key`...) —
  последними.
- Permission-границы сессии фиксируются при старте opencode (hot-reload
  конфига нет): чтение `~/.local/share/opencode/*` из агентской сессии идёт
  через ask-одобрение, **запись** туда заблокирована; правки
  `~/.config/opencode/**` возможны только в сессии, запущенной после
  рестарта с allow в проектном конфиге.
- **LinaliAPI** (linaliapi.com) — OpenAI/Anthropic-совместимый шлюз,
  `https://api.linaliapi.com/v1`, ключи `sk-ant-*`, ID моделей с вендорными
  префиксами (`anthropic/...`, `openai/...`, `z-ai/...`). Подключён как
  5-й провайдер (custom), 6 моделей: claude-opus-5, gpt-5.6-sol,
  gpt-5.6-luna, gemini-3.8-flash, glm-5.3, deepseek-v4-pro. Конфиг в
  глобальном `opencode.jsonc`; детали [[01-Reference/providers]].
- **2026-09-06 (канонизация):** живой `~/.config/opencode/opencode.jsonc` —
  обычный файл, НЕ stow-симлинк; блок провайдера добавлен субагентом в
  dotfiles-канон `~/dotfiles/opencode-global/.config/opencode/opencode.jsonc`
  (jq VALID). Live↔канон — два физических файла; конвергенция через
  `stow --adopt opencode-global` (за пользователем). **GUI M Code Desktop:**
  конфиг-рут подтверждён `~/.config/mcode/opencode.jsonc`, `provider.linaliapi`
  уже присутствовал (внесён пользователем), jq VALID; auth-стор M Code для
  linaliapi не проверен `[проверить]` (401 в GUI → ключ через /connect в GUI).

### Promo-provider protocol / JustDoWork (2026-09-16)

- **JustDoWork (`justwoker`)** — аутентифицированный `GET /v1/models`
  (`https://api.justwoker.icu/v1`) вернул пустой `data: []`. По правилу метода
  [[02-Methods/promo-provider-protocol]] пустой список = `DEGRADED`/`BLOCKED`
  даже при ненулевом dashboard-балансе. Карточка:
  [[01-Reference/provider-cards/justwoker]].
- **Dashboard JustDoWork** показывал баланс `$121.34` (referral/promotional) и
  при этом не имел секций Models / Channels / Tokens / Top-up. Фактическая
  API-спендируемость referral-баланса не подтверждена `[проверить]`.
- **Чат-проб JustDoWork** на `gpt-4o-mini` вернул Cloudflare 403. Model IDs
  отсутствуют — провайдер не подключается и не становится default.
- **LinaliAPI (`linaliapi`)** — провайдер имеет 6 настроенных моделей и
  работает в TUI по подтверждению пользователя. Баланс не измерен `[проверить]`;
  карточка: [[01-Reference/provider-cards/linaliapi]].
- **Правило ID провайдера:** provider ID в конфиге обязан совпадать с ID
  записи в auth-сторе — только тогда `apiKey` подтягивается автоматически;
  `apiKey` в конфиге не хранится (обобщение правила LinaliAPI 2026-09-06).

### Promo-provider protocol update (2026-09-24)

- **JustDoWork (`justwoker`)** — каталог ожил: `GET /v1/models` вернул HTTP 200
  и 1 модель `claude-opus-4-8` (ранее пустой `data: []`). Но
  `POST /v1/chat/completions` отдаёт Cloudflare 403 captcha при любом UA —
  браузерной сессии (cookies/JWT/JS-challenge) у API-ключа нет, одного
  Bearer-ключа мало. Статус DEGRADED, в конфиги не добавлен.
- **AMD Radeon (`amd-radeon`)** — 7 моделей живы (HTTP 200), канонический
  baseURL `https://developer.amd.com.cn/radeon/api/v1`. Дневной лимит
  **$1 per period** даёт HTTP 429 `rate_limit_exceeded`, отдельно ловится
  `global_concurrency_rate_limit_exceeded`. Бенч отложен до сброса квоты.
- **Урок промо-протокола:** `GET /v1/models` HTTP 200 НЕ означает
  работоспособность — обязателен отдельный chat-smoke, иначе провайдер
  помечается CONNECTED ошибочно.

### OpenCode agent infrastructure (2026-09-24)

- **Плагины защиты НЕ существуют физически.** Каталоги `.opencode/plugin/`
  и `~/.config/opencode/plugin/` пусты (внутри только `node_modules/@opencode-ai/plugin/dist/`
  — SDK). `main-protector.ts` и «плагин защиты секретов», числившиеся в памяти
  как работающие, **физически отсутствуют**. Блок коммитов в main делает
  git-хук `.git/hooks/pre-commit` → симлинк на `05-Templates/pre-commit-check.sh`.
  Это ответ на давний техдолг: `.env` не блокировался плагином, потому что
  блокировать было нечему. `.env` закрыт правилом `external_directory` →
  `"**/.env*": deny`, чтение внутри рабочей директории им не покрывается.
  | 2026-09-24 |
- **Venv волта: `.venv` (с точкой).** Агентские allowlist-правила
  `"./venv/bin/python*": allow` не совпадали с реальностью — venv называется
  `.venv`. Инцидент verifier-цикла: агент не мог запустить pytest, а промпт
  запрещал сдаться → перебор команд до исчерпания кредитов. Починено
  2026-09-24: allowlist расширен на `.venv/bin/python*`, `*/.venv/bin/python*`,
  `python -m pytest*`, плюс `ls/cat/grep/find/head/tail/wc/stat`.
  | 2026-09-24 |
- **Agent step/task guards инцидент.** Verifier был единственным агентом
  кернела без `steps:` и `task: deny`. При невыполнимой задаче (evidence
  блокируется permission, промпт запрещает сдаваться) крутился до исчерпания
  кредитов. Починено 2026-09-24: verifier → `steps: 12` + `task: deny` +
  расширенный bash-allowlist + промпт с явным правилом «один заблокированный
  вызов = немедленно FAIL с причиной, не перебирать варианты». Researcher
  добавлено `steps: 15`, meta → `steps: 20`. System-audit/system-ops уже
  имели ограничения. | 2026-09-24 |
- **Cloudflare 403/1010 на отсутствие User-Agent.** Запросы к моделям через
  Cloudflare-проксированные эндпоинты (например, AnyModel) без `User-Agent`
  возвращали 403 (error 1010). Бенч `tools/model-bench/client.py` изначально
  не ставил UA → систематический сбой живых прогонов. Починено: фикс
  `User-Agent: opencode-vault-model-bench/0.1` в заголовках. Общий урок для
   будущих probe/balance-скриптов: UA обязателен. | 2026-09-24 |
- **Матрица capability-бенчмарков (2026-09-24, 6 моделей AnyModel, hash
  acd13ac0c8d9).** `cx/gpt-5.6-sol` проходит все 4 гейта за $0.000633/3164 tok —
  лучшее цена/способности. `cc/claude-opus-5` тот же результат за $0.0463/154190
  tok (73× дороже). `cx/gpt-6-astra` все гейты, $0.0179. `kmc/k3`: reasoning 1.0,
  build 1.0, **tools 0.6 ✗** (strict JSON). Бесплатные `am/free` и
  `am/nemotron-3-ultra-550b-a55b`: tools/build проходят, **reasoning 0.5 ✗**.
  Вывод: бесплатные модели не годятся для задач на рассуждение; K3 не годится
  для strict tool-calling. Матрица: [[01-Reference/model-benchmarks/matrix]].
  | 2026-09-24 |
- **Reasoning-токены ломают оценку стоимости.** Фактический расход
  `cc/claude-opus-5` превысил оценку по `max_tokens` в ~36× (154K токенов против
  ожидаемых ~4K): reasoning-модели тратят токены на скрытые рассуждения, которые
  в `max_tokens` ответа не видны. Любая оценка бюджета по одному `max_tokens`
  систематически занижена → T-148. | 2026-09-24 |
- **AnyModel отдаёт HTTP 503** `service_unavailable` на бесплатных моделях под
  нагрузкой (наблюдалось на `am/nemotron-3-ultra-550b-a55b`, 2 из 17 запросов).
  Probe-скрипты должны переносить частичные сбои без падения прогона.
  | 2026-09-24 |

### Bench/провайдеры (2026-09-28)

- **6 багов бенча из брифа закрыты**: tools `max_tokens` 200→1500 + статус
  `TRUNCATED` с `finish_reasons` в артефакте; ретрай 429 паузой 20с;
  `resolve_coefficient` (таблица → `--price-per-1m` → живой GET /models
  billing/pricing, иначе null) + валидация флага; `tokens_estimated` рядом с
  raw `cost_tokens`, `KNOWN_INFLATED_USAGE={"anymodel"}` — деньги по панели;
  герметичные тесты (conftest подменяет CONFIG_PATHS/AUTH/VAULT_ROOT);
  `http.client.HTTPException` ловится как network. 98 passed офлайн.
  | 2026-09-28 |
- **auth.json закрыт для агентов**: строка allow удалена из vault
  `opencode.json` (2026-09-28). `config.resolve_key` читает auth.json
  напрямую питоновским open — permission ему не нужен.
  | 2026-09-28 |
- **Vercel AI Gateway ACTIVE** (2026-09-28): каталог 391 модель (HTTP 200),
  smoke `google/gemini-2.5-flash-lite` → PROBE_OK, $2.4e-06. Ключ только в
  auth.json id `vercel`. Подключён в TUI + M Code. Ежемесячная квота и
  неработающие модели со слов пользователя — `[проверить]` поштучным smoke.
  | 2026-09-28 |
- **JustDoWork chat недоступен с нашей сети обоими транспортами**
  (2026-09-28): `/v1/messages` (x-api-key, direct и прокси) → 403
  `server: cloudflare`, пустое тело; каталог при этом 200. Шлюз автора
  отчёта ходит со своих IP — блок сетевой, не ключевой. В конфиги не
  добавлен осознанно. | 2026-09-28 |

- **JustDoWork ВЗЯТ (2026-09-28)**: рабочий путь — Anthropic `/v1/messages` с
  `x-api-key` и РЕАЛЬНОЙ моделью (`claude-opus-4-8`) → HTTP 200 PROBE_OK,
  $0.000634. Тест с несуществующей моделью давал ложный 403. Подключён в TUI
  (обе секции) + M Code через `@ai-sdk/anthropic`. Скрытая подсказка ~6.6K
  входных токенов — считать в бюджете. Статус ACTIVE. | 2026-09-28 |
- **recruiting-hr: TG-аккаунт оператора подключён (2026-10-03)**: telethon
  1.45.0, сессия `data-private/tg_user.session` (вне git), ключи в
  gitignored `data-private/tg.env`. Прямой MTProto заблокирован →
  обязателен локальный SOCKS5 (`TG_PROXY`, python-socks в .venv); telethon
  `HTTP(S)_PROXY` из env НЕ читает — при заблокированном прямом MTProto это
  даёт TimeoutError. `git init` сделан 2026-10-03. Урок: `data-private/` и
  `.venv/` живут только локально (вне git/zip) — при переносе проекта их
  восстанавливать отдельно. | 2026-10-03 |
- **Мир-слой VibeOS/RPG: канон «великий мудрец layer v1.2-альфа» принят (2026-10-05)**:
  имена и роли — Рудра (оператор, двойная прогрессия), Майя (мир), Allis Maya (Сила,
  дух-хранитель, сверхспособность Симуляция Мира, пишет законы Мира), Вельзевул
  (Великий мудрец, читает законы, декодирует в операции), Голос Мира (канал Силы).
  Вельдора = M Code (распечатывание = мост T-156). Именование сущности = gate
  raw→canon. Это творческий/продуктовый канон экосистемы, не программный релиз;
  source of truth — [[04-Memory/idea-graph/index]] (v2: 129 узлов/160 рёбер, 8 графов,
  verifier PASS 2026-10-05) + [[04-Memory/session-log/2026-10-05]]. | 2026-10-05 |
- **B21 закрыт: массовые «удаления» `.opencode/agents|commands|plugin*` в dv-hub (16),
  ChaT (18), AndroidOS (10) — это НЕ потеря, а миграция в `.mcode/` (2026-10-07)**:
  проверено по совпадению имён файлов — удалённые из `.opencode` агенты
  присутствуют в `.mcode/agents/…` с теми же путями (`agents/build.md`,
  `agents/chat-reviewer.md`, `agents/builder.md` и т.д.). Во всех трёх репо
  `.mcode/` **не отслеживается git** (0 файлов в `git ls-files`), поэтому объекты
  есть на диске, но не в истории. dotfiles чистый — миграция его не коснулась.
  Следствие для карточек проектов: описания агентов в карточках ChaT/AndroidOS
  устарели (ссылаются на `.opencode`), требует отдельного обновления карточек.
  Метод замера: `git status --porcelain` + `comm` по списку путей, ноль LLM. | 2026-10-07 |
- **T-159 решён Рудрой (2026-10-07): `.mcode/` в проектах НЕ версионировать** —
  это зона другого разработчика (M Code). Объекты миграции из `.opencode/`
  (агенты/команды/плагины dv-hub, ChaT, AndroidOS) остаются только на диске;
  риск потери при переустановке принят осознанно. Карточки проектов обновлены
  под `.mcode` (T-160, коммит 7cea208). | 2026-10-07 |
- **Процессный дефект «устаревший снимок дерева» (2026-10-07, дважды за вечер)**:
  сессия читает git-состояние в начале своего хода и далее работает по нему; пока
  она думает, сосед коммитит — и её отчёт описывает уже несуществующее состояние.
  Проявления: sysop объявил мои закоммиченные правки `freed.py` «чужими
  незакоммиченными» (видел дерево до 01:29, коммит acc6023); igraphv2 получил
  scope T-160 уже после того, как я его закрыл (7cea208) — мнимый дубль.
  Правило для Дирижёра: **приёмка только по факту на диске/в git, не по тексту
  отчёта**; при расхождении сначала `git log`/`git status`, потом вердикт.
  Правило для исполнителя: перед записью scope — сверить, что артефакт ещё
  не изменён/не закрыт соседом. | 2026-10-07 |

- **Факт 2026-10-07 (исправлен): профиль агента сессии ≠ её заголовок.** Сессия
  «великий мудрец - внедрение» (ses_ef77a5cf…) несёт агентский профиль librarian
  изначально (не после ребута): «внедрение» — имя в title, не агент. Ответы в
  письмах печатаются как «librarian · …». Дирижёр сверяет авторство по
  session_message/agent, а не по заголовку. ЗАПРЕТ: выдавать баг по одному
  наблюдению — проверять всех затронутых (B16 мнимый, 4d53004).
- **Именование терминала (blessed Рудрой 2026-10-07)**: наружу — постоянное
  внешнее имя «терминал» (линия: пульт → рубка → терминал); внутреннее игровое —
  **Pip-Boy** (шлюз-хранитель-транслятор: состояние↔реальность; толстая морда
  над кластером, доступ с ноутбука и смартфона). Версионирование:
  `VibeOS <major>.<minor> «<имя-эволюции>»-<стадия>`; первая после нулевой —
  **VibeOS 1.0 Pip-Boy Eco-Sys alfa** (1.0 = переход гаджет→экосистема).
  Имя мажорной версии = обязательство перехода. Canonical:
  [[04-Memory/idea-graph/index]] узел world-entity-terminal-pipboy.
  Контекст: внутренний игровой мир Рудры; IP-правообладателей не касаемся
  (внешний контур — нейтральное «терминал»). | 2026-10-07 |

### 2026-10-07 (вечер: Граница v2, классификация, тишина)
- **T-164. Граница v2 (благословение Рудры).** Внутренняя терминология
  запрещена только в продуктах коммерческих и волонтёрских проектов
  (код/UI/их репо). Методы, мир, сцены, инфра — публичны и не маскируются:
  вайбкодинг как приключение + понятный переводной слой игровая↔действительность.
- **T-165. Классификация продуктов:** SERPlux=коммерческий (приватит Рудра);
  dv-hub=волонтёрский (сейчас GPL-3.0; MIT как альтернатива — ждёт выбор);
  ChaT=детище Рудры, комьюнити-ориентированный (лицензия/тип — TBD);
  AndroidOS=детище волта, наследует лицензию (предложено GPL-3.0).
- **T-166. TradingMind — правило тишины (подтверждено повторно).** Ни в
  отчётах Рудре, ни в промптах агентов, ни в аудитах — до явного слова о
  бутстрапе. Uрок B7: имя просочилось через словарь графа; фильтровать в
  dispatch.

### 2026-10-07 (skill-инвокация)
- **T-167. Квирк вызова skills-инструмента.** Утилита skill требует параметр
  с именем "id" (не "name"/"arguments"), иначе '{"type":"permission…"}'-стиль
  ошибки 'id: Missing key'. Повторный вызов с явным id + arguments проходит.
  Симптом наблюдён 2026-10-07 (вызов decision-queue дважды упал с пустым
  {} на серверной стороне). Харнес-квирк, НЕ наш код: фикс = всегда передавать
  id строки скилла первым аргументом; баг-фикс ядра OpenCode не делаем.

### 2026-10-07 (шим justwoker: ECONNRESET / 504)
- **T-168. Корень сбоев рабочих сессий через shим — не «шлюз лежит».** Symptom:
  `Retry due attempt N: ECONNRESET: socket closed unexpectedly` / `shim: upstream
  timeout` у Рудры в чате, при этом curl в тот же апстрим 12/12 = 200.
  Root cause: шим держал HTTP-коннект OpenCode пустым, пока ждал non-stream
  ответ апстрима (Opus генерация десятки секунд); соединение простаивало и
  рвалось (Bun idleTimeout default 10s + нетранспарентные обрывы).
  Fix (justwoker-shim.ts): SSE открывается сразу и держится стандартными
  Anthropic `ping` каждые 8с; idleTimeout=255; forward()-ретраи 403/503
  (пульс балансировщика: CF-rate-limit 403 ~0.5c, New API «No available
  channel, distributor» 503); try/catch хендлера вместо падения процесса;
  UPSTREAM_TIMEOUT_MS=600s; при ошибке апстрима — SSE error-событие.
  Evidence: стрим max_tokens=1500 прожил 34.9c и завершился message_stop
  (5 пингов в потоке); сервис active, crash count 0. Факт: **апстрим
  justwoker жив и отвечает 200 за 2.5–6c** — предыдущий вывод «канал лёг»
  был артефактом этого бага шима.

### 2026-10-07 (B18 + инцидент перехвата HEAD)
- **B18 принята (dotfiles main=1cab443).** letter.sh пишет receipts-out журнал
  (no-resend), delivery-check.sh — read-gate по sqlite: rc=0 доставлено /
  rc=1 не доставлено / rc=2 ошибка. Дирижёр воспроизвёл сам: positive rc=0,
  negative rc=1, нет-сессия rc=2. Журнал: ~/.local/state/opencode/mail/.
  Канон приёмки писем: доставка проверяется delivery-check, не верой.
- **B22 (новое). Перехват HEAD в общем checkout.** Симптом: параллельная
  сессия переключила общий worktree посреди чужой работы — коммиты легли на
  чужую task-ветку (sysop разобрал штатно, чужое не тронуто). Root cause:
  pre-commit различает main vs task/*, но не владельца task-ветки. Фикс
  (предложение sysop): фиксация владельца ветки в claims.jsonl scope +
  проверка «чья HEAD» перед коммитом. Мандат выдан sysop.
- **Double-ack контракт принят всеми адресатами.** igraphv2 исполняет с
  2026-10-06 фактически (started/finished receipts); librarian принимает как
  контракт: входящий мандат → started, завершение хода → finished.

### 2026-10-07 (B22)
- **B22 принят (dotfiles main=faaf45b).** head-guard.sh + claim/release в
  hello.sh + гейт-5 pre-commit. Режим soft-block: блок только при свежем
  чужом claim (rc=1); legacy/stale/unknown — GO или WARN в
  ~/.local/state/opencode/head-guard.log. Дирижёр воспроизвёл: чужой→1,
  свой→0, после claim-release→0. Синтаксис: hello.sh claim-release
  --session --branch (НЕ release). B18-довинт: журнал sent пишется ДО
  блокирующего run (timeout больше не теряет запись).
- **Вопрос-флаг:** sysop заявил garbage-guard «подтверждён Рудрой» — у
  Дирижёра подтверждения нет (ни facts, ни route-log, ни TASKS). Ждёт слова
  Рудры; до него мандат не выдаётся.
