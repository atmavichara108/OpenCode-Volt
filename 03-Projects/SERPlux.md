---
type: project
repo: /home/rudra/Projects/serp
kind: коммерция / продукт SERP Factory
stack: Python 3.11+ / requests / gspread / FastAPI / DeepSeek / SQLite / Tailwind CSS / Docker
---
# SERPlux — продукт SERP Factory

> **SERP Factory** — производственная линия по созданию deployable-продуктов для работы с поисковой выдачей.
> **SERPlux** — первый продукт фабрики.

Сбор позиций Google через Topvisor Snapshots API, классификация URL (DeepSeek), выгрузка в Google Sheets.
**MVP почти готов:** осталось собрать UI, упаковать в Docker, развернуть на сервере.

**Окружение:** Python venv. Секреты в `.env` (см. `.env.example`).
**Запуск (dev):** `python main.py`
**Провайдер:** OpenCode Zen (primary) + DeepSeek (labeler)
**Дедлайн деплоя:** сегодня

---

## Что сделано (core ready)

- ✅ Коллектор: topvisor.py (run_check / poll_status / get_snapshot)
- ✅ Сборщик: collector.py (collect(config) → list[Row])
- ✅ Классификатор: labeler.py (кэш + DeepSeek LLM)
- ✅ Хранилище: storage.py (SQLite — кэш, история)
- ✅ Экспортёр: exporter.py (Google Sheets с цветовой разметкой)
- ✅ Отчётность: reporter.py
- ✅ Конфиг: config.py (управляющий Google Sheet)
- ✅ Webhook: webhook.py (FastAPI endpoint — пустая заготовка)
- ✅ Модульная архитектура с контрактами (docs/contracts.md)

## Что делаем сейчас (first approximation)

### 1. UI / Интерфейс
Расширить FastAPI-заглушку (webhook.py) в полноценный веб-интерфейс:
- Дашборд: последний сбор, статус, метрики
- Кнопка ручного запуска сбора
- Просмотр результатов (таблица с фильтрацией)
- Tailwind CSS, без тяжёлых фреймворков

### 2. Docker
- `Dockerfile` — Python-приложение + зависимости
- `docker-compose.yml` — сервис + SQLite + nginx (опционально)
- Multi-stage сборка для минимального размера

### 3. Deploy
- VPS (хостинг)
- Поднять контейнер
- Настроить CI (git push → авто-деплой, опционально)

---

## Архитектура (MVP)

```
                    ┌──────────────────┐
                    │   Google Sheets  │
                    │   (управление +   │
                    │    отчётность)    │
                    └────────┬─────────┘
                             │
┌────────────────────────────┴────────────────────────────┐
│                   SERPlux (FastAPI)                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Collector│→│ Labeler  │→│ Storage  │→│Exporter │ │
│  │(topvisor)│  │(DeepSeek)│  │(SQLite)  │  │(Sheets) │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Web UI (FastAPI routes + Tailwind)              │   │
│  │  / ─ дашборд · /run — запуск · /history — лог   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │   Docker контейнер │
                    │   (alpine + Python)│
                    └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │   VPS / Сервер   │
                    └─────────────────┘
```

---

## Агенты (первое приближение)

> Расширение текущей архитектуры под дедлайн. После деплоя — глубокая модернизация.

| Агент | Mode | Модель | Назначение | edit |
|-------|------|--------|-----------|------|
| **architect** | primary | claude-sonnet-4-6 | Спеки, ADR, архитектура | deny |
| **builder** | primary | claude-sonnet-4-6 | Разработка (код, тесты, докеризация) | allow |
| **collector-dev** | subagent | claude-sonnet-4-6 | Topvisor + сбор данных | allow |
| **reviewer** | subagent | gpt-5.3-codex | PASS/FAIL верификация | deny |
| **ux-dev** | **subagent (NEW)** | claude-sonnet-4-6 | Web UI: FastAPI-роуты + Tailwind | allow |
| **infra-dev** | **subagent (NEW)** | deepseek-v4-flash-free | Docker + deploy + сервер | allow |

### ux-dev
- **Режим:** subagent (вызывается из контекста builder)
- **Модель:** claude-sonnet-4-6 (UI требует качества)
- **Назначение:** проектирование и реализация веб-интерфейса SERPlux
- **Права:** edit: allow, bash (python*, npm*, cat*, ls*)
- **Контекст:** FastAPI + Jinja2 или Vanilla JS + Tailwind
- **Anti-goals:** не лезть в core-модули (collector, labeler, etc.)

### infra-dev
- **Режим:** subagent (вызывается из builder)
- **Модель:** deepseek-v4-flash-free (дешёвая, инфра-задачи)
- **Назначение:** Docker, docker-compose, deploy, CI/CD
- **Права:** edit: allow, bash (docker*, python*, cat*, ls*)
- **Контекст:** alpine + Python multi-stage Dockerfile
- **Anti-goals:** не трогать код приложения, не менять окружение

---

## Команды (пайплайны первого приближения)

| Команда | Пайплайн | Что делает |
|---------|----------|-----------|
| `/interface` | ux-dev → builder → reviewer | Спроектировать и реализовать веб-интерфейс |
| `/container` | infra-dev → builder → reviewer | Создать Dockerfile + docker-compose |
| `/deploy` | infra-dev → builder | Развернуть на сервере (первый деплой) |
| `/review` | reviewer | Code review по запросу |

После деплоя: `/pipeline` (architect → builder → reviewer) — полный цикл фабрики.

---

## Конфиг (opencode.json — предлагаемые изменения)

```json
{
  "default_agent": "builder",
  "agent": {
    "architect": {
      "mode": "primary",
      "model": "opencode/claude-sonnet-4-6",
      "permission": { "edit": "deny", "task": { "*": "allow" } }
    },
    "builder": {
      "mode": "primary",
      "model": "opencode/claude-sonnet-4-6",
      "steps": 30,
      "permission": { "task": { "*": "allow" } }
    },
    "ux-dev": {
      "mode": "subagent",
      "model": "opencode/claude-sonnet-4-6",
      "permission": { "edit": "allow", "bash": { "*": "ask", "python*": "allow", "cat*": "allow", "ls*": "allow" } }
    },
    "infra-dev": {
      "mode": "subagent",
      "model": "opencode/deepseek-v4-flash-free",
      "permission": { "edit": "allow", "bash": { "*": "ask", "docker*": "allow", "python*": "allow", "cat*": "allow", "ls*": "allow" } }
    },
    "reviewer": {
      "mode": "subagent",
      "model": "opencode/gpt-5.3-codex",
      "permission": { "edit": "deny" }
    }
  }
}
```

---

## Состояние методов

| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | нет команды /loop |
| [[verifier-pattern]] | 🟡 | reviewer есть, PASS/FAIL в процессе внедрения |
| [[context-as-docs]] | 🟡 | docs/contracts.md + decisions.md есть, DoD не формализован |
| [[distill-pattern]] | 🟡 | `/interface`, `/container`, `/deploy` — первые команды |
| [[memory-management]] | ❌ | нет flush-протокола |
| [[model-routing]] | 🟡 | architect/builder на Sonnet, infra-dev на DeepSeek, reviewer на GPT — 3 модели |
| [[multi-agent-pipeline]] | 🟡 | Первое приближение: 2 primary + 4 subagent |

---

## Плагины
env-guard.js · notify.js

---

## После деплоя (что модернизируем)
- Полноценный `/pipeline` — architect → builder → reviewer
- verifier-pattern ✅ — reviewer с PASS/FAIL
- closed-loop — авто-итерация
- memory-management — flush-протокол
- model-routing — полное разведение
- SERP Factory: вторая линия (новый продукт)

---

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-29: обновлён стек, статусы методов
- 2026-06-30: ревью — модели, stack, labeler
- 2026-06-30: **SERP Factory** — SERPlux как продукт фабрики. Агенты: architect, ux-dev, infra-dev. Команды: /interface, /container, /deploy. Дедлайн деплоя: сегодня.
