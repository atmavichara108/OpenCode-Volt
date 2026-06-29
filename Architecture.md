---
type: Architecture
title: Принцип и структура волта
description: Четырёхслойная архитектура Reference → Methods → Projects → Templates. Теперь также OKF-бандл.
timestamp: 2026-06-29
---
## **Принцип, на котором строим**

Один источник правды по OpenCode, организованный как **OKF-бандл** (Open Knowledge Format v0.1): справочник (как устроен OpenCode сам по себе), методы (твои рабочие приёмы и протоколы), проекты (живые карточки каждого репозитория), память (контекст сессий), и шаблоны (заготовки для новых проектов).

>Главное правило, которое спасёт от хаоса: методичка описывает приёмы абстрактно, а карточки проектов содержат конкретику. Когда захочешь проапгрейдить все проекты разом — ты меняешь метод в одном месте и прогоняешь по карточкам. Карточка проекта никогда не дублирует объяснение приёма, она только ссылается на него и фиксирует, что именно из него внедрено.
>
>Память — OKF-подбандл `04-Memory/`. Три уровня: active-context (фокус сессии), facts (реестр фактов), session-log (хроника). При старте librarian читает их — и не перечитывает весь волт целиком.

**Структура волта (OKF v0.1 Knowledge Bundle)**

OpenCode-Vault/                    ← OKF-бандл + OpenCode-проект
├── index.md                       ← OKF bundle root index (генерируемый, для навигации)
├── log.md                         ← OKF bundle update log
├── .opencode/                     ← конфигурация OpenCode (не часть OKF)
│   ├── agent/librarian.md
│   └── command/{ask,capture,project,commit,project-add,audit}.md
├── AGENTS.md                      ← правила для librarian
├── 00-INDEX.md                    ← дашборд: детальная таблица проектов и конвенции
├── 01-Reference/                  ← OKF-концепты: возможности OpenCode
│   ├── agents.md                  → type: Reference
│   ├── commands.md                → type: Reference
│   ├── config.md                  → type: Reference
│   ├── memory.md                  → type: Reference (система памяти на OKF)
│   ├── permissions.md             → type: Reference
│   ├── plugins.md                 → type: Reference
│   └── rules-AGENTS.md            → type: Reference (формат AGENTS.md)
├── 02-Methods/                    ← OKF-концепты: приёмы
│   ├── closed-loop.md             → type: Method
│   ├── context-as-docs.md         → type: Method
│   ├── distill-pattern.md         → type: Method
│   ├── memory-management.md       → type: Method
│   ├── model-routing.md           → type: Method
│   └── verifier-pattern.md        → type: Method
├── 03-Projects/                   ← OKF-концепты: карточки проектов
│   ├── dv-hub.md                  → type: Project Card
│   ├── SERPlux.md                 → type: Project Card
│   ├── dotfiles.md                → type: Project Card
│   └── vault.md                   → type: Project Card
├── 04-Memory/                     ← OKF-подбандл: система памяти
│   ├── index.md                   ← OKF sub-bundle index
│   ├── log.md                     ← OKF sub-bundle log
│   ├── active-context.md          → type: Active Context
│   ├── facts.md                   → type: Fact Registry
│   └── session-log/               → type: Session Log
│       ├── 2026-06-27.md
│       └── 2026-06-29.md
├── 05-Templates/                  ← шаблоны (project-card, method, README, pre-commit-check, archive-session-log)
├── 99-Inbox.md                    ← type: Inbox — буфер сырых заметок
├── Architecture.md                ← этот файл, type: Architecture
├── DEVELOPMENT-ROADMAP.md         ← type: Roadmap
└── .obsidian/                     ← конфиги редактора (не OKF)

---
## Как заполнять Reference без переписывания доков

Не копируй документацию OpenCode целиком — она устареет и ты будешь её синхронизировать вручную. В `01-Reference/` держи только выжимку: те факты и таблицы, которые реально используешь (таблица permission-ключей, синтаксис команд `$ARGUMENTS`/`!`shell``/`@file`, разница primary vs subagent), плюс ссылку на официальную страницу. Reference — это твоя шпаргалка, а не зеркало доков.

## Протокол ведения волта (чтобы не зарос)

Три правила, которые держат методичку живой. Идея, которая пришла в процессе работы — сразу в `99-Inbox.md` одной строкой, не отвлекаясь. Раз в неделю (или когда Inbox распух) — разбор: каждая строка либо становится методом/протоколом, либо удаляется. Когда метод меняется — обновляешь его один раз в `02-Methods/`, потом открываешь `00-INDEX` таблицу проектов и прогоняешь изменение по карточкам, отмечая статусы. Так «централизованный апгрейд всех проектов» превращается из абстракции в конкретный обход таблицы.

### Источник правды статусов методов

**Карточка проекта (`03-Projects/<name>.md`) — единственный источник правды** для статуса внедрения метода. Метод-файл (`02-Methods/<name>.md`) только **ссылается** на карточки в строке «Внедрён в:», не определяет статус. 00-INDEX и facts.md — вторичны, должны совпадать с карточками. Это правило предотвращает расхождения: когда метод говорит ✅, а карточка ❌, права карточка (она отражает реальное состояние репо).