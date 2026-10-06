---
type: Research
title: CRM для recruiting-hr — исследование open-source решений (выбор EspoCRM)
description: Полный разбор open-source CRM под рекрутинг рабочих на стройку (кейс КПО Новосёлки + будущие объекты). Сравнение 12 решений, выбор EspoCRM (#1) и Baserow (#2), антирекомендации, черновик внедрения, открытые вопросы 152-ФЗ.
tags: [research, crm, espocrm, recruiting-hr]
timestamp: 2026-10-01
status: done
---

# CRM для recruiting-hr — исследование open-source решений

> **Итог:** выбрана **EspoCRM** (self-hosted на **RF-VPS**), запасной вариант —
> **Baserow**. Решение зафиксировано как ADR-001 в `recruiting-hr/docs/decisions.md`.
> Этот документ — доказательная база исследования, на которую ADR ссылается.

## Методология и источники

- **Дата проверки:** 2026-10-01.
- **Источники:** GitHub REST API:
  - `GET /repos/{owner}/{repo}` → поля `license.spdx_id`, `pushed_at`, `stargazers_count`;
  - `GET /repos/{owner}/{repo}/releases/latest` → `tag_name`, `published_at` (последний релиз);
  - `GET /repos/{owner}/{repo}/license` → текст лицензии.
- **Критерии сравнения:** лицензия / free-для-коммерции, русская локализация,
  self-host / docker / требования RAM, модель воронки + мультиобъектность, приём
  из форм, Telegram-уведомления, пригодность для не-технической команды, живость
  проекта (последний релиз), соответствие 152-ФЗ, риски.
- **Пометки:** `src/…` — факт с источником из выжимки исследования; `[не подтверждено]` —
  факт не подтверждён источником на момент фиксации (честный пропуск, не выдумка).

## Сравнительная таблица кандидатов

> Исследованы 12 решений (данные GitHub API + страницы релизов, проверка 2026-10-01). `src:` — факт с источником; `[не подтв.]` — не подтверждено источником.

| Решение | Лицензия / free-коммерция | Рус. локализация | Self-host / docker / RAM | Воронка + мультиобъект | Приём из форм | Telegram | Не-тех команда | Живость (релиз) | 152-ФЗ | Риски |
|---|---|---|---|---|---|---|---|---|---|---|
| **OpenCATS** | MPL 2.0 (+CATS PL 1.1a) — свободно (src: LICENSE.md) | Частичная; UI англ., есть фиксы не-ASCII [не подтв. полный ru] | PHP+MySQL, docker, ~0.5–1 ГБ [RAM не подтв.] | Нативный ATS: кандидаты→job orders→pipeline; неск. job orders = объекты | CSV-импорт нативно; Career Portal; API ограничен | Нет; через внешн. хук/n8n | Средне (ATS готов, UI 2010-х) | Активен: v0.11.1, 2026-09-03, PHP 8.4/8.5 (src: releases) | Self-host RF-VPS ОК | UI устарел; ru неполный; кастом. поля ограничены |
| **CandidATS** (ОТКЛОНЁН) | форк → MPL/CATS | — | — | — | — | — | — | Похоже заброшен: репо 404, домен candidats.net = спам-казино (src: webfetch) | — | Не брать: мёртв |
| **EspoCRM** (#1, выбор) | AGPL-3.0 — свободно, без seat-лимитов (src: /license) | Нативная ru (ru_RU в комплекте) [косвенно подтв.] | PHP+MySQL/MariaDB, docker офиц., ~1–2 ГБ [оценка] | Multiple pipelines + Kanban (с 10.0.0); кастом. сущности/поля | REST API + webhooks + CSV нативно | Нет нативно; webhook/workflow → Bot API | Высоко (Kanban drag-n-drop) | Очень активен: 10.0.9, 2026-09-29 (src: releases) | Self-host RF-VPS; Personal data erasure (10.0.9) (src: changelog) | AGPL (сетевой копилефт) — для внутр. использования неважно |
| **NocoDB** (ОТКЛОНЁН) | ⚠️ Sustainable Use License (с 29.01.2026, source-available): internal business ok, продавать/SaaS нельзя (src: LICENSE.md) | Частичная i18n [не подтв. ru] | Node, docker, ~1–2 ГБ [оценка] | Таблицы/связи, Kanban, views; воронка = поле-статус | Формы, webhooks, API, CSV нативно | Через webhook/workflow | Высоко | Очень активен: 2026.09.1, 2026-09-29 (src: releases) | Self-host RF-VPS ОК | Лицензия больше не OSS; платное гейтирование фич (RLS/UUID/Color) (src: changelog) |
| **Baserow** (#2) | MIT (OSE-ядро) + premium/enterprise каталоги (src: LICENSE) | Частичная i18n [не подтв. ru] | Django+Postgres+Redis, docker, тяжелее ~2 ГБ+ [оценка] | Таблицы, Kanban, формы; воронка = статус | Формы, webhooks, API, CSV нативно | Через webhook/n8n | Высоко | Активен: 2.4.0, 2026-09-30 (src: /releases) | Self-host RF-VPS ОК | Часть фич premium/enterprise; ресурсы выше |
| **Grist** | Apache-2.0 — свободно (src: /license) | [не подтв. ru] | Node, docker, умеренный RAM | Таблицы+формулы; воронка = статус | Формы, API, CSV; webhooks [частично] | Через API/webhook | Средне-высоко (умная таблица) | Активен: v1.7.20, 2026-09-28 (src: /releases) | Self-host RF-VPS ОК | Меньше «CRM-готовности» из коробки |
| **Teable** | AGPL-3.0 (src: LICENSE) | [не подтв. ru] | Postgres, docker, ~1–2 ГБ [оценка] | Airtable-like, Kanban | Формы, API, webhooks | Через webhook | Высоко | Активен (rolling): 2026-09-30 (src: /releases) | Self-host RF-VPS ОК | Молодой; ru под вопросом; коммерч. cloud-грань |
| **Twenty** | AGPLv3 (+ enterprise-файлы, MIT-SDK) (src: LICENSE) | [не подтв. ru] | Node+Postgres+Redis+worker, тяжёлый | CRM pipeline/Kanban | API; формы/импорт [частично] | Через API | Средне (dev-ориентир) | Очень активен: v2.44.0, 2026-10-01 (src: /releases) | Self-host RF-VPS ОК | Ресурсоёмкий; ru слабый [не подтв.]; быстро меняется |
| **SuiteCRM** | AGPL-3.0 (src: /license) | ru есть [не подтв. полнота] | PHP+MySQL, тяжелее OpenCATS | Полный CRM; кастом. модули | API, импорт | Через хук | Низко-средне (переусложнён) | Активен: 7.15.2, 2026-07-31 (src: /releases) | Self-host ОК | Переусложнение для крошечной команды |
| **Odoo (Recruitment)** | Community LGPLv3 [не подтв. fetch] | ru есть | Python, docker, тяжёлый | модуль Recruitment = воронка стадий | API/формы | Через хук/модуль | Средне | [версия не проверена fetch] | Self-host ОК | Монолит-ERP, overkill; многое в Enterprise |
| **Dolibarr** | GPL-3.0 (src: /license) | ru есть | PHP+MySQL | ERP/CRM, модуль Recruitment | API, импорт | Через хук | Средне | Активен: 24.0.1, 2026-09-07 (src: /releases) | Self-host ОК | ERP-уклон, не под масс-рекрутинг |
| **Krayin** | MIT (src: /license) | [не подтв. ru] | Laravel/PHP+MySQL | Sales-CRM (leads), kanban | API, формы | Через хук | Средне | Активен: v2.2.6, 2026-09-10 (src: /releases) | Self-host ОК | Заточен под продажи, не под ATS-воронку |

## ТОП-2 рекомендации

### EspoCRM — #1 (выбор)

1. **Лицензия AGPL-3.0** — свободно для коммерческого использования, без seat-лимитов (src).
2. **Нативная русская локализация** — нет костылей с переводом (src).
3. **Готовая мультиобъектная воронка** — несколько pipeline + Kanban (с v10), закрывает
   «сейчас 1 объект → после 10 пристроенных — 2-й» (src).
4. **Приём заявок** через REST API / webhook / CSV (src).
5. **Telegram** через встроенный Workflow → Bot API (уведомления без внешних скриптов) (src).
6. **Personal data erasure** (10.0.9) — инструмент под требования 152-ФЗ (src).
7. **Лёгкий стек** PHP + MariaDB + docker; активнейший проект (10.0.9 от 29.09.2026) (src).

### Baserow — #2 (запасной)

- **MIT**, «умная таблица с формами/Kanban» — подходит как low-code fallback (src).
- Минусы: **тяжелее по RAM**, **часть фич premium** (src). Использовать, если EspoCRM
  по какой-то причине не встанет.

## Антирекомендации

- **NocoDB — ОТКЛОНЁН:** с 29.01.2026 ушёл под несвободную Sustainable Use License —
  не подходит под требование «free для коммерции» (src).
- **CandidATS — ОТКЛОНЁН:** проект мёртв, репозиторий 404 (src).
- **SuiteCRM / Odoo / Dolibarr / Twenty — переусложнение / ресурсоёмкость** для
  крошечной команды (src). У Odoo лицензия/версия не подтверждены (`[не подтверждено]`).
- **Krayin — не тот домен** (не под задачи рекрутинга) (src).
- **OpenCATS — второй эшелон:** чистый ATS, но устаревший UI, неполный русский,
  слабый API (src).

## Черновик внедрения для EspoCRM

### Деплой-эскиз (инфраструктура)

- **Хост:** RF-VPS (рос. хостер) — белый IP + HTTPS из коробки, данные в РФ.
- **Стек:** docker-compose `espocrm + mariadb`.
- **Сеть:** reverse-proxy + TLS (Let's Encrypt).
- **Харден:** firewall, fail2ban, доступ по SSH-ключу.
- **Бэкапы:** БД.
- **ThinkPad** — только для тестовой обкатки перед боевым деплоем (не боевой хост:
  серый IP за NAT, ПД из домашней сети — риск).

### Модель данных

- Сущности **Candidate** (кандидат) и **Account** (объект/работодатель).
- Воронка стадий: **отклик → контакт → квалификация → передан работодателю → пристроен**.
- Мультиобъектность: несколько pipeline (сейчас 1 объект, после 10 пристроенных — 2-й).

### Импорт из Яндекс-формы

- **Вариант A (основной, согласован в ADR):** handler приёма заявки → **REST API EspoCRM**
  (handler — python-парсеры проекта / Apps Script, связь с существующими скриптами).
- **Вариант B (fallback):** CSV-импорт / webhook-приём.
- Нативный webhook Яндекс-форм → EspoCRM — `[не подтверждено]`.

### Telegram Workflow

- Встроенный Workflow → Bot API: уведомление оператору о новой заявке и смене стадий.

### 152-ФЗ — открытые вопросы

- Ретеншн-политика (сроки хранения ПД).
- Необходимость уведомления РКН как оператора ПД.
- Согласие на обработку ПД собирается формой; хранить факт согласия (дата/версия).
- Юридическая достаточность мер не подтверждена — нужен юрист (это НЕ правовой совет).

## [не подтверждено]

Честно открытые позиции (источников не хватило — не выдумывать):

1. **Полнота русской локализации** EspoCRM/NocoDB/Baserow/Grist/Teable/Twenty — прямых скринов перевода не снимали.
2. **Точные требования RAM** всех решений — цифры оценочные, официальные sizing-данные не фетчились.
3. **Нативный webhook Яндекс-форм** → CRM в 2026 — не проверено на first-party доке; согласован путь handler → REST API.
4. **Odoo** — точная версия и лицензия Community/Recruitment не фетчились (GitHub/odoo.com).
5. **CandidATS** — живой канонический репозиторий не найден; вывод «заброшен» на основе 404 + спам-домена.
6. **Юридическая достаточность 152-ФЗ-мер** — не правовая оценка, нужен юрист.

## Связь с ADR

- **ADR-001** — `recruiting-hr/docs/decisions.md` (решение: EspoCRM на RF-VPS).
- Карточка проекта — [[03-Projects/recruiting-hr]].

## Addendum 2026-10-03 — Stage 0: верификация деплоя (researcher) + выбор VPS

> Проверка 2026-10-03. Источники — официальные docs.espocrm.com / espocrm.com /
> GitHub releases / Docker Hub. `src:` — факт с источником; `[не подтверждено]` —
> честный пропуск.

### Верифицировано

- **EspoCRM 10.0.9** — latest, релиз 29.09.2026 (src).
- **Официальный образ `espocrm/espocrm`** + compose из 4 сервисов: `espocrm`,
  `espocrm-db` (mariadb), **ОБЯЗАТЕЛЬНЫЙ `espocrm-daemon`**, опциональный
  `espocrm-websocket` (src: Docker Hub / docs).
- **PHP 8.3–8.5** (src: docs/README).
- **MariaDB 10.6+** — пол выяснить: docs/README говорят 10.6+, страница download —
  10.3+; **брать 10.6+** (src: docs/README vs download).
- **`ESPOCRM_SITE_URL` обязателен** (https при TLS); docker-secrets через `_FILE`
  (src: docs).
- **REST API** с `X-Api-Key` + **Lead Capture** endpoint `POST /api/v1/LeadCapture/{apiKey}`
  без авторизации (src).
- **Multi-pipeline** — с v10.0 (src).
- **Нативный CSV-импорт** (src).
- **Исходящие native Webhooks** — ядро, бесплатно (src).

### КЛЮЧЕВАЯ ПОПРАВКА К ADR-001

- **Workflow / Send HTTP Request / сценарий Telegram** из
  `workflows-telegram-message.md` — часть **платного Advanced Pack, НЕ ядра**.
  «Встроенный Workflow→Bot API» без лицензии невозможен.
- **Решение оператора (ADR-002):** свой relay-handler
  (Espo webhook/API → python-handler → Bot API `sendMessage`), бесплатно.

### Входящие webhook-и и Яндекс-формы

- **Входящего generic-webhook в EspoCRM нет** (только исходящие); приём с
  Яндекс-форм = relay-handler → REST API или Lead Capture.
- Способность самой Яндекс-формы слать на произвольный URL — **[не подтверждено]**,
  вопрос стороны Яндекса.

### TLS

- 3 официальных пути: compose+Traefik (TLS-ALPN-01), compose+Caddy (авто-TLS),
  installer nginx+certbot (src). Выбор пути отложен до инфра-спеки T-157.

### Ресурсы

- Официальных минимумов RAM/CPU/диск у EspoCRM нет (только «prefer VPS/dedicated»).
- Инженерная оценка для 1–2 пользователей: **2 ГБ RAM достаточно** (сторонние:
  Railway min 512MB/1vCPU, selfhosting.sh idle ~630MB стек).

### Вывод researcher

- Данных для execution-spec деплоя достаточно; открытые выборы зафиксированы
  в ADR-002.
