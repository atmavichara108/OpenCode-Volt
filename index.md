# OpenCode Vault — Knowledge Bundle

> OKF v0.1 — Knowledge Bundle Root

## Reference (OpenCode facts)
* [agents](/01-Reference/agents.md) — Agent types: primary, subagent, frontmatter spec, orchestration
* [commands](/01-Reference/commands.md) — Command definitions, placeholders, built-in commands
* [config](/01-Reference/config.md) — Configuration files, JSON skeleton, providers, models
* [memory](/01-Reference/memory.md) — File-based memory system (OKF-backed, not claude-mem)
* [permissions](/01-Reference/permissions.md) — Permission keys, fine-tuning, project-specific rules
* [plugins](/01-Reference/plugins.md) — Lifecycle hooks, plugin registry

## Methods (техники и паттерны)
* [closed-loop](/02-Methods/closed-loop.md) — Итеративный цикл: план → действие → проверка
* [context-as-docs](/02-Methods/context-as-docs.md) — Контекстные файлы как документация для ИИ
* [distill-pattern](/02-Methods/distill-pattern.md) — Сжатие/структурирование знаний в заметки
* [memory-management](/02-Methods/memory-management.md) — Управление памятью сессии + файловая память
* [model-routing](/02-Methods/model-routing.md) — Разные модели для разных шагов
* [verifier-pattern](/02-Methods/verifier-pattern.md) — Проверка через отдельный скрипт/воркфлоу

## Projects (карточки проектов)
* [dv-hub](/03-Projects/dv-hub.md) — Волонтёрская платформа, TS/Hono/SQLite
* [SERPlux](/03-Projects/SERPlux.md) — Коммерческий SEO-пайплайн, Python/FastAPI
* [dotfiles](/03-Projects/dotfiles.md) — Системные конфиги Manjaro (план)
* [vault](/03-Projects/vault.md) — Этот волт, справочник по OpenCode

## Memory (контекст сессий и факты)
* [active-context](/04-Memory/active-context.md) — Текущий фокус сессии
* [facts](/04-Memory/facts.md) — Реестр подтверждённых фактов
* [session-log](/04-Memory/session-log/) — Хроника сессий (по дням)

## System
* [dashboard](/00-INDEX.md) — Полный дашборд с таблицей проектов и конвенциями
* [vibeos](/VibeOS.md) — Концептуальный дашборд системы вайбкодинга (философия, методы, проекты, рост)
* [architecture](/Architecture.md) — Принципы и структура волта
* [agents](/AGENTS.md) — Правила librarian-агента
* [roadmap](/DEVELOPMENT-ROADMAP.md) — Стратегический план P0–P4
* [tasks](/TASKS.md) — Оперативный трекер задач
* [inbox](/99-Inbox.md) — Буфер для сырых заметок
