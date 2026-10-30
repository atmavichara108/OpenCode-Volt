---
type: project
repo: /home/rudra/Projects/SSA/products/seo-outreach
spec-home: /home/rudra/Projects/SSA/products/seo-outreach/docs/specs/
kind: коммерция
status: active
stack: "Python / Docker / Sheets / SQLite (будущее: web / PostgreSQL / queues)"
timestamp: 2026-10-29
---

# seo-outreach — SEO-аутрич-конвейер

> **Статус:** 🟢 Активный продукт SSA — 247 коммитов, ветка `main`, последний коммит 2026-10-30 01:15; релизная линия 0.3.x (0.3.8 — отправка есть, каждое письмо с «да», колонки v0.2).
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

Runtime `.opencode/agent/` — 4 агента (сверка 2026-10-29):
- `top-man.md` — primary
- `engineer.md`
- `tg-bridge.md`
- `office-tg.md` — untracked, новый

Скиллы `.opencode/skill/` — 10:
campaign, contacts, discovery, export, handoff, inbox, monitor, pre-send-gate, scoring, tg-bridge (последний — untracked).

Команды `.opencode/command/` — 4:
campaign, dryrun, status, stop.

## Canonical specs
`spec-home` = `docs/specs/` в этом репозитории (задано карточкой Vault).
Execution-спека продукта: `docs/specs/seo-outreach-mvp-v0.1.md` — **status: approved** (2026-10-10).
Proposal единого первого релиза: `docs/specs/proposals/seo-outreach-first-release-v0.2-proposal.md` (2026-10-13, status: proposed).

Релизная линия: 0.3.8 — сценарий отправки под 0.3.8, выбор [email]-строки по номеру, ручной адрес обходом для [форма], теги строк, ящик, «да» на каждое письмо; install.command шаги 1–6.

## Окружение
- `.gitignore` — без секретов и клиентских БД (`*.db`, `*.sqlite`, `data/`, `.env`).
- Стек по факту: Python (pyproject.toml), Dockerfile, docker-bake.hcl, packaging/dist, tests (619 тестов в истории).
- Remote-ов нет.

## Лог изменений
- 2026-10-10: карточка заведена (bootstrap)
- 2026-10-29: сверка карточки↔репо (Служитель, по поручению владельца): 247 коммитов, main, релиз 0.3.8; агенты 4 (top-man primary), скиллы 10, команды 4; spec MVP approved; Python/Docker; remote-ов нет.
