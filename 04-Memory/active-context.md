---
type: Active Context
title: Активный контекст
description: SERPlux — Core ✅, Docker ✅, Deploy ✅. Приоритет: веб-интерфейс. Агенты ui-dev + infra-dev созданы.
tags: [memory]
timestamp: 2026-07-03
---

# Активный контекст

> Автоматически обновляется librarian. Читается при старте каждой сессии.

## Текущий фокус
- **Проект:** SERPlux / SERP Factory
- **Задача:** Веб-интерфейс SERPlux — дашборд, запуск прогона, история, статус. Агенты ui-dev + infra-dev созданы, команды /interface /container /deploy готовы.

## Активная задача
Реализация веб-интерфейса SERPlux через команду `/interface` (агент ui-dev) в репо SERPlux (`/home/rudra/Projects/serp`).
Волт: мониторинг, документация, поддержка архитектуры.

## Что сделано в этой сессии (2026-07-02, part2)
- [x] Централизованное удаление claude-mem из экосистемы
  - [x] Удалён плагин `~/.config/opencode/plugins/claude-mem.js`
  - [x] Очищен `~/.config/opencode/AGENTS.md` (блок `<claude-mem-context>`)
  - [x] Обновлён `02-Methods/memory-management.md` (убрана строка с `[проверить]`)
- [x] Создан бэкап `claude-mem.js.bak`

## Завершённые изменения (все сессии)
- [x] README.md — визитка репозитория как VibeOS (для GitHub, основа для лендинга)
- [x] LICENSE — GPL-3.0 (copyleft + коммерция разрешена) + секция в README + упоминание фонда инженера
- [x] SERP Factory — SERPlux как продукт фабрики. Архитектура: ux-dev, infra-dev, команды /interface /container /deploy. multi-agent-pipeline: Factory variant.
- [x] Имя пользователя: Макс/Max → Max Rudra / Rudra / mr — обновлено во всех файлах волта + LICENSE + facts.md
- [x] distill-pipeline + multi-agent-pipeline метод — дистилляция пайплайнов
- [x] dotfiles v2: полная мульти-агентная архитектура (7 агентов, 8 пайплайнов, память, UX)
- [x] VibeOS v0.2.0–v0.2.3 — дашборд, ревью 17 багов, dotfiles, distill-pipeline
- [x] opencode.json, config.md, facts.md, 00-INDEX, Architecture.md — обновлены
- [x] Модель librarian: Claude Sonnet 4.6 → DeepSeek v4-flash-free
- [x] OKF v0.1 — полная архитектура волта, 6 методов, 4 карточки проектов, память, трекер
- [x] SERPlux: агенты ui-dev + infra-dev, команды /interface /container /deploy, карточка актуализирована

## Отложено (P5 будущее)
- T-015: Telegram-бот для классификации фич
- T-016: /project-upgrade — автоматический апгрейд проектов
- T-017: Команда /project-upgrade
- T-046: R-005 — Project Orchestrator (оркестрация из волта всеми проектами + Android)
- **Напряжения:** память (flush-протокол), теория vs практика

## Открытые вопросы
- (нет открытых вопросов на данный момент)

## Что сделано в этой сессии (2026-07-03)
- [x] Инфраструктурный техдолг Уровня 0
  - [x] Модель librarian: glm-5.2 → qwen3.7-plus
  - [x] Синхронизация модели в agents.md (таблица vault)
  - [x] verifier.md: bash-whitelist python → ./venv/bin/python
  - [x] Факты: папки агентов (ед./мн.ч.), commit-guard, session-flush
  - [x] Команда /done (протокол завершения задачи)
  - [x] Плагин session-flush (file.edited → session-log при idle)
- [x] Убрана привязка `agent: librarian` из /done (команда теперь работает во всех проектах)
- [x] Создан 01-Reference/global-config.md — документация глобальной инфраструктуры (~/.config/opencode/)
- [x] Фикс commit-guard: pytest-вывод захватывается через `.quiet()`, в TUI только итог

## Последнее обновление
2026-07-03 — Фикс commit-guard (pytest-вывод), документация глобальной конфигурации.
