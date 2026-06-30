---
type: project
kind: mobile / ai
status: planning
stack: Kotlin / Jetpack Compose / DeepSeek API / Room / MediaPipe (local LLM)
device: Redmi Note 15 Pro (Android)
timestamp: 2026-06-30
---

# rudra-ai — AI-ассистент на Android

> **Статус:** 🟢 Planning — концепция, дорожная карта
> **Связано:** [[99-Inbox]] (R-004), [[rudra-phone]], [[prod-monitor]], [[00-INDEX#Methods]]

**Цель:** ИИ-ассистент на Android, эволюционирующий от простого планера до полноценного ассистента.

**Ключевой принцип:** Eat your own dogfood — первый Android-проект, созданный через VibeAndroid (R-002).

## Фазы развития

### Фаза 1: Planner (MVP, 1-2 недели)
- TODO-лист с приоритетами (P0-P4 как в TASKS.md)
- Интеграция с проектами (чтение TASKS.md)
- Напоминания по времени
- UI: Jetpack Compose + Material You
- Хранение: Room (SQLite)
- **Статус:** ❌ не начато

### Фаза 2: Agent-aware (2-4 недели)
- Чтение статусов проектов из волта
- Напоминание о проблемах (❌ методы, упавшие сервисы)
- Интеграция с Telegram bot
- Голосовой ввод (Speech-to-Text, Android)
- Push-уведомления
- **Статус:** ❌ не начато

### Фаза 3: Proactive (1-2 месяца)
- Анализ логов → предложения действий
- Предсказание задач на день
- Push с контекстом («SERPlux упал, перезапустить?»)
- Локальный LLM (Gemma 2 2B / Phi-3 через mlc-llm или MediaPipe)
- **Статус:** ❌ не начато

### Фаза 4: Full Assistant (3+ месяца)
- Полноценный текстовый/голосовой интерфейс
- Выполнение команд (через API Gateway → проекты)
- Multi-agent (специализированные суб-агенты)
- Интеграция с календарём, контактами
- Распознавание контекста (проектный / личный)
- **Статус:** ❌ не начато

## Технические решения (предварительно)
- **Язык:** Kotlin (нативный Android)
- **UI:** Jetpack Compose + Material You (под Redmi Note 15 Pro)
- **Local LLM:** Gemma 2 2B через MediaPipe (или mlc-llm)
- **Cloud LLM:** DeepSeek API (как в VibeOS) — для сложных задач
- **Хранение:** Room (локально) + Git-backed (для проектов)
- **Сеть:** Retrofit / Ktor client → API Gateway

## Архитектура (предварительная)

```
┌──────────────────────┐
│   rudra-ai (Android) │
│  ┌────────────────┐  │
│  │ Jetpack Compose │  │
│  │   UI (M3)      │  │
│  └───────┬────────┘  │
│  ┌───────┴────────┐  │
│  │  ViewModel     │  │
│  │  + UseCases    │  │
│  └───────┬────────┘  │
│  ┌───────┴────────┐  │
│  │   Repository   │  │
│  └───┬────┬───────┘  │
│      │    │           │
│  ┌───┴┐ ┌─┴────────┐ │
│  │Room│ │Retrofit  │ │
│  │    │ │API GW    │ │
│  └────┘ └──────────┘ │
└──────────────────────┘
        │
[API Gateway] → [Projects / Vault / OpenCode]
```

## Зависимости
- R-002 (VibeAndroid) — методология для создания Android-проектов
- R-001 (rudra-phone) — приложение может быть модулем rudra-phone или standalone
- R-003 (ProdWatch) — данные мониторинга для proactive-режима
- [[00-INDEX#Methods]] — новые Android-методы

## Вопросы к решению
1. Начинать как отдельное приложение или как модуль rudra-phone?
2. Offline-first или online-only?
3. Какой первый use case? (TODO planner — понятная точка входа)

## Чеклист
- [ ] Установка Android Studio / настройка окружения
- [ ] Фаза 1: TODO Planner MVP
- [ ] Фаза 2: Agent-aware интеграция с проектами
- [ ] Фаза 3: Proactive + local LLM
- [ ] Фаза 4: Full Assistant
