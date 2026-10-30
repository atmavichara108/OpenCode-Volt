---
type: Manifest
id: office-serplux-primary
name: Primary офиса SERPLUX (перенос top-man из аутрича)
shadow: операционное ведение офиса SERPLUX по канону top
jurisdiction: >
  Продукт SERPlux (~/Projects/serp — сбор выдачи Topvisor, разметка
  тональности LLM, выгрузка в Google Sheets, SQLite, Docker): ведение
  конвейера, контракты модулей (FLAT layout), dry-run гейты, версии схем,
  журналирование, доки/changelog. Роль — копия control-канона top
  (source: control, schema-version: 1), как в seo-outreach.
carrier-sessions: ses_e7936c4f7ffenXVozON2bsu5mk
agent-file: ~/Projects/serp/.opencode/agent/top-man.md — НЕ создан (проект без агентского слоя; образец: ~/Projects/SSA/products/seo-outreach/.opencode/agent/top-man.md)
agent-location: serp (проектный слой, контур SSA); копия control-канона
mandate-source: >
  Слово владельца 2026-10-29 (basis: quoted): «нужен примари агент в
  серплюкс. что если перенести top-man из аутрича? в общем вот офис
  серплюкс если надо ses_e7936c4f7ffenXVozON2bsu5mk и обрати особое
  внимание на права, чтобы агент не спотыкался на пермишенах. хотя нужно
  отдать должное top-man не спотыкается — это хороший и умный агент».
  Задание ЦУ/мандатная линия УАС (Р-004/Р-014). Мандат не самозванный.
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_ece7b76c8ffeOkYZqZe38QbTVx
spec-home: /home/rudra/Projects/serp/docs/specs/
status: active, 2026-10-31 (вердикт УАС: Serp-office + Senior-dev созданы в serp, коммит b0de867; красные линии verbatim; было proposed 2026-10-29)
boundaries: >
  Красные линии канона top сохраняются ДОСЛОВНО (именно они — причина
  «не сптыкается», а не права): никогда не читает секреты/креды
  (проект содержит credentials.json — строка критична); внешняя отправка
  только с ручным апрувом на КАЖДОЕ письмо; код приложения — только по
  подтверждённому scope; не настраивает провайдеров/SMTP/деплой; не
  создаёт второго primary; пишет только внутри репо; main — только merge;
  dry_run по умолчанию. Права образца широкие (external_directory allow,
  edit allow, task allow, bash "*" allow) — широкие права при красных
  линиях = проверенный паттерн, при переносе не «сужаем ради красоты».
ports: манифест-реестр docs/org/manifest-registry.md (куратор УАС); peer-registry — строка «Офис SERPLUX» (операционная запись через ЦУ)
capabilities: [outreach-pipeline, module-contracts, dry-run-safety, product-ops]
memory-zones: [serplux-office-notes]
file-zones: [docs/org/office-serplux-primary.md]
evidence-policy: независимый verifier PASS + commit/tag; рапорты — в ЦУ
next-step: >
  Сессия ses_e7936c4f... работает агентом build (без собственного primary).
  Лестница: (1) моя рекомендация → слово владельца на перенос; (2) файл
  агента в serp — ИЦ/ОШ (проектный контур, копия образца + красные линии
  verbatim); (3) вердикт УАС → active; (4) строка peer-registry «Офис
  SERPLUX» через ЦУ. Maya-канал: sender представителя для внешних писем
  офиса — по мандату представителя (переобувка по слову владельца).
---

# Манифест primary офиса SERPLUX

Перенос top-man из аутрича в SERPlux — не изобретение роли, а копия
проверенного канона в новом репо. Паттерн control-канона: широкие права +
железные красные линии в тексте + dry_run по умолчанию. Именно этим
top-man «не спотыкается» — подтверждено словом владельца 2026-10-29.

## Почему перенос обоснован

- Роль уже существует и работает в seo-outreach (единственный primary,
  контракты модулей, skills campaign/discovery/scoring/...).
- Устав SERPlux (AGENTS.md проекта) по духу совпадает с каноном top:
  dry-run ориентация, модульные контракты, «не лезь в чужой модуль».
- Сессия офиса существует, агента своего нет (build) — перенос закрывает
  дыру «сессия без primary».

## Риск, который закрываем при переносе

В serp лежит `credentials.json`. Красная линия «никогда не читать секреты»
обязана быть в файле дословно — не «по контексту», а строкой. При копии
образца она переносится verbatim.
