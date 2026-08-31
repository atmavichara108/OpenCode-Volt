---
type: Research
title: Vault Upgrade Research — token-optimization & vibe-coding 2026-08-02
date: 2026-08-02
tags: [vault, token-optimization, vibe-coding, research]
---
# Vault Upgrade Research — нетривиальные апгрейды для экономии токенов и усиления вайбкодинга

> Источник запроса: исследование OpenCode-Vault на предмет передовых open-source
> утилит/демонов/архитектур для снижения token spend, контекстной компрессии,
> кэширования, долговременной памяти, локальной индексации, closed-loop агентности,
> наблюдаемости и Telegram/daemon-интеграции.
> Правила: только проверяемые факты; неподтверждённое помечать `[проверить]`;
> ссылки на репозитории обязательны; не выдавать маркетинг за измеренный результат;
> не делать вид, что интеграция подтверждена, если нет источника.

## Executive summary

Волт — сильная, зрелая система (OKF v0.1, 8 методов, 4 карточки, plugin-слой с
`tool.execute.before`, `session-flush`, `verifier`, `closed-loop`, `model-routing`,
`tool-integration-pattern`). Главный системный пробел — **нет observability по
токенам/стоимости и нет semantic-retrieval поверх facts/inbox/session-log**. Поэтому
дистиллированные методы (model-routing, distill) работают «вслепую»: экономия от
дешёвой модели не измеряется, повторное чтение одних и тех же файлов агентами не
дедуплицируется, facts.md растёт линейно и грузится целиком при старте сессии.

Подтверждено с opencode.ai/docs (2026-08-02): OpenCode **нативно** поддерживает
**MCP-серверы** (local+remote, через `mcp`-блок `opencode.json`),
**Custom Tools** (`@opencode-ai/plugin` `tool()`, в `.opencode/tools/` или
`~/.config/opencode/tools/`, может вызывать Python через `Bun.$`) и
**Agent Skills** (`SKILL.md` с `name`/`description`, `skill`-tool с permissions).
Это снимает главный интеграционный риск: предлагаемое не требует патчей OpenCode.

Из ~20 просмотренных кандидатов отобрано 8 (по приоритетам P0 / P1 / Watch):

- **P0 (vault-level, без кода приложений):**
  1. Mem0 (через skills-стандарт — OpenCode уже в списке поддерживаемых клиентов).
  2. sqlite-vec (локальный SQLite-векторный индекс над facts/inbox/session-log).
  3. Custom Tool `token-budget` + `audit-log` (нативные Custom Tools OpenCode).
- **P1 (отдельный локальный daemon):**
  4. LiteLLM Proxy (AI Gateway: spend tracking, MCP-агрегатор, virtual keys).
  5. Langfuse self-host (observability + cost/trace, native LiteLLM-интеграция).
  6. Aider repo-map **паттерн** (tree-sitter + ранжирование символов) — реализовать
     как Custom Tool для SERPlux/dv-hub, не устанавливая сам Aider.
- **Watch (перспективно, но дорого/рискованно):**
  7. Graphiti (временной knowledge-graph как MCP-сервер; требует Neo4j/FalkorDB).
  8. Letta (MemGPT-наследник; архитектурно интересен, но V1-сервер в legacy,
     активная разработка ушла в `letta-code` — отдельный coding-агент).

Самое дешёвое по внедрению и самое прямое по ROI: **Mem0 + sqlite-vec** (закрывает
«long-term память без перечитывания facts») и **Custom Tool для telemetry**
(закрывает «нет измерения токенов»). LiteLLM+Langfuse — `P1`, отдельный docker,
но это единственный способ увидеть реальный token spend по всем проектам и агентам.

---

## Current-state audit

### Что уже есть и работает (подтверждено по файлам волта)

| Механизм | Где | Источник |
|----------|------|----------|
| Model routing (static) | dv-hub ✅ (5 агентов/4 модели), SERPlux ✅ (6/3), vault ➖ | `02-Methods/model-routing.md`; `04-Memory/facts.md` |
| Distill-pattern (команды) | 9 (vault) + 10 (dotfiles) + 7 (dv-hub) + 5 (SERPlux) | `02-Methods/distill-pattern.md` |
| Memory-management + pre-compaction flush | dotfiles ✅, vault ✅ (`/flush` + `session-flush.ts`), SERPlux 🟡, dv-hub 🟡 | `02-Methods/memory-management.md`; `~/.config/opencode/plugins/` |
| Verifier-pattern | SERPlux ✅, dotfiles ✅; dv-hub ❌, vault ❌ (справочник) | `02-Methods/verifier-pattern.md` |
| Closed-loop (`/loop`) | SERPlux ✅, dotfiles ✅ (HARD STOP 5) | `02-Methods/closed-loop.md`; `~/.config/opencode/command/loop.md` |
| Multi-agent-pipeline + Factory-variant | dotfiles ✅, SERPlux ✅ | `02-Methods/multi-agent-pipeline.md` |
| Tool-integration-pattern (`tools/`) | vault 🟡: telegram-capture (Telethon+Tor), ecosystem-map | `02-Methods/tool-integration-pattern.md`; `tools/` |
| Plugin SDK `tool.execute.before` | commit-guard (SERPlux), env-guard, notify, compaction, session-flush | `01-Reference/plugins.md` |
| OKF-память (active-context/facts/session-log) | `04-Memory/` | `Architecture.md` |
| Трекер задач + roadmap | TASKS.md, DEVELOPMENT-ROADMAP.md | — |
| direnv + .venv (vault, SERPlux) | авт. активация Python venv | `04-Memory/facts.md` |

### Заявлено, но не измеряется

- **model-routing** — экономия 51% против uniform Opus заявлена в методе как
  расчётная, но в волте **нет инструментальной telemetry**, чтобы подтвердить
  фактический token spend по агенту/модели/проекту. Границы `doom_loop` и
  `steps` заданы, `budgetTokens` в конфиге волта **не включён** (`facts.md`:
  «не требуется для командного центра»).
- **distill-pattern / commands** — цифр по вызовам команд и jejich token-cost нет.
- **verifier / closed-loop** — `HARD STOP 5` стоит, но числоverify-циклов на
  задачу не пишется в файл; трудно оценить, когда дешёвая модель в петле съедает
  экономию (прямо warning в `model-routing.md`).
- **session-flush** — копит `file.edited`, но обычные `task`-агенты general
  и их LLM-вызовы логируются только в session-log текстом.

### Где токены тратятся напрасно (gap candidates)

1. **Полное перечитывание facts.md при старте сессии.** `facts.md` уже ~129 строк
   и растёт. librarian читает его весь — linear O(n) по входным токенам. Это
   базовый gap, который Mem0/sqlite-vec закрывают top-k retrieval.
2. **Отсутствие semantic cache / дедупликации исследований.** Один и тот же
   пост из @inbox_tools может попасть в capture, потом в инбокс, потом в
   карточку — и каждый раз читается заново. Нет индекса «мы это уже разбирали».
3. **Нет context-budget перед делегацией субагенту.** librarian делегирует в
   general без явной проверки, что целевой контекст (+новые артефакты) влезет
   в лимит модели. Возможен тихий overflow → compact с потерей.
4. **telegram-capture → /inbox → карточка: полностью ручная координация LLM.**
   7-step процесс в SKILL.md, классификация делается librarian'ом руками каждый
   раз. Категорийная реакция уже детерминирована, но «к какому проекту? какой
   приоритет?» решает LLM — это регулярный повтор.
5. **Слабые границы между facts/Inbox/memory/project-cards.** Они текстовые
   markdown без версионирования во времени. Факт «модель librarian =
   qwen3.7-plus» уже пережил миграции (DeepSeek → Go-подписка), и в `facts.md`
   он перезаписывается, теряя provenance «когда стало правдой».
6. **Нет фонового индексатора/репо-карты.** build-агенты SERPlux/dv-hub при
   навигации по незнакомому файлу ходят `grep`/`read` вслепую — типичный
   «Aider solves»-сценарий, где tree-sitter repo-map экономит exploration-токены.
7. **Нет token/cost telemetry.** Ключевой gap: нет ни одного источника правды
   «сколько за прошлую неделю ушло на SERPlux build vs dv-hub plan».
8. **Ручная координация librarian → general.** librarian в читает волт и
   принимает решения о маршрутизации, но сам не может вызвать детерминированный
   «cache命中?»-tool, чтобы не перезапускать исследование повторно.

### Чего внедрять НЕ надо (anti-goals из AGENTS.md / сложности)

- **Не править код приложений `*.py`/`*.gs`** — librarian только через build.
  Любой инстумент, требующий деплоя в `serp/` код — зона build-агентов.
- **Не вводить claude-mem обратно** — уже однажды удалён (`facts.md`,
  T-000 «Убрать claude-mem»). Внешний MCP-сервис памяти в редеплой-форме —
  риск рецидив. Память — на диске, версионная (git). Это(filter) исключает
  Letta managed / Zep cloud и оправдывает preference для self-hosted/sqlite.
- **Не разветвлять репо продуктовой логикой** — SERPlux FLAT layout,
  ADR Sheets-only UI. Любой observability-стек должен жить в волте/daemon,
  не в `serp/`.
- **Не переустанавливать OpenCode-замену** (Aider/Cursor/Goose/OpenHands) —
  нарушает принцип centralized-know::OpenCode. Их можно изучать только как
  **архитектурные референсы** (repo-map, compaction, subagents, verification).

---

## Selection criteria

Кандидат проходит фильтр, если выполнено ≥3 из 5:
1. **Реальный open-source проект** с публичным репо/лицензией (не выдумка).
2. **OpenCode-native путь интеграции** (MCP / Custom Tool / Skill / Plugin) —
   либо отсутствие необходимости патчей.
3. **Прямой token ROI**: кэш/компрессия/индекс/retrieval/budget — не «удобнее»,
   а «меньше токенов» или «измеримо».
4. **Не противоречит anti-goals** (файловая память, не код приложений,
  не замена OpenCode).
5. **Самостоятельность** (есть зрелость/активность — stars, commits, releases).

Подтверждение OpenCode-native:
- Skills: https://opencode.ai/docs/skills/ (проверено 2026-08-02) — SKILL.md,
  `name`+`description`, нативный `skill`-tool, permissions (`allow`/`deny`/`ask`).
- MCP: https://opencode.ai/docs/mcp-servers/ — `mcp` блок в `opencode.json`,
  local (`command: [...]`) и remote (`url`), OAuth, per-glob disable.
- Custom Tools: https://opencode.ai/docs/custom-tools/ — `@opencode-ai/plugin`
  `tool()`, `.opencode/tools/` или `~/.config/opencode/tools/`, может вызывать
  Python через `Bun.$`. Имя инструмента = имя файла.

---

## P0 candidates (vault-level, без кода приложений)

### 1. Mem0 — универсальный memory-layer (через OpenCode skills)

- **URL/ репо / лицензия:** https://github.com/mem0ai/mem0 (Apache-2.0, ~62.3k★,
  2,541 commits, Y Combinator S24). Документация: https://docs.mem0.ai
- **Что делает:** memory-layer для AI-агентов с multi-level memory
  (user/session/agent), hybrid retrieval (semantic + BM25 + entity matching).
  April-2026 new algorithm: single-pass ADD-only extraction (1 LLM-call на add),
  entity-linking, temporal reasoning; benchmark LoCoMo 92.5 (+21 pt).
- **Token/контекст-механизм:** вместо «гружу всю facts.md» — top-k retrieval
  (~6.8K tokens на retrieve вместо всей истории). Single-pass extraction
  означает: на каждом ADD — ровно 1 LLM-call_extractor (дёшев, детерминирован).
- **Реальный fit с vault:** Mem0 в README **явно перечисляет OpenCode** среди
  клиентов skills-стандарта (раздел «Agent Skills»:«Claude Code, Codex, Cursor,
  Windsurf, OpenCode, OpenClaw, and any tool that supports the skills standard»).
  Это подтверждённая интеграция, не маркетинг. Конкретно:
  `npx skills add https://github.com/mem0ai/mem0 --skill mem0` — кладёт
  `SKILL.md` в `~/.claude/skills/`, который OpenCode и поддерживает
  (`.claude/skills/*/SKILL.md` — подтверждено в `/docs/skills/`).
- **Зрелость:** high — managed cloud + OSS self-host (`docker compose up`),
  Python+TS SDK, CLI (`@mem0/cli`), MCP-интеграции (Claude/Cursor插件).
- **Интеграционный риск:** **M**. Чтобы не нарушать anti-goal «память на диске,
  git-версионная», использовать **только self-hosted OSS** (`mem0ai` + локальный
  векторный стор — Qdrant/Chroma), **не cloud**. Данные памяти живут рядом с
  vault (`.mem0/` или SQLite). Скилл `mem0` автогрузится в `skill`-tool, агент
  сам решает когда его вызывать — ленивая подгрузка (matching `description`).
- **Цена внедрения:** S–M. `pip install mem0ai` в `vault/.venv`, добавить скилл
  в `~/.config/opencode/skills/mem0/` (или через `npx skills add`), прописать
  PermissionRule `skill:"mem0": allow` в opencode.json. Опционально self-host
  сервер (`cd server && make bootstrap`) если нужна dashboard/auth.
- **Критерий успеха:** librarian при старте сессии вместо `read facts.md`
  (весь файл) делает `memory.search(query=текущий_фокус, top_k=5)`; факт
  «модель librarian = qwen3.7-plus» возвращается за ~6K токенов вместо
  «весь facts.md ≈ N строк». Команда измерения:
  `opencode ... /ask "какая модель librarian?"` → сравнить число entry-tokens
  до/после (логируем через P1 telemetry).
- **Rollback:** удалить скилл и `.mem0/` (или SQLite). Все原生 facts/inbox
  остаются в markdown — потерян только векторный индекс.

### 2. sqlite-vec — локальный векторный индекс (pure-C SQLite extension)

- **URL/репо/лицензия:** https://github.com/asg017/sqlite-vec (MIT + Apache-2.0,
  ~8.0k★, 464 commits, Mozilla Builders project).
- **Что делает:** SQLite-расширение `vec0` для vector search (float/int8/binary),
  pure C, no deps, работает где работает SQLite (incl. WASM/browsers). KNN-query
  через `MATCH` + `ORDER BY distance LIMIT k`.
- **Token/контекст-механизм:** даёт **локальную** семантическую индексацию над
  markdown-документами волта без отдельного daemon. Скрипт в `.venv` строит
  embedding'и (через `sqlite-lembed` локально из `.gguf`, либо remote
  `text-embedding-3-small`/Qwen-600M) по `facts.md`, `99-Inbox.md`, всем
  `04-Memory/session-log/*.md`. Retrieve: top-k похожих past facts/session
  notes перед делегированием — не перечитывать всё.
- **Специфично для vault:** идеально стыкуется с **direnv+.venv** конвенцией
  (`facts.md`: «каждый Python-проект использует direnv + .venv»). SQLite-файл
  живёт в `vault/.cache/vault-vec.sqlite` (gitignored). Никакого daemon.
- **Зрелость:** staged pre-v1 (явный warning «expect breaking changes»),
  но стабилен для read-mostly use-case. Active (commits в 2026).
- **Интеграционный риск:** **S**. Расширение грузится через `load_extension`
  в Python (`pip install sqlite-vec`). Главная неопределённость: где брать
  embedding-модель. Варианты: (a) `sqlite-lembed` локально из `.gguf` —
  полностью offline, но нужен gguf-файл на диске; (b) OpenAI/Qwen API —
  добавляет зависимость от external API. `[проверить]` доступность
  `sqlite-lembed` в PyPI/обновлениях.
- **Цена внедрения:** S. Один скрипт `tools/index-engine` (по образцу
  `tools/telegram-capture/` в `SKILL.md`), вызывается bash-плагином/Custom
  Tool. Чтение индекса — Custom Tool `query-memory` (нативный инструмент,
  который вызывает Python через `Bun.$`).
- **Критерий успеха:** `query-memory("DeepSeek" → про model-routing)` возвращает
  ссылки на `facts.md` и `2026-06-30` session-log за <50ms без перечитывания
  файлов. Прирост hit-rate в librarian'е: «дублирующих read'ов одного и того же
  файла в сессии снизилось» (измерить через audit-log из пункта 3).
- **Rollback:** удалить `tools/index-engine` + `.cache/vault-vec.sqlite`.

### 3. Custom Tool `token-budget` + `audit-log` (нативные Custom Tools OpenCode)

- **URL/документация:** https://opencode.ai/docs/custom-tools/ (Custom Tools),
  https://opencode.ai/docs/plugins/ (Plugin SDK, `tool.execute.before`/`after`).
- **Что делает:** два локальных TypeScript-инструмента (могут вызывать Python
  через `Bun.$`):
  - `token-budget` — по входным параметрам (agent, модель, целевой документ)
    возвращает примерное число токенов (tiktoken/sjcl-encoding) и
    `ok|overflow|truncated` verdict перед делегированием в субагента.
  - `audit-log` — на `tool.execute.after` для LLM-вызовов дописывает в
    `vault/.cache/audit.jsonl` строчку `{ts, agent, model, prompt_tokens,
    completion_tokens, cost_usd, project}`. Aggregate weekly в `04-Memory/log.md`.
- **Token/контекст-механизм:** не экономит токены напрямую, **но делает
  экономию измеримой** (закрывает gap «нет telemetry» — без неё model-routing
  неизмерим). `token-budget` предотвращает тихий overflow → compact с потерей.
- **Зрелость:** это не внешний репозиторий, это **нативный механизм**
  OpenCode (подтверждено в `/docs/custom-tools/` и `/docs/plugins/`).
  Tiktoken: https://github.com/openai/tiktoken (MIT, mature).
- **Интеграционный риск:** **S**. Лежит в `~/.config/opencode/tools/`,
  глобально виден во всех проектах через мёрж. Не трогает код приложений.
- **Цена внедрения:** S. ~50 строк TS + tiktoken-call. Опционально —
  плагин на `tool.execute.after` (Plugin SDK).
- **Критерий успеха:** после 2 недель аудита появляется первый **честный**
  weekly token/cost report по агент/модель/проект в `04-Memory/log.md`.
  Решается T-049 (профили моделей под провайдера) — теперь не «на глаз».
- **Rollback:** удалить два `.ts` файла.

---

## P1 candidates (полезно, требует отдельного локального daemon)

### 4. LiteLLM Proxy — AI Gateway / MCP-агрегатор

- **URL/репо/лицензия:** https://github.com/BerriAI/litellm (MIT — OSS core,
  есть Enterprise tier; ~55.4k★, 41k+ commits, YC W23).
  Документация: https://docs.litellm.ai.
- **Что делает:** единый gateway перед всеми провайдерами (OpenAI/Anthropic/
  Bedrock/Azure/Vertex/vLLM/Deepseek/Ollama — 100+). **Spend tracking по
  virtual keys/budgets**, load balancing, guardrails, **MCP Gateway**
  (`/mcp/` — агрегация MCP-инструментов за одним endpoint), A2A-протокол,
  admin dashboard. Прямая совместимость с OpenAI-форматом.
- **Token/контекст-механизм:** сам по себе не сжимает контекст, но:
  (a) даёт **честную spend telemetry per agent/project** — закрывает gap;
  (b) виртуальные ключи = per-project/per-agent бюджетные лимиты;
  (c) single endpoint → упрощает `model-routing` migration Zen↔Go (T-049):
    правка на сервере, а не во всех `opencode.json`.
- **Реальный fit с vault:** OpenCode `mcp` блок (подтв. `/docs/mcp-servers/`)
  может указывать на `http://localhost:4000/mcp/` — LiteLLM MCP-gateway
  становится единой точкой маршрутизации всех внешних инструментов.
  Документация LiteLLM прямо приводит Cursor IDE config `[LiteLLM]` как
  пример — аналогично OpenCode remote MCP + headers.
- **Зрелость:** очень high — listed adopters Stripe/Netflix/Google ADK/
  OpenHands. 8ms P95 на 1k RPS (по их benchmarks; `[проверить]` условия).
- **Интеграционный риск:** **M**. Требует:
  (1).Singleton `litellm --config config.yaml` daemon (или docker);
  (2)переписать `opencode.json` провайдеров во всех проектах →
  `base_url: http://localhost:4000`. Это массовая правка, делается
  через meta-агента (`~/.config/opencode/agent/meta.md`) — не librarian'ом.
  Anti-goal проверка: не код приложений, только агентная инфра — допустимо.
- **Цена внедрения:** M. Один локальный docker-compose, экспорт model
  prices (`model_prices_and_context_window.json` — в репозитории,
  обновляется в каждом релизе), правка 4× `opencode.json` (meta-агентом).
- **Критерий успеха:** dashboard показывает spend по ключам `vault-librarian`,
  `serp-build`, `serp-plan`, `dvhub-build` —weekly в `session-log`. Позволяет
  решить «заменяю ли я Sonnet на Haiku в dv-hub verifier'е?» экономически.
- **Rollback:** вернуть прямые провайдеры в `opencode.json`; остановить daemon.

### 5. Langfuse(self-host) — observability + prompt versioning + cost/trace

- **URL/репо/лицензия:** https://github.com/langfuse/langfuse (MIT — OSS,
  кроме `ee/` папки; ~32.3k★, 8314 commits, YC W23, part of ClickHouse с
  Jan 2026). Документация: https://langfuse.com/docs.
- **Что делает:** LLMOps-платформа — tracing, LLM-as-a-judge evals, prompt
  management (versioned + cached), datasets/playground/cost observability.
  Self-host через `docker compose up` (5 мин), backend ClickHouse.
  **Native LiteLLM integration** (Langfuse integration section официально).
- **Token/контекст-механизм:** не сжатие, но **полная картинка** каждого
  вызова: prompt_tokens, completion_tokens, latency, model, агент, cost.
  Trace-replay позволяет посмотреть «что реально отправилось в Sonnet после
  компакции» — критично для отладки `session-flush`/`/dream`/compact loop.
  Prompt management + cache снижает latency итерации по prompts.
- **Реальный fit с vault:** P0 audit-log (кандидат 3) — ручная минималка;
  Langfuse — промышленная версия того же. Если LiteLLM уже стоит (кандидат 4),
  Langfuse подключается через его callback за минуты. Может быть **второй
  фазой после LiteLLM** (не отдельно).
- **Зрелость:** production-grade, self-host в production (Kubernetes Helm,
  AWS/Azure/GCP Terraform). MIT — self-hosted без vendor lock-in.
- **Интеграционный риск:** **M–L**. ClickHouse+Redis+web+worker docker compose
  — относительно тяжело для «_single пользователю». Альтернатива — Langfuse
  Cloud free tier (privacy trade-off, нарушает «память у нас»). Рекомендовать
  self-host только если уже разворачивают LiteLLM + есть машину ресурсов.
- **Цена внедрения:** M–L. Один docker-compose, LiteLLM callback config.
- **Критерий успеха:** session.idle в Langfuse показывает дерево
  librarian → general → sub-call с cost/токенами. Сравнение «до/после
  внедрения Mem0 (#1)» — visible в tracing, не «на глаз».
- **Rollback:** выключить LiteLLM callback; остановить compose.

### 6. Aider repo-map паттерн (не сам Aider) — tree-sitter + ранк

- **URL/референс:** Aider https://github.com/Aider-AI/aider (ISC-style у
  [проверить]; гиперссылка на repo-map docs 404 — высказывать как
  архитектурный паттерн). tree-sitter:
  https://github.com/tree-sitter/tree-sitter (MIT). ast-grep:
  https://github.com/ast-grep/ast-grep (MIT, CC-BY-SA for corpuses).
- **Что делает (паттерн, не установка):** строит **compact ranked symbol-map**
  репозитория: tree-sitter парсит AST, выбирает символы (functions/classes),
  ранжирует по **referencing frequency** (как часто имя встречается в коде),
  сверху-самые-связанные появляются. В итоге в промпт вставляется ~1–2KB
  компактного репо-описания вместо «grep вслепую по всем файлам».
- **Token/контекст-механизм:** прямая экономия при навигации build-агентов
  SERPlux/dv-hub по незнакомым модулям. Сейчас build делает `grep`→`read`
  несколько раз; repo-map даёт навигацию «по карте» с первого вызова.
  Особенно полезно в `closed-loop` (когда verifier возвращает FAIL по
  конкретному файлу, a build не знает соседей).
- **Зрелость:** tree-sitter и ast-grep — production-grade, mature
  (используются GitHub/Neovim/Helix). Сам Aider — production coding agent
  (не устанавливаем; только паттерн перенимаем).
- **Реальный fit с vault:** для **vault** (markdown) не нужен — нет AST.
  Для SERPlux (Python) и dv-hub (TS) — прямой fit. Реализация как Custom
  Tool `repo-map` в проектном `.opencode/tools/` (нативный механизм,
  подтверждено `/docs/custom-tools/`), который вызывает Python или
  `ast-grep` через `Bun.$`. Возвращает компактный Markdown с ranked
  symbols → build-агент вставляет в контекст.
- **Интеграционный риск:** **M**. Требует tree-sitter-парсера на каждый язык
  SERPlux — tree-sitter-python, dv-hub — tree-sitter-typescript. А
  ранжирование по referencing frequency — самописный ~200 строк.
- **Цена внедрения:** M. Один shared `tools/repo-map/` (нет в vault ещё;
  добавить в `tools/`). Вызывается Custom Tool из проектных `.opencode/tools`.
- **Критерий успеха:** в `/loop`-задачах SERPlux/build число `read`-шагов до
  первой правки снижается (измерить через audit-log #3). Качественно:
  build-агент сразу понимает модули, не «ползает по импортам».
- **Rollback:** удалить Custom Tool и `tools/repo-map/`.

---

## Watchlist (перспективно, но пока не окупается)

### 7. Graphiti / Zep — temporal knowledge-graph MCP-сервер

- **URL/репо/лицензия:** https://github.com/getzep/graphiti (Apache-2.0,
  ~29.5k★, 931 commits). Документация: https://help.getzep.com/graphiti.
  Paper: https://arxiv.org/abs/2501.13956.
- **Что делает:** **temporal context graph** — entities + facts с validity
  windows (when became true, when superseded), episodes как provenance.
  Bi-temporal tracking с auto fact-invalidation. hybrid retrieval
  (semantic + BM25 + graph traversal). Есть **MCP server** (готовый,
  `mcp_server/` в репо) — прямой путь для OpenCode (`mcp` блок).
- **Где был бы полезен:** именно для проблемы «слабые границы между
  facts/inbox/memory/project-cards + нет temporal provenance». Текущий
  `facts.md` перезаписывает факт «модель librarian = X», Graphiti хранил бы
  «истина в период 2026-06-30..2026-07-13, superseded by Y».
- **Почему Watch, не P1:**
  - требует **Neo4j 5.26** или **FalkorDB 1.1.2** (доп. daemon),
  - по умолчанию использует OpenAI для LLM+embedding извлечения фактов
    (external spend), Best works with structured-output LLMs
    (Anthropic/Gemini/OpenAI) — это extra token cost на каждый add episode,
  - bi-temporal — избыточен для волта на текущей зрелости (4 проекта,
    ~100 фактов в facts.md). Mem0 + sqlite-vec закрывают 80% случаев
    на 1% сложности.
- **Когда пересмотреть:** когда `facts.md` перерастёт ~1000 фактов с
  конфликтующей хронологией, или появятся **мульти-проектные временные
  состояния** (несколько instance одного проекта одновременно).
- **Интеграция (когда созреет):** `opencode.json` → `mcp.graphiti = {type:
  "local", command: ["python","-m","graphiti.mcp_server"]}` — нативно
  OpenCode MCP. Anti-goal: `letta-code` Cloud-drop нет, FalkorDB embedded
  (`falkordblite`, Python 3.12+) — можно локально без Neo4j daemon.

### 8. Letta (MemGPT) — stateful agents with self-editing memory

- **URL/репо/лицензия:** https://github.com/letta-ai/letta (Apache-2.0,
  ~24.1k★, 7469 commits). Активная разработка ушла в
  https://github.com/letta-ai/letta-code (отдельный coding agent CLI).
- **Что делает:** stateful agents с memory-blocks, self-editing memory,
  continual learning. V1 SDK (`letta-client`) + новый Agent SDK
  (TypeScript, cloud/local/Constellation).
- **Архитектурно интересно:** паттерн «agent сам редактирует свою память
  в ходе разговора,LRU-head продвижение Main-context vs archival» — это
  более продвинутая версия `memory-management.md` flush-протокола. Для
  вдохновения при дизайне下一步 `04-Memory/` (auto-archival) — но сейчас
  vault flush-протокол уже ✅ и работает.
- **Почему Watch:** (a)V1-сервер `letta-ai/letta` — **объявлен legacy**
  (`AGENTS.md` в их репо — «active development moved to letta-code»);
  (b)`letta-code` — это **coding-агент CLI**, отдельный от OpenCode, который
  строит своего агента — нарушение anti-goal «centralized-know::OpenCode»;
  (c) Self-hosted server = Postgres+docker, тяжёлый для одиночного
  пользователя.
- **Когда пересмотреть:** если `letta-code` добавит server-mode SDK или
  появится «Letta Agent as MCP» — можно использовать как memory-MCP без
  замены OpenCode. До этого — только как **идеи для метода** в `02-Methods/`.
- **Не возвращать claude-mem:** `facts.md` T-000 явно отмечает удаление
  external MCP-memory. Letta managed cloud — та же категория риска.
  Допустим только Letta **self-hosted** и **только память**, не агентский
  рантайм.

### Дополнительно просмотрено, но не вошло в кандидатов

- **Helicone** (https://github.com/Helicone/helicon, MIT) — observability,
  lighter чем Langfuse. Альтернатива, если Langfuse покажется тяжёлым.
- **Phoenix** (Arize, MIT) — OpenTelemetry-native tracing; менее
  LangChain-friendly, но хорош для OpenTelemetry-purists.
- **Portkey AI Gateway** —♶  коммерческий аналог LiteLLM; OSS-gateway
  слабее — LiteLLM лучше.
- **Chroma/LanceDB/CozoDB/Redis** — векторные БД. Все тяжелее sqlite-vec
  для single-user vault; выбран sqlite-vec из-за «pure C, no daemon».
- **GPTCache** (https://github.com/zilliztech/GPTCache, MIT) — semantic cache
  LLM-ответов. Идея strong (отсечь повторные одинаковые вопросы), но
  применение в **agentic**-контексте опасно: cache hit на «похожем» запросе
  может вернуть устаревший план (анти-pattern для closed-loop). Watch-только.
- **OpenHands / SWE-agent / Roo Code / Goose / Cursor** — изучены как
  **архитектурные референсы** (compaction, subagents, verify-loop, repo
  map, background tasks). Их установка == замена OpenCode (запрещено
  anti-goal). `/loop` + `/flush` + Multi-Agent Pipeline у Rudra уже covers
  паттерны этих систем по OpenCode-way.
- **tree-sitter / ast-grep** — взяты только как часть кандидата 6.

---

## Recommended roadmap

### A. Быстрый P0 без кода приложения (внедряет librarian/general/meta)

| # | Действие | Файл/путь | Эффект | Цена | Зависимости |
|---|----------|----------|--------|------|-------------|
| A1 | Custom Tool `token-budget` + `audit-log` | `~/.config/opencode/tools/token-budget.ts`, `audit-log.ts`; плагин на `tool.execute.after` (опц.) | Появляется telemetry по токенам/стоимости на агента/модель/проект. `token-budget` предотвращает тихий overflow перед делегацией. | S | tiktoken (npm) |
| A2 | `sqlite-vec` индекс над facts/inbox/session-log | `tools/index-engine/` + `vault/.cache/vault-vec.sqlite` (gitignore) | Top-k retrieval по прошлым фактам/сессиям вместо полного read `facts.md`. Дедупликация исследований («мы это уже разбирали»). | S | sqlite-vec (pip), `sqlite-lembed` (.gguf) или embedding API |
| A3 | Mem0 (self-hosted OSS, local vector) — добавить skill | `~/.config/opencode/skills/mem0/` (`npx skills add https://github.com/mem0ai/mem0 --skill mem0`); `opencode.json` permission `skill:"mem0": allow`; `.venv` install mem0ai | Кросс-сессионная memory с entity-linking + hybrid retrieval; ~6.8K tokens на retrieve вместо всего facts.md. | S–M | mem0 (pip), local vector store (Qdrant/Chroma) |
| A4 | Документировать telemetry-строку в weekly | `04-Memory/log.md`: новый раздел «Token spend / неделя» (aggregate audit-log) |ebeинными цифрами — основа для будущих model-routing решений (T-049). | S | зависит от A1 |
| A5 | `99-Inbox/` как директория inbox-исследований (`99-Inbox.md` остаётся буфером) | создать `99-Inbox/README.md` как индекс длинных research-файлов; этот файл — первый обитатель | Длинные research-доки (как этот) не раздули 99-Inbox.md. | S | — |

**Порядок:** A1 → A2 → A3 → A4. A3 необязателен если A2 уже даёт хорошее
local-retrieval; но Mem0 добавляет **managed extraction** (single-pass 1 LLM
на ADD) и entity-graph — это качественно больше.

### B. P1 с отдельным локальным daemon/инструментом

| # | Действие | Эффект | Цена | Зависимости |
|---|----------|--------|------|-------------|
| B1 | LiteLLM Proxy как AI Gateway | Единая точка провайдеров, spend tracking per virtual key, модели по цене (auto-prices JSON из репо), упрощение Zen↔Go миграции (T-049) | M | docker, port 4000 |
| B2 | Langfuse self-host (после B1, через LiteLLM callback) | Trace-level observability, prompt versioning, LLM-as-a-judge evals, cost-per-trace. Закрывает «заявлено, но не измеряется» на трейс-уровне. | M–L | LiteLLM (#B1), ClickHouse docker |
| B3 | `tools/repo-map/` (Aider repo-map паттерн) + Custom Tool `repo-map` в SERPlux/dv-hub | Compact tree-sitter ranked symbol map → меньше grep/read cycles в build-агенте | M | tree-sitter (python/ts), ast-grep (опц.) |

**Порядок:** B1 → B2 (только если B1 уже стоит). B3 — независимо, может быть
раньше (стоит меньше, чем B1/B2).

### C. Отложенное (Watch, revisit через 3–6 мес)

| # | Действие | Триггер для пересмотра |
|---|----------|----------------------|
| C1 | Graphiti MCP server | `facts.md` > 1000 фактов ИЛИ мульти-instance проекты ИЛИ конфликтующая хронология версий метода |
| C2 | Letta (memory-only, self-hosted) | Если появится Letta-memory-as-MCP (без `letta-code` замены OpenCode) |
| C3 | GPTCache semantic LLM cache | Только если появятся _idempotent_ LLM-tasks (один и тот же вопрос → тот же ответ). Сейчас agentic — опасно. |

---

## Measurement plan

Без observability все «экономии» — качественные. Поэтому **A1 — обязательный
первый шаг**, всё остальное измеряется через audit-log:

| Метрика | Источник | Целевое | Команда измерения |
|---------|----------|---------|-------------------|
| Tokens-in за сессию (librarian, среднее) | audit-log (#A1) | ↓ на 30% после Mem0/sqlite-vec | `python tools/audit-report --week --agent librarian` |
| Дублирующих `read` одного файла за сессию | audit-log (#A1, `read`-tool hooks) | ↓ >50% после sqlite-vec (#A2) | тот же |
| Spend USD/неделя/проект | audit-log (#A1) или LiteLLM (#B1) | visible; базлайн — после 2 нед | weekly aggregate в `session-log` |
| Hit-rate cache Mem0 (recall в top-5) | Mem0 search API | >80% на «известные» запросы | Mem0 Benchmark `memory.search` |
| Verify-cycle count в /loop (/loop logs) | новой Custom Tool `loop-stats` (опц.) | HARD STOP <5 в 95% задач | `/loop` отчёт |
| Prompt_tokens перед делегированием | `token-budget` (#A1) | jamais не overflow-compact | 0 events в audit-log |
| Bundle reduction в build-агентах | repo-map (#B3) + audit-log | ↓ число `read` до первой правки в /loop | — |

Все числа `[проверить]` первой неделей после внедрения — заявленные ориентиры
качественные (есть ли подтверждение на практике — увидим по замерам).

## Risks and non-goals

### Риски

1. **Mem0 cloud vs OSS blur.** Mem0 активно пиарит cloud (`app.mem0.ai`).
   Anti-goal (`facts.md` T-000 «Убрать claude-mem») требует **только self-hosted**.
   Условие при внедрении: `pip install mem0ai` + local vector store, **не**
   signup на app.mem0.ai.
2. **Embedding API dependency.** sqlite-vec/Mem0 по умолчанию тянут OpenAI
   embeddings — external spend. Mitigation: локально через `sqlite-lembed`
   (.gguf, e.g. `nomic-embed-text`) или Qwen 600M. Размер .gguf ~100MB.
3. **anti-goal «не править код приложений».** Все install/config делает
   **meta-агент** (`~/.config/opencode/agent/meta.md`) — librarian только
   инициирует. A1–A3 не трогают `*.py` SERPlux/dv-hub. B1/B2 трогают
   `opencode.json` всех проектов — формально это агентная инфра (допустимо).
4. **Stack daemon overhead (B1/B2).** LiteLLM+Langfuse = 4–5 контейнеров.
   Проверить ресурсы (`free`, `docker stats`) до запуска. Альтернатива —
   Langfuse Cloud free (нарушает «память у нас» только для трейсов, не
   памяти — приемлемо `[проверить]`PrivacyPolicy).
5. **Letta/Graphiti_VENDOR_LOCK.** Letta managed / Zep cloud — снова
   «claude-mem-style» внешний сервис. Спокойно только self-hosted.
6. **Security outreach.** Custom Tool `audit-log` пишет prompt/completion
   tokens (не content). Внимание: **не логировать сами промпты** в vault
   (только метаданные). Иначе можно случайно закоммитить чувствительные
   данные в git репо.
7. **Skill auto-loading.** Mem0 скилл, объявленный в `description`, будет
   подтягиваться при любой задаче про «memory». Проверить `permission.ask`
   (`/docs/skills/` → ask mode) — для начала режима «approve before load».

### Non-goals (не делать)

- НЕ заменять OpenCode на Aider/Cursor/Goose/OpenHands/SWE-agent (centralized-know).
- НЕ подключать claude-mem / Letta cloud / Zep cloud (anti-goal из `facts.md`).
- НЕ логировать содержимое промптов в vault (только метаданные).
- НЕ править `*.py`/`*.gs`/prod-конфиги проектов напрямую — только build-агенты.
- НЕ усложнять dynamic model-routing (метод явно: при <500 calls/day overhead
  классификатора дороже экономии). Observability first, dynamic-routing потом.

## Sources

Подтверждено 2026-08-02:

### Репозитории/проекты
- Mem0: https://github.com/mem0ai/mem0 — Apache-2.0, 62.3k★. README прямо
  перечисляет OpenCode как клиент skills-стандарта. API/benchmarks/docs:
  https://docs.mem0.ai , https://mem0.ai/research
- sqlite-vec: https://github.com/asg017/sqlite-vec — MIT/Apache, 8k★,
  Mozilla Builders. Docs: https://alexgarcia.xyz/sqlite-vec/
- LLMLingua (LLMLingua-2): https://github.com/microsoft/LLMLingua — MIT,
  6.5k★. (упомянут в Executive summary; de-prioritized из-за overhead Берt-модели
  локально; paper ACL-2024 Findings — https://aclanthology.org/2024.findings-acl.57/)
- LiteLLM: https://github.com/BerriAI/litellm — MIT (core), 55.4k★.
  Docs: https://docs.litellm.ai
- Langfuse: https://github.com/langfuse/langfuse — MIT (кроме `ee/`), 32.3k★.
  Docs: https://langfuse.com/docs. LiteLLM integration:
  https://langfuse.com/docs/integrations/litellm
- Aider: https://github.com/Aider-AI/aider — (репо-мап только как паттерн,
  лично `repo-map.html` docs 404 на 2026-08-02; `[проверить]` на docs.aider.chat)
- tree-sitter: https://github.com/tree-sitter/tree-sitter — MIT.
- ast-grep: https://github.com/ast-grep/ast-grep — MIT.
- Graphiti: https://github.com/getzep/graphiti — Apache-2.0, 29.5k★.
  Paper: https://arxiv.org/abs/2501.13956
- Letta (MemGPT): https://github.com/letta-ai/letta — Apache-2.0, 24.1k★
  (legacy server; active dev → https://github.com/letta-ai/letta-code).
- GPTCache: https://github.com/zilliztech/GPTCache — MIT.
- Helicone: https://github.com/Helicone/helicon — MIT.
- OpenHands / SWE-agent / Roo Code / Goose / Cursor — только как
  архитектурные референсы.

### OpenCode docs (источник правды по интеграциям)
- Agent Skills: https://opencode.ai/docs/skills/ — SKILL.md, name/description,
  `skill`-tool, permissions allow/deny/ask, compatibility `opencode`/`.claude`/`.agents` paths.
- MCP servers: https://opencode.ai/docs/mcp-servers/ — `mcp` блок в
  `opencode.json`, local (`command: [...]`) + remote (`url`), OAuth, glob disable.
- Custom Tools: https://opencode.ai/docs/custom-tools/ — `@opencode-ai/plugin`
  `tool()`, `.opencode/tools/` или `~/.config/opencode/tools/`, может вызывать
  Python через `Bun.$` (пример в docs).
- Plugins: https://opencode.ai/docs/plugins/ — `tool.execute.before/after`,
  `experimental.session.compacting`.

### Vault-артефакты (исходный аудит)
- `AGENTS.md`, `00-INDEX.md`, `TASKS.md`, `Architecture.md`, `DEVELOPMENT-ROADMAP.md`
- `02-Methods/{model-routing,distill-pattern,memory-management,multi-agent-pipeline,closed-loop,verifier-pattern,tool-integration-pattern,context-as-docs}.md`
- `03-Projects/{vault,SERPlux,dv-hub,dotfiles}.md`
- `04-Memory/{active-context,facts.md,session-log/2026-07-13-part2.md}`
- `01-Reference/{global-config,commands,plugins}.md`
- `.opencode/agent/librarian.md`, `.opencode/skills/capture/SKILL.md`,
  `~/.config/opencode/{agent,command,plugins}/*`

---

## Независимый синтез librarian-а — context compiler и token economics

> Это не новая разведка, а фиксация независимого анализа, проведённого
> librarian-ом поверх собранных кандидатов и архитектуры волта. Цель —
> перейти от «набор инструментов» к «единый механизм compiler/cache/routing
> с provable token economics». Всё ниже — проектные предложения, не
> подтверждённое имущество волта; OpenCode-specific cache hooks помечены
> `[проверить]`.

### 1. Context Compiler (P0/P1, собственный vault-level tool)

- **Вход:** task intent (что хочет пользователь/делегирующий агент),
  project card (`03-Projects/<name>.md`), git HEAD целевого репозитория,
  active-context, relevant facts (retrieved top-k), changed files (по
  `git diff`/`session-flush` журналу).
- **Выход:** content-addressed `context capsule` — артефакт, идентифицируемый
  своим хешем, с manifest `{path, sha256, role, token_count, freshness}`.
  Capsule собрана в **компактные слои** (порядок важен, см. пункт 2):
  1. invariant rules — статичные принципы AGENTS.md/anti-goals (редко меняются);
  2. project map — компактный ranked map из пункта 4;
  3. task slice — только релевантные срезу задачи участки кода/документов;
  4. recent evidence — свежие evidence-факты/диффы с коротким TTL.
- **Ключевое свойство:** compiler **детерминированно не отправляет исходные
  документы LLM**. LLM получает только capsule; исходники остаются на диске
  и адресуются через manifest. Это устраняет повторное чтение одних и тех же
  markdown-файлов всеми агентами в одной задаче.
- **Главный эффект:** (a) устраняет повторное чтение (agent re-reads);
  (b) создаёт **стабильный prefix** для prompt caching — поскольку первые
  слои (rules + project map) меняются редко, их хеш стабилен, и провайдер
  может переиспользовать cache hits между запросами в одной ревизии.
- **Ошибки и mitigation:**
  - *Stale capsule* (исходник изменился после компиляции): обязателен
    `source_hash` в manifest; перед использованием capsule verifier сверяет
    `sha256` исходников с записанным. Расхождение → invalidation + fallback
    к исходнику (compile-on-demand).
  - *Неверный ranking* (попал не тот файл): capsule помечает `confidence`
    каждого слоя; агент может явно запросить `escalate → raw read` для слоя.
- **Файловая форма:** `.cache/context/<capsule-hash>.json` (машинный,
  content-addressed) + human-readable `.cache/context/<capsule-hash>.md`
  (для отладки/audit). Каталог `.cache/` в `.gitignore`. Capsule
  идемпотентен: тот же вход + та же ревизия → тот же hash.
- **Success-критерии:**
  - одна и та же задача в одной git-ревизии даёт **тот же capsule hash**
    (детерминизм — тестируется unit-тестом compiler'а);
  - **duplicate reads** одного файла в сессии ↓ (измеряется по audit-log,
    пункт 8);
  - agent tool calls в среднем на задачу ↓ (по тому же audit-log);
  - cache hit ratio prefix-части ↑ (по provider telemetry, когда доступна).

### 2. Cache-aware prompt ABI (P0 design rule, provider-aware)

- **Не считать prompt caching универсальной функцией OpenCode.** Поддержка
  cache конкретным провайдером/адаптером — отдельное свойство, которое может
  отсутствовать. Перед опорой на cache — `[проверить]` наличие cache
  параметров в adapter'е OpenCode для целевого провайдера.
- **По официальной Anthropic-документации** (см. Источники):
  - cache hit требует **100% идентичного prefix** — любое расхождение байт
    инвалидирует весь prefix;
  - кэшируется последовательность `tools → system → messages` (именно в
    этом порядке блоков);
  - breakpoint ставится **на последнем стабильном блоке** (обычно конец
    system/tools или конец неизменной префиксной части messages);
  - максимум **4 breakpoints** и lookback **20 blocks** — глубина кэширования
    ограничена;
  - использование нужно измерять **отдельно** по `cache_read_input_tokens`,
    `cache_write_input_tokens`, `input_tokens`, `output_tokens` — сливать
    их в один «total» некорректно и маскирует экономию.
- **Следствие для capsule:** в стабильный prefix **запрещены**:
  - timestamps (всегда меняются → ломают prefix);
  - случайный JSON key order (нужен canonical/сортированный JSON, например
    RFC 8785 JCS или deterministic stringify);
  - volatile status («now», «today», «last commit just now») до cache
    breakpoint — такие поля выносятся в динамическую часть после prefix.
- **Динамический task request** (конкретный вопрос пользователя,_CHANGED
  files delta, tool results) **помещается после стабильного prefix** —
  чтобы вес prefix сохранялся между переиспользованиями capsule.
- **Артефакт:** создать `context-abi.md` — контракт capsule-сериализации:
  - порядок блоков (`tool_defs`, `system`, `invariant_rules`,
    `project_map`, `task_slice`, `recent_evidence`, `user_request`,
    `tool_results`);
  - canonical JSON rules (key sort, без trailing whitespace-volatility);
  - hash policy (что входит в подпись prefix, что в подпись capsule);
  - cache diagnostics (какие блоки помечены cache breakpoint, какой версии
    ABI).
- **Не обещать экономию до telemetry.** Любое утверждение «capsule экономит
  X%» недействительно до того, как пункт 8-start telemetry покажала реальный
  cache_read/write split. `[проверить]` фактический cache support в каждом
  провайдере отдельно.

### 3. Local cognition daemon: llama.cpp (P1, только после hardware probe)

- **Репозиторий/лицензия:** https://github.com/ggml-org/llama.cpp — MIT.
  OpenAI-compatible server (`llama serve`), CPU/GPU hybrid (можно часть
  слоёв на GPU, часть на CPU), full quantization (GGUF Q4_K_M/Q5_K_S/etc.).
- **Роль в стеке:** локальная малая модель (3–8B, quantized) выполняет
  **детерминированные-ish preprocessing** задачи делегируемые сейчас remote:
  - intent classification (что хочет пользователь: build/research/fix/refactor);
  - project routing (какой проект/агент/модель — замена статических правил
    model-routing на динамический классификатор);
  - rerank (переупорядочить retrieved top-k facts перед подачей remote);
  - compression (LLMLingua-стиль compress stable prefix);
  - duplicate detection (новая задача vs уже решённая в capsule cache).
  Remote model (Sonnet/opus-эквивалент) выполняет **planning/implementation**
  задачи, где требуется longue-context reasoning.
- **Это не замена OpenCode.** llama.cpp работает как **Custom Tool/MCP**,
  вызываемый из capsule compiler (пункт 1) или librarian'ом напрямую. Не
  трогает `opencode.json`-провайдеров; добавляет новое tool определение.
- **Guard:** не включать тяжёлую модель без:
  - `hardware-profile` — замер RAM/VRAM/CPU threads/диска;
  - latency benchmark — целевая: preprocessor < 200ms при batch 1, иначе
    overhead съест экономию;
  - quality benchmark — false-route rate	kfree local классификатор не
    должен отправлять build-задачу в plan-агента чаще, чем удалённая модель
    (`[проверить]` на replay set из session log).
  - Fallback **всегда remote** при недоступности/перегрузке локального daemon.
- **Success-критерии:**
  - percentage задач routed locally (не дошло до remote на preprocessor
    этапе) — целевая [`проверить`] по замерам;
  - remote input tokens avoided (vs baseline «вся capsule → remote»);
  - false-route rate (misclassification на replay set) — целевая < X%
    [`проверить`].

### 4. Repo/knowledge map compiler (P0/P1)

- **Для кода:** Aider repo-map как **validated architectural reference**
  (но не установка). Концепция: tree-sitter AST symbols + dependency graph
  (imports/calls/references) + **rank under token budget** — частота
  упоминаний символа в графе = его вес. URL:
  https://aider.chat/docs/repomap.html `[проверить]` (docs.aider.chat
  репортовался 404 в основном research'е).
- **Для vault (markdown):** применить тот же алгоритм, но nodes = headings,
  edges = wikilinks + path-mentions + recency + **supersession edges**
  (факт A superseded by B — направленное ребро). Top-ranked map подаётся в
  capsule вместо чтения всех markdown-файлов волта. Это решает gap «facts.md
  читается целиком при старте» (Executive summary).
- **ast-grep** (https://github.com/ast-grep/ast-grep, MIT) — структурный
  search+rewriting (pattern-based, по AST). Полезен для surgical правок в
  capsule update pipeline (найти все `tool.execute.after`-хуки), но
  **не** заменяет dependency graph. Не переобещать: ast-grep не строит
  call-graph, только match-rewrite.
- **Incremental rebuild:** после изменения пересобирать только changed
  modules — по `git diff` (что изменилось) + content hashes (что
  перепарсить). Полный rebuild — only on schema/grammar change.
- **Integration:** Custom Tool `repo-map` (нативный, `/docs/custom-tools/`),
  вызывается capsule compiler'ом и build-агентами. Не трогает код приложений.

### 5. Event-sourced memory вместо растущего facts.md (P0 design, не внешний dependency)

- **Модель:** memory = immutable append-only log of **claims**. Каждая
  claim = record со схемой:
  `{fact_id, subject, predicate, value, source, observed_at,
   valid_from, valid_to, supersedes, confidence}`.
  - `fact_id` — content-hash записи (immutable);
  - `supersedes` — `fact_id` предыдущей claim, которую эта замещает;
  - `valid_to` — null пока claim активна, timestamp когда superseded;
  - `source` — указатель на session-log/commits (provenance).
- **`facts.md` остаётся** как **human-readable projection** текущего
  состояния (compacted view активных claims). Не источник правды, а её
  представление — пересобирается из claims по запросу.
- **Compact active view** (только `valid_to IS NULL`, top-k по freshness/
  relevance) генерируется для startup context capsule — librarian видит
  компактную выжимку вместо всего `facts.md`.
- **Ключевые свойства:**
  - **provenance сохраняется** — всегда видно когда/из какого source
    стала правдой, кем/чем superseded;
  - **история изменений не отправляется LLM** — LLM видит только compact
    active view; full history остаётся в git;
  - **rollback = удалить projection/index**, claims остаются в git (как
    обычные файлы в `04-Memory/facts.jsonl` или SQLite);
  - **quality queries** — «какой факт был истинен на дату X?» решается
    filter по `valid_from/valid_to` — без ручного git archaeology.
- **Не внешний dependency:** это дизайн-решение для `04-Memory/`,
  реализуется Custom Tool (`facts-project` / `facts-query`) на SQLite или
  JSONL. Не требует Mem0/Graphiti (хотя последние предоставляют похожий
  bi-temporal механизм — см. пункт 7 почему Mem0 не на первом шаге).

### 6. Exact research cache с version fence (P0)

- **Ключ кэша:** `normalized_query + vault_git_HEAD + source_urls/ETags
  OR fetched-content hashes + tool_version`.
  - нормализация запроса — lowercase + canonical whitespace + sorted tokens;
  - vault HEAD — потому что ответы на «какой агент?» зависят от текущей
    ревизии волта;
  - source URLs/ETags — для web-fetch источников;
  - fetched-content hashes — для источников без ETag (считаем sha256
    ответа);
  - tool_version — версия скрапера/парсера, чтобы не отдать кэш из-под
    старой версии логики.
- **Семантический hit разрешён только внутри одной версии snapshot.**
  Любое изменение в любом компоненте ключа → miss → revalidation.
  Revalidation = легитимно перезапросить, сравнить с закэшированным, и
  только при идентичности ответа отдавать cache (без повторной processing).
- **Не кэшировать blindly** ответы о конфигурации/топологии системы
  (живая инфраструктура: процессаugенные `opencode.json`, число агентов,
  список MCP-серверов) — эти ответы intentlyیشه expensive `дорого устареть`.
  Кэшируются: исследования статичных внешних ресурсов (docs/репо/markdown
  repositaries),.archive@inbox_tools посты, distill-method extractions.
- **Эффект:** повторная web/vault разведка в той же ревизии превращается
  в cache lookup (ms vs seconds/hundreds tokens). Но **не скрывает
  изменения** — version fence гарантирует инвалидацию при движении волта.

### 7. Tool-surface budget / lazy capability loading (P0 design)

- **Проблема:** глобальный agent видит **все tool definitions одновременно**.
  Каждый `tool` description входит в prompt (особенно MCP/custom tools с
  длинными JSON schemas). Это:
  - (a) съедает input tokens на каждый запрос (даже если tool не вызываете);
  - (b) **инвалидирует prefix cache** при любом изменении tool list —
    поскольку `tools` идут в prefix, добавление/удаление одного инструмента
    сбрасывает кэш для всех задач.
- **Решение:** на старте задачи agent не видит весь tool-surface. Только
  `catalog` (summary всех групп с короткими описаниями) . Конкретные
  tool definitions активируются «lazy», только для группы capов, нужной
  задаче (skill/permission scope = capability registry).
- **Механика в OpenCode:** использовать `skills` и `permission scopes`
  как capability registry. Например: профиль «research» активирует
  только capture/webfetch/read инструменты; «build» — edit/bash/test;
  «librarian» — read/repo-map/context-compiler/audit-query. Остальное —
  `ask` или `deny` по умолчанию.
- **Success-критерии:**
  - tool-definition tokens per request ↓ (измерить по audit-log и
    prompt-inspection);
  - cache hit ratio ↑ (поскольку tool-surface стабилен внутри профиля);
  - accidental tool calls ↓ (меньше «агент вызывает редкий инструмент
    не по делу» — известная проблема при перегруженном tool list).

### 8. Observability как acceptance gate (P0)

- **Не просто total tokens.** Нужен **trace**:
  `task_id → delegation(s) → tool calls → model calls → verifier cycles
   → result`. На каждом шаге — метрики: `input_tokens`,
  `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cost_usd`,
  `latency_ms`, `success|rework`, `agent`, `model`, `project`.
- **Почему это acceptance gate:** любой compression/router/cache merge
  принимается **только после A/B на replay set** из session logs. Replay
  set = зафиксированный набор прошых задач, реран с/без new mechanism, сравнение
  метрик. Без этого «заявленная экономия» остается unverifiable claims
  (та же проблема что сейчас: «model-routing 51% economy» не измерена).
- **Инструменты (сверить версии/лицензии перед внедрением):**
  - **Phoenix** (https://github.com/Arize-ai/phoenix, Apache-2.0):
    OpenTelemetry-native tracing, experiments/datasets, MCP integration,
    LLM-as-judge evals. Подходит для trace-replay и A/B-сравнения.
  - **LiteLLM** (https://github.com/BerriAI/litellm, MIT): AI gateway +
    cost tracking per virtual key; служит data source для Phoenix (metrics
    по реальным вызовам).
  - Точные версии, лимиты self-host wheel/docker и лицензионные условия
    сверь в репозиториях **перед** внедрением —nofollow «as of 2026-08-02»
    statements без commit hash.
- **Self-imposed non-goal:** не собирать content промптов (только
  метаданные + хеш), против тех же защит что и audit-log (risk #6 в
  основном research'е).

### Мой приоритет внедрения

Порядок выбран так, чтобы каждый шаг давал **измеримую основу для
следующего**, и не блокировал anti-goals:

1. **Telemetry + replay set** (пункт 8). Без observability все
   последующие «экономии» остаются верой. Сначала — зафиксировать
   baseline по session logs, собрать replay set прошлых задач, потом
   любой следующий mechanism мерять против baseline. Это первичный смисл
   audit-log и Phoenix; делается `npx`/`pip` нами без daemon-стека, чтобы
   не ждать LiteLLM compose.
2. **Context compiler + repo-map** (пункты 1 и 4). Только когда telemetry
   меряет duplicate reads и cache hit ratio, Compiler имеет смысл
   включать — иначе не докажешь эффект. repo-map — часть compiler'а,
   нельзя их разделять (compiler без map = «всё равно перечитываю»).
3. **Exact research cache** (пункт 6). Зависит от compiler, потому что
   capsule hash — первичный cache key для повторюх задач; version fence
   использует тот же `git HEAD`-механизм.
4. **Event-sourced facts projection** (пункт 5). это refactor памяти;
   даёт quality (provenance, compact startup view) но не прямой token
   ROI до того как compiler потребляет compact active view. Поэтому
   после compiler.
5. **Local llama.cpp daemon** (пункт 3). Самый дорогой по внедрению
   (hardware probe, latency benchmark, fallback). Ставится последним,
   когда всё предыдущее стабилизирует token economics — иначе местная
   модель может «оптимизировать» не то, что действительно дорого.

**Почему НЕ начинать с Mem0 / Graphiti:**
- **Mem0** (candidate #1 основного research'а) — managed-layer поверх
  внешнего API; решает «long-term memory retrieval», но (a) тянет
  external embedding dependency (anti-goal risk #2), (b) прячет
  provenance в своей внутренной схеме (контрастирует с event-sourced
  моделью пункта 5), (c) даёт экономию «при старте сессии», но не
  устраняет повторные reads **внутри** сессии (compiler решает) и не
  даёт deterministic prefix для cache (ABI решает). Полезно как **layer
  поверх event-sourced facts** (point 5) после того, как тот стоит — не
  вместо.
- **Graphiti** (watchlist #7) — bi-temporal knowledge graph, требует
  Neo4j/FalkorDB daemon; избыточен по complexity на текущей зрелости
  волта (~100 фактов). Event-sourced JSONL/SQLite (пункт 5) закрывает
  provenance на 1% сложности. Graphiti пересматривается при facts > 1000
  или мульти-instance проектах — те же триггеры, что в watchlist.
- **Общий принцип:** external memory backend без observability + без
  compiler = нельзя доказать, что он лучше текущего «facts.md + read».
  Сначала observability (1) и compiler (2), потом уж memory layer —
  иначе оптимизируем вслепую.

### Источники независимой проверки

- **LLMLingua**: https://github.com/microsoft/LLMLingua — MIT, prompt
  compression (используется в компрессии prefix, не как standalone tool).
  Paper: ACL-2024 Findings — https://aclanthology.org/2024.findings-acl.57/
- **Aider repo-map**: https://aider.chat/docs/repomap.html — архитектурный
  reference (ranked symbol map под token budget). `[проверить]`
  availability (в основном research'е docs.aider.chat репортовался 404).
- **Anthropic prompt caching**:
  https://platform.claude.com/docs/en/build-with-claude/prompt-caching —
  первоисточник для cache-aware ABI (пункт 2): prefix requirements,
  tools→system→messages order, 4 breakpoints / 20 blocks lookback,
  separate cache_read/write/input usage.
- **vLLM APC** (Automatic Prefix Caching):
  https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html —
  self-hosted cache для open-source inference; годится как local cache
  layer если выбран локальный inference (но сам vLLM heavy-weight vs
  llama.cpp из пункта 3).
- **llama.cpp**: https://github.com/ggml-org/llama.cpp — MIT, local
  cognition daemon (пункт 3).
- **ast-grep**: https://github.com/ast-grep/ast-grep — MIT, structural
  search/rewrite (часть repo-map update pipeline, не замена dependency
  graph).
- **LiteLLM**: https://github.com/BerriAI/litellm — MIT, gateway/cost
  tracking, source метрик для Phoenix (точные лицензионные условия и
  version fence — сверять перед внедрением).
- **Phoenix**: https://github.com/Arize-ai/phoenix — Apache-2.0,
  OpenTelemetry tracing, experiments/datasets, MCP.

### Граница уверенности

Чтобы не смешивать факт и архитектурное предложение:

- **Подтверждённые свойства OpenCode** (из /docs/, проверено 2026-08-02 в
  основном research'е): MCP-серверы, Custom Tools, Skills с permissions,
  Plugin SDK `tool.execute.before/after`. Эти mechanisms можно использовать
  для построения compiler/cache/observability без патчей OpenCode.
- **`[проверить]` — OpenCode-specific:**
  - нативная поддержка prompt caching в adapters OpenCode для конкретных
    провайдеров (Anthropic/OpenAI/Google) — cache_read/write tokens
    passthrough в plugin hooks?;
  - фактический hook для interceptor'а перед LLM-call, чтобы compiler
    мог встроить capsule (есть `tool.execute.before`, но LLM-call ≠ tool);
  - возможность lazy load tool definitions per-agent/per-skill (пункт 7);
  - наличие `budgetTokens` / context-limit hook (упомянуто в facts.md как
    off в vault).
- **`[проверить]` — окружение пользователя:**
  - hardware profile (RAM, VRAM, CPU cores) для llama.cpp daemon (пункт 3);
  - доступные ресурсы для LiteLLM/Phoenix docker (B1/B2 из основного
    research'а, риск #4);
  - доступность embedding модели для sqlite-vec/repo-map (risk #2).
- **Архитектурные предложения (не подтверждённое имущество волта):**
  весь **Context Compiler**, **cache-aware ABI**, **event-sourced facts**,
  **research cache с version fence**, **tool-surface budget** — это
  design proposals, которые требуют реализации (`tools/` Custom Tools) и
  acceptance через replay-set A/B (пункт 8). Не выдавать их за «уже есть»
  или «доказавшая экономию» до замеров.
- **Лицензии**: все URL приводятся по состоянию на 2026-08-02. Перед
  внедрением — сверять commit hash/repos актуальную LICENCE/NOTICE, не
  полагаться на «MIT/Apache as stated» в этом документе.

---

## Harness-first: главный апгрейд волта

> Этот раздел — архитектурное предложение, а не перечень инструментов. Цель —
> переформулировать следующий апгрейд волта от «добавить ещё одного агента /
>.memory-layer» к «построить детерминированный control plane вокруг уже
> существующих моделей и агентов». Подтверждённые свойства внешних проектов
> отделены от предложенной архитектуры; OpenCode-specific runtime hooks
> помечены `[проверить]`. Никаких маркетинговых процентов; никаких выдуманных
> OpenCode API.

### 1. Определение

**Harness** (контрольная обвязка) — детерминированный **control plane** вокруг
**сменной** модели. LLM/агент — worker, а не источник истины; harness решает,
какой task contract получить модели, какой контекст ей отправить, какие tools
доступны, когда остановиться, что считать успехом и что залогировать для
replay. Модель и harness разделены так же, как CPU и kernel: ядро —
детерминированное, модель — hot-swappable.

Минимальный состав harness (не агент, не промпт — отдельная подсистема):

- **Task contract** — формальный контракт задачи (YAML/JSON), не свободный текст
  в `AGENTS.md`.
- **Context compiler** — сборка content-addressed capsule (см. независимый
  синтез, пункт 1) вместо «агент читает файлы сам».
- **Tool / policy firewall** — capability groups, path allowlist, command
  policy; не «все MCP-tools каждому агенту».
- **Model router** — выбор модели под контракт (продолжение `model-routing.md`,
  но как runtime-переход, а не статическое правило).
- **State machine** — конечный автомат задачи с явными переходами.
- **Verifier** — runtime transition `execute → finalize`, не инструкция в
  markdown.
- **Budget breaker** — hard limits на токены/стоимость/время/циклы,
  останавливающий **до** следующего LLM-вызова, а не после.
- **Artifact / event log** — append-only JSONL, единая лента состояний задачи.
- **Replay / eval harness** — фиксированный набор прошлых задач для A/B-сравнения
  изменений harness.

Параллель с операционной системой намеренная: harness — это «kernel +
syscall ABI» для агентных задач волта. Без него модель и промпт —
«userspace без scheduler».

### 2. Gap текущего волта

Зафиксированные наблюдения (по файлам волта и dotfiles, проверено 2026-08-02 в
основном research'е):

- **`general` вызывается вручную без единого task contract.** librarian
  читает волт, принимает решение о маршрутизации и делегирует в `general`
  текстом; контракта «какая задача, какой scope, какой budget» нет в виде
  machine-readable объекта. Это повторяемый неопределённый шаг.
- **`/loop` глобально указывает `agent: build`, тогда как в dotfiles есть
  `builder`.** Имя агента в глобальной команде и имя агента в dotfiles не
  сходятся; при исполнении в разных проектах задача уходит не туда или
  падает на missing agent. Метод `closed-loop.md` фиксирует HARD STOP 5, но
  не фиксирует, **кому** loop направляется.
- **`/done` зависит от `/commit`, который не глобален.** Команда `/done`
  ожидает готового commit-шага, но `/commit` живёт в dotfiles, не в
  `~/.config/opencode/command/`. Результат: `/done` в vault/librarian не
  имеет backing-перехода и становится no-op или ручным шагом.
- **Verifier существует, но обязательность перед commit не является единым
  runtime gate.** `verifier-pattern.md` — описанный метод; в SERPlux/dotfiles
  он есть, в vault — справочник. Нет единого перехода state machine
  `verify=PASS → finalize`, который держит harness, а не агент.
- **Session-flush фактически не оставляет `file.edited flush` в session-log.**
  `memory-management.md` описывает flush перед compact; на практике
  `session-log/*.md` получает текст narrative, а structured `file.edited`
  events не фиксируются как отдельные записи — это нарушает replay
  (восстановить «что было изменено» по session-log нельзя без повторного
  парсинга narrative).
- **Нет token/cost budget breaker и единого event ledger.** `budgetTokens`
  в `opencode.json` волта выключен (`facts.md`: «не требуется для командного
  центра»); audit-log (кандидат #3 основного research'е) ещё не внедрён.
  Любое «ограничение» сейчас — advisory в markdown, не hard gate.
- **Нет replay-набора для сравнения harness-изменений.** Любое изменение
  agent-конфигурации/метода сегодня принимается «на глаз» — нет зафиксированного
  набора прошлых задач, по которому можно A/B сравнить старый и новый harness
  (observability как acceptance gate — пункт 8 независимого синтеза — не
  запущен).

Каждый gap — это место, где сегодня **агент принимает решение, которое должно
быть инвариантом harness**. Это и есть системный пробел, глубже чем «нет
telemetry»: даже при наличии telemetry мы измеряем поведение агента, а не
контракт.

### 3. Предлагаемый Vault Harness Kernel

**Поток задачи (state machine):**

```
intake → contract → snapshot → route → execute → verify → repair(loop) → finalize
                                                                         ↘ blocked
```

Каждый переход — детерминированная функция harness, а не LLM-решение. LLM
работает **только** на `execute` (и, при необходимости, на `repair` внутри
 blk-loop). Остальные шаги — код harness.

**Task contract** — YAML/JSON объект, минимум полей:

```yaml
id:                       # уникальный идентификатор задачи (UUID/content-hash)
goal:                     # что должно быть достигнуто (одна фраза, DoD-form)
scope:                    # что входит в задачу (files/modules/commands)
project:                  # целевой проект из 03-Projects/<name>.md
base_ref:                 # git HEAD целевого репозитория на момент intake
context_capsule:          # ссылка на content-addressed capsule (см. компилятор)
model_policy:             # допустимые модели/тиры + fallback chain
token_budget:              # hard max input+output tokens
time_budget:               # hard max wallclock
allowed_tools:             # capability groups, разрешённые задаче
allowed_paths:             # path allowlist для записи/чтения
verification:              # DoD + test command + diff scope
max_repair_cycles:         # hard cap для repair-loop
artifacts_dir:             # куда складываются artifacts/provenance
```

Контракт — единственный вход в `execute`; агент не может изменить контракт
внутри исполнения (только вернуть `repair` proposal, который harness
эваливает).

**Event ledger — append-only JSONL**, одна запись на каждый переход
состояния:

```json
{"ts": "...", "task_id": "...", "state": "execute",
 "agent": "...", "model": "...",
 "input_tokens": 0, "output_tokens": 0,
 "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.0,
 "tool_calls": [...], "git_ref": "...",
 "artifact_hashes": {...}, "verifier_result": null,
 "reason": null}
```

Ledger — не трейсинг-система (Phoenix/LiteLLM из основного research'е решают
это), а **локальный инвариант harness**. Достаточно одного JSONL-файла на
задачу в `artifacts_dir/<task_id>/events.jsonl`.

**Контрольные инварианты harness** (детерминированные guards, не мягкие
правила):

- нет `verify=PASS` → нет `finalize` / `commit`. Это **runtime transition**,
  не предложение в `AGENTS.md`.
- `token_budget` / `time_budget` / `max_repair_cycles` достигнуты →
  `STOP` → `blocked`. Остановка **до** следующего LLM-вызова, а не после.
- изменённые пути вне `allowed_paths` → `reject` (diff scope check на
  `verify`).
- повторный `snapshot hash` для того же `(base_ref, capsule)` → **reuse**
  capsule и events, не перечитывать заново. Это связывает harness с
  context compiler из независимого синтеза (пункт 1) и exact research cache
  (пункт 6).
- любой результат имеет `artifact` (файл/дифф/capsule) + `provenance`
  (ledger entry с origin chain). Результат без provenance → rejected.

Эти инварианты — законы harness, они исполняются кодом, а не вписываются в
`AGENTS.md` с надеждой, что агент их прочтёт.

### 4. Пять harness-модулей

#### 4.1. Context firewall

- В модель отправляется **только capsule** (из context compiler, см.
  независимый синтез пункт 1), а не исходные markdown/исходники.
- Capsule содержит `source_hashes` (sha256 исходников), по которым verifier
  на `execute → verify` проверяет freshness; расхождение → invalidation.
- Жёсткий **token ceiling** на capsule: compiler не превышает
  `token_budget * κ` (например, κ=0.6) под prefix; остаток — task slice и
  tool results.
- Volatile blocks (timestamps, «now», «today», last-commit) выносятся
  **после** cache prefix (см. cache-aware ABI, пункт 2 независимого
  синтеза). Prefix стабилен внутри одной ревизии.
- Связь с repo-map compiler: capsule включает compact ranked map, а не
  «все файлы». Это решает gap «facts.md читается целиком» на уровне harness,
  а не memory-layer.

#### 4.2. Tool firewall

- **Capability groups** вместо «все tools всем»: research-профиль активирует
  `capture/webfetch/read/repo-map`; build — `edit/bash/test`; librarian —
  `read/repo-map/context-compiler/audit-query`. Остальное — `ask`/`deny` по
  умолчанию (см. tool-surface budget, пункт 7 независимого синтеза).
- **Lazy tool definitions**: agent не получает полный tool-list на старте —
  только `catalog` (короткие summary групп). Полные JSON schemas
  активируются при вызове конкретной группы. Это снижает input tokens и
  battled с prefix-cache invalidation при любом изменении tool list.
  `[проверить]` нативная OpenCode поддержка lazy tool loading per-agent/per-skill.
- **Path allowlist**: каждый tool, пишущий на диск, сверяет destination с
  `allowed_paths` контракта. Write вне allowlist → blocked, не error внутри
  tool, а reject harness'ом на `verify` (или до, если hook доступен).
- **Command policy**: белый/серый/чёрный список исполняемых команд для
  `bash`-tool; `deny` по умолчанию для destructive (`rm -rf`, `git push
  --force` без явного allow в контракте).
- **Optional sandbox**: bubblewrap / firejail для изоляции `execute` от
  хоста — `[проверить]` доступность и overhead на целевой машине; не
  promise как обязательный компонент. OpenHands/OpenAI container runtime
  (см. пункт 5) — reference, не замена.

#### 4.3. Budget circuit breaker

- **Hard limits**: `input_tokens`, `output_tokens`, `cost_usd`, `time_ms`,
  `repair_cycles`. Все четыре — на контракт. Ни один не advisory.
- **Остановка до следующего LLM-вызова**, не после. Harness хранит
  running totals в ledger; на каждом переходе проверяет, не превысит ли
  следующий `execute` бюджет. Если да → `blocked` с `reason=budget_exceeded`,
  не запуск новой итерации.
- Это главное отличие от текущего `closed-loop.md` HARD STOP 5: STOP сегодня
  описан как.ceil, но执行的 сторона — агент; harness должен держать счётчик и
  сам решать переход `execute → blocked`, не передавая это в LLM.
- Связь с LiteLLM gateway (кандидат #4 основного research'е): virtual
  key per project/agent дает вторую линию обороны на провайдер-стороне; harness
  — первая, локальная.

#### 4.4. Verification gate

- Verifier как **runtime transition** `execute → finalize`. Не markdown-
  инструкция (`verifier-pattern.md` описывает паттерн; harness исполняет).
- Состав gate:
  - **DoD check** — формальный критерий «done» из контракта (например,
    «test command exits 0», «diff non-empty within scope», «no removed
    public API»);
  - **test command** — детерминированная проверка (`npm test`, `pytest`,
    `ruff`, `mypy`) из `verification.test_command`;
  - **diff scope** — `git diff` сверяется с `allowed_paths`; правки вне
    scope → `reject`, не `repair`.
- `verify=PASS` → единственное условие разрешения `finalize`/`commit`
  (контрольный инвариант 1, пункт 3).
- `verify=FAIL` → `repair` (с proposal от модели → harness эваливает,
  cycle++), пока `cycle < max_repair_cycles` и `budget > 0`.
- `[проверить]` наличие OpenCode hook на pre-commit / pre-finalize, чтобы
  gate исполнялся в runtime, а не как рекомендация агенту. Отсутствие hook =>
  fallback: harness сам вызывает verifier как Custom Tool до разрешение
  commit.

#### 4.5. Replay / eval harness

- **Чего нет сегодня:** зафиксированного набора прошлых задач, по которому
  можно A/B сравнить старый и новый harness (или новый context compiler,
  новый router, новый verifier gate).
- **Что предлагает harness:**
  - зафиксировать 10–20 реальных задач из session-log'ов как replay set
    (task contract + base_ref + capsule + expected artifacts/verifier
    result);
  - при любом изменении harness/compiler/router — реран replay set;
  - метрики: **token cost** (in/out/cache_read/cache_write), **tool
    calls**, **cycle count** (repair iterations), **pass rate**
    (verify=PASS в frozen зладе), **regressions** (задача, ранее
    PASS, теперь FAIL или дороже по токенам).
- Не использовать GPTCache-style semantic cache для replay — каждое
  повторение запускает реальную модель на реальном capsule, только артефакты
  и метрики сравниваются с прошлым прогоном.
- Связь с observability (пункт 8 независимого синтеза): Phoenix/replay
  dataset — это и есть eval harness для trace-уровня; Vault Harness Kernel
  добавляет state-machine-level инварианты поверх.

### 5. Open-source reference patterns

**Только как архитектурные референсы, не замены OpenCode** (анти-goal
`centralized-know::OpenCode`). Для каждого — что заимствовать и что НЕ
переносить.

#### SWE-agent — https://github.com/SWE-agent/SWE-agent

- **Заимствовать:** **agent-computer interface** (ACI) — constrained set of
  commands, predictable output format, thinking before acting; framework for
  trajectory recording and evaluation against task instances. Их
  evaluation harness (задачиLEC2 + verdict) — образец для replay set.
- **Не переносить:** их собственный agent loop как замена OpenCode; их
  LM-server stack. Мы сохраняем OpenCode agent loop, заимствуем только
  (а) формат ACI как контракт `execute` и (б) trajectory+verdict pattern
  для replay.

#### OpenHands — https://github.com/All-Hands-AI/OpenHands

- **Заимствовать:** runtime/sandbox pattern (container-isolated execution
  для `execute`), agent loop как managed state machine (их `RUNNING/PAUSED/
  STOPPED/ERROR`), event stream (по сути их `events.py` — хороший образец
  ledger schema).
- **Не переносить:** установка OpenHands как runtime — это замена OpenCode
  (запрещено). Их runtime как reference для **design** Vault Harness Kernel,
  не как binary dependency. Container sandbox из OpenHands — опциональный
  reference для tool firewall module 4.2, но не обязательный компонент.

#### Aider repo-map — https://aider.chat/docs/repomap.html

- **Заимствовать:** **budgeted context map** — tree-sitter AST symbols +
  ranking по referencing frequency под token budget. Это桂皮 context
  firewall (4.1) и repo-map compiler (независимый синтез пункт 4). Концепция
  «карта вместо чтения» — основной механизм capsule.
- **Не переносить:** сам Aider как coding-агент (замена OpenCode). Их
  `repo-map.html` docs репортовался 404 на 2026-08-02 — `[проверить]`
  availability; ранжирование воспроизводится нами (nрепо-map AST + dependency
  graph), не pull'ится из Aider.

#### LLMLingua — https://github.com/microsoft/LLMLingua

- **Заимствовать:** **optional compression stage** для stable prefix —
  compressor подачи улучшает cache hit / token efficiency, когда prefix
  можно детерминированно сжать без потерь для task reasoning. Paper:
  https://aclanthology.org/2024.findings-acl.57/
- **Не переносить:** как обязательный модуль harness. Compression добавляет
  latency и нужен BERT-модель локально — deferred до measurable gain
  (пункт 3 llama.cpp daemon — local inference как место, где компрессор
  живёт). Не делать compression универсальным — это plugin (module slot),
  не invariant.

#### llama.cpp — https://github.com/ggml-org/llama.cpp

- **Заимствовать:** local **router / compressor daemon** — OpenAI-compatible
  server (`llama serve`) как local engine для intent classification, project
  routing, rerank, duplicate detection (детерминированные-ish preprocessing
  до remote model). Это плагинно к model router harness.
- **Не переносить:** замена OpenCode провайдеров на локальную inference
  глобально — local daemon служит **дополнительной** линией (preprocessor /
  router), fallback всегда remote. `[проверить]` hardware profile (RAM, VRAM)
  перед включением; `[проверить]` latency preprocessor < 200ms batch 1.

#### Phoenix — https://github.com/Arize-ai/phoenix

- **Заимствовать:** **trace/eval/replay observability** — OpenTelemetry-native
  tracing, experiments/datasets, LLM-as-judge evals. Это назад-end для replay/
  eval harness (4.5): Phoenix dataset = наш replay set, Phoenix experiment =
  A/B прогон старого/нового harness.
- **Не переносить:** замена локального event ledger. Phoenix — observability
  backend (remote/heavy), ledger — local invariant harness (single JSONL per
  task). Ledger кормит Phoenix, Phoenix не замена ledger. `[проверить]`
  self-host wheel/docker лимиты на целевой машине (стан同 risk #4 основного
  research'е).

### 6. Приоритет внедрения

#### P0 (без замены OpenCode)

1. **Task contract + state machine** в vault tool (Custom Tool или plugin на
   `tool.execute.before`, `[проверить]` доступный hook). Контракт как YAML
   объект, переходы как функции harness, а не markdown.
2. **JSONL event ledger** per task (`artifacts_dir/<task_id>/events.jsonl`).
   Один файл, append-only, схема из пункта 3.
3. **Hard budget / cycle / path gate** — runtime invariant: budget breaker
   до следующего LLM-call; path allowlist enforcement на verify; cycle cap.
4. **Verifier-before-finalize** — runtime transition `verify=PASS →
   finalize`; отвергнутый diff-scope или FAIL — repair/blocked. Связь с
   `verifier-pattern.md` (метод) и `closed-loop.md` (state) уже описаны —
   harness их исполняет, не повторяет.
5. **Replay set из 10–20 реальных задач** — зафиксировать из session-log'ов,
   по ним rebateaseline. Без этого любой следующий шаг — unverifiable claims
   (та же проблема, что «model-routing 51% economy»).

#### P1 (после P0 baseline замерен)

- **Context capsule / repo-map compiler** (независимый синтез пункт 1 и
  пункт 4) — только когда telemetry (P0-5) показывает duplicate reads и cache
  hit ratio; иначе compiler не имеет acceptance gate.
- **Worktree-per-task** — изолировать `execute` в отдельный git worktree,
  патчи `base_ref` стабилен, finalize = merge. `[проверить]` интеграцию с
  OpenCode worktree-aware tooling.
- **Local llama.cpp router** (независимый синтез пункт 3) — preprocessor для
  intent/route/rerank/duplicate; после hardware probe.
- **Sandbox daemon** (bubblewrap/firejail, опц. OpenHands-container pattern) —
  tool firewall 4.2, `[проверить]` overhead на целевой машине.

#### Watch (не внедрять)

- **Полноценный OpenHands / SWE-agent runtime как замена OpenCode** — прямо
  нарушает анти-goal `centralized-know::OpenCode`. Их архитектура —
  **reference only** (пункт 5). Их binary — не ставится.
- **GPTCache-style semantic LLM cache** в качестве replay — повторное
  использование «похожих» ответов опасно в agentic-контексте (см. watchlist
  основного research'е).

### 7. Критерии успеха

Измеримые критерии того, что Vault Harness Kernel заработал (а не «добавлен»):

- **Возобновляемость:** каждая задача возобновляется по `task_id` после
  compact / crash — состояние читается из ledger, capsule переиспользуется по
  hash.
- **Zero finalize without verifier PASS.** Контрольный инвариант 1 — это не
  advisory, а enforced runtime transition. Audit: ни одной записи
  `state=finalize` в ledger без предшествующей `state=verify` с
  `verifier_result=PASS` в том же `task_id`.
- **Zero writes outside allowlist.** Диф любой `finalize`-задачи — строго
  внутри `allowed_paths` из контракта; расхождения → rejected на verify.
- **Duplicate context snapshot reuse.** Тот же `(base_ref, capsule_hash)`
  для той же задачи не перекомпилируется — ledger фиксирует reuse, не
  новый snapshot.
- **Per-state metrics:** `token / cost / tool_calls / cycles` logируются
  **по состоянию state machine**, не только по итогу — видно, где в потоке
  тратится. Метрики попадают в weekly report (`04-Memory/log.md`).
- **Replay benchmark:** прогон нового harness на replay set (P0-5) **не
  ухудшает pass rate** при **снижении median input tokens**. Это точный
  количественный критерий; без него любой апгрейд harness — unverifiable
  claim. Целевое снижение median input tokens — `[проверить]` первым
  A/B прогоном (baseline vs harness-enabled), не обещать заранее.

### 8. Главный тезис

Следующий апгрейд волта — не **Mem0**, не **ещё один агент**, не **дополнительный
memory-layer` поверх facts.md**. Следующий апгрейд — **Vault Harness Kernel**:
детерминированный control plane вокруг уже существующих моделей и агентов с
`task contract → state machine → verify gate → budget breaker → event ledger
→ replay`. Memory, vector store, cache, local model, repo-map — это
**модули** harness, подключаемые через его ABI (capsule, capability groups,
model policy), а не конкурирующие слои поверх OpenCode.

Без harness они лишь добавят очередной слой неопределённости: Mem0 без
observability — unverifiable claims; local model без budget breaker — новый
quiet overflow; cache без contract — не доказать hit rate; верификатор без
runtime gate — мягкая рекомендация, которая пропускается. Harness — то
ядро, которое делает эти modules **подотчётными** и **сопоставимыми** через
replay. Это переформулирует онтологию волта от «набор методов и инструментов»
к «ядро + slotted модули» — тот же сдвиг, что от bare-metal к OS kernel, но
применённый к agentic loop.

---

### Граница уверенности (harness-раздел)

- **Подтверждённые свойства внешних проектов** (пункты 5): SWE-agent открыт и
  имеет evaluation harness; OpenHands имеет event-stream and sandbox runtime;
  Aider описывает budgeted repo-map; LLMLingua имеет compression methodology
  (paper ACL-2024 Findings); llama.cpp — локальный OpenAI-совместимый server;
  Phoenix — OpenTelemetry tracing/datasets. Лицензии и текущие версии —
  сверять в репозиториях перед внедрением, не полагаться на «as of 2026-08-02».
- **Архитектурные предложения, не подтверждённое имущество волта** (пункты
  3, 4, 6, 7, 8): весь Vault Harness Kernel — design proposal; task contract
  schema, state machine, JSONL ledger schema, harness-инварианты, replay set,
  success-критерии — требуют реализации (Custom Tools / plugins) и acceptance
  через replay A/B.
- **`[проверить]` — OpenCode-specific runtime hooks:**
  - нативный OpenCode hook pre-commit / pre-finalize для verifier gate (4.4);
  - lazy tool definition loading per-agent/per-skill (4.2);
  - interceptor hook перед LLM-call для context capsule injection (есть
    `tool.execute.before`, но LLM-call ≠ tool);
  - worktree-aware tooling для worktree-per-task (P1);
  - фактическое наличие `budgetTokens` / context-limit hook в adapter'ах
    (упомянуто как off в vault `facts.md`).
- **`[проверить]` — окружение пользователя:**
  - hardware для llama.cpp router daemon (P1) и sandbox;
  - ресурсы для Phoenix/docker если выбран replay backend (4.5);
  - закрытый/открытый worktree workflow в целевых проектах.
- **Не обещать**: что harness снизит token spend на конкретную величину до
  A/B прогона на replay set. Любые проценты в разделах выше — намеренно
  отсутствуют; критерии успеха требуют измерения, не цитаты.

---

## Addendum 2026-08-31 — OpenCode UI/UX/Workspace research

> **Append-only addendum.** Исходные разделы и выводы 2026-08-02 не
> переписываются и не отменяются; этот раздел добавляет результаты
> read-only исследования UI/UX/Workspace-поверхности OpenCode по официальным
> докам (источник правды по конвенции волта). Всё ниже проверено по
> opencode.ai/docs **2026-08-31** (страницы датированы «Last updated: Aug 30,
> 2026»), кроме пунктов, явно помеченных `[проверить]`. Свежий researcher
> brief на момент сессии недоступен — исследование выполнено напрямую по
> докам, что не заменяет independent researcher evidence.

### 1. Подтверждённые TUI capabilities (docs/tui/, docs/keybinds/, docs/intro/)

- Slash-команды TUI: `/connect`, `/compact` (alias `/summarize`), `/details`,
  `/editor`, `/exit`, `/export`, `/help`, `/init`, `/models`, `/new`,
  `/redo`, `/sessions`, `/share`, `/themes`, `/thinking`, `/undo`, `/unshare`.
- `@` — fuzzy file references (контент файла добавляется в разговор);
  настроенные references тоже появляются в `@`-autocomplete.
- `!` в начале сообщения — запуск shell-команды, вывод попадает в разговор.
- Plan/Build режимы переключаются `Tab`; режим виден в правом нижнем углу.
- Leader-ключ `ctrl+x` (дефолт) + keybinds; command palette `ctrl+p`.
- `/undo`/`/redo` откатывают сообщения **и file changes** через Git — проект
  обязан быть git-репозиторием.
- `/editor`/`/export` используют `$EDITOR` (GUI-редакторам нужен `--wait`).
- Drag&drop изображений в терминал — картинки попадают в промпт.
- `tui.json`/`tui.jsonc` (отдельно от `opencode.json`): `theme`,
  `keybinds` (merge с дефолтами), `leader_timeout`, `scroll_speed`,
  `scroll_acceleration`, `diff_style` (`auto`/`stacked`), `cursor`
  (style/blinking), `mouse` (default `true`), `attention` (desktop
  notifications + sounds: `enabled`, `notifications`, `sound`, `volume`,
  `sound_pack`, `sounds`), `OPENCODE_TUI_CONFIG` для кастомного пути.
- Attention: уведомления для questions/permissions/session errors/completed
  sessions; desktop notifications только когда терминал blurred.

### 2. TUI SDK/API — что подтверждено, что нет

- **Подтверждено (server-side TUI control):** `opencode serve` экспонирует
  TUI-эндпоинты: `POST /tui/append-prompt`, `/tui/open-help`,
  `/tui/open-sessions`, `/tui/open-themes`, `/tui/open-models`,
  `/tui/submit-prompt`, `/tui/clear-prompt`, `/tui/execute-command`,
  `/tui/show-toast`, `GET /tui/control/next`, `POST /tui/control/response`.
  Архитектура: TUI = клиент к server; это используется IDE-плагинами.
- **Подтверждено (plugin TUI events):** `tui.prompt.append`,
  `tui.command.execute`, `tui.toast.show` — плагины могут влиять на TUI
  через события (docs/plugins/).
- **НЕ подтверждено `[проверить]`:** публичный TUI SDK для встраивания
  кастомных виджетов/панелей внутрь TUI (аналог widget API). Доки
  описывают только themes/keybinds/tui.json-опции. Кастомные дашборды
  внутри TUI не документированы — не проектировать Pip-Boy как TUI-виджет.
- **НЕ подтверждено `[проверить]`:** OSC8 clickable hyperlinks в выводе
  tools/TUI. Доки не описывают кликабельные ссылки; `/export` (markdown в
  `$EDITOR`) — задокументированный обходной путь. Wikilinks волта в TUI
  не кликабельны (не заявлять).

### 3. Custom Tools — подтверждено с уточнениями (docs/custom-tools/)

- `tool()` helper из `@opencode-ai/plugin`; Zod-схемы аргументов; имя
  инструмента = имя файла; несколько tools в файле → `<filename>_<export>`;
  custom tool может override built-in (по имени); `context` = `{agent,
  sessionID, messageID, directory, worktree}`; вызов Python через `Bun.$`
  (пример в docs). Локация: `.opencode/tools/` или `~/.config/opencode/tools/`.
- Для экосистемы: read-only local endpoint (snapshot-инструмент) реализуем
  как custom tool без новых зависимостей — предпочтительный путь vs MCP.

### 4. Plugin/TUI hooks — полный подтверждённый event list (docs/plugins/)

- `command.executed`; `file.edited`, `file.watcher.updated`;
  `installation.updated`; `lsp.client.diagnostics`, `lsp.updated`;
  `message.part.removed/updated`, `message.removed/updated`;
  `permission.asked/replied`; `server.connected`; `session.created/compacted/
  deleted/diff/error/idle/status/updated`; `todo.updated`; `shell.env`;
  `tool.execute.after/before`; `tui.prompt.append`, `tui.command.execute`,
  `tui.toast.show`; `experimental.session.compacting` (включая полный
  `output.prompt` override).
- Plugins: local dirs (`.opencode/plugins/`, `~/.config/opencode/plugins/`)
  + npm-пакеты в config; load order global config → project config →
  global dir → project dir; deps через `package.json` в config-директории
  (bun install при старте).
- `file.watcher.updated` — подтверждённый файловый watcher-event (для
  будущего observer/event ingestion; runtime-поведение в vault-окружении
  `[проверить]`).

### 5. MCP — подтверждено (docs/mcp-servers/)

- Local (`command: [...]`, `environment`, `cwd`, `timeout` default 5000ms)
  и remote (`url`, `headers`, OAuth). OAuth: automatic Dynamic Client
  Registration (RFC 7591) + pre-registered credentials; CLI `opencode mcp
  auth/list/logout/debug`; токены в `~/.local/share/opencode/mcp-auth.json`.
- Управление: `enabled`, per-agent `tools` enable/disable, glob-паттерны
  (`my-mcp*`), tools регистрируются с префиксом имени сервера.
- **Caveat из docs:** MCP-серверы добавляют контекст; большое число tools
  легко превышает context limit — «being careful with which MCP servers
  you use». Это подтверждает осторожность vault-политики: read-only MCP
  только с минимальным числом tools, prefer custom tools.

### 6. References — новое подтверждённое capability (docs/references/)

- `references` в `opencode.json`: локальная директория (`path`) или git-репо
  (`repository` + `branch`, materialize в локальный cache); `description`
  попадает в agent system context; `hidden` скрывает из autocomplete;
  `@alias`/`@alias/` в TUI; reference-директории автоматически разрешаются
  через external-directory permission boundary (edit-права не наследуются).
- Для Agent Workspace: references — нативный механизм «внешнего контекста
  без копирования» (например, карточки волта как reference для проектных
  сессий). Runtime-поведение в экосистеме `[проверить]` smoke'ом.

### 7. Server / attach / web — подтверждено (docs/server/, docs/web/)

- `opencode serve [--port 4096] [--hostname] [--cors] [--mdns]`;
  `OPENCODE_SERVER_PASSWORD` (basic auth); OpenAPI 3.1 spec на `/doc`;
  SSE: `GET /event` (первое событие `server.connected`, затем bus events) и
  `GET /global/event`.
- REST: `/project`, `/path`, `/vcs`, `/config` (GET/PATCH),
  `/config/providers`, `/provider`, `/session` (+`/status`, `/:id`,
  `/:id/children`, `/:id/todo`, `/:id/diff`, `/:id/abort`, `/:id/fork`,
  `/:id/revert`, `/:id/summarize`, `/:id/permissions/:pid`), `/session/:id/
  message`, `/session/:id/prompt_async`, `/session/:id/command`,
  `/session/:id/shell`, `/command`, `/find`, `/find/file`, `/find/symbol`,
  `/file`, `/file/content`, `/file/status`, `/experimental/tool`,
  `/lsp`, `/formatter`, `/mcp` (GET status + POST add), `/agent`, `/log`,
  `/tui/*`, `/auth/:id`.
- `opencode web` — браузерный клиент (sessions, server status);
  `opencode attach http://localhost:4096` — подключить TUI к работающему
  web-серверу: web + TUI одновременно, shared sessions/state.
- Для Pip-Boy «live»-режима: SSE `/event` — задокументированный путь
  event ingestion; до внедрения observer+ingestion не заявлять real-time.

### 8. tmux / Docker limitations

- **tmux:** docs не описывают tmux-специфику. Подтверждённые смежные факты:
  `mouse: true` (default) захватывает мышь в TUI — в tmux это может
  конфликтовать с tmux mouse-режимом `[проверить]`; attention
  notifications завязаны на terminal blurred — поведение внутри tmux
  `[проверить]`; `/editor` через `$EDITOR` работает в tmux-панели как
  обычный процесс. Клавиатурные keybinds (`ctrl+x` leader) в tmux
  проходят как обычные escape-последовательности `[проверить]` на
  практике (префикс tmux может перехватывать).
- **Docker:** `docker run -it --rm ghcr.io/anomalyco/opencode` —
  подтверждённый официальный способ (docs/intro). Интерактивная сессия
  требует `-it`; монтирование проекта/проброс API-ключей/глубокая
  интеграция с host-git в docs не детализированы `[проверить]`. Для
  vault-окружения Docker не требуется (нативный Manjaro).

### 9. MVP vs later (для Pip-Boy / observer / workspace)

- **MVP (текущая сессия, static/generated):** canonical registry
  (`registry.json`) + multi-view Pip-Boy (Matrix/Kanban/Projects/Agents/
  Blockers/Workspace поверх registry + data.json) + детерминированный
  read-only snapshot CLI (observer). Всё — static/generated данные,
  real-time не заявляется.
- **Later (после MVP acceptance):** live event ingestion через SSE `/event`
  (server), `file.watcher.updated` plugin-события, OSC8/clickable links
  `[проверить]`, tmux-панель Pip-Boy `[проверить]`, references-based
  workspace smoke. Каждый шаг — отдельный acceptance gate.

### Sources (проверено 2026-08-31)

- TUI: https://opencode.ai/docs/tui/ — slash-команды, tui.json, attention.
- Keybinds: https://opencode.ai/docs/keybinds/ — leader/palette (через tui).
- Custom Tools: https://opencode.ai/docs/custom-tools/ — tool(), context,
  Bun.$, override, `<filename>_<export>`.
- Plugins: https://opencode.ai/docs/plugins/ — полный event list, load
  order, npm, compaction hooks.
- MCP: https://opencode.ai/docs/mcp-servers/ — local/remote, OAuth RFC 7591,
  per-agent, context caveat.
- References: https://opencode.ai/docs/references/ — path/repository,
  description→agent context, hidden.
- Server: https://opencode.ai/docs/server/ — OpenAPI 3.1, SSE, /tui/*.
- Web/attach: https://opencode.ai/docs/web/ — opencode web, attach.
- Intro/Docker: https://opencode.ai/docs/ — docker run -it, Tab, @, !.

> Граница уверенности: всё в разделах 1–7 — «подтверждено docs 2026-08-31»;
> раздел 8 и пункты `[проверить]` — runtime-неопределённость, закрываемая
> только живым smoke'ом в целевом окружении. Этот addendum не меняет
> приоритеты основного research'а (P0/P1/Watch) и harness-раздела; он
> уточняет интеграционную поверхность для ecosystem upgrade plan v2.