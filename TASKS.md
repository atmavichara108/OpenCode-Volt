---
type: Task Tracker
title: TASKS — трекер задач по волту
description: Оперативные задачи по доведению волта до рабочего состояния и дальнейшему развитию.
tags: [meta, tasks]
timestamp: 2026-07-07
---
# TASKS — Трекер задач OpenCode Vault

> Основа для планомерной работы. Активную задачу на сессию бери из **Active**.
> Статусы: `🟤 backlog` · `🔵 planned` · `🟡 active` · `✅ done` · `⛔ blocked` · `➖ cancelled`
> Приоритеты: **P0** (блокер) · **P1** (структура) · **P2** (наполнение) · **P3** (полировка) · **P4** (автоматизация)

---

## 🟡 Active — текущая сессия

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| | _Пусто — Phase 1 (kernel stabilization) завершена 2026-08-04._ | | |

## 🔵 Planned — следующие задачи

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-028 | Планирование новой архитектуры: 4 направления (Phone Remote, VibeAndroid, ProdWatch, Rudra AI) — **пауза, активен SERPlux** | P2 | [[99-Inbox]] |
| T-046 | R-005: Project Orchestrator — оркестрация из волта всеми проектами + Android-управление | P2 | [[99-Inbox]] (R-005) |
| T-015 | Telegram-бот для приёма фич и подходов — **эволюция T-062** (сначала команда /capture, бот как real-time слой позже) | P5 | [[DEVELOPMENT-ROADMAP]], [[02-Methods/tool-integration-pattern]] |
| T-016 | Классификация фич по проектам (автомат) — **реализуется в /capture** (librarian классифицирует) | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-017 | Команда `/project-upgrade` — авто-внедрение методов | P5 | [[DEVELOPMENT-ROADMAP]] |
| T-068 | `tools/doc-converter/` — второй инструмент VibeOS (PDF→Markdown). Референсы: MinerU (C-001), Chandra (C-054), revpdf (C-048). Связь с distill-pattern и context-as-docs | P3 | [[02-Methods/tool-integration-pattern]], [[99-Inbox]] (C-001) |
| T-029 | VibeAndroid — расширение архитектуры вайбкодинга для Android-разработки (методы, команды, интеграция) | P2 | [[99-Inbox]] (R-002), [[VibeOS]] |
| T-030 | Telegram Bot MVP — статусы проектов + базовые команды (расширение T-015) | P2 | [[rudra-phone]], T-015 |
| T-031 | ProdWatch Фаза 0 — health-check скрипты + Telegram алерты | P2 | [[prod-monitor]] |
| T-032 | Rudra AI Фаза 1 — TODO Planner на Android (первое Android-приложение) | P2 | [[rudra-ai]] |
| T-033 | Настроить Android-окружение (Android Studio, SDK, эмулятор, ADB) | P3 | [[rudra-ai]], [[rudra-phone]] |
| T-034 | API Gateway — центральный хаб для команд к проектам (авторизация, роутинг) | P3 | [[rudra-phone]], [[SERPlux]], [[dv-hub]] |
| T-035 | Создать Android-методы в 02-Methods/ (android-preview-pattern и др.) | P3 | [[00-INDEX#Methods]] |
| T-036 | ProdWatch Фаза 1 — веб-дашборд мониторинга (uptime-kuma или самописный) | P3 | [[prod-monitor]] |
| T-037 | Rudra AI Фаза 2 — интеграция с проектами, чтение статусов, напоминания | P3 | [[rudra-ai]] |
| T-038 | ProdWatch Фаза 2 — Prometheus + node_exporter + алерты с уровнями | P4 | [[prod-monitor]] |
| T-039 | Rudra AI Фаза 3 — Proactive Assistant + локальный LLM | P4 | [[rudra-ai]] |
| T-040 | Android-приложение rudra-phone (нативный UI, Jetpack Compose) | P4 | [[rudra-phone]] |
| T-041 | Rudra AI Фаза 4 — Full Assistant (multi-agent, голос, контекст) | P4 | [[rudra-ai]] |
| T-042 | ProdWatch Фаза 3 — полная observability (логи, метрики, интеграция с rudra-phone) | P4 | [[prod-monitor]] |
| T-047 | prompt-engineer агент — специализированный агент-промптовик в Vault/экосистеме: свои команды (/prompt по образцу dotfiles + расширения), встроен в skills (авто-подгрузка при формулировке задач субагентам) и пайплайны (промпт-фаза перед делегированием); librarian и build перестают формулировать промты ad-hoc — вызывают prompt-engineer как роль; зависит от: skills-поддержка в OpenCode [проверить], distill-pattern, multi-agent-pipeline; референс: /prompt (dotfiles, planner→docs) | P3 | [[02-Methods/multi-agent-pipeline]], [[03-Projects/dotfiles]] |
| T-048 | Вернуть Zen-модели после пополнения кредитов (профили моделей под провайдера — будущий апгрейд) | P3 | [[04-Memory/facts.md]] |
| T-049 | Профили моделей под провайдера (Zen/Go): переключение одной правкой. Абстракция model-routing — чтобы следующий переезд Zen↔Go не был ручной перестановкой всех агентов | P2 | [[02-Methods/model-routing]] |
| T-050 | Дистиллировать verify-gate в метод (02-Methods/) после обкатки в SERPlux /commit | P3 | [[02-Methods/verifier-pattern]] |
| T-053 | Машинная граница инфра/код для meta через плагин (env-guard-подобный, tool.execute.before) — сейчас граница текстовая | P3 | [[01-Reference/agents]], [[02-Methods/verifier-pattern]] |
| T-054 | Дистиллировать команды в skills [проверить надёжность автозагрузки] | P4 | [[01-Reference/commands]] |
| T-055 | Изучить packagemain.tech agentic pre-commit via Go SDK как референс для умного гейта | P3 | [[01-Reference/plugins]] |

### Контур планирования апгрейдов вайбкодинг-слоя (seed: `06-Audits/2026-08-02-upgrade-planning-seed`)
| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-070 | `guardian` — агент-страж: холит конвенции/границы/неотвратимость verify перед коммитом; общий гейт экосистемы, дополняет per-project verifier и commit-guard | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[02-Methods/verifier-pattern]] |
| T-071 | `sysop` (global) — инспектор уровня экосистемы: аудит инфры всех проектов, единый сводный отчёт; поднимает dotfiles /sysaudit до глобального слоя | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[03-Projects/dotfiles]] |
| T-072 | Глобальные `researcher`/`reviewer` — пара для исследования и ревью до/во время build-пайплайнов; сейчас researcher/view в dv-hub локально — вынести в глобаль | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[03-Projects/dv-hub]] |
| T-073 | Фикс global `/loop` `build`→`builder` — зафиксировать каноническое имя агента-строителя (`builder`) и совместимость/алиас `build` в глобальной команде `/loop` | P2 | [[04-Memory/facts.md]], [[06-Audits/2026-08-02-upgrade-planning-seed]] |
| T-074 | Redesign `/done` scope — vault-спецфичные сущности (зависимость от `/commit`, scope general vs vault-only) в глобальной команде `/done` | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[01-Reference/commands]] |
| T-075 | Rework memory/event-log — редизайн `04-Memory/` + event-log: событийный лог вместо/вместе с session-log, чёткие слои факт/контекст/лог | P3 | [[04-Memory/facts.md]], [[04-Memory/active-context.md]], [[06-Audits/2026-08-02-upgrade-planning-seed]] |
| T-076 | Глобальный `notify` + voice — единый слой уведомлений (Telegram/desktop) и голосовой обратной связи для агентов | P4 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[01-Reference/plugins]] |
| T-077 | Routing spec / capability-routing — формальная спецификация маршрутизации задач к агентам по capability (kill ad-hoc dispatch) | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[02-Methods/multi-agent-pipeline]] |
| T-078 | Code quality conventions / anti-shitcode layer — общий слой конвенций качества и гейт против шиткода в пайплайнах (с `guardian`/`verifier`) | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[02-Methods/verifier-pattern]], T-070 |
| T-079 | `capture` → dotfiles/software-upgrade agent — продвижение capture из intake-заметок в полноценного агента апгрейдов софта/dotfiles | P3 | [[02-Methods/tool-integration-pattern]], [[06-Audits/2026-08-02-upgrade-planning-seed]], [[03-Projects/dotfiles]] |
| T-080 | `ecosystem-map` как upgrade planning interface — превратить tools/ecosystem-map/ из визуализатора в интерфейс планирования апгрейдов (выбор навыка→роадмап для агентов) | P3 | T-069, [[06-Audits/2026-08-02-upgrade-planning-seed]] |
| T-081 | Policy global vs local plugins — правило принадлежности плагинов (что живёт в `~/.config/opencode/plugins/`, что в проекте), политика мёржа/переопределения | P3 | [[01-Reference/plugins]], [[04-Memory/facts.md]], [[06-Audits/2026-08-02-upgrade-planning-seed]] |
| T-082 | Спроектировать `engineering-style-contract` — контракт инженерного качества кода: **короткий общий контракт + language profiles** (Bash/Python/TS-Node/Kotlin-Android/HTML-CSS-JS-config) + decision rules (когда ООП/функциональный стиль/класс/модуль/plain script; деление файлов; оформление конфиг/ shell/утилит) + anti-shitcode антипаттерны + интеграция routing (выбор subagent по языку/задаче) и reviewer/verifier (минимальный расход токенов, детерминированные checks). **Спроектировать, не написать метод и не внедрить.** | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], [[02-Methods/verifier-pattern]], [[02-Methods/multi-agent-pipeline]], [[03-Projects/dotfiles]] |
| T-083 | Эволюция `ecosystem-map` (T-069 / Pip-Boy) из визуального артефакта в рабочий planning UI: карта показывает **узлы проектов** + **глобальный слой** + **capture sources** + **planned upgrades** + **tensions/tech debt** + **status of methods and agents**; связи capture→узел→planned upgrade→зависимость, tension→узел. Planning-роль карты; runtime-контракт — отдельный open question, не утверждать. **Спроектировать planning-интерфейс, не внедрять runtime.** | P3 | [[06-Audits/2026-08-02-upgrade-planning-seed]], T-069 |

### Контур ecosystem upgrade plan v1 (seed → plan: `06-Audits/2026-08-03-ecosystem-upgrade-plan-v1`)
| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| T-090 | dv-hub acceptance restoration — восстановление acceptance-поверхности dv-hub до любого kernel-overlay: минимальный test-gate (`tests/` пуст, `npm test` exit 1 → наполнить первые tests + CI test-step), runtime health (Telegram auth 404 — G-D-RUN-1; D1 migration incomplete — G-D-RUN-2), docs reconciliation (ADR Zomro↔Fornex G-D-DOC-1, README 5 vs 7 G-D-DOC-2, VibeOS 6 vs 5 G-D-DOC-3). **Recovery gate, не kernel-апгрейд; wording: «operational integration with global nerve is not confirmed». Не первая kernel-цель.** | P2 | [[06-Audits/2026-08-03-dv-hub-phase-d-audit]], [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]], [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[03-Projects/dv-hub]] |
| T-091 | Security finding normalization format — зафиксировать формат доказательной спецификации security-находок до stable fact: exact package, version range, advisory ID (GHSA/CVE), impact, exploitability assessment for project codepath, source/date, fix availability. **Design format, не правка карточек; применяется к dv-hub Hono candidate/unverified finding и рамочно к экосистеме.** | P2 | [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]], [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[04-Memory/facts]] |
| T-092 | prompt-engineer / task-compiler layer — спроектировать двухрежимную прослойку (режим 1 `prompt-normalizer`: свободная задача → цель/ограничения/контекст/DoD → spec; режим 2 `task-compiler`: знает roster/routing/порядок/артефакты → pipeline) перед routing/guardian/meta; цепочка пользователь → prompt-engineer spec → guardian → meta/planner execution. **Design/proposal, не внедрение; кандидат Phase 2 global role extraction.** | P3 | [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[06-Audits/2026-08-02-upgrade-planning-seed]], T-047 |
| T-093 | Global role extraction sequence — спроектировать последовательность подъёма глобальных ролей (sysop / researcher / reviewer / guardian / prompt-engineer / verifier) как global role kernel + local extensions; explicit decision о порядке (одним батчем или по приоритету) и о границах (meta vs guardian подчинение/параллель/ортогональ). **Design/proposal, не внедрение; зависит от kernel contracts Phase 1.** | P3 | [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[06-Audits/2026-08-02-upgrade-planning-seed]], T-070, T-071, T-072 |
| T-094 | Engineering-style-contract drafting/approval — draft `engineering-style-contract` как planned artifact (общее ядро + language profiles TS/JS/Python/Shell/Config-docs + anti-shitcode patterns + routing table + reviewer/verifier integration с детерминированными checks) из ecosystem plan v1 §engineering-style-contract; approval gate через guardian/reviewer до оформления в `02-Methods/`. **Draft+approval, не внедрение и не метод в `02-Methods/` пока.** | P3 | [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[06-Audits/2026-08-02-upgrade-planning-seed]], T-082, T-078 |
| T-095 | Declaration-vs-reality reconciliation mechanic — спроектировать permanent meta-mechanic сверки декларации (карточка/INDEX/VibeOS) ↔ факта (репо/инфра) как diff-based drift audit (auto `card ↔ repo ↔ AGENTS ↔ VibeOS`); применимо к dv-hub (G-D-DOC-1..4) и рамочно к экосистеме. **Design mechanic, не разовый аудит; кандидат-meta proactive loop.** | P3 | [[06-Audits/2026-08-03-dv-hub-phase-d-addendum]], [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]], [[06-Audits/2026-08-02-upgrade-planning-seed]] |

## 🟤 Backlog — идеи на потом

| ID | Задача | Приоритет | Связано |
|----|--------|-----------|---------|
| | _Пока пусто._ | | |

## ✅ Done — выполнено

| ID | Задача | Приоритет | Когда | Связано |
|----|--------|-----------|-------|---------|
| T-098 | SERPlux test-metrics docs-sync after WIP merge — performed run на WIP (254 collected) после merge + update executed section в `serp/docs/test-metrics.md`; sync artifact claims (карточка SERPlux, `serp/AGENTS.md`, `docs/verification.md`, `serp/TASKS.md`) → единый source-of-truth, replaces stale 224/172/95/111. Зависит от WIP merge (executed run на WIP остаётся `[проверить]`). Закрывает docs-sync часть T-087. **Выполнено 2026-08-04:** WIP смёржен в HEAD `f7ccd3e`; executed run = **256 collected, 256 passed, exit 0**; `docs/test-metrics.md` обновлён до канона (executed 256/256, definitions 212); sync claims → записан техдолг в `serp/docs/techdebt.md` (запись 2026-08-04, «Test-metrics claims не синхронизированы с каноном») — реализация за пользователем при проектной работе, НЕ за librarian. | P2 | 2026-08-04 | T-087, [[03-Projects/SERPlux]] |
| T-097 | Live Bun plugin import + hook-fire smoke — подтвердить live загрузку плагинов (`plugins/*.{js,ts}`) и срабатывание hook (`event` catch-all, `tool.execute.before`, `experimental.session.compacting` `(input, output)` / `output.context`) в реальной agent session через OpenCode runtime (Bun), а не только статические/runtime discovery checks (`scripts/check-plugins.mjs`, `opencode debug config`, headless `opencode serve`). **Residuals `[проверить]` (после partial smoke):** реальный compaction event session-dispatch; commit-guard на реальном `git commit` (обе безопасно непротестированы). Закрывает последние `[проверить]` T-084/T-088. **Verification task, не design contract; зависит от T-084.** | P2 | 2026-08-04 | T-084, T-088, [[04-Memory/facts]] |
| T-096 | Execution sequencing / live adoption gate — зафиксировать порядок исполнения ecosystem upgrade plan v1 как gate-sequence: Phase 1 kernel stabilization → Phase 2 SERPlux first adoption → Phase 3 dotfiles/global hardening → Phase 4 dv-hub recovery; global layer на полшага впереди SERPlux, не big-design-upfront; dv-hub не первый kernel target. **Planning artifact (= execution sequence note), не внедрение и не правка кода.** | P3 | 2026-08-04 | [[06-Audits/2026-08-03-execution-sequence-note]], [[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]] |
| T-089 | Runtime gate enforcement — зафиксировать runtime-механизм `verify=PASS → finalize` для closed-loop `/loop`→`/done`. **Подтверждённая часть:** `commit-guard` через `tool.execute.before` повторно запускает pytest и блокирует `git commit` при FAIL = runtime gate для testable DoD в working tree. **Unresolved:** полный gate на отдельный `verifier PASS` marker/state не реализован — payload capture для subagent/task в `tool.execute.after` не подтверждён `[проверить]`, verifier остаётся read-only; real `git commit` smoke для commit-guard `[проверить]`. Зависит от loader-контракта (T-084) и reviewer/verifier split (T-085). T-086 `/done` memory-model adaptation нужна раньше полного finalize-chain. **Design contract, не внедрение harness. Статус Planned (НЕ done).** | P3 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-addendum]], T-084, T-085, T-086 |
| T-087 | Test-metrics normalization contract — различать test definitions (grep `def test_`), documented suite claims per artifact, pytest total; единый source-of-truth по тестовому покрытию в карточке/AGENTS/docs. **Design contract, не правка claims артефактов отдельно от нормализации.** **Active progress, НЕ Done:** verified measurement this gate (isolated worktree) — clean canonical HEAD SERPlux `ee28637`: pytest executed 248 collected, 248 passed, 0 failed, 0 skipped, 0 errors, exit 0; `rg def test_`=204 (separate metric). Working tree WIP (uncommitted): collected=254, 254/254 remains unverified/not canonical (executed run на WIP не проводился this gate). `docs/test-metrics.md` exists но executed section stale; live docs claims 224 (`serp/AGENTS.md`)/172 (`docs/verification.md` CI)/95 (`serp/TASKS.md` T-001)/111 (карточка SERPlux) + grep=94 остаются stale/untyped; test definitions — отдельный metric, old grep=94 source untraceable. T-087 contract evidence достаточен для executed metric; task остаётся Active до docs-sync / source-of-truth update. **Выполнено 2026-08-04:** канон `docs/test-metrics.md` актуализирован на HEAD `f7ccd3e` (executed 256/256, definitions 212); sync stale claims → техдолг (см. T-098). | P2 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-audit]], [[06-Audits/2026-08-03-serplux-phase-c-addendum]] |
| T-086 | `/done` memory-model adaptation — адаптация `/done` под docs-based vs vault-based memory-модели (общая абстракция `/done` + `/dream` либо разделение «волтовский vs проектный flush»); зависит от verifier split (T-085). **Active progress, НЕ Done:** глобальная `/done` (source `~/dotfiles/opencode-global/.config/opencode/command/done.md`) получила generic memory-model branches — vault-based (`04-Memory`/vault-маркеры), docs-based (`docs/decisions`/`progress`/`techdebt` + локальные `TASKS`/`AGENTS`), fallback; неоднозначная модель → явный вопрос пользователю. `/commit` dependency explicit — делегирует проектной `/commit` (`.opencode/command/commit.md`) или глобальной с проверкой доступности в проекте; global `/commit` НЕ assumed. `/done` явно НЕ гарантирует T-089 verifier PASS/runtime gate. Source и resolved stow path идентичны. **Implementation uncommitted** (`done.md` modified, не staged). Vault refs update — отдельный follow-up, не часть T-086 implementation. T-086 НЕ объявляется Done: dotfiles working tree uncommitted + vault refs follow-up + T-089 verifier/runtime gate не закрыт. **Выполнено 2026-08-04:** `done.md` закоммичен в dotfiles, vault refs (commands.md, facts, active-context, TASKS) обновлены. | P3 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-addendum]], [[06-Audits/2026-08-02-upgrade-planning-seed]], [[01-Reference/commands]] |
| T-085 | Reviewer/verifier split contract — разделить `reviewer` (quality) и `verifier` (acceptance) как global role kernel + local extensions; явная декларация в карточках, какой verifier закрывает closed-loop. **Design contract, не правка файлов проектов.** **Выполнено 2026-08-04:** в SERPlux создан project-local `.opencode/agents/verifier.md` (acceptance-only, edit deny, `python -m pytest -v`, VERDICT PASS/FAIL); `/loop` `@verifier` резолвится проектным verifier; debug config видит reviewer+verifier; merge behavior permissions allowlist — наблюдение `[проверить]`. | P2 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-audit]], [[06-Audits/2026-08-03-serplux-phase-c-addendum]], [[02-Methods/verifier-pattern]] |
| T-088 | SERPlux plugin stabilization — стабилизация `commit-guard.js` (ESM SyntaxError) и `env-guard.js` (named-export без default, webfetch gap) в `serp/.opencode/plugins/` после прояснения loader-контракта (T-084). Стабилизировано в working tree: webfetch check перенесён внутрь catch-all `tool.execute.before` (неканоничный `tool.execute.before.webfetch` удалён), smoke allow/block прошёл. **Implementation НЕ committed.** Residuals `[проверить]`: commit-guard на реальном `git commit` (T-097). **Выполнено 2026-08-04:** закоммичено в SERPlux. | P2 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-audit]], T-084, T-097, [[03-Projects/SERPlux]] |
| T-084 | Plugin loader / compaction contract — зафиксировать loader-контракт OpenCode для `.opencode/plugins/*.{js,ts}` (default vs named exports, обязан ли `export default`) и канонические hook keys (`tool.execute.before`, `event` catch-all, `experimental.session.compacting` `(input, output)` / `output.context`). Блокирует стабилизацию guard-плагинов и verifier runtime-gate. **Design contract, не правка кода проектов.** Loader/compaction contract стабилизирован в working tree; live Bun import/registration всех 4 плагинов подтверждён; `experimental.session.compacting` function-level fire и `tool.execute.before` registration/fire confirmed; реальный compaction session-dispatch остаётся `[проверить]`. | P2 | 2026-08-04 | [[06-Audits/2026-08-03-serplux-phase-c-audit]], [[06-Audits/2026-08-03-serplux-phase-c-addendum]], [[06-Audits/2026-08-02-upgrade-planning-seed]], T-097 |
| T-066 | mark.py: `break`→`continue` на FloodWaitError + `time.sleep(fw.seconds+1)` — не прерывать остальные message_ids | P2 | 2026-07-09 | [[03-Projects/vault]], [[02-Methods/verifier-pattern]] |
| T-067 | Smoke-тест: проверка эмодзи из EMOJI_MAP против Telegram API (GetAvailableReactions). `test_smoke.py`, маркер `--smoke`, 1 PASS (74 доступных, все 7 валидны) | P3 | 2026-07-09 | [[02-Methods/tool-integration-pattern]], [[02-Methods/verifier-pattern]] |
| T-062 | `/capture` команда + `tools/telegram-capture/` — Telethon-скрипт: извлечение постов из группы @inbox_tools по теме, маркировка реакциями, JSON-вывод для librarian. Восстановлена `/inbox` (обработка 99-Inbox). **Ждёт первый запуск (установка зависимостей + авторизация)** | P2 | 2026-07-08 | [[02-Methods/tool-integration-pattern]], [[03-Projects/vault]] |
| T-065 | VibeOS.md v0.3.0 — раздел «Инструменты (tools/)», новый метод в таблице, Linux UX Lab в направлениях, чейнджлог | P3 | 2026-07-07 | [[VibeOS]] |
| T-064 | Linux UX Lab — направление R-006 в 99-Inbox: систематический апгрейд UX Linux (Manjaro), источник идей — Telegram группа, связь с dotfiles | P3 | 2026-07-07 | [[99-Inbox]], [[03-Projects/dotfiles]], [[VibeOS]] |
| T-063 | `tool-integration-pattern` — седьмой метод VibeOS (02-Methods/): «LLM думает, API делает» — внешние API как детерминированные инструменты агентов | P2 | 2026-07-07 | [[02-Methods/tool-integration-pattern]], [[VibeOS]] |
| T-059 | dotfiles: verifier-pattern (🟡→✅) — создать verifier.md агента по образцу SERPlux | P1 | 2026-07-03 | [[03-Projects/dotfiles]], [[02-Methods/verifier-pattern]] |
| T-060 | dotfiles: closed-loop (🟡→✅) — создать /loop команду + verifier | P1 | 2026-07-03 | [[03-Projects/dotfiles]], [[02-Methods/closed-loop]] |
| T-061 | memory-management flush-протокол (🟡→✅) — формализация pre-compaction flush в dotfiles + vault | P1 | 2026-07-03 | [[02-Methods/memory-management]], [[03-Projects/dotfiles]], [[03-Projects/vault]] |
| T-069 | `tools/ecosystem-map/` — интерактивная карта развития экосистемы в стиле Pip-Boy (468 постов → 36 навыков → 326 инструментов). Вкладки: НАВЫКИ/СПОСОБНОСТИ/ИНСТРУМЕНТЫ/ПРОЕКТЫ. CRT-эффекты, фильтры, привязка к проектам | P2 | 2026-07-13 | [[02-Methods/tool-integration-pattern]], [[99-Inbox]] |
| T-045 | SERPlux: мультиклиентность + мультипровайдерность (Web UI ⏸ приостановлено) | P1 | 2026-07-03 | [[03-Projects/SERPlux]] |
| T-051 | Git pre-commit hook + commit-guard плагин (tool.execute.before) — неотвратимый гейт: pytest перед коммитом | P1 | 2026-07-03 | [[03-Projects/SERPlux]], [[01-Reference/plugins]] |
| T-058 | plan-агент SERPlux: делегирование build через task-tool. plan.md (был inline в opencode.json), права task.build: allow, edit/bash deny | P2 | 2026-07-03 | [[03-Projects/SERPlux]] |
| T-057 | commit-guard: pytest-вывод захвачен через `.quiet()`, не засоряет TUI | P1 | 2026-07-03 | [[03-Projects/SERPlux]], [[01-Reference/plugins]] |
| T-056 | Инфраструктурный техдолг Уровня 0: модель librarian, verifier, факты, /done, session-flush | P1 | 2026-07-03 | [[01-Reference/agents]], [[01-Reference/commands]], [[01-Reference/plugins]], [[04-Memory/facts]] |
| T-052 | Глобальный мета-агент infra (@meta) — создан ~/.config/opencode/agent/meta.md, виден из всех проектов | P1 | 2026-07-02 | [[01-Reference/agents]] |
| T-044 | SERPlux: создать ui-dev + infra-dev агентов, команды /interface /container /deploy, актуализировать карточку | P1 | 2026-07-02 | [[03-Projects/SERPlux]] |
| T-020 | Создать VibeOS — концептуальный дашборд системы вайбкодинга | P2 | 2026-06-30 | [[VibeOS]] |
| T-021 | Смена модели librarian Claude Sonnet 4.6 → DeepSeek v4-flash-free | P2 | 2026-06-30 | [[04-Memory/facts.md]] |
| T-022 | Ревью волта: исправить 17 багов (статусы, модели, команды, docs) | P1 | 2026-06-30 | [[Architecture]] |
| T-023 | Инициализировать OpenCode в dotfiles — sysop, /sysaudit | P3 | 2026-06-30 | [[03-Projects/dotfiles]] |
| T-024 | dotfiles v2 — мульти-агентная архитектура (7 агентов, 8 пайплайнов) | P2 | 2026-06-30 | [[03-Projects/dotfiles]] |
| T-025 | distill-pipeline + multi-agent-pipeline метод | P2 | 2026-06-30 | [[02-Methods/multi-agent-pipeline]] |
| T-026 | Создать README.md — визитка репозитория как VibeOS | P1 | 2026-06-30 | [[README]] |
| T-027 | Добавить лицензию GPL-3.0 + секция в README (copyleft, коммерция, фонд инженера) | P1 | 2026-06-30 | [[LICENSE]] |
| T-043 | SERP Factory — архитектура в волте: SERPlux как продукт, агенты ux-dev + infra-dev, команды /interface /container /deploy | P1 | 2026-06-30 | [[03-Projects/SERPlux]] |
| T-019 | Инициализировать OpenCode в dotfiles — sysop, /sysaudit | P3 | 2026-06-30 | [[03-Projects/dotfiles]] |
| T-000 | Переименовать `99-Inbox.md.md` → `99-Inbox.md` | P0 | 2026-06-27 | — |
| T-000 | Убрать claude-mem из всей базы | P0 | 2026-06-27 | [[01-Reference/memory.md]] |
| T-000 | Создать OKF-подбандл памяти `04-Memory/` | P0 | 2026-06-27 | [[04-Memory/index.md]] |
| T-000 | Исправить `external_directory` librarian (ask → allow) | P0 | 2026-06-27 | [[.opencode/agent/librarian.md]] |
| T-000 | Применить OKF v0.1 ко всему волту | P1 | 2026-06-27 | [[index.md]] |
| T-000 | Обновить `00-INDEX.md` под OKF | P1 | 2026-06-27 | [[00-INDEX.md]] |
| T-000 | Обновить `AGENTS.md` — убрать claude-mem, новая память | P1 | 2026-06-27 | [[AGENTS.md]] |
| T-000 | Обновить `Architecture.md` — OKF-структура | P1 | 2026-06-27 | [[Architecture.md]] |
| T-000 | Наполнить `rules-AGENTS.md` | P1 | 2026-06-27 | [[01-Reference/rules-AGENTS.md]] |
| T-000 | Создать `TASKS.md` — трекер задач волта | P1 | 2026-06-27 | [[TASKS.md]] |
| T-000 | Создать команду `/commit` | P1 | 2026-06-27 | [[.opencode/command/commit.md]] |
| T-000 | Прописать авто-документирование в librarian.md | P1 | 2026-06-27 | [[.opencode/agent/librarian.md]] |
| T-000 | Добавить `/commit` в 01-Reference/commands.md | P1 | 2026-06-27 | [[01-Reference/commands.md]] |
| T-001 | Создать `opencode.json` в корне волта (с `$schema`) | P1 | 2026-06-27 | [[opencode.json]] |
| T-002 | Проверить консистентность `wikilink` ссылок по всему волту | P1 | 2026-06-27 | [[DEVELOPMENT-ROADMAP]] |
| T-003 | Наполнить `config.md` — OpenCode Zen провайдер | P2 | 2026-06-27 | [[01-Reference/config.md]] |
| T-004 | Наполнить `config.md` — doom_loop, budget, steps (cost control) | P2 | 2026-06-27 | [[01-Reference/config.md]] |
| T-005 | Наполнить `permissions.md` — skills, doom_loop | P2 | 2026-06-29 | [[01-Reference/permissions.md]] |
| T-006 | Наполнить `plugins.md` — Plugin SDK (@opencode-ai/plugin) | P2 | 2026-06-29 | [[01-Reference/plugins.md]] |
| T-007 | SERPlux — добавить список команд в карточку | P3 | 2026-06-29 | [[03-Projects/SERPlux.md]] |
| T-008 | Обновить карточку SERPlux — актуальные статусы методов | P3 | 2026-06-29 | [[03-Projects/SERPlux.md]] |
| T-009 | Создать единую таблицу «Статус методов × Проекты» | P3 | 2026-06-29 | [[00-INDEX.md]] |
| T-010 | Создать `05-Templates/` — шаблоны проектов и методов | P2 | 2026-06-29 | [[Architecture.md]] |
| T-011 | Пре-коммит хук на проверку пустых файлов | P4 | 2026-06-29 | [[05-Templates/pre-commit-check.sh]] |
| T-012 | Плагин валидации викилинков | P4 | 2026-06-29 | [[05-Templates/pre-commit-check.sh]] |
| T-013 | Авто-архивация session-log раз в месяц | P4 | 2026-06-29 | [[05-Templates/archive-session-log.sh]] |
| T-014 | Команда `/audit` — пакетный обход проектов | P3 | 2026-06-29 | [[.opencode/command/audit.md]] |
| T-018 | Сводка состояния проектов на дашборд | P3 | 2026-06-29 | [[00-INDEX.md]] |

---

## Как работать с трекером

1. **Каждая сессия** — librarian читает TASKS.md, выбирает задачу из **Planned**, переносит в **Active**.
2. **Начал задачу** — перемести строку в `🟡 Active`. Обнови `active-context.md`.
3. **Сделал задачу** — перемести строку в `✅ Done`, укажи дату. Обнови `active-context.md`.
4. **Задача заблокирована** — `⛔ blocked` с причиной.
5. **Новая идея** — добавь в `🟤 Backlog` или в `99-Inbox.md`.

Каждая задача содержит:
- **ID** — T-NNN (уникальный номер)
- **Описание** — что конкретно сделать
- **Приоритет** — P0..P4
- **Связано** — `wikilink` на файл/карточку/метод

Номера ID в Done — T-000 для задач первой волны (без сквозной нумерации), T-001+ для нумерованных задач.
T-066/067 — последние выполненные (mark.py FloodWait, smoke-тест эмодзи). T-068 — последняя запланированная (doc-converter концепция).
