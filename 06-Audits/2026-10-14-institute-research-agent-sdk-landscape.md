---
type: research-audit
title: SDK-ландшафт агентских систем — внешняя инженерия и схема манифеста ведомства
status: draft-research
timestamp: 2026-10-14
project: OpenCode-Vault
source: "мандат Института Передовых Технологий, трек П2 (ref: p2-sdk-20261014, Rudra 2026-10-14)"
related:
  - 06-Audits/2026-10-14-institute-research-tsu-uas-architecture.md
  - 06-Audits/2026-10-09-agency-counteragency-brainstorm.md
  - docs/specs/ship-research-network.md (dotfiles, kind: contract)
  - 06-Audits/2026-10-13-ship-research-registry.md
---

# SDK-ландшафт агентских систем и схема манифеста ведомства

Целевое sourced-исследование внешней инженерии агентских систем с одной целью:
вывести (а не угадать) обоснование схемы манифеста ведомства. Уже принятое Rudra
(дано как контекст): слой манифестов — `docs/org/` в волте; порядок —
SDK-сверка → УАС-спека → спека Лабы. Этот файл — шаг «SDK-сверка», артефакт для
УАС-спеки, не внедрение и не канонизация.

Статусы: `draft-research` — рабочий материал Института. Внешние факты проверены
живым вебом 2026-10-14 (см. раздел «Провена»); внутренние факты — по локальным
файлам на ту же дату.

---

## (a) Стандарты и тулкиты: что это, зрелость, что переносимо

### 1. A2A Protocol (Agent2Agent)

**Что это.** Открытый стандарт взаимодействия между независимыми, возможно
непрозрачными (opaque) агентными системами разных вендоров и фреймворков.
Ключевые объекты — AgentCard (идентичность, capabilities, skills, endpoints,
auth), AgentSkill (id / name / description / tags / examples), AgentInterface
(binding + tenant), AgentProvider, AgentExtension, AgentCardSignature. Ядро
операций — SendMessage, SendStreamingMessage, GetTask, ListTasks, CancelTask,
SubscribeToTask, конфиги push-уведомлений, GetExtendedAgentCard. Задача (Task)
идёт по жизненному циклу состояний: submitted / working / completed / failed /
canceled / rejected; Context группирует связанные задачи; Message / Part /
Artifact — единицы контента. Discovery — well-known URI
`.well-known/agent-card.json` плюс каталоги/registry (§8 спеки: механизмы
обнаружения, подпись карточки, кэширование).

**Зрелость.** v1.0.0 (2026); в августе 2026 перешёл под Agentic AI Foundation
(объявление в блоге проекта от 2026-08-27). Спека — три слоя: каноническая
модель данных (proto — единственный нормативный источник), абстрактные операции,
привязки протокола (JSON-RPC, gRPC, HTTP/REST, кастомные). SDK для Python, Go,
Java, JS, .NET, Rust.

**Принципы, важные для нас.** Opaque execution (агенты сотрудничают по
заявленным capabilities, не открывая внутреннее состояние/память/инструменты);
async-first; modality-agnostic; переиспользование HTTP / JSON-RPC / SSE.

**Что переносимо.** AgentCard как прообраз манифеста ведомства (идентичность +
capabilities + skills + endpoints + auth); принцип opaque execution как
обоснование границы «письмо ≠ внутренняя история»; сама идея discovery-карточки
и каталога; подпись карточки как механизм provenance/достоверности; typed task
lifecycle как эталон того, что у нас пока только в виде receipt-квитанций.

**Что не переносимо.** Полноценные wire-привязки (JSON-RPC/gRPC/HTTP) — избыточно:
мы одна локальная экосистема на одном хосте, не кросс-вендорная сеть. Строгий
opaque execution — слишком жёстко: наши письма осознанно переносят контекст.
Typed task lifecycle целиком — возможно перебор при текущих «письмо + квитанция».

### 2. MCP (Model Context Protocol)

**Что это.** Протокол host/client/server поверх JSON-RPC 2.0, stateful. Сервер
отдаёт три класса: Resources (контекст-данные), Prompts (шаблоны), Tools
(функции). Клиентская сторона — Sampling, Roots, Elicitation. Есть capability
negotiation; безопасность — user consent, tool safety, аннотации недоверенных
источников.

**Зрелость.** Де-факто индустриальный стандарт подключения инструментов/контекста
к моделям; поддерживается Anthropic и широким списком SDK/CLI (включая OpenAI
Agents SDK и Google ADK — оба имеют встроенную интеграцию MCP, см. ниже).

**Что переносимо.** Модель «сервер заявляет свои способности, клиент договаривается»
= наш capability-routing и явный `UNROUTABLE`; user consent gate = наш
human-in-the-loop контракт (подтверждение плана); разделение «что отдаётся
наружу» (декларация) от «что внутри».

**Что не переносимо.** MCP — это клиент-серверная выдача инструментов и ресурсов,
а не peer-to-peer координация равноправных сессий; наши peer-comms — письма между
равными, а не вызов инструмента серверу.

### 3. Claude Agent SDK

**Что это.** SDK Anthropic для сборки субагентов. Subagents — отдельные инстансы.
AgentDefinition-поля: description, prompt, tools / disallowedTools, model, skills
(прелоад), memory (user / project / local), mcpServers, initialPrompt, maxTurns,
background, omitClaudeMd, effort, permissionMode. Три пути определения:
программно, файлами `.claude/agents/*.md`, встроенный general-purpose. Контекст
субагента — свой system prompt + prompt вызова + проектный CLAUDE.md, БЕЗ истории
родителя. Инструмент «Agent»/«Task». Лимиты: MAX_SUBAGENT_SPAWN_DEPTH (default 3),
MAX_CONCURRENT_SUBAGENTS (default 20), maxBudgetUsd. Workflow tool — для
десятков-сотен агентов (TS SDK).

**Зрелость.** Продакшен-фича Claude Code / Agent SDK, активно развивается;
файловый путь определения (`.claude/agents/*.md`) стал распространённым
конвенционным форматом.

**Что переносимо.** Файловое определение агента (`.claude/agents/*.md` ≈ наши
`.opencode/agent/*.md`); изоляция субагента «без истории родителя» = обоснование
нашей границы письма; тройка memory user/project/local ≈ наши memory-zones;
явные лимиты (spawn depth, concurrent) ≈ поле boundaries/limits манифеста.

**Что не переносимо.** Субагенты Claude — эфемерные экземпляры внутри одного
runtime и одного вызова, а не постоянные именованные «сессии-места» (наши
ведомства — персистентные сессии). Инструмент «Agent» работает внутри одного
процесса, а не через межсессионную доставку писем.

### 4. OpenAI Agents SDK

**Что это.** Продакшен-апгрейд эксперимента Swarm. Минимум примитивов: Agents
(LLM + instructions + tools), Handoffs (делегирование другому агенту, включая
agents-as-tools), Guardrails (валидация входов/выходов параллельно исполнению,
fail fast). Встроенные: sessions (персистентная память в цикле агента), tracing
(визуализация/отладка/оценка), MCP tool calling, human-in-the-loop, sandbox
agents (изолированные воркспейсы).

**Зрелость.** Активный продукт OpenAI (openai-agents-python, `pip install
openai-agents`); документация с разделами handoffs, guardrails, sessions, tracing,
multi-agent orchestration, sandbox agents.

**Что переносимо.** Handoffs как первоклассный примитив делегирования — прямой
аналог нашего правила «перенаправить чужой интент релевантной локации»; метаданные
handoff (input_type: reason/priority/summary) = наша причина перенаправления и
provenance; input_filter = контроль того, что видит принимающий агент (= что мы
кладём в письмо); guardrails = наши reviewer/verifier как раздельные гейты качества
и приёмки; tracing = наш route-log/телеметрия.

**Что не переносимо.** Handoffs живут внутри одного run/процесса — у нас
координация межсессионная. Guardrails — внутрипроцессная проверка; у нас гейты —
отдельные именованные сессии (verifier/reviewer), а не код в цикле.

### 5. Google ADK (Agent Development Kit)

**Что это.** Открытый фреймворк сборки/деплоя агентов. LlmAgent (name, model,
instruction, tools); sub-agents (через MCP-делегацию — «agent as MCP server»,
sub-agent delegation); multi-agent workflows (collaboration, template-паттерны
sequential / loop / parallel, agent routing); graph workflows (в ADK 2.0);
тройка Session / State / Memory; evaluation (criteria, user simulation,
environment simulation, custom metrics); Skills for Agents; нативная интеграция
A2A (exposing и consuming); observability (logging / metrics / traces).

**Зрелость.** Полиязычный (Python, TypeScript, Go, Java, Kotlin); ADK 2.0 GA
объявлен с graph workflows; активно развивается Google (Copyright Google 2026).

**Что переносимо.** Тройное разделение Session / State / Memory — прямой аналог
нашего session-log / active-context / facts; evaluation как первоклассный объект
(у нас — verifier acceptance + evidence); Agent routing ≈ перенаправление интента;
интеграция A2A показывает индустриальный тренд сходимости.

**Что не переносимо.** ADK — это runtime-фреймворк, внутрь которого деплоятся
агенты; мы не берём фреймворк, мы описываем слой манифестов/контрактов над уже
существующими сессиями OpenCode.

### 6. AGENTS.md-стандарт

**Что это.** Открытый формат инструкций для кодинг-агентов — «README для агентов»:
предсказуемое место с контекстом и правилами проекта (build/test, код-стайл,
PR-конвенции, безопасность). Нет обязательных полей, обычный Markdown. В монорепо —
вложенные AGENTS.md, правило «ближайший к файлу — главный». Поддерживается
OpenAI Codex, Jules (Google), Cursor, Amp, Factory, Goose, Aider, Zed, Warp,
opencode и др. (60k+ проектов).

**Зрелость.** Де-факто кросс-вендорный конвенционный стандарт; передан под
Agentic AI Foundation (Linux Foundation) — тот же управляющий дом, что теперь
курирует A2A.

**Что переносимо.** Само существование слоя правил, который читает агент при
старте; правило «ближайший файл главный» ≈ по-ведомственные инструкции; идея
«манифест — это README для ведомства».

**Что не переносимо.** AGENTS.md — проза для чтения агентом, без схемы, без
машинной читаемости, без discovery. Наш `ministry-manifest.yaml` — машинно-читаемый
структурный слой поверх этого.

### 7. Agent registry / registry-as-code и аналогия service-mesh

**Что это.** В индустрии складываются два взаимодополняющих паттерна:

- **Discovery/registry** — A2A описывает discovery через well-known URI
  `.well-known/agent-card.json` и каталоги/registry; MCP имеет собственный
  каталог серверов. Агент заявляет себя карточкой, каталог индексирует.
- **Registry-as-code** — агенты/локации декларируются версионируемыми файлами
  конфигурации в git (наш случай: `.opencode/agent/*.md`, `registry.md` в
  dotfiles, `tools/ecosystem-map/registry.json` в волте), а не в runtime-БД.
- **Аналогия service-mesh** — разделение на control plane (конфигурация,
  discovery, политика, телеметрия — напр. Istiod) и data plane (сам трафик между
  сервисами — напр. sidecar Envoy). У нас это ложится на: control plane =
  librarian (route-log, capability-routing, реестр, решения о маршруте); data
  plane = peer-comms (hello.sh / letter.sh — собственно доставка писем).

**Зрелость.** Service mesh — зрелый паттерн микросервисной инфраструктуры;
agent registry — оформляется (A2A discovery, MCP directory), но единого
стандарта «registry-as-code для агентов» пока нет.

**Что переносимо.** Разделение плоскостей управление/исполнение как чистая
архитектурная метафора; идея «карточка + каталог»; ведение реестра как кода в git.

**Что не переносимо.** Service mesh — про сетевой трафик между репликами
микросервисов; наш «трафик» — письма между постоянными именованными сессиями,
а «сервисы» — не реплики, а уникальные места.

---

## (b) Маппинг: внешние паттерны → наши сущности

Сведение внешних понятий на нашу сеть ведомств. «Наш аналог» — что уже есть
фактически (по локальным файлам); «взять / не хватает» — вывод для УАС-спеки.

| Внешнее понятие | Наш аналог | Что взять / чего не хватает |
|---|---|---|
| AgentCard (A2A) | ministry-manifest.yaml (проект, `docs/org/`) | взять: identity / capabilities / skills / endpoints / auth как поля; не хватает: подписи карточки (provenance) и discovery-URI |
| AgentSkill (A2A) | OpenCode skills (`.opencode/skills/*`) + capabilities | взять: id / name / description / tags / examples; есть частично, не сведено в манифест |
| opaque execution (A2A) | письмо как ограниченный контекст (не полная история родителя) | взять принцип; но мы осознанно переносим больше контекста, чем «opaque» |
| Task + typed lifecycle (A2A) | задача/ход + receipt (started / finished / cannot) | взять: типизированные состояния; не хватает: id задачи и явных состояний, есть только квитанции |
| Discovery (A2A: well-known + catalog) | peer-comms `claims.jsonl` + реестр отсеков | взять: registry-as-code; не хватает: стандартизированного discovery-URI и каталога ведомств |
| SendMessage / GetTask / ListTasks (A2A) | letter.sh (send) + delivery-check (get) | есть доставка и проверка; не хватает: list / cancel / subscribe |
| capability negotiation (MCP) | capability-routing + явный UNROUTABLE | взять: декларация способностей и явный отказ; есть как control-plane |
| user consent (MCP) | human-in-the-loop контракт (подтверждение плана) | уже есть, соответствует |
| agent-definition file (`.claude/agents/*.md`) | `.opencode/agent/*.md` | уже есть, соответствует |
| subagent без истории родителя (Claude SDK) | письмо без истории родителя | уже есть, соответствует |
| caps spawn-depth / concurrent (Claude SDK) | boundaries / limits в манифесте | взять: явные лимиты как поле |
| memory user / project / local (Claude SDK) | memory-zones / file-zones | взять: зоны памяти как поле |
| handoffs + input_type (OpenAI SDK) | перенаправление чужого интента (`ship-research-network` §3) | взять: метаданные-причина перенаправления (provenance); не хватает: формализованного payload |
| guardrails (OpenAI SDK) | reviewer (качество) + verifier (приёмка) | взять: раздельные гейты; у нас это отдельные сессии, не код в цикле |
| sessions + tracing (OpenAI SDK) | session-log + route-log | уже есть, соответствует |
| Session / State / Memory (ADK) | session-log / active-context / facts | уже есть тройное разделение, соответствует |
| evaluation (ADK) | verifier acceptance + evidence | взять: критерии приёмки как первоклассный объект |
| Agent routing (ADK) | перенаправление интента | уже есть как правило, соответствует |
| AGENTS.md nearest-file-wins | AGENTS.md по проектам/ведомствам | уже есть; манифест — машинно-читаемое дополнение |
| service-mesh control vs data plane | librarian control-plane (route-log/реестр/routing) vs peer-comms data plane | взять: явное разделение плоскостей |

Ключевой вывод маппинга: ни один внешний стандарт не совпадает с нами целиком,
но почти каждая наша сущность находит внешний прообраз. Самое ценное заимствование —
не форматы, а три принципа: (1) opaque/ограниченная передача контекста,
(2) типизированный жизненный цикл задачи, (3) разделение control/data plane.

---

## (c) Черновик схемы `ministry-manifest.yaml`

Машинно-читаемый манифест ведомства. Артефакт для УАС-спеки, не внедрение.
Ниже — поля как обычный текст с комментариями (имя → назначение → статус:
обязательное / опциональное).

**Обязательные поля:**

- `id` — устойчивый идентификатор ведомства (короткий slug, латиницей). Аналог
  имени файла агента в OpenCode; по нему адресуются письма и строки реестра.
- `name` / `shadow` — рабочее имя и «тень» (persona/роль, канон закона тени).
  Разделение важно: имя для адресации, тень для диалога.
- `jurisdiction` — компетенция: что входит в ведомство, что перенаправляется.
  Источник — карта компетенций из `ship-research-network` §3.
- `carrier-sessions` — сессии-носители: какие реальные сессии OpenCode являются
  этим ведомством (форма В2 — полноправная именованная сессия). Ссылка на
  session id и/или роль из `claims.jsonl`.
- `mandate-source` — provenance мандата: откуда взята компетенция и полномочие
  (цитата/ссылка на решение Rudra, на спека-контракт). Обязательно, чтобы
  мандат не был самозванным.
- `peer-address` — адрес для peer-comms: как доставить письмо (session id,
  роль для `find --role`). Аналог endpoint в AgentCard.
- `spec-home` — где лежат спеки этого ведомства (`<repo>/docs/specs/`).
- `status` — состояние ведомства (proposed / active / archived) + дата. Аналог
  статуса карточки проекта.
- `boundaries` / `limits` — границы и лимиты: что ведомство не делает, и
  количественные потолки (аналог caps Claude SDK: глубина, параллельность).
- `ports` — ЦУ-порт (центральный узел / центральное управление-порт): точки
  входа, через которые ведомство принимает и отдаёт интенты.

**Опциональные поля:**

- `capabilities` / `skills` — заявленные способности и скиллы (id / name /
  description / tags / examples, как AgentSkill).
- `memory-zones` — зоны памяти, которыми владеет ведомство (по реестру отсеков:
  один отсек = одна тема = одна файловая зона).
- `file-zones` — файловые зоны записи (что ведомство имеет право править).
- `evidence-policy` — политика доказательств: какой verifier/reviewer, какой
  критерий приёмки, что считается evidence.

**Короткий пример (Институт Передовых Технологий):**

- id: `institute-adv-tech`
- name: Институт Передовых Технологий
- shadow: носитель исследования передовых технологий (тень — по закону тени)
- jurisdiction: исследования передовых технологий и внешних кейсов; принимает
  и маршрутизирует, не исследует чужую компетенцию
- carrier-sessions: роль `institute-adv-tech` (из `claims.jsonl`)
- mandate-source: `ship-research-network` §3 + фрагмент 1 сообщения Rudra
- peer-address: роль `institute-adv-tech` через `find --role`
- spec-home: `OpenCode-Vault/docs/specs/` (для ваулт-ведомства)
- status: active, 2026-10-14
- boundaries: не правит код приложений; не канонизирует чужие темы
- ports: ЦУ-порт приёма внешних кейсов; порт перенаправления в Лабораторию

**Короткий пример (Мастерская БагФикс):**

- id: `bugfix-workshop`
- name: Мастерская БагФикс
- jurisdiction: точечный багфикс сбоев в рамках подтверждённого scope
- carrier-sessions: отдельная сессия Мастерской
- mandate-source: реестр исследований Корабля (строка «Мастерская БагФикс»)
- peer-address: роль/сессия Мастерской
- spec-home: по репозиторию, где чинится баг
- status: active
- boundaries: чинит только подтверждённый scope, фикс точечным коммитом
- ports: ЦУ-порт приёма инцидента (symptom → repro → гипотеза → fix)

---

## (d) Вывод: что подтверждается, что корректируется

**Подтверждается внешней практикой (наш гибрид A+B обоснован):**

- Манифест ведомства ≈ AgentCard (A2A) — прямое внешнее подтверждение слоя
  `docs/org/`: идентичность + capabilities + skills + endpoints. Наш выбор
  «манифест как машиночитаемый файл в git» совпадает с registry-as-code.
- Opaque execution (A2A) и «subagent без истории родителя» (Claude SDK)
  совместно подтверждают наш принцип «письмо ≠ полная история», а не опровергают.
- Разделение гейтов «качество отдельно от приёмки» (reviewer → verifier)
  подтверждается guardrails (OpenAI SDK) и evaluation (ADK) — у нас они вынесены
  в отдельные сессии, что сильнее, чем внутрипроцессная проверка.
- Тройное разделение памяти Session / State / Memory (ADK) — буквально наш
  session-log / active-context / facts.
- Перенаправление чужого интента (`ship-research-network` §3) — подтверждается
  handoffs (OpenAI SDK) и agent routing (ADK) как правильный примитив.

**Корректируется / открытые вопросы:**

- **Discovery-механизм нужен, но в лёгкой форме.** A2A делает это через well-known
  URI + каталог; у нас уже есть `claims.jsonl` (роль → session id) и реестр
  отсеков. Недостаёт единого каталога ведомств (где «все манифесты ведомств
  видны одним списком»). Достаточно registry-as-code, полный A2A-discovery не нужен.
- **Typed task lifecycle — частично, не целиком.** A2A Task (7 состояний) —
  избыточен для наших писем; наши receipt-квитанции (started / finished /
  cannot) уже покрывают минимум. Если брать типизацию — то только три состояния
  плюс id задачи, без push-подписок и cancel.
- **Манифест ≈ AgentCard, но с нашим обязательным отличием: provenance.**
  Внешние карточки заявляют capabilities; у нас мандат не самозванный, поэтому
  поле `mandate-source` (источник полномочия) — обязательное, а не опциональное.
  Это наше дополнение поверх AgentCard, у которого такого поля нет.
- **Где контроль-плоскость vs исполнение.** Подтверждается метафорой service-mesh:
  librarian держит control plane (route-log, реестр, capability-routing, решения
  о маршруте), peer-comms — data plane (доставка писем). Это надо зафиксировать
  в УАС-спеке явно, чтобы не смешивать «кто решает» и «кто доставляет».
- **Форма В2 (полноправная сессия) vs внешние subagents.** Внешние SDK делают
  субагентов эфемерными; наша форма В2 (персистентная именованная сессия-место)
  — осознанное отклонение, обоснованное каноном («сессии-места», `048`) и
  С3-становлением, а не инженерной необходимостью. Это надо пометить как
  отклонение, а не как «внешне подтверждённый» паттерн.

---

## (e) Провена — источники

Проверено живым вебом 2026-10-14:

- A2A Protocol Specification v1.0.0 — https://a2a-protocol.org/latest/specification/ (дата проверки 2026-10-14)
- A2A: переход под Agentic AI Foundation — https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/ (2026-08-27)
- MCP Specification 2025-06-18 — https://modelcontextprotocol.io/specification/2025-06-18 (проверка 2026-10-14, по ранее собранному материалу)
- Claude Agent SDK, subagents — https://code.claude.com/docs/en/agent-sdk/subagents (проверка 2026-10-14, по ранее собранному материалу)
- OpenAI Agents SDK — https://openai.github.io/openai-agents-python/ и https://openai.github.io/openai-agents-python/handoffs/ (проверка 2026-10-14)
- Google ADK — https://google.github.io/adk-docs/ и https://google.github.io/adk-docs/sessions/ (проверка 2026-10-14)
- AGENTS.md — https://agents.md/ (проверка 2026-10-14)

Локальные файлы (чтение, вне worktree):

- `/home/rudra/Projects/OpenCode-Vault/06-Audits/2026-10-09-agency-counteragency-brainstorm.md`
- `/home/rudra/dotfiles/docs/specs/ship-research-network.md`
- `/home/rudra/dotfiles/.opencode/memory/registry.md`
- `/home/rudra/dotfiles/tools/peer-comms/` (hello.sh, letter.sh, delivery-check.sh, claims.jsonl)
- `/home/rudra/Projects/OpenCode-Vault/.opencode/` (agent/, agents/, command/, skills/, tools/, opencode.json)
- `/home/rudra/Projects/OpenCode-Vault/.opencode/skills/capability-routing/SKILL.md`
- `/home/rudra/Projects/OpenCode-Vault/01-Reference/rules-AGENTS.md`
- `/home/rudra/Projects/OpenCode-Vault/01-Reference/agents.md`
- `/home/rudra/Projects/OpenCode-Vault/06-Audits/2026-10-13-ship-research-registry.md`

Замечание: файл `06-Audits/2026-10-14-institute-research-tsu-uas-architecture.md`
(предыдущий диагноз гибрида A+B) на момент записи этого отчёта в волте отсутствует —
он создаётся параллельной сессией. Выводы (d) опираются на формулировку мандата
(«гибрид A+B: docs/org манифесты + contracts; вариант C отклонён»), а не на текст
того файла.
