---
type: Dashboard
title: OpenCode Vault — Dashboard
description: Точка входа, таблица проектов, методы, конвенции волта.
timestamp: 2026-06-29
---
# OpenCode Vault — Dashboard

> Справочник по OpenCode и моим проектам. OKF v0.1 Knowledge Bundle.
> Reference = факты об OpenCode. Methods = мои приёмы. Projects = состояние каждого проекта. Memory = контекст сессий.

## Быстрый вход
- **Визитка репозитория** → [[README]] (для внешних, GitHub)
- **Вся система в одном документе** → [[VibeOS]] (философия, методы, проекты, рост)
- Спросить базу → `/ask "..."`
- Разгрести инбокс → `/inbox`
- Извлечь посты из Telegram → `/capture <тема>`
- Сводка по проекту → `/project <имя>`
- Дистилляция пайплайнов → `/distill-pipeline`
- Coordination Bridge → FROZEN BY USER 2026-08-30 (historical, не вызывать); local-first → `/android-plan`
- Capability route → `/route <свободный intent>`
- Посмотреть дорожную карту → [[DEVELOPMENT-ROADMAP]]
- Execution specs → [[06-Specs/README]] / `/spec <selector>`
- Навигация по OKF → [[index]]
- Трекер задач → [[TASKS]]

## Проекты
| Проект | Тип | Стек | OpenCode-агент особый | Карточка | Статус |
|--------|-----|------|----------------------|----------|--------|
| SERPlux | коммерция | Python / FastAPI | **6 агентов**: build, plan, collector-dev, reviewer, ui-dev, infra-dev · 5 команд | [[SERPlux]] | ✅ active |
| dv-hub | волонтёрский | TS / Hono | plan, build, reviewer, researcher, infra | [[dv-hub]] | ✅ active |
| ChaT | knowledge-operations | Markdown / Obsidian / OpenCode | curator | [[ChaT]] | 🟢 planning |
| dotfiles | система | shell/configs | **multi-agent** (8 агентов, 10 команд) | [[dotfiles]] | ✅ active |
| vault | справочник | markdown | librarian | [[vault]] | ✅ active |
| rudra-phone | инфраструктура | Kotlin/Flutter/Telegram API | — | [[rudra-phone]] | 🟢 planning |
| prod-monitor | инфраструктура | Prometheus/Python/Bash | — | [[prod-monitor]] | 🟢 planning |
| rudra-ai | mobile/ai | Kotlin/Jetpack Compose | — | [[rudra-ai]] | 🟢 planning |
| AndroidOS | umbrella mobile/ecosystem | Android / OpenCode / offline-first | planned | [[AndroidOS]] | 🟢 planning |

> 📊 **Сводка:** `/audit` — проверить все проекты · Таблица статусов методов ниже · Новые проекты в planning

## Reference (возможности OpenCode)
[[agents]] · [[commands]] · [[config]] · [[global-config]] · [[memory]] · [[permissions]] · [[plugins]]

## Сторонний софт (01-Reference/tools/)
[[tools/GTweak]] — Windows-твикер (редко, для чужой машины)

## Methods (мои приёмы)
[[closed-loop]] · [[verifier-pattern]] · [[context-as-docs]] · [[memory-management]] · [[model-routing]] · [[capability-routing]] · [[distill-pattern]] · [[multi-agent-pipeline]] · [[tool-integration-pattern]]

### Cross-project contracts
[[user-profile-contract]] · [[06-Audits/2026-08-22-androidos-open-source-first]] · [[TASKS]] T-103–T-105

### Статус внедрения методов по проектам

> **Источник правды:** карточка проекта (`03-Projects/<name>.md`). Метод-файл ссылается, не определяет.

| Метод | SERPlux | dv-hub | dotfiles | vault |
|-------|---------|--------|----------|-------|
| [[closed-loop]] | ✅ | ❌ | 🟡 | ❌ |
| [[verifier-pattern]] | ✅ | ❌ | 🟡 | ❌ |
| [[context-as-docs]] | ✅ | 🟡 | ✅ | ✅ |
| [[distill-pattern]] | ✅ | ✅ | ✅ | ✅ |
| [[memory-management]] | 🟡 | 🟡 | 🟡 | 🟡 |
| [[model-routing]] | ✅ | ✅ | ➖ | ➖ |
| [[capability-routing]] | ❌ | ❌ | ❌ | ❌ |
| [[multi-agent-pipeline]] | ✅ | ❌ | ✅ | ❌ |
| [[tool-integration-pattern]] | ➖ | ➖ | ➖ | 🟡 |

> ❌ не внедрён · 🟡 частично · ✅ внедрён · ➖ не применимо

## Шаблоны (05-Templates/)
[[05-Templates/README]] · [[05-Templates/project-card]] · [[05-Templates/method]]

## Аудиты (06-Audits/)
[[06-Audits/README]] · [[06-Audits/2026-08-02-vibecoding-layer-audit]] · [[06-Audits/2026-08-02-upgrade-planning-seed]] · [[06-Audits/2026-08-28-androidos-coordination-bridge-spec]] · [[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]]

> Аудит = подтверждённые находки + открытые вопросы + влияние на план апгрейдов.
> Отличается от Methods / Projects / Memory: датированный снимок, не
> приём/карточка/контекст сессии. Новый аудит — новый файл, не правка старого.
> **Ecosystem upgrade plan v2 (2026-08-31):** Layers × Facets matrix, OSS-first
> gate, Agent Workspace, observer, read-only MCP policy, Pip-Boy planning UI;
> Aider retired из roadmap; v1 остаётся историческим canonical.

## Runbooks (07-Runbooks/)
[[07-Runbooks/README]] · [[07-Runbooks/vibecoding-operator-handbook]] · [[07-Runbooks/coordination-bridge-operator-guide]] · [[07-Runbooks/vibecoding-changelog]]

> **Methods** = abstract reusable techniques. **Audits** = dated findings.
> **Runbooks** = live usage and operator workflows.

## Execution specs
[[06-Specs/README]] · [[06-Specs/Vault/ecosystem-registry]] · [[06-Specs/Vault/mcp-readonly]] · SERPlux local specs:
`file:///home/rudra/Projects/serp/docs/specs/`

> Для всех проектов, кроме SERPlux, canonical execution specs находятся в Vault.
> Approved exception SERPlux: authoritative specs находятся только в
> `/home/rudra/Projects/serp/docs/specs/` и читаются project-local `/spec`.
> Vault SERPlux files выше сохранены как archived legacy artifacts. Specs не
> являются evidence выполнения.
> **Ecosystem registry spec (2026-08-31):** canonical schema Layers × Facets,
> lifecycle IDEA→RETIRED, card schema, one-source/multiple-projections;
> canonical данные — `tools/ecosystem-map/registry.json`.
> **MCP read-only spec (2026-08-31):** контракт ecosystem-state MCP;
> implementation BLOCKED; preferred path — custom tool `ecosystem-snapshot`.

## Temporary (98-Temporary/)
[[98-Temporary/README]] — сырые файлы от пользователя на экстракцию; обрабатываются и удаляются (не источник правды, не смешивать с `99-Inbox/`)

## Инструменты (tools/)
`tools/telegram-capture/` — извлечение постов из Telegram (в разработке, T-062)
`tools/ecosystem-map/` — Pip-Boy карта экосистемы (T-069 → v3 multi-view T-121): SKILLS-граф + MATRIX/KANBAN/PROJECTS/AGENTS/BLOCKERS/WORKSPACE поверх canonical `registry.json` + generated snapshot; static/generated, real-time не заявляется. Observer: `python3 tools/ecosystem-map/observer.py` — read-only детерминированный snapshot (T-120).

## Память (04-Memory/ — OKF sub-bundle)
[[active-context]] · [[facts]] · [[session-log/2026-06-27]] · [[session-log/2026-06-29]] · [[session-log/2026-06-30]] · [[session-log/2026-08-14]] · [[session-log/2026-08-29]] · [[04-Memory/index]] · [[04-Memory/log]]

## Конвенции
- Метод описывается ОДИН раз в `02-Methods/`. Карточки только ссылаются `wikilink`.
- Карточка = реальное состояние репо (агенты/команды/скрипты/окружение), не копия кода.
- Новое знание → `99-Inbox.md` → оформляется через `/inbox`.
- Память сессии → `04-Memory/` → читается при старте, пишется по ходу и в конце.
- Статусы внедрения: ❌ нет · 🟡 частично · ✅ внедрено
- Неподтверждённые факты по OpenCode помечать `[проверить]`.
- Reference — выжимка, источник правды доки opencode.ai (с датой проверки).
- Аудит (`06-Audits/`) — датированный снимок: подтверждённые находки + открытые
  вопросы + влияние на план апгрейдов. Новый аудит — новым файлом, не правкой
  старого; seed — каркас, не финальный план.
- ВСЕГДА думать и отвечать на русском, если не указано иное.
