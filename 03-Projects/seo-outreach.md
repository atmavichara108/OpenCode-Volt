---
type: project
repo: /home/rudra/Projects/SSA/products/seo-outreach
spec-home: /home/rudra/Projects/SSA/products/seo-outreach/docs/specs/
kind: коммерция
status: bootstrap
stack: Sheets / SQLite (будущее: web / PostgreSQL / queues)
timestamp: 2026-10-10
---

# seo-outreach — SEO-аутрич-конвейер

> **Статус:** 🟡 Bootstrap — репозиторий инициализирован, ветка `task/seo-outreach-bootstrap`, ничего не закоммичено; реализация не одобрена.
> **Связано:** [[SSA]] (контрольный слой портфеля)

**Функция:** первый продукт SSA — полный конвейер SEO-аутрича. Продукт
эксплуатирует клиент самостоятельно; SSA тестирует перед сдачей и сохраняет
возможность последующих модификаций.

## Ключевые свойства (принятые решения)
- **Две фазы:** фаза 1 — обработка под контролем человека (human-supervised
  processing); фаза 2 — автоматизация обработки. Внешние письма/сообщения не
  отправляются без человеческого approval; переговоры, принятие условий и
  финансовые обязательства — за человеком.
- **Лёгкий стек сейчас:** Sheets/SQLite. Тяжёлый web/PostgreSQL/queues — только
  задокументированная будущая опция.
- **Изоляция клиентов:** данные и инстансы клиентов изолированы; нет общего
  tenant-runtime.
- **Владение:** код и переиспользуемые модули — за SSA; клиентские данные и
  настроенная БД — за клиентом.

## Агенты
Один primary-агент **`top`** — назначен в `AGENTS.md`. **Runtime-конфиг
`.opencode/agents/top.md` ещё НЕ создан**: договорённость о роли ≠ runtime
implementation. Список кандидатов в subagent-способности
(discovery/scoring/contacts/outreach/parsing/reviewer) — плоский список, не
активный runtime.

## Canonical specs
`spec-home` = `docs/specs/` в этом репозитории (задано карточкой Vault).
Execution-спека продукта: `docs/specs/seo-outreach-mvp-v0.1.md` (draft, не
одобрена — не даёт разрешение на реализацию).

## Окружение
- `.gitignore` — без секретов и клиентских БД (`*.db`, `*.sqlite`, `data/`, `.env`).

## Лог изменений
- 2026-10-10: карточка заведена (bootstrap)
