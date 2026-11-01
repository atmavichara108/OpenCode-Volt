---
type: Reference
title: Реестр вендоров
status: active
owner: Кафедра изучения вендоров (куратор AllIs Maya, линия Maya; агентный контур УАС)
timestamp: 2026-11-01
related:
  - docs/specs/vendors-chaurea-uas.md
  - 03-Projects/inception-application.md
  - 10-Deck/drafts/nvidia-letter-draft.md
  - 11-Quests/quests.md (Q-001)
---

# Реестр вендоров

## WIP-1 · goal (Р-039)

- **objective** (одобрение ЦУ 2026-11-01, ref vendors-wip1-approve): «Реестр вендоров-0 (NVIDIA) — единая точка «мы ↔ вендор»: контакт, продукты, квоты/лимиты, канал связи, статус.»
- **criteria:**
  1. файл `01-Reference/vendors.md` существует;
  2. запись NVIDIA заполнена по 5 полей, каждое поле либо sourced-факт со ссылкой на источник, либо честная метка `[проверить]`;
  3. ни одного секрета (пароли/ключи/токены) в файле;
  4. в `00-INDEX.md` есть ссылка `[[vendors]]`.
- **kill:** если факт по полю не подтверждается источником волта и нечем проверить сейчас — пишем «[проверить: <как проверить>]», НЕ додумываем; если начались обязательства/деньги — стоп, эскалация куратору.

## Назначение кафедры и красные линии

Кафедра изучения вендоров (линия Maya, агентный контур УАС; сессия `ses_eV2O1NnTDdkWQ1sf8BU1m6o`, `04-Memory/peer-registry.md`) ведёт этот реестр — единую точку «мы ↔ вендор» по контакту, продуктам, квотам/лимитам, каналу связи и статусу. Письма от имени владельца идут из реестра отправителей представителя.

**Красные линии кафедры:**
- Обязательства/деньги/подписи — только по явному слову владельца.
- Секреты — через Ворота (owner-gate), не в репо; в этом файле секретов нет и быть не должно.
- Переписка от имени владельца — только из реестра отправителей представителя, со следом «кто внутри».

## Реестр (сводка)

| Вендор | Контакт | Продукты | Квоты/лимиты | Канал связи | Статус | Обновлено |
|---|---|---|---|---|---|---|
| **NVIDIA** | Developer Program member since 09/26; аккаунт Atmavichara108 (msivyhin@gmail.com), профиль Industry HPC/Scientific Computing, организация re-search.wiki | NIM/Nemotron (build.nvidia.com), NGC/blueprints (NeMo, Dynamo, NIM), Inception, DLI, nemotron-3.5-content-safety | free-tier 1000 кредитов / 40 RPM; рост — Credit & Rate-Limit Increase Request; заявка Inception — ready (Q-001.1) | письма домена re-search.wiki (mail-hub); исходящий rudra108@re-search.wiki; адресат 10-23 — nvidia-inception@; линия Maya | warm — письмо-знакомство отправлено 10-23, ответ [проверить]; заявка Inception готовится | 2026-11-01 |
| **Genmail** | msivyhin@gmail.com (аккаунт владельца, платная подписка) | облачный почтовый исполнитель рутины | по подписке — [проверить: тариф/лимиты] | папк-шина: Genmail→папки→mbsync→mail-hub (Р-067 узел 1 / Р-068-А) | active-кандидат (scope назначает Maya) | 2026-11-01 |

> Остальные вендоры (AMD, GitHub и др.) — по стратегическому слову владельца, пока не заполняем.

## Запись NVIDIA

### 1. Контакт
- Членство **NVIDIA Developer Program — member since 09/26**, профиль **Industry HPC/Scientific Computing**, организация **re-search.wiki**. Слово владельца 2026-10-23 (basis: quoted): «мы уже имеем членство в NVIDIA Developer Program с сентября (member since 09/26), profile HPC/Scientific Computing, и нам нужен доступ к квотам для развития открытой экосистемы агентных систем». Источник: `03-Projects/inception-application.md`.
- Аккаунт NVIDIA: **Atmavichara108 / msivyhin@gmail.com** (Max Rudra). Учётка личная — для портальной части (Developer Program, Members Area / My Developer Profile). Факт 10-22: вкладка Developer Program у учётки уже есть — запрос можно вести из этой учётки, письмо связано с ней (профиль → Project Description). Источники: `03-Projects/inception-application.md`, `10-Deck/drafts/nvidia-letter-draft.md`.

### 2. Продукты (релевантные нам)
- **Эндпоинты NIM/Nemotron (build.nvidia.com, blueprints)** — цель: испытание целостности экосистемы на NVIDIA NIM (квест Q-001.3); GitHub-проекты экосистемы — github.com/atmavichara108 (dv-hub, OpenCode-Volt). Источники: `10-Deck/drafts/nvidia-letter-draft.md`, `11-Quests/quests.md`.
- **nemotron-3.5-content-safety** — кандидат в guardrail-эндпоинт pre-send гейта (15 автоматических проверок), заявлен в письме; роль модели-актуатора `[проверить: проба в Ability Lab — в аудите 10-13 статус «поиском не подтверждён» (06-Audits/2026-10-13)]`. Источник: `10-Deck/drafts/nvidia-letter-draft.md`.
- **NGC / catalogs и blueprints (NeMo, Dynamo, NIM)** — разведка, квест Q-001.6 (ready). Источник: `11-Quests/quests.md`.
- **NVIDIA Inception** — бесплатные cloud credits от NVIDIA и партнёров, preferred pricing на железо/софт, доступ к DGX-климатам и программам обучения (DLI), VC-сеть, бейджи, members-only newsletter (из открытого описания). Источник: `03-Projects/inception-application.md`.
- **DLI-курсы** — обучение в составе Inception; курс «Securing Agents With OpenShell and NemoClaw» — квест Q-001.2 (ready). Источники: `03-Projects/inception-application.md`, `11-Quests/quests.md`.
- **NemoClaw / OpenShell** — open-source reference stack безопасных агентов (Docker + K3s, policy-слои в контейнере); кандидат в Ability Lab (сравнение с нашей permission-моделью; известные обходы изоляции — обязательная часть протокола). Источник: `06-Audits/2026-10-13-institute-case-nvidia-agents-infra.md`.
- **DGX Cloud grants / DGX Spark** — входят в выгоды Inception; DGX Spark (GB10, 128 ГБ) подтверждён как продукт (CES 2025) — «перспектива, не текущая задача». Источники: `03-Projects/inception-application.md`, `06-Audits/2026-10-13-institute-case-nvidia-agents-infra.md`.
- **GPU-стек / драйверы / CUDA** — `[проверить: применимость на нашем железе источником волта не подтверждена — ThinkPad P51 с Quadro старшего поколения; применимость TensorRT-LLM там же помечена [проверить]. Как проверить: bench/проба при появлении NVIDIA-GPU в контуре]`. Источник: `06-Audits/2026-10-13-institute-case-nvidia-agents-infra.md`.

### 3. Квоты/лимиты
- **NVIDIA Build free-tier: 1000 кредитов / 40 RPM** — ПОДТВЕРЖДЕНО (проверка фактов живым веб-поиском 10-13: forums.developer.nvidia.com, обзоры NIM free tier). Источник: `06-Audits/2026-10-13-institute-case-nvidia-agents-infra.md`.
- **Официальный путь роста: Credit & Rate-Limit Increase Request** на developer-форумах — процесс запроса, не автоматическое расширение; «5000 кредитов / 200 RPM при верификации корпоративной почтой» — ЧАСТИЧНО, апгрейд free-tier RPM не гарантирован ответами форумов. Источник: тот же аудит.
- **Позиция письма: правильный канал, не исключение** — «We're not asking to bypass limits — we're asking how a project like ours can grow inside NVIDIA's ecosystem the right way» (обходных исключений не просим). Источник: `10-Deck/drafts/nvidia-letter-draft.md`.
- **Заявка в NVIDIA Inception** — бесплатная регистрация без взносов и дедлайнов, стадия пред-стартапа; proposed credits usage: **$500–1000** на прототипирование и тестирование в первый месяц; статус **Q-001.1 ready** — подаёт владелец, текст у ЦУ. Источники: `03-Projects/inception-application.md`, `11-Quests/quests.md`.
- **Забор NIM-кредитов + проверка целостности на Nemotron** — Q-001.3 (ready), предусловие: Q-001.1 или free-кредиты. Источник: `11-Quests/quests.md`.
- **Платный dedicated NIM** — Q-001.7 parked: «решение владельца о бюджете» (без слова владельца не оцениваем). Источник: `11-Quests/quests.md`.
- **Метахаб квот (10 компаний)** — Q-002: предусловие «письмо NVIDIA ✓»; рассылка писем Q-002.1 — ready. Источник: `11-Quests/quests.md`.

### 4. Канал связи
- **Почта — домен re-search.wiki (mail-hub)**; исходящий адрес **rudra108@re-search.wiki**; получатель письма 10-23 — **nvidia-inception@**. Источники: `03-Projects/inception-application.md`, `04-Memory/active-context.md` (фокус 2026-10-23, ночь: «письмо отправлено (nvidia-inception@, 250)»).
- **Хаб почты жив**: dkim/spf/dmarc = pass подтверждены заголовками; спам у Gmail — прогрев. Источник: `04-Memory/active-context.md`.
- **Переписку от имени владельца ведёт линия Maya**; primary кафедры — **AllIs Maya** (слово владельца 11-01: «примари — AllIs Maya; отдельный агент не нужен»). Источник: `04-Memory/peer-registry.md` (строка кафедры).
- Учётка **msivyhin@gmail.com** — личная, для портальной части; переписка от имени владельца — не через неё. Источники: `03-Projects/inception-application.md`, `10-Deck/drafts/nvidia-letter-draft.md`.

### 5. Статус
- **warm** — членство активно (member since 09/26); письмо-знакомство отправлено **10-23** (адресат nvidia-inception@). Источник: `04-Memory/active-context.md`.
- Ответ NVIDIA — `[проверить: ящик mail-hub / письма NVIDIA — ответа нет ни в одном источнике волта; проверить при вытягивании писем (Q-001.4)]`.
- Заявка Inception — **готовится** (Q-001.1 ready; подаёт владелец). Источник: `11-Quests/quests.md`.
- Вытягивание писем NVIDIA + разбор анонсов — **Q-001.4 active** (владелец ЦУ; предусловие mail-hub ✓). Источник: `11-Quests/quests.md`.
- Первое дело кафедры — этот реестр-0 (квест **Q-009**, active). Источники: `04-Memory/peer-registry.md`, `11-Quests/quests.md`.

## Запись Genmail

### 1. Контакт
- Аккаунт владельца **msivyhin@gmail.com**, платная подписка Genmail подключена. Слово владельца 2026-11-01 (basis: quoted, через Maya): «у меня подключён genmail к msivyhin на платной подписке и он уже там много что сделал». Источник: `01-Policies/decisions-registry.md` (Р-068).
- Genmail работает на личном аккаунте владельца; переписка от имени владельца — только через реестр отправителей представителя (красные линии Р-064), не через сам аккаунт Genmail. Источники: `01-Policies/decisions-registry.md` (Р-064), этот файл (красные линии кафедры).

### 2. Продукт
- **Облачный почтовый исполнитель рутины** — внешний подрядчик переписки/рутины; в реестре вендоров присутствует как внешний исполнитель, не как поставщик моделей. Источник: `01-Policies/decisions-registry.md` (Р-068).
- Смысл заведения в реестре — распределение работы: слово владельца 2026-11-01 (basis: quoted): «можно с ним распределить как то работу, повесить на него всю рутину». Источник: `01-Policies/decisions-registry.md` (Р-068).

### 3. Квоты/лимиты
- Квоты — **по платной подписке**; точные лимиты `[проверить: кабинет/тариф Genmail — слово владельца]`.
- Смысл задачи не в квотах, а в объёме рутины (слово владельца: «повесить на него всю рутину»). Источник: `01-Policies/decisions-registry.md` (Р-068).

### 4. Канал связи
- **Почтовая папк-шина — узел 1 механики стыка Р-067 (Р-068-А)**: Genmail работает только в назначенном scope рутины, пишет результат в свои папки, mbsync забирает, один хозяин на направление, владелец только смотрит результат. Источники: `01-Policies/decisions-registry.md` (Р-067, Р-068).
- Ведомства шины: **Maya** (куратор внешней линии) + **Приложения** (дом mail-hub) + **ИС** (инструменты). Точная схема папок — предложение Maya, канон — слово владельца. Источник: `01-Policies/decisions-registry.md` (Р-068-А).
- Слово владельца (basis: quoted): «нужно только продумать как вас соеденить чтобы у вас был прямой мост а не так чтобы я копипастил между вами». Источник: `01-Policies/decisions-registry.md` (Р-068).

### 5. Статус
- **active-кандидат**: scope рутины назначает Maya (линия Р-067); доступ Genmail — только в назначенный scope (красная линия Р-068). Источник: `01-Policies/decisions-registry.md` (Р-068).

### 6. Границы (красные линии)
- **Обязательства/деньги по подписке** — только по слову владельца (факт подключения зафиксирован словом 2026-11-01). Источник: `01-Policies/decisions-registry.md` (Р-064).
- **Доступ к аккаунту и папкам Genmail** — только в назначенный scope рутины. Источник: `01-Policies/decisions-registry.md` (Р-068-А).
- **Секреты** — Ворота (owner-gate), не в репо; в этом файле секретов нет и быть не должно. Источники: красные линии кафедры в этом файле, `01-Policies/decisions-registry.md` (Р-064).

## Следующие шаги

1. Ждём ответа NVIDIA на письмо 10-23 — при новом письме обновить эту запись (вытягивание писем — Q-001.4).
2. По стратегическому слову владельца — записи AMD, GitHub (и др.); до слова владельца не заполняем.
3. Реестр отправителей представителя — линия Maya: переписка от имени владельца только из него, со следом «кто внутри».
4. Обновление записи при новом письме/квоте/решении по заявке Inception (Q-001.1) и по Credit & Rate-Limit Increase Request.

## Источники

| Файл волта | За что отвечает |
|---|---|
| `03-Projects/inception-application.md` | Контактные данные NVIDIA-аккаунта и членства, состав программы Inception, proposed credits usage ($500–1000), что просим. |
| `10-Deck/drafts/nvidia-letter-draft.md` | Текст письма-знакомства (черновик v1, ssot:false): продукты и цели, позиция «правильный канал, не исключение», content-safety как guardrail. |
| `11-Quests/quests.md` | Квесты Q-001.* (путь разработчика NVIDIA) и Q-009 (реестр-0 кафедры вендоров). |
| `04-Memory/active-context.md` | Факт отправки письма 10-23 (nvidia-inception@, 250), состояние mail-hub (dkim/spf/dmarc = pass). |
| `04-Memory/peer-registry.md` | Строка кафедры: линия Maya, куратор AllIs Maya, спека, первое дело — реестр вендоров-0. |
| `06-Audits/2026-10-13-institute-case-nvidia-agents-infra.md` | Квоты free-tier (1000 кредитов / 40 RPM), процесс Credit & Rate-Limit Increase Request, кандидаты (NemoClaw, content-safety), оценка нашего железа. |
| Письмо ЦУ ref genmail-vendor-row (2026-11-01) | Заказ строки Genmail в реестре вендоров; содержание взятого блока. |
| `01-Policies/decisions-registry.md` (Р-068) | Канон Genmail-моста: папк-шина (узел 1 Р-067), ведомства шины (Maya + Приложения + ИС), красные линии; слово владельца 2026-11-01. |
