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
- **Вся система в одном документе** → [[VibeOS]] (философия, методы, проекты, рост)
- Спросить базу → `/ask "..."`
- Разгрести инбокс → `/capture`
- Сводка по проекту → `/project <имя>`
- Дистилляция пайплайнов → `/distill-pipeline`
- Посмотреть дорожную карту → [[DEVELOPMENT-ROADMAP]]
- Навигация по OKF → [[index]]
- Трекер задач → [[TASKS]]

## Проекты
| Проект | Тип | Стек | OpenCode-агент особый | Карточка |
|--------|-----|------|----------------------|----------|
| SERPlux | коммерция | Python | collector-dev, reviewer | [[SERPlux]] |
| dv-hub | волонтёрский | TS / Hono | plan, build, reviewer, researcher, infra | [[dv-hub]] |
| dotfiles | система | shell/configs | **multi-agent** (7 агентов, 8 пайплайнов) | [[dotfiles]] |
| vault | справочник | markdown | librarian | [[vault]] |

> 📊 **Сводка:** `/audit` — проверить все проекты · Таблица статусов методов ниже

## Reference (возможности OpenCode)
[[agents]] · [[commands]] · [[config]] · [[memory]] · [[permissions]] · [[plugins]]

## Methods (мои приёмы)
[[closed-loop]] · [[verifier-pattern]] · [[context-as-docs]] · [[memory-management]] · [[model-routing]] · [[distill-pattern]] · [[multi-agent-pipeline]]

### Статус внедрения методов по проектам

> **Источник правды:** карточка проекта (`03-Projects/<name>.md`). Метод-файл ссылается, не определяет.

| Метод | SERPlux | dv-hub | dotfiles | vault |
|-------|---------|--------|----------|-------|
| [[closed-loop]] | ❌ | ❌ | 🟡 | ❌ |
| [[verifier-pattern]] | ❌ | ❌ | 🟡 | ❌ |
| [[context-as-docs]] | 🟡 | 🟡 | ✅ | ✅ |
| [[distill-pattern]] | ❌ | ✅ | ✅ | ✅ |
| [[memory-management]] | ❌ | 🟡 | 🟡 | 🟡 |
| [[model-routing]] | 🟡 | ✅ | ➖ | ➖ |
| [[multi-agent-pipeline]] | ❌ | ❌ | ✅ | ❌ |

> ❌ не внедрён · 🟡 частично · ✅ внедрён · ➖ не применимо

## Шаблоны (05-Templates/)
[[05-Templates/README]] · [[05-Templates/project-card]] · [[05-Templates/method]]

## Память (04-Memory/ — OKF sub-bundle)
[[active-context]] · [[facts]] · [[session-log/2026-06-27]] · [[session-log/2026-06-29]] · [[session-log/2026-06-30]] · [[04-Memory/index]] · [[04-Memory/log]]

## Конвенции
- Метод описывается ОДИН раз в `02-Methods/`. Карточки только ссылаются `wikilink`.
- Карточка = реальное состояние репо (агенты/команды/скрипты/окружение), не копия кода.
- Новое знание → `99-Inbox.md` → оформляется через `/capture`.
- Память сессии → `04-Memory/` → читается при старте, пишется по ходу и в конце.
- Статусы внедрения: ❌ нет · 🟡 частично · ✅ внедрено
- Неподтверждённые факты по OpenCode помечать `[проверить]`.
- Reference — выжимка, источник правды доки opencode.ai (с датой проверки).
- ВСЕГДА думать и отвечать на русском, если не указано иное.
