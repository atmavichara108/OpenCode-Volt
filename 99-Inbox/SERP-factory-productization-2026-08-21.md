---
type: Decision Note
title: SERP Factory productization — вопросы для decision gate
date: 2026-08-21
tags: [inbox, serp, productization]
---
# SERP Factory productization — decision note

Центральная идея: SERPlux уже мультиклиентный продукт-прототип, но ещё не
фабрика продуктов. Ближайший шаг — не код, а decision gate по boundaries и
модели поставки. Рекомендуемый промежуточный вариант: modular monolith, один
image, отдельный deployment instance/customer DB, immutable tags.

## Вопросы

- **Hosted vs installed:** продаём shared hosted service, dedicated hosted
  instance или устанавливаем продукт у клиента?
- **Source delivery:** доставляем исходники, image/artifact или только managed
  service?
- **Isolation:** logical tenancy в общей инсталляции или physical instance + DB
  на клиента?
- **Product differences:** что является core, а что product/customer-specific
  configuration, labels, reports и integrations?
- **Expected scale:** сколько клиентов, запусков и параллельных jobs ожидается
  в 12 месяцев?

См. аудит: [[06-Audits/2026-08-21-serp-factory-productization-audit]].
