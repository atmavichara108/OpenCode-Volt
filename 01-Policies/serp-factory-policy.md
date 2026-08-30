---
type: Policy
status: approved
date: 2026-08-21
---

# SERP Factory Policy

1. SERPlux — первый коммерческий продукт в сервисном/maintenance режиме. Точечные доработки = отдельные оплачиваемые работы.
2. Каждый новый продукт — отдельный репозиторий с первого дня. SERPlux как baseline, не как общая кодовая база. При старте — манифест: взято/временная копия/своя логика/не переносить.
3. Один сервер — полностью изолированные деплои: свой каталог, .env, БД/volume, compose project, порт/subdomain, backup, логи. НЕ делить SQLite/.env/volume/run lock.
4. Фабрика сейчас = процесс (шаблон, operational-паттерны, docs), НЕ код. serp-core / serp-template / GitHub Template / shared multi-tenant — не создавать до третьего продукта.
5. Понятийная модель: Продукт ≠ Заказчик ≠ Инстанс ≠ Кастомизация. Один продукт многим клиентам = один repo + разные конфиги + разные БД. Уникальный запрос = новый продукт/fork.
6. Пересмотр политики — после третьего продукта: оценить выделение serp-core+template.

Связанный аудит: [2026-08-21-serp-factory-productization-audit.md](../06-Audits/2026-08-21-serp-factory-productization-audit.md)
