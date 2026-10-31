---
type: Registry
title: Реестр манифестов ведомств
ssot: true
timestamp: 2026-10-23
owner: УАС (куратор по Р-014), операционная запись — ЦУ
---
# Реестр манифестов ведомств

Единственный реестр манифестов. Каждый манифест — один файл `docs/org/<id>.md`
(YAML-frontmatter по схеме ministry-manifest: 11 обязательных + 4 опциональных поля).
Схема — `06-Audits/2026-10-14-institute-extract-ministry-manifest.md`.
Решение слоя — Р-005 (`docs/org/` в волте); куратор — УАС (Р-014).

| id | Ведомство | Статус | Манифест |
|---|---|---|---|
| `uas` | Университет Агентских Систем (сетей) | active, 2026-10-23 | [[uas]] |
| `uas-special-rotator` | Спец-отдел «Ротатор моделей» (УАС) | active, 2026-10-23 | [[uas-special-rotator]] |
| `apps-department` | Отдел «Приложений» (подотдел ИЦ; graduating — Ability Lab; первый клиент — mail-hub) | active, 2026-10-31 (вердикт УАС: сессия ses_eKDfprGN0tGPmzJnQChkmOT есть, агент Apps-dev подключён) | `docs/org/apps-department.md` |
| `csipm-center` | Центр стратегического планирования и менеджмента (ЦСПиМ; агент SCRUM-master, сессия ses_e0JGLx9sw7hTttx3t1BXQh5) | active, 2026-10-31 (Р-043 + вердикт УАС: сессия и агент-файл подключены) | `docs/org/csipm-center.md` |
| `sb-service` | Служба Безопасности (агент SB) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/sb-service.md` |
| `reverse-craft-department` | Отдел «Реверс-инженерии движков» (Reverse-craft) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/reverse-craft-department.md` |
| `counterparties-chair` | Кафедра контрагентов при УАС (Rector) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/counterparties-chair.md` |
| `git-freed` | Git Freed (Гит Освобождённый) | proposed, 2026-10-25 (манифест+агент есть; сессии-носителя нет — активен после создания сессии владельцем; функция пока несётся командой /ship + гейтами) | `docs/org/git-freed.md` |
| `dv-hub-custodian` | Агент «Смотритель ДВ» (ДВ-Хаб) | active, 2026-10-31 (вердикт УАС: файл dv-custodian.md создан в dv-hub, коммит 49a26ad) | `docs/org/dv-hub-custodian.md` |
| `sero` | Агент «SerO» — Служитель Обсидиан (глобальный) | active, 2026-10-26 (файл 99c9b00, реконсиляция УАС; расхождение чертежа рапортовано ЦУ) | `docs/org/sero.md` |
| `obsidian-plugin-dev` | Агент «obsidian-plugin-dev» — разработчик плагинов Обсидиан (субагент Служителя) | active, 2026-10-27 (вердикт УАС: файл в main, зоны машинные 6adbd34 — оговорка снята после подтяжки ИЦ) | `docs/org/obsidian-plugin-dev.md` |
| `ship-representative-maya` | Представитель Корабля «AllIsMaya» (@AllIsMaya) — единый sender; Голос Корабля: все исходящие в TG, мультиагент (профили ssa/dv/serp/portal), Капитанский портал в ведении | active, 2026-10-29 (слово «активен», реестр Р-Д-002; переобувка 4/4 профилей = AllIsMaya, tg-whoami; recruiting на паузе Р-Д-007) | `docs/org/ship-representative-maya.md` |
| `hpf-school` | Школа концептуальных изысканий (ХПФ, исследовательское крыло) | active, 2026-10-30 (вердикт УАС: 11+4 полей, mandate-source = слово владельца дословно + Р-034; спека approved 10-30, сессия ses_eQRHoixARq3RNJnKLFTS4IW, peer-registry строка на месте) | `docs/org/hpf-school.md` |
| `office-serplux-primary` | Primary офиса SERPLUX (перенос top-man из аутрича) | active, 2026-10-31 (вердикт УАС: Serp-office + Senior-dev созданы в serp, b0de867; красные линии verbatim) | `docs/org/office-serplux-primary.md` |

## Правила
1. Манифест обязателен с момента approval спеки ведомства (Р-014).
2. Первые записи реестра — УАС (spec approved 2026-10-17) и спец-отдел «Ротатор»
   (учреждён 2026-10-23) — по пробелу, подсвеченному ИПТ 2026-10-23 (ref: uas-spec-actual-20261023).
3. Операционная запись реестра — через ЦУ; курирование схемы и реестра — УАС.
4. Расхождение манифеста с карточкой проекта (`03-Projects/`) = инцидент слоя.
