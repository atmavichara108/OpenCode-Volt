---
type: project
kind: инфраструктура / mobile
status: planning
stack: Kotlin / Flutter / Telegram API / Python
device: Redmi Note 15 Pro (Android 15?)
timestamp: 2026-06-30
---

# rudra-phone — Управление проектами с телефона

> **Статус:** 🟢 Planning — концепция, выбор архитектуры
> **Связано:** [[99-Inbox]] (R-001), [[SERPlux]], [[dv-hub]], [[dotfiles]], [[vault]], T-015, T-016

**Цель:** Полноценное управление любым проектом (SERPlux, dv-hub, dotfiles, vault) с Android-телефона (Redmi Note 15 Pro).

## Варианты архитектуры

### A: Telegram Bot (быстрый старт)
- Минимальный UI через Telegram
- Команды: `/project <name> status`, `/audit`, `/deploy`, `/monitor`
- Расширение существующего T-015
- Бэкенд: Python (aiogram 3.x) или TS (grammy)
- **Срок:** 1-2 недели до MVP

### B: Android-приложение (нативное)
- Kotlin + Jetpack Compose (Material You)
- Push-уведомления, биометрия, офлайн-кэш
- **Срок:** 1-2 месяца до MVP

### C: PWA (веб-дашборд)
- Hono/Vite (как dv-hub)
- Работает в браузере на телефоне
- **Срок:** 2-3 недели

### D: Termux + SSH
- Минимальные усилия, консоль
- **Срок:** 1-2 дня, но UX минимальный

## Архитектура (предварительная)

```
[Telegram / Android App / PWA]
       ↓ (HTTPS / WebSocket)
[API Gateway] — авторизация, роутинг, кэш
       ↓
[SERPlux] [dv-hub] [dotfiles] [vault]
       ↓
[OpenCode CLI / shell] — выполнение команд
```

## План внедрения (спринты)

- **Спринт 0:** Выбор архитектуры (эта сессия)
- **Спринт 1:** Telegram Bot MVP (статусы + простые команды)
- **Спринт 2:** API Gateway + SSH-шлюз к проектам
- **Спринт 3:** Android-приложение (нативный UI)

## Зависимости
- T-015 (Telegram-бот) — базовый слой для R-001
- R-003 (ProdWatch) — данные мониторинга для отображения в приложении
- R-004 (Rudra AI) — AI-ассистент может быть встроен в приложение

## Чеклист
- [ ] Выбор первичного варианта (A/B/C/D)
- [ ] Дизайн API Gateway
- [ ] Создание Telegram Bot
- [ ] Разработка Android-приложения
- [ ] Интеграция с ProdWatch
