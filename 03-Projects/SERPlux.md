---
type: project
repo: /home/rudra/Projects/serp
kind: коммерция / продукт SERP Factory
stack: Python 3.11+ / requests / gspread / FastAPI / DeepSeek / SQLite / Docker
---
# SERPlux — продукт SERP Factory

> **SERP Factory** — производственная линия по созданию deployable-продуктов для работы с поисковой выдачей.
> **SERPlux** — первый продукт фабрики.

Сбор позиций Google через Topvisor Snapshots API, классификация URL (DeepSeek), выгрузка в Google Sheets.
**Статус:** Core ✅, Docker ✅, Deploy ✅. Интерфейс = Google Sheets. Web UI — приостановлено (не запрошено заказчиком, требуется ADR). Безопасность: тесты пройдены, техдолг зафиксирован.

**Окружение:** Python venv / Docker. Секреты в `.env` (см. `.env.example`).
**Структура:** FLAT layout — все модули (.py) в корне репозитория. Каталога `src/` нет и не будет.
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
- ✅ Новая схема БД: clients / positions / labels (версионирование меток, migrate.py)
- ✅ Режим `domains` разметки: справочник `domain_labels` (без LLM), поле `confidence`, параметр `client_id`
- ✅ POST /run расширен: `client_id`, `label_mode` (default `domains`), `force_relabel` + валидация
- ✅ migrate.py идемпотентен (любое состояние БД → корректная схема)
- ✅ Тесты: 111/111 зелёных (pytest, :memory:)

## Что делаем сейчас

### 🎯 Приоритет: Мультипровайдерность и закрытие техдолга
- Фолбек-цепочка LLM, API /providers
- API /clients (профили клиентов — схема готова, эндпоинт в планах)
- Закрытие техдолга (docs/techdebt.md — httpx/starlette deprecation и пр.)

### ⏸ Приостановлено
- **Web UI** — ADR от 2026-07-02: единственный UI = Google Sheets. Веб-фронт не строим без явного запроса заказчика.

---

## Агенты (актуально на 2026-07-03)

| Агент | Mode | Модель | Назначение | edit |
|-------|------|--------|-----------|------|
| **build** | primary | opencode-go/kimi-k2.7-code | Основная разработка, коммит через `/commit` | allow |
| **plan** | primary | opencode-go/glm-5.2 | Планирование, анализ, делегирование build (task: build allow) | deny |
| **collector-dev** | subagent | opencode-go/kimi-k2.7-code | Topvisor + сбор данных (topvisor.py, collector.py) | allow |
| **reviewer** | subagent | opencode-go/glm-5.2 | PASS/FAIL верификация контрактов | deny |
| **ui-dev** | subagent | opencode-go/kimi-k2.7-code | Google Sheets UI (Apps Script меню, лист «Настройки») | allow |
| **infra-dev** | subagent | opencode-go/qwen3.7-plus | Docker, deploy, серверная инфраструктура | allow |

### ui-dev
- **Режим:** subagent (вызывается из build или через `/interface`)
- **Статус:** ✅ активен — Google Sheets UI (Apps Script). Web UI ⏸ приостановлен (требуется ADR)
- **Модель:** opencode-go/kimi-k2.7-code
- **Назначение:** Apps Script меню (apps_script.gs), лист «Настройки», связь Sheets ↔ webhook
- **Права:** edit: allow, bash (python*, curl*, cat*, ls*; прочее — ask)
- **Контекст:** Google Sheets — основной UI. Web UI не строим (опция под будущий ADR)
- **Anti-goals:** не трогать core-модули (.py кроме webhook.py), не менять Docker

### infra-dev
- **Режим:** subagent (вызывается из build или через `/container`, `/deploy`)
- **Модель:** opencode-go/qwen3.7-plus
- **Назначение:** Docker, docker-compose, deploy, CI/CD, сервер, reverse proxy, SSL
- **Права:** edit: allow, bash (docker*, python*, nginx*, certbot*, systemctl*, cat*, ls*, curl*; прочее — ask)
- **Контекст:** multi-stage Dockerfile (python:3.11-slim, non-root), docker-compose, volume, healthcheck
- **Anti-goals:** не трогать код приложения (.py файлы)

---

## Команды (пайплайны)

| Команда | Агент | Что делает |
|---------|-------|-----------|
| `/commit` | build (deepseek-v4-flash, subtask) | Коммит с conventional-сообщением; тесты — через commit-guard |
| `/interface` | ui-dev | Google Sheets UI: Apps Script меню, лист «Настройки», webhook |
| `/container` | infra-dev | Создать/обновить Dockerfile + docker-compose |
| `/deploy` | infra-dev | Развернуть на сервере: проверка, обновление, proxy, SSL |
| `/dream` | build | Финальный memory-flush сессии в docs/ (decisions/progress/techdebt) |

---

## Состояние методов

| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ✅ | /loop создан (глобальный), зависит от @verifier |
| [[verifier-pattern]] | ✅ | verifier.md создан (GLM-5.2), PASS/FAIL верификация активна |
| [[context-as-docs]] | ✅ | docs/contracts.md, decisions.md, ui-spec.md, techdebt.md, progress.md |
| [[distill-pattern]] | ✅ | `/interface`, `/container`, `/deploy` — команды-пайплайны |
| [[memory-management]] | 🟡 | compaction.js: flush summary в docs/decisions.md + persistent-context в summary; команда /dream |
| [[model-routing]] | ✅ | build на Kimi K2.7 Code, plan на GLM-5.2, ui-dev на Kimi K2.7 Code, infra-dev на Qwen 3.7 Plus, reviewer на GLM-5.2 |
| [[multi-agent-pipeline]] | ✅ | 2 primary + 4 subagent, команды через .opencode/command/ |

---

## Плагины
env-guard.js · notify.js · compaction.js · commit-guard.js

---

## После мультиклиентности (что модернизируем)
- Web UI (если заказчик одобрит через ADR)
- verifier-pattern ✅ — reviewer с PASS/FAIL
- closed-loop — авто-итерация
- memory-management — flush-протокол ✅ (compaction.js + /dream, см. Шаг 4)
- SERP Factory: вторая линия (новый продукт)

---

## Лог изменений
- 2026-06-26: карточка заведена из состояния репо
- 2026-06-29: обновлён стек, статусы методов
- 2026-06-30: ревью — модели, stack, labeler; SERP Factory — SERPlux как продукт
- 2026-07-02: **Core ✅, Docker ✅, Deploy ✅**. Созданы агенты ui-dev + infra-dev. Команды /interface, /container, /deploy. **ADR: интерфейс = только Google Sheets**, Web UI не строим.
- 2026-07-03: Шаг 4 memory-management — плагин `compaction.js` (flush в docs/decisions.md + persistent-context в summary), команда `/dream`, правило flush-протокола в AGENTS.md. Статус метода: ❌ → 🟡.
- 2026-07-03: plan-агент → `.opencode/agents/plan.md` (был inline в opencode.json). Добавлено `task: { build: allow }` — plan делегирует исполнение build через task-tool. edit/bash deny сохранены.
- 2026-07-03: **Актуализация карточки по реальному состоянию репо.** Агенты: ui-dev — активен (Google Sheets UI, kimi-k2.7-code), не PAUSED; infra-dev — qwen3.7-plus (не deepseek-v4-flash). Команды: добавлены `/commit` и `/dream`, убран несуществующий `/review`. Убран мусор (stray `}`). Таблицы агентов/команд приведены в соответствие с `.opencode/`.
- 2026-07-03: **Мультиклиентность + domains mode.** T-001 (новая схема БД clients/positions/labels + migrate.py + тесты), T-002 (режим `domains` разметки + справочник `domain_labels` + `confidence`), T-003 (идемпотентность migrate.py), T-004 (расширение POST /run: client_id, label_mode, force_relabel). 111/111 тестов. Default `label_mode=domains` (без LLM). Плагин commit-guard.js добавлен в список. Приоритет сместился на мультипровайдерность.
