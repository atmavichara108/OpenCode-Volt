---
type: Runbook Index
title: Runbooks — operational use layer
description: Живые сценарии и operator workflows для практического использования VibeOS.
tags: [runbooks, operations]
---
# Runbooks — operational use layer

`07-Runbooks/` — operational use layer волта: живые сценарии, usage patterns,
operator workflows и правила обновления практики.

Слой не дублирует `02-Methods/`, [[06-Audits/README]] или `AGENTS.md`:

- **Methods** — абстрактные reusable techniques.
- **Audits** — датированные findings и снимки состояния.
- **AGENTS.md** — правила поведения агента.
- **Runbooks** — как оператор реально пользуется системой сейчас.

[[07-Runbooks/vibecoding-operator-handbook]] — текущее рабочее состояние.
[[07-Runbooks/coordination-bridge-operator-guide]] — historical reference,
Coordination Bridge FROZEN BY USER (2026-08-30); он не является обязательным
workflow.
Для AndroidOS использовать local-first `/android-plan` или свободный запрос; для
отдельного host audit в dotfiles — `/sysaudit`. Vault `/ask` даёт контекст без
обязательного копипаста отчётов.
[[07-Runbooks/vibecoding-changelog]] — краткая история изменения практики.

Обновлять слой можно только по подтверждённым изменениям практики. Предложения,
кандидаты и неподтверждённые наблюдения остаются в соответствующих audit,
memory или planning-артефактах.
