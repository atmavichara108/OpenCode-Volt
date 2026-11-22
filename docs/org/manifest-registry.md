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
Схема — `06-Audits/2026-10-14-institute-extract-ministry-manifest.md` (сам документ
помечен «проект для спеки, не внедрение» — каноном здесь считается фактическое
применение схемы в файлах). Решение слоя — Р-005 (`docs/org/` в волте); куратор —
УАС (Р-014).

Факт на диске 22.11: манифестов — 20, строк реестра — 20 (расхождений нет). По
полной схеме (11 обязательных + 4 опциональных поля, сверх `type`) — 17 файлов;
упрощённый frontmatter нового стиля (8–10 полей) — 3 (`master-freela`,
`serp-forge`, `spells-chair`). `dv-hub-department` имел 4 поля — приведён к схеме
21.11 (вердикт УАС), 22.11 дополнен последним опциональным полем `memory-zones`.
Frontmatter у 5 файлов не парсился как YAML (значения без кавычек) — исправлено
21.11; сейчас парсятся все 26 файлов `docs/org/`. В `docs/org/` лежат и документы
других типов (`Audit`, `Registry`, `CanonNote`) — это не манифесты, строки реестра
им не полагаются.

**Сессия-носитель: четыре состояния — отсутствие сессии ≠ дефект.** Сверка 22.11 по
всем 20 манифестам (поле `carrier-sessions` + тело манифеста + `04-Memory/peer-registry.md`):
- **носитель назван в манифесте, строка в peer-registry есть** — 15: 12 с сессией в
  поле `carrier-sessions` (`uas`, `uas-special-rotator`, `apps-department`,
  `business-school`, `csipm-center`, `dv-hub-custodian`, `dv-hub-department`,
  `hpf-school`, `office-serplux-primary`, `vendors-chair`, `counterparties-chair`,
  `sb-service`) + 3 в теле при упрощённом frontmatter (`serp-forge` —
  `ses_e1116cabdffeW9SrcjuL36bhjM`, `spells-chair` — `ses_spe11s2026no7Chair01`,
  `master-freela` — `ses_e4bbf9330ffeAQ6hTrv1HmF0yb`);
- **носитель назван, но строка в peer-registry помечена «мёртв»** — 1:
  `reverse-craft-department` (`ses_ewdWZMlHOJE3UloUrwdXHi`; preflight 404 на 20.11,
  пометка по мандату ic-u2-cop-dead-rows-20261108) — действующего носителя нет;
- **сессии-носителя нет по замыслу** — 3: `obsidian-plugin-dev` (субагент без своей
  сессии), `sero` (глобальный агент), `ship-representative-maya` (идентичность
  отправителя, а не сессия) — носителями в peer-registry не числятся, расхождения нет;
- **носителя нет ни в манифесте, ни в peer-registry** — 1: `git-freed` (в поле —
  адрес ЦУ, который создаст носителя; статус `proposed`).

22.11 по факту peer-registry приведены в соответствие 4 манифеста:
`counterparties-chair` и `sb-service` (вместо «создаёт ЦУ» — фактическая сессия),
`reverse-craft-department` (строка помечена «мёртв»), `master-freela` (носитель назван
в теле). Ячейка «Кафедра контрагентов» в peer-registry продублирована — две строки с
одной сессией; зона ЦУ, доложено письмом.

| id | Ведомство | Статус | Манифест |
|---|---|---|---|
| `uas` | Университет Агентских Систем (сетей) | active, 2026-10-23 | [[uas]] |
| `uas-special-rotator` | Спец-отдел «Ротатор моделей» (УАС) | active, 2026-10-23 (обновлён 2026-11-21: **шлюз по умолчанию для всего флота** — слово владельца 20.11, Р-Д-031/Р-Д-032; носитель — линия РМПП ses_e5455a2f2ffe6b9EqBT1aziN2A, примари Keymaster; каталог провайдеров SSOT — tools/key-rotator/providers.json; живой каталог — control-plane/live-model-catalog.json, второй источник гейта pin-check; протокол выпила по сроку бесплатного периода — слово владельца 18.11) | [[uas-special-rotator]] |
| `apps-department` | Отдел «Приложений» (подотдел ИЦ; graduating — Ability Lab; первый клиент — mail-hub) | active, 2026-10-31 (вердикт УАС: сессия ses_eKDfprGN0tGPmzJnQChkmOT есть, агент Apps-dev подключён) | `docs/org/apps-department.md` |
| `csipm-center` | Центр стратегического планирования и менеджмента (ЦСПиМ; агент SCRUM-master, сессия ses_e0JGLx9sw7hTttx3t1BXQh5) | active, 2026-10-31 (Р-043 + вердикт УАС: сессия и агент-файл подключены) | `docs/org/csipm-center.md` |
| `sb-service` | Служба Безопасности (агент SB) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/sb-service.md` |
| `reverse-craft-department` | Отдел «Реверс-инженерии движков» (Reverse-craft) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/reverse-craft-department.md` |
| `counterparties-chair` | Кафедра контрагентов при УАС (Rector) | active, 2026-10-31 (ночная программа владельца; манифест+агент в глобальном слое) | `docs/org/counterparties-chair.md` |
| `vendors-chair` | Кафедра изучения вендоров (примари AllIsMaya) | active, 2026-11-01 (Р-064; манифест+activation; примари AllIsMaya — слово владельца 11-01, отдельный агент не заводится) | `docs/org/vendors-chair.md` |
| `git-freed` | Git Freed (Гит Освобождённый) | proposed, 2026-10-25 (манифест+агент есть; сессии-носителя нет — активен после создания сессии владельцем; функция пока несётся командой /ship + гейтами) | `docs/org/git-freed.md` |
| `dv-hub-custodian` | Агент «Смотритель ДВ» (ДВ-Хаб) | active, 2026-10-31 (вердикт УАС: файл dv-custodian.md создан в dv-hub, коммит 49a26ad) | `docs/org/dv-hub-custodian.md` |
| `dv-hub-department` | Отдел разработки ДВ-Хаб (слово владельца 2026-11-01; носитель — **Master-enginer** — вывод УАС по факту на диске 21.11: глобальный файл `master-enginer.md`, тот же агент, что у ИЦ; своего файла в `dv-hub/.opencode/agent/` нет) | active, 2026-11-01 (вердикт УАС 21.11: ведомство живо — сессия-носитель `ses_e68e4eb9dffe9odzQJRgs7WgAi` в peer-registry; манифест приведён к схеме ministry-manifest и внесён в реестр — строки ранее не было; написание имени носителя исправлено по Р-Д-009: «Master-Enginer» → **Master-enginer**; ячейка peer-registry исправлена ЦУ 21.11, коммит `c36d7d47`) | `docs/org/dv-hub-department.md` |
| `sero` | Агент «SerO» — Служитель Обсидиан (глобальный) | active, 2026-10-26 (файл 99c9b00, реконсиляция УАС; расхождение чертежа рапортовано ЦУ) | `docs/org/sero.md` |
| `obsidian-plugin-dev` | Агент «obsidian-plugin-dev» — разработчик плагинов Обсидиан (субагент Служителя) | active, 2026-10-27 (вердикт УАС; **перепроверено 2026-11-07**: файл `dotfiles/.opencode/agent/obsidian-plugin-dev.md` на месте, mode subagent, scoped-права — слово владельца 07.11: субагент Служителя Обсидиан) | `docs/org/obsidian-plugin-dev.md` |
| `ship-representative-maya` | Представитель Корабля «AllIsMaya» (@AllIsMaya) — единый sender; Голос Корабля: все исходящие в TG, мультиагент (профили ssa/dv/serp/portal), Капитанский портал в ведении | active, 2026-10-29 (слово «активен», реестр Р-Д-002; переобувка 4/4 профилей = AllIsMaya, tg-whoami; recruiting на паузе Р-Д-007) | `docs/org/ship-representative-maya.md` |
| `hpf-school` | Школа концептуальных изысканий (ХПФ, исследовательское крыло; агент **Skolar**) | active, 2026-10-30 (вердикт УАС: 11+4 полей, mandate-source = слово владельца дословно + Р-034; спека approved 10-30, сессия ses_eQRHoixARq3RNJnKLFTS4IW, peer-registry строка на месте). Обновлено 2026-11-19: каноническое имя агента — **Skolar** (выбор УАС/Корабля, не слово владельца; слово владельца на имя запрошено 19.11, ожидается); файл агента создан УАС (`~/.config/opencode/agent/skolar.md`, dotfiles a9999b3); переключение сессии-носителя на Skolar — зона ЦУ. 19.11 в манифест вписана свидетельская часть крыла по слову lead'а Храма (basis: quoted; уточнение зоны УАС — печать/сверка/замеры, запись — только под санкцией лида) | `docs/org/hpf-school.md` |
| `office-serplux-primary` | Primary офиса SERPLUX (перенос top-man из аутрича) | active, 2026-10-31 (вердикт УАС: Serp-office + Senior-dev созданы в serp, b0de867; красные линии verbatim). Обновлено 2026-11-21: имя `Senior-dev` совпадает с каноном Аутрич·Цеха (Р-Д-011) — коллизия не разведена, ждёт слова владельца | `docs/org/office-serplux-primary.md` |
| `spells-chair` | Кафедра заклинаний при УАСе (агент Spellmaster; производство укреплённых скиллов, линия при Бизнес-школе) | active, 2026-11-08 (Р-118 + слово владельца 07.11 о создании кафедры; файл агента создан УАС, имя — выбор Корабля) | `docs/org/spells-chair.md` |
| `serp-forge` | Продуктовый Цех SERP (агент Foreman, primary; контур SSA под control-top) | active, 2026-11-18 (слово владельца 18.11: «сделать примари агента в цех серп»; имя — выбор УАС; activation глобальная + продуктовая копия) | `docs/org/serp-forge.md` |
| `master-freela` | Фриланс-линия Корабля (агент Master-FreeLa, примари; ведомство — Бизнес-школа) | active, 2026-11-07 (файл агента создан УАС по слову владельца, реестр имён строка Master-FreeLa; канон Р-113) | `docs/org/master-freela.md` |
| `business-school` | Бизнес-школа Корабля (коммерческие проекты, ресурсно-ориентированная экономика, финучёт, наставничество; агент-имя Bizmaster — выбрано Кораблём по Р-097, не словом владельца; ресурс: репо freelance-line — Р-113, клиентские данные вне git) | active, 2026-11-05 (Р-071; имя Bizmaster зарегистрировано, activation-копия ~/.config/opencode/agent/bizmaster.md создана, реестр имён обновлён) | `docs/org/business-school.md` |

## Правила
1. Манифест обязателен с момента approval спеки ведомства (Р-014).
2. Первые записи реестра — УАС (spec approved 2026-10-17) и спец-отдел «Ротатор»
   (учреждён 2026-10-23) — по пробелу, подсвеченному ИПТ 2026-10-23 (ref: uas-spec-actual-20261023).
3. Операционная запись реестра — через ЦУ; курирование схемы и реестра — УАС.
4. Расхождение манифеста с карточкой проекта (`03-Projects/`) = инцидент слоя.
5. Документ в `docs/org/` с типом, отличным от `Manifest` (`Audit`, `Registry`,
   `CanonNote`), манифестом не является и строки реестра не получает.
