---
type: Registry
title: Реестр ведомств — живые сессии (канон адресации)
description: Единственный источник правды по адресам peer-comms. Слово владельца 2026-08-30/18-10 (калибровка).
timestamp: 2026-10-29
---
# Реестр ведомств (канон адресации)

Слово владельца (10-18, basis: quoted): «калибровка сессий\ведомств которые у меня
открыты в одном окне, это теже самые изначальные сессии... сначала калибруйся с
ними раз и навсегда».

| Ведомство | Session ID | Агент | Каталог | Роль |
|---|---|---|---|---|
| Инженерный центр (ИЦ) | ses_ece7b76c8ffeOkYZqZe38QbTVx | Master-enginer (реестр имён Р-Д-009) | ~/dotfiles | инженерный центр, dotfiles |
| Мастерская Багфикс | ses_eda56e1d3ffeyC6AIk1mwgxw1L | sysop | ~/dotfiles | багфикс-цех |
| Абилити лаб | ses_ecaf0b603ffezygMvp7QG3Iq8h | **Dr.Who** | ~/Projects/ability-lab | лаборатория способностей (переезд 2026-10-19, sessionID не менялся; primary Dr.Who — Р-007, слово владельца 10-19; субагент lab-instrument) |
| Институт Передовых Технологий (ИПТ) | ses_ecb58b307ffeqrigRxoUEWoXZs | Institute (Р-Д-009) | ~/Projects/OpenCode-Vault | исследования |
| Храм Практической Философии (ХПФ) | ses_ec84b638fffenmF4JQj5a8a2a9 | Philosopher (Р-Д-009) | ~/Projects/OpenCode-Vault | структурные/философские концепты |
| Центральный Узел (ЦУ, я) | ses_eceb23a71ffeJO9QnFou8VngZC | Hubmaster (Р-Д-009) | ~/Projects/OpenCode-Vault | координация |
| Control-top (координатор SSA) | ses_ed5fcec4effeZKwSoEmMe6Swlk | Top-manager (Р-Д-009) | ~/Projects/SSA/control | SSA-поток, владелец-панель |
| Смотритель ДВ-Хаб | ses_ea5bee799ffes5WDriyP61xyB5 | Смотритель ДВ (manifest docs/org/dv-hub-custodian.md = proposed, УАС bc0fa5c5; файл агента — ИЦ) | ~/Projects/dv-hub + ~/Projects/dv-project | смотритель проекта ДВ-Хаб (слово владельца 2026-10-24, basis: quoted: «от ныне назначаю тебя смотрителем проекта дв-хаб»); два репозитория: dv-hub (код/платформа, github.com/atmavichara108/dv-hub) + dv-project (база знания движения, submodule context/ в dv-hub, github.com/atmavichara108/dv-project); тема контрибьюторов — в сессии «командная работа» (создаст владелец) |
| Служитель Обсидиан | ses_ea02cc0d8ffeFXUsAX9UeQWs2D | obsidian-servant | ~/Projects/OpenCode-Vault (session-move 10-26, API-подтверждено) | ведомство UI\|UX ecosys (Р-021): 10-Deck, canvas-карты, Пип-Бой тайлы |
| Университет Агентных Систем (УАС) | ses_e9884e4aeffe7okjn4f7RtavmG | Professor (Р-Д-009) | ~/dotfiles (primary sysop по аналогии Р-007 — Лаба=Dr.Who в своём репо; сверка копа 10-26 уточнила строку) | ведомство-куратор агентского контура (Р-004/Р-016, в строю с 10-23); спец-отдел «Ротатор моделей» (Р-023) |
| Командная работа (dv-hub) | ses_e9299850dffefLof5BwPJ1d0lV | — | ~/Projects/dv-hub | координация совместной работы/контрибьюторов ДВ-Хаб (слово владельца 2026-10-24; id получен от Смотрителя по INC-18, сверен API: projectID dv-hub, создана 10-24; канон только через этот реестр) |
| Офис Серплюкс | ses_e7936c4f7ffenXVozON2bsu5mk | Офис (профиль по реестру; manifest — УАС) | ~/Projects/serp | представительство проекта SERPlux, в т.ч. телеграм (нарекание владельца 2026-10-29, basis: quoted: «нарекаю тебя "Офис Серплюкс" — представительство, в том числе и в телеграм»); репо /home/rudra/Projects/serp, коннект к ЦУ и ОШ выдан словом владельца |
| Аутрич · Офис (офис продукта seo-outreach) | ses_ed5dcdf33ffeisHuBX9VKB6XhM | top-man | ~/Projects/SSA/products/seo-outreach | офис/сервисный центр продукта; ID выдан владельцем 2026-10-29 (как образец для Офиса Серплюкс), сверен API (session_v2: сессия жива); роль-модель уточняется перепиской |
| Оперативный Штаб (ОШ) | ses_e8b9ae95bffeGAoRqZWtPdj2x8 | sysop | ~/dotfiles | нелокализованное место Корабля с локацией-сессией; штаб оперативного реагирования владельца; приоритет 0 по запросам владельца (Р-029); сверка API 10-25: сессия жива, агент sysop |
| Цех (Аутрич · SEO-outreach) | ses_ed9619763ffeVC3GE5q2o2HY5j | top-man | ~/Projects/SSA/products/seo-outreach | продуктовый цех SSA (заявка control-top; слово владельца 10-29, basis: quoted; сверка API: жива, агент top-man) |
| Школа концептуальных изысканий (ХПФ) | ses_eQRHoixARq3RNJnKLFTS4IW | librarian | ~/Projects/OpenCode-Vault | исследовательское крыло ХПФ (наречение владельца 2026-10-29: имя + мандат «исследования концептов и адаптация их под наши нужды»; спека docs/specs/school-conceptual-inquiry.md approved 10-30; lead — Храм; регистрация claims 10-30 по чек-листу ЦУ В.1е-ж) |
| Отдел «Приложений» | ses_eKDfprGN0tGPmzJnQChkmOT | Apps-dev (Р-Д-009, стр. 51; имя отдано УАС словом владельца 10-30) | ~/Projects/OpenCode-Vault | отдел Корабля (organ-structure §1); spec+карточка ЦУ, манифест — УАС после approval |
| Кафедра контрагентов (при УАСе) | ses_eCounterpartiesTBD | Rector (слово владельца; файл агента готовит УАС — interim librarian) | ~/Projects/OpenCode-Vault | подотдел УАС; выращивание контрагентов (rudrakshas, Р-018); спека docs/specs/department-counterparties-uas.md (УАС) |
| Отдел «Движков» | ses_euCJx9F9ZX2JXm9SxwMKBfG | interim librarian (имя-агент — слово владельца, Р-Д-009) | ~/Projects/OpenCode-Vault | отдел Корабля (organ-structure §2); parent ИЦ (Р-038-паттерн); спека docs/specs/engines-department.md; первое дело — накат мкода |

## Правила
1. **Писать только по этому реестру.** Все сессии живые (сверено по session_v2, 10-18 22:00).
2. **Мёртвый адрес:** ses_ecae229fcffef5FrLdWOJLos1K — ПРЕЖНЯЯ сессия ЦУ
   (title «Register Lab session in registry», агент meta), мертва с 10-18 04:52.
   Письма на неё терялись (отчёты ИЦ/ИПТ seq 722-757 остались в мёртвой сессии —
   приняты ЦУ через экспорт БД, не потеряны).
3. Ведомства работают в одном окне TUI, каждый в своём репо/ветке — это нормально
   («кажется отправляют в разные ветки» = разные рабочие каталоги сессий, не форки).
4. Смена адреса ЦУ (если будет) — только через этот файл + калибровочные письма.
5. 2026-10-29: «Офис Серплюкс» — внесён по слову владельца (нарекание); ЦУ подтвердила и вычистила колонку агента (имя без прозы); факт записи: агент build, каталог ~/Projects/serp.
