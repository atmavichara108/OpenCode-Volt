---
type: Audit
title: SERP Factory — productization audit
date: 2026-08-21
status: read-only
scope: Проверка архитектурной готовности SERPlux к SERP Factory productization.
  Репозиторий приложения не изменялся.
sources:
  - /home/rudra/Projects/serp/main.py
  - /home/rudra/Projects/serp/webhook.py
  - /home/rudra/Projects/serp/collector.py
  - /home/rudra/Projects/serp/topvisor.py
  - /home/rudra/Projects/serp/storage.py
  - /home/rudra/Projects/serp/labeler.py
  - /home/rudra/Projects/serp/exporter.py
  - /home/rudra/Projects/serp/reporter.py
  - /home/rudra/Projects/serp/config.py
  - /home/rudra/Projects/serp/migrate.py
  - /home/rudra/Projects/serp/deploy.sh
  - /home/rudra/Projects/serp/docs/deploy.md
  - /home/rudra/Projects/serp/docs/verification.md
  - /home/rudra/Projects/serp/AGENTS.md
  - /home/rudra/Projects/serp/TASKS.md
  - /home/rudra/Projects/OpenCode-Vault/03-Projects/SERPlux.md
  - /home/rudra/Projects/OpenCode-Vault/06-Audits/2026-08-03-serplux-phase-c-audit.md
source_date: 2026-08-21
tags: [audit, serp, serp-factory, productization, read-only]
---
# SERP Factory — productization audit (2026-08-21)

> Датированный read-only снимок. Источник наблюдений: чтение файлов
> `/home/rudra/Projects/serp` и существующего аудита в волте 2026-08-21.
> Репозиторий SERP и application code в рамках этой фиксации не изменялись.
> Факты отделены от рекомендаций; рекомендации не являются текущими свойствами
> системы.

## Verdict

Текущее состояние: **мультиклиентный продукт-прототип, не фабрика продуктов**.
Схема `clients / positions / labels` и параметр `client_id` дают основу для
нескольких клиентов, но границы tenancy, продукта и deployment пока не являются
самостоятельными архитектурными контрактами.

## Confirmed facts

### Runtime pipeline

- Входной контур: Google Sheets + Apps Script (`apps_script.gs`) вызывает FastAPI
  (`webhook.py`), который запускает orchestration через `main.py`.
- Основной pipeline проходит через `collector.py` и `topvisor.py` (Topvisor
  snapshots), затем через `storage.py`, `labeler.py`, `exporter.py` и
  `reporter.py`. Это flat layout в корне репозитория, без отдельного `src/`.
- Google Sheets одновременно является configuration/UI surface и каналом
  выгрузки (`config.py`, `exporter.py`, `apps_script.gs`); это не выделенный
  product/deployment boundary.

### Tenancy and data model

- В схеме присутствуют `clients`, `positions` и `labels`; `client_id` передаётся
  в запуск (`webhook.py`) и используется в связанных операциях хранения.
- `domain_labels` является справочником доменных меток без `client_id`.
  Следовательно, доменные метки в текущей схеме глобальны, а не принадлежат
  клиенту (`migrate.py`, `storage.py`, `labeler.py`).
- `migrate.py` содержит customer-specific миграционные предположения/логику,
  что связывает эволюцию схемы с конкретным текущим продуктом, а не с
  нейтральным core-контрактом.

### Execution and isolation

- `run_status` реализован как singleton/global status, а run lock является
  глобальным для instance, не scoped по клиенту.
- Фоновые jobs запускаются daemon threads (`webhook.py`/`main.py`); отдельного
  durable job queue или worker boundary нет.
- Topvisor credentials читаются как глобальные configuration credentials, а не
  как credentials, scoped к клиенту/продукту (`config.py`, `topvisor.py`).
- Используется SQLite single-instance database (`storage.py`, `serplux.db`), то
  есть фактическая изоляция сейчас достигается границей инстанса/БД, а не
  полноценной shared multi-tenant моделью.

### Configuration and deployment

- Configuration concerns scattered по `config.py`, `.env`/`.env.example`,
  Apps Script, Docker Compose и deploy-документации; единого product/deployment
  configuration contract не обнаружено.
- Deployment описан как обновление через `git pull origin main`/`latest` в
  `deploy.sh` и `docs/deploy.md`, а не как immutable release artifact.
- В репозитории остаются тестовые и документальные расхождения: разные claims о
  размере test suite (`AGENTS.md`, `docs/verification.md`, корневой `TASKS.md`,
  карточка SERPlux и фактические test definitions), а также дрейф между
  operational/deployment документацией и фактической структурой проекта. Детали
  предыдущей сверки: [[06-Audits/2026-08-03-serplux-phase-c-audit]].

## Recommendations

Это проектные рекомендации по результатам аудита, не подтверждённые свойства
репозитория.

### Intermediate target

- **Modular monolith + one image + separate deployment instance/customer DB +
  immutable tags.** Сохранить один репозиторий и один deployable image, но
  явно разделить core, product configuration/overrides и deployment contract.
- Не начинать с преждевременного split репозитория: сначала зафиксировать
  boundaries и доказать их на отдельном deployment instance.

### Twelve-month target

- Выделить границы `core` (pipeline/domain contracts), `product` (customer or
  product-specific behavior) и `deployment` (instance, secrets, DB, release).
- После стабилизации этих контрактов оценить переход к `core + product` repos
  и/или shared hosted model. Repo split не является исходной целью на первом
  шаге.

### Blockers

- **P0:** отсутствие подтверждённой модели поставки и isolation contract;
  глобальные run status/lock, daemon jobs и global credentials не дают безопасно
  масштабировать shared instance без отдельного решения.
- **P0:** mutable deployment (`git pull origin main/latest`) не даёт
  воспроизводимый immutable release boundary.
- **P1:** scattered config и customer-specific `migrate.py` затрудняют отделение
  product от core.
- **P1:** глобальный `domain_labels` без `client_id` требует решения о scope
  labels и совместимости продуктов.
- **P1:** тестовые/documentation claims должны быть нормализованы до единого
  source of truth перед архитектурными migration gates.

## Transition criteria

Переход к `core + product` repos допустим, когда core contracts, product
extension points и deployment inputs проверены на нескольких продуктах, миграции
не содержат customer-specific assumptions, а release собирается из immutable
tag/artifact.

Переход к shared hosted допустим только после явного решения о logical isolation:
tenant-scoped status/locks/jobs/credentials/data, durable job execution,
observability и recovery. До этого рекомендуемая модель поставки — отдельный
deployment instance и customer DB на продукт/клиента.

## Audit boundary

- Проверка выполнена 2026-08-21, read-only.
- Этот документ фиксирует состояние на дату источника; он не утверждает, что
  рекомендации реализованы.
- Код приложения, репозиторий `/home/rudra/Projects/serp` и deployment не
  изменялись и не коммитились.

### Git snapshot

- На дату аудита репозиторий SERP находился на ветке
  `fix/labeling-cache-and-quality`.
- `HEAD`: `bdc9a54b7989cf1c2139357a34dd6c0e33ed30d1`; `HEAD` совпадал с
  `origin/main`.
- Working tree имел pre-existing изменения в `.opencode/agents/*`,
  `opencode.json` и untracked-файл
  `docs/review_2026-08-02_labeling-cache-and-quality.md`.
- Facts в vault и карточке проекта с прежними HEAD или test metrics могут быть
  stale и требуют отдельной reconciliation.
