---
type: project
repo: /home/rudra/Projects/serp
kind: коммерция / продукт SERP Factory
stack: Python 3.11+ / requests / gspread / FastAPI / DeepSeek / SQLite / Tailwind CSS / Docker / Jinja2
---
# SERPlux — продукт SERP Factory

> **SERP Factory** — производственная линия по созданию deployable-продуктов для работы с поисковой выдачей.
> **SERPlux** — первый продукт фабрики.

Сбор позиций Google через Topvisor Snapshots API, классификация URL (DeepSeek), выгрузка в Google Sheets.
**Статус:** Core ✅, Docker ✅, Deploy ✅, Web UI ❌ (приоритет сейчас). Безопасность: тесты пройдены, техдолг зафиксирован.

**Окружение:** Python venv / Docker. Секреты в `.env` (см. `.env.example`).
**Запуск (dev):** `python main.py`
**Запуск (prod):** `docker compose up -d`
**Провайдер:** OpenCode Zen (primary) + DeepSeek (labeler)
**Сервер:** задеплоено, собственный домен

---

## Что сделано (✅ готово)

- ✅ Коллектор: topvisor.py (run_check / poll_status / get_snapshot)
- ✅ Сборщик: collector.py (collect(config) → list[Row])
- ✅ Классификатор: labeler.py (кэш + DeepSeek LLM)
- ✅ Хранилище: storage.py (SQLite — кэш, история)
- ✅ Экспортёр: exporter.py (Google Sheets с цветовой разметкой)
- ✅ Отчётность: reporter.py (матрица под формат заказчика)
- ✅ Конфиг: config.py (управляющий Google Sheet)
- ✅ Webhook: webhook.py (FastAPI: /health, /status, /run)
- ✅ Apps Script: apps_script.gs (меню SERPlux в Google Sheets)
- ✅ Docker: Dockerfile (multi-stage, non-root, healthcheck)
- ✅ Docker Compose: docker-compose.yml (volume, credentials, ресурсы)
- ✅ Deploy: на сервере с собственным доменом
- ✅ Безопасность: тесты пройдены, критических дыр нет
- ✅ Техдолг: зафиксирован в docs/techdebt.md
- ✅ UI-спецификация: docs/ui-spec.md (609 строк, подробная)
- ✅ Модульная архитектура с контрактами (docs/contracts.md)

## Что делаем сейчас

### 🎯 Приоритет: Веб-интерфейс
Расширить FastAPI-заглушку (webhook.py) в полноценный веб-интерфейс:
- Дашборд: последний сбор, статус, метрики
- Форма запуска прогона с параметрами
- Просмотр результатов (таблица с фильтрацией)
- Статус прогона в реальном времени (polling)
- Jinja2 + Tailwind CSS, без тяжёлых фреймворков

### Следующее (после UI)
- Мультиклиентность: профили клиентов в SQLite, API /clients
- Мультипровайдерность: фолбек-цепочка LLM, API /providers
- Закрытие техдолга (docs/techdebt.md)

---

## Агенты (актуально на 2026-07-02)

| Агент | Mode | Модель | Назначение | edit |
|-------|------|--------|-----------|------|
| **build** | primary | claude-sonnet-4-6 | Основная разработка | allow |
| **plan** | primary | claude-sonnet-4-6 | Планирование, анализ | deny |
| **collector-dev** | subagent | claude-sonnet-4-6 | Topvisor + сбор данных | allow |
| **reviewer** | subagent | gpt-5.3-codex | PASS/FAIL верификация | deny |
| **ui-dev** | subagent **(NEW)** | claude-sonnet-4-6 | Web UI: FastAPI + Jinja2 + Tailwind | allow |
| **infra-dev** | subagent **(NEW)** | deepseek-v4-flash-free | Docker + deploy + сервер | allow |

### ui-dev
- **Режим:** subagent (вызывается из build или через `/interface`)
- **Модель:** claude-sonnet-4-6 (UI требует качества)
- **Назначение:** проектирование и реализация веб-интерфейса SERPlux
- **Права:** edit: allow, bash (python*, curl*, cat*, ls*)
- **Контекст:** FastAPI + Jinja2 + Tailwind CSS + Vanilla JS
- **Anti-goals:** не лезть в core-модули (collector, labeler, etc.), не менять Docker

### infra-dev
- **Режим:** subagent (вызывается из build или через `/container`, `/deploy`)
- **Модель:** deepseek-v4-flash-free (дешёвая, инфра-задачи)
- **Назначение:** Docker, docker-compose, deploy, CI/CD, сервер
- **Права:** edit: allow, bash (docker*, nginx*, certbot*, cat*, ls*)
- **Контекст:** multi-stage Dockerfile, docker-compose, reverse proxy
- **Anti-goals:** не трогать код приложения (.py файлы)

---

## Команды (пайплайны)

| Команда | Агент | Что делает |
|---------|-------|-----------|
| `/interface` | ui-dev | Реализовать веб-интерфейс: дашборд, запуск, история, статус |
| `/container` | infra-dev | Создать/обновить Dockerfile + docker-compose |
| `/deploy` | infra-dev | Развернуть на сервере: проверка, обновление, proxy, SSL |
| `/review` | reviewer (через build) | Code review по запросу |
  }
}
```

---

## Состояние методов

| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ❌ | нет команды /loop |
| [[verifier-pattern]] | 🟡 | reviewer есть, PASS/FAIL в процессе внедрения |
| [[context-as-docs]] | ✅ | docs/contracts.md, decisions.md, ui-spec.md, techdebt.md, progress.md |
| [[distill-pattern]] | ✅ | `/interface`, `/container`, `/deploy` — команды-пайплайны |
| [[memory-management]] | ❌ | нет flush-протокола |
| [[model-routing]] | ✅ | build/plan на Sonnet, ui-dev на Sonnet, infra-dev на DeepSeek, reviewer на GPT |
| [[multi-agent-pipeline]] | ✅ | 2 primary + 4 subagent, команды через .opencode/command/ |

---

## Плагины
env-guard.js · notify.js

---

## После UI (что модернизируем)
- Мультиклиентность: профили клиентов, API /clients
- Мультипровайдерность: фолбек-цепочка LLM, API /providers
- Закрытие техдолга (docs/techdebt.md) — провайдеры, project_id, date, валидация
- verifier-pattern ✅ — reviewer с PASS/FAIL
- closed-loop — авто-итерация
- memory-management — flush-протокол
- SERP Factory: вторая линия (новый продукт)

---

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-29: обновлён стек, статусы методов
- 2026-06-30: ревью — модели, stack, labeler; SERP Factory — SERPlux как продукт
- 2026-07-02: **Core ✅, Docker ✅, Deploy ✅**. Созданы агенты ui-dev + infra-dev. Команды /interface, /container, /deploy. Приоритет — веб-интерфейс.
