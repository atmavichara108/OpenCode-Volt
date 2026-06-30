---
type: project
kind: инфраструктура / monitoring
status: planning
stack: Python / Bash / Prometheus / uptime-kuma / Grafana / Telegram
timestamp: 2026-06-30
---

# prod-monitor — Production Monitoring System

> **Статус:** 🟢 Planning — концепция, выбор стека
> **Связано:** [[99-Inbox]] (R-003), [[SERPlux]], [[dv-hub]], [[rudra-phone]]

**Цель:** Система мониторинга продуктов на проде — SERPlux, dv-hub, будущие деплои.

## Что мониторим
- **Uptime:** сервис жив? HTTP 200? Response time?
- **Errors:** логи ошибок, 5xx, исключения
- **Resources:** CPU, RAM, диск
- **Data:** БД соединения, очередь задач
- **Business:** метрики продукта (сбор данных, пользователи)

## Стек (варианты)

### Минималистичный (Фаза 0)
- Shell-скрипты + cron + Telegram bot
- Health-check каждые N минут
- Ошибки → Telegram на телефон
- **Срок:** 1-2 дня

### Лёгкий (Фаза 1)
- `uptime-kuma` — дашборд uptime + уведомления
- JSON-логи → простой веб-дашборд
- **Срок:** 1 неделя

### Полный (Фаза 2-3)
- Prometheus + node_exporter — метрики
- Loki + promtail — логи
- Grafana — дашборды
- Gotify / Telegram — алерты на телефон
- **Срок:** 1-2 месяца

## Архитектура (полная)

```
[Product Servers]
  ↓ (metrics endpoint / promtail)
[Prometheus] [Loki]
  ↓           ↓
[Grafana] ← ─ ┘
  ↓
[Alertmanager → Gotify / Telegram → Redmi Note 15 Pro]
```

## План внедрения

### Фаза 0: Онлайн-статус (1-2 дня)
- Health-check: `curl` → `if fail → Telegram`
- Скрипт `/usr/local/bin/healthcheck.sh`
- cron: `*/5 * * * *`

### Фаза 1: Дашборд (1 неделя)
- uptime-kuma или самописный дашборд
- Список сервисов + статус + история
- Доступ с телефона через PWA

### Фаза 2: Метрики + алерты (2 недели)
- Prometheus + node_exporter
- Базовые алерты (CPU > 90%, диск > 95%, сервис dead)
- Уровни: info / warning / critical

### Фаза 3: Observability (1 месяц)
- Логи (Loki или просто journald + grep)
- Трассировка (опционально)
- Интеграция с rudra-phone

## Зависимости
- Где хостинг? (свой сервер/VPS)
- SERPlux: где запущен? уже в проде?
- dv-hub: нужен мониторинг?

## Чеклист
- [ ] Определить хостинг-инфраструктуру
- [ ] Фаза 0: Health-check + Telegram
- [ ] Фаза 1: Дашборд
- [ ] Фаза 2: Prometheus + алерты
- [ ] Фаза 3: Полная observability
- [ ] Интеграция с rudra-phone
