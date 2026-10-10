---
type: project
repo: /home/rudra/Projects/SSA/control
spec-home: /home/rudra/Projects/SSA/control/docs/specs/
kind: портфель / control plane
status: bootstrap
stack: markdown / git
timestamp: 2026-10-10
---

# SSA (control) — портфельный/контрольный слой

> **Статус:** 🟡 Bootstrap — репозиторий инициализирован, ветка `task/ssa-bootstrap`, ничего не закоммичено.
> **Связано:** [[seo-outreach]] (первый продукт)

**Функция:** контрольный слой портфеля SSA (временное имя). Здесь **нет кода
продуктов** и **нет клиентских данных**. Ведёт правила агентной инфраструктуры,
журнал решений (ADR), портфельный реестр и execution-спеки слоя.

## Что здесь живёт
- `AGENTS.md` — правила контрольного слоя;
- `docs/portfolio-registry.md` — какие продукты существуют и где их spec-home;
- `docs/decisions/` — журнал решений (ADR);
- `docs/specs/` — spec-home контрольного слоя (execution-спеки слоя).

## Границы
- Не трогает код продуктов и клиентские данные.
- Продукты — отдельные Git-репозитории `~/Projects/SSA/products/<имя>/`.
- Не копирует архивные артефакты `seo_project_pack`.

## Продукты портфеля
| Продукт | Репозиторий | Карточка | Статус |
|---|---|---|---|
| seo-outreach (SEO-аутрич-конвейер) | `~/Projects/SSA/products/seo-outreach/` | [[seo-outreach]] | 🟡 bootstrap |

## Окружение
- `~/Projects/SSA/` — рабочая папка портфеля (НЕ Git-workspace).
- `control/` — этот репозиторий (control plane).

## Лог изменений
- 2026-10-10: карточка заведена (bootstrap)
