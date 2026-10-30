---
type: project
repo: /home/rudra/Projects/SSA/control
spec-home: /home/rudra/Projects/SSA/control/docs/specs/
kind: портфель / control plane
status: active
stack: markdown / git
timestamp: 2026-10-29
---

# SSA (control) — портфельный/контрольный слой

> **Статус:** 🟢 Active — репозиторий живой, ветка `task/control-w2`, последний коммит 2026-10-29.
> **Связано:** [[seo-outreach]] (первый продукт), [[SERPlux]] (поглощение SERP Factory)

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
| seo-outreach (SEO-аутрич-конвейер) | `~/Projects/SSA/products/seo-outreach/` | [[seo-outreach]] | 🟢 active |
| SERPlux (SERP Factory) | `~/Projects/serp/` | [[SERPlux]] | 🟡 в процессе поглощения SSA |

## Окружение
- `~/Projects/SSA/` — рабочая папка портфеля (НЕ Git-workspace).
- `control/` — этот репозиторий (control plane).

## Лог изменений
- 2026-10-10: карточка заведена (bootstrap)
- 2026-10-29: сверка карточки↔репо (Служитель): статус поднят до active, ветка `task/control-w2` живая; портфель дополнен SERPlux в статусе поглощения SERP Factory; seo-outreach переведен в active.
