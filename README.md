# VibeOS — Персональная операционная система вайбкодинга

> **Вайбкодинг — это не про «бросить задачу нейросети и получить результат».**
> Это про построение системы, внутри которой ИИ делает то, что умеет лучше человека,
> а человек — то, что ИИ пока не может.

VibeOS — это **открытая методология и инфраструктура** для системного вайбкодинга.
Не очередной AI-фреймворк, а рабочий процесс, основанный на принципах инженерии знаний,
мульти-агентной архитектуры и дисциплины документирования.

Вся система живёт в этом репозитории — **командном центре знаний** под управлением
агента `librarian`.

---

## Проблема

Большинство разработчиков, использующих ИИ-агентов, сталкиваются с одним и тем же:

- Контекст теряется после каждой компакции — агент «забывает», что делал вчера
- Нет единого источника правды — знания размазаны по чатам, заметкам и README
- Одноразовые промпты вместо переиспользуемых протоколов — каждый раз с нуля
- Агенты не имеют памяти о проекте, пользователе и принятых решениях
- Нет системы — есть набор хаотичных взаимодействий с LLM

VibeOS решает эти проблемы **системно**, а не очередным «супер-промптом».

---

## Решение: Системный вайбкодинг

VibeOS строится на четырёх столпах:

### 🧠 OKF v0.1 — Open Knowledge Format
Собственная архитектура организации знаний: строгие слои (Reference → Methods →
Projects → Memory → Templates), YAML frontmatter, викилинки вместо дублирования.
Один файл — одна сущность. Никакой свалки заметок.

### 🎯 Методы — переиспользуемые протоколы
Каждый повторяющийся паттерн дистиллируется в метод с чётким описанием,
статусом внедрения и привязкой к проектам. Тринадцать методов описано
(10 stable + parallel-sessions/peer-comms proposed + promo-provider-protocol 🟡),
каждый с реальным статусом (✅ внедрён / 🟡 частично / ❌ не внедрён).

### 🤖 Мульти-агентная архитектура
Агенты — не рабы, а инструменты. Разделение ролей: `plan` думает, `build` пишет,
`reviewer` проверяет, `sysop` инспектирует систему. Каждый агент со своей моделью,
правами и зоной ответственности. В системе — 29+ агентов в 10 проектах
(librarian + tree-cop в волте, 6 в SERPlux, 5 в dv-hub, 8 в dotfiles,
8 в ChaT; recruiting-hr — [проверить]).

### 💾 Файловая память вместо внешних сервисов
Контекст, факты и логи сессий хранятся в git-версионируемых файлах.
Три уровня: `active-context` (что сейчас в фокусе) → `facts` (реестр подтверждённых
фактов) → `session-log` (история сессий). Никакой зависимости от облачных MCP-сервисов.

---

## Архитектура

```
┌──────────────────────────────────────────────────┐
│              VibeOS Vault (этот репо)              │
│  Штаб · Справочник · Память · Пульт управления     │
│         librarian — командный центр                │
└──────────┬────────────────────┬───────────────────┘
           │ аудит / апгрейды    │ мониторинг
     ┌─────┴──────┐      ┌──────┴──────┐
     ▼            ▼      ▼             ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│ SERPlux │ │ dv-hub  │ │ dotfiles │ │ (новые…) │
│ Python  │ │ TS/Hono │ │ Manjaro  │ │          │
│ SEO     │ │ comm.   │ │ sysop    │ │          │
│ 6 агентов│ │ 5 агентов│ │ 8 агентов│ │          │
└─────────┘ └─────────┘ └──────────┘ └──────────┘
```

### Командный центр
Агент **librarian** управляет всеми проектами из vault:
- Мониторит состояние проектов через `/audit`
- Сверяет карточки проектов с реальным состоянием репо
- Предлагает апгрейды методов
- Ведёт реестр фактов и контекст сессий
- В будущем — классифицирует внешние фичи через Telegram-бота

---

## Что внутри

### Проекты под управлением

| Проект | Тип | Стек | Агентов | Статус методов |
|--------|-----|------|---------|----------------|
| [SERPlux](03-Projects/SERPlux.md) | Продукт SERP Factory | Python / FastAPI / SQLite / Docker | 6 | core ✅ deploy ✅ |
| [dv-hub](03-Projects/dv-hub.md) | Волонтёрский | TypeScript / Hono | 5 | активная разработка |
| [dotfiles](03-Projects/dotfiles.md) | Система | Shell / Manjaro | 8 | мульти-агент v3 + verifier + loop + flush |
| [vault](03-Projects/vault.md) | Справочник | Markdown / OpenCode | 2 (librarian + tree-cop) | командный центр |
| [recruiting-hr](03-Projects/recruiting-hr.md) | Коммерция / рекрутинг | Python / docx→md | [проверить] | 🟡 Bootstrap (2026-10-01) |
| [AndroidOS](03-Projects/AndroidOS.md) | Umbrella / mobile | [проверить] | [проверить] | 🟢 Planning |
| [ChaT](03-Projects/ChaT.md) | Knowledge-operations | Markdown / Obsidian / OpenCode | 8 | активная территория |
| [rudra-ai](03-Projects/rudra-ai.md) / [rudra-phone](03-Projects/rudra-phone.md) | Mobile / AI | [проверить] | [проверить] | 🟢 Planning |
| [prod-monitor](03-Projects/prod-monitor.md) | Инфраструктура / monitoring | [проверить] | [проверить] | 🟢 Planning (заглушки) |

### 13 методов вайбкодинга

| Метод | Что даёт | Статус |
|-------|----------|--------|
| [context-as-docs](02-Methods/context-as-docs.md) | Документация как инфраструктура | ✅ stable |
| [distill-pattern](02-Methods/distill-pattern.md) | Команды вместо промптов | ✅ stable |
| [model-routing](02-Methods/model-routing.md) | Модель под каждую роль | ✅ stable |
| [memory-management](02-Methods/memory-management.md) | Файловая память с протоколом | ✅ stable |
| [multi-agent-pipeline](02-Methods/multi-agent-pipeline.md) | Мульти-агент с ролями | ✅ stable |
| [closed-loop](02-Methods/closed-loop.md) | Авто-итерация build→verify→fix | ✅ stable |
| [verifier-pattern](02-Methods/verifier-pattern.md) | Независимая проверка кода | ✅ stable |
| [capability-routing](02-Methods/capability-routing.md) | Маршрутизация по capability + named role | ✅ stable |
| [tool-integration-pattern](02-Methods/tool-integration-pattern.md) | Внешние API как детерминированные инструменты | ✅ stable |
| [git-worktree-isolation](02-Methods/git-worktree-isolation.md) | Изоляция потоков через worktree/ветки | ✅ stable |
| [parallel-sessions](02-Methods/parallel-sessions.md) | Параллельные сессии | proposed |
| [peer-comms](02-Methods/peer-comms.md) | Координация параллельных сессий | proposed |
| [promo-provider-protocol](02-Methods/promo-provider-protocol.md) | Промо-провайдер протокол | 🟡 |

> Полная карта с раскладкой по каждому проекту → [VibeOS.md](VibeOS.md#Методы)

### 29+ агентов в экосистеме

| Агент | Проект | Роль | Модель |
|-------|--------|------|--------|
| **librarian** | vault | Командный центр знаний (primary) | opencode-go/gpt-5.6-luna |
| **tree-cop** | vault | Чистота дерева и выкладка ветки (subagent) | [проверить] |
| **build / plan + collector-dev / reviewer / ui-dev / infra-dev** | SERPlux | Фабрика продуктов: разработка, планирование, сбор, ревью, UI, Docker | kimi-k2.7-code / glm-5.2 / qwen3.7-plus |
| **plan / build / reviewer / researcher / infra** | dv-hub | Архитектор, разработчик, ревьюер, исследователь, DevOps | Qwen / DeepSeek |
| **sysop / planner / builder + 5 subagent** | dotfiles | Полная мульти-агентная система | DeepSeek v4-flash-free |
| **8 агентов** | ChaT | Knowledge-operations (состав — [проверить]) | [проверить] |

Глобальная модель по умолчанию — `opencode-go/glm-5.3-flash` (opencode.json).

### 34 команды-пайплайна

| Проект | Команд |
|--------|--------|
| **vault** | `/ask` · `/capture` · `/inbox` · `/project` · `/commit` · `/project-add` · `/audit` · `/decisions` · `/distill-pipeline` · `/handoff` · `/route` · `/verify` |
| **dv-hub** | `/morning` · `/spec` · `/review` · `/hygiene` · `/sync-context` · `/sync-context-self` · `/sync-task` |
| **dotfiles** | `/sysaudit` · `/script` · `/qtile` · `/util` · `/prompt` · `/notify` · `/macro` · `/plugin` · `/loop` · `/flush` |
| **SERPlux** | `/commit` · `/container` · `/deploy` · `/dream` · `/interface` |

---

## Ключевые принципы

1. **Документация — это инфраструктура.** Спеки и контекст — исполняемые контракты,
   ограничивающие пространство решений агента.
2. **Метод важнее промпта.** Одноразовый промпт проигрывает переиспользуемому протоколу.
3. **Централизованное знание.** Один источник правды по OpenCode, методам и проектам.
4. **Разделение ролей.** build не проверяет свою работу — для этого есть reviewer.
5. **Память — это диск, а не RAM.** Всё важное сбрасывается в файлы до компакции.
6. **Системный инжиниринг > промпт-инжиниринг.** Строй конвейеры, не пиши инструкции.

Подробнее → [Философия VibeOS](VibeOS.md#Философия) и [Нетривиальные решения](VibeOS.md#Нетривиальные-решения)

---

## Быстрый старт

Этот репозиторий — **knowledge bundle**, а не кодовая база. Он работает с OpenCode.

```bash
# Клонировать
git clone https://github.com/<user>/opencode-vault.git
cd opencode-vault

# Открыть в OpenCode — librarian активируется автоматически
opencode .
```

**Для чего это можно использовать:**
- Как **личный командный центр** для управления проектами через ИИ-агентов
- Как **справочник по OpenCode** (01-Reference) с подтверждёнными фактами
- Как **библиотеку методов** вайбкодинга для внедрения в свои проекты
- Как **стартовый шаблон** для построения собственной системы управления знаниями

---

## Дорожная карта

| Фаза | Статус | Что сделано |
|------|--------|------------|
| P0–P1: Фундамент | ✅ Завершено | OKF v0.1 · 6 методов · 4 карточки проектов · память · pre-commit |
| P2: Справочник OpenCode | ✅ Завершено | Все разделы Reference: agents, commands, config, memory, permissions, plugins |
| P3: Проекты | ✅ Завершено | Карточки синхронизированы, статусы реконсилированы, VibeOS v0.2.3 |
| P4: CI волта | ✅ Завершено | Pre-commit hook, валидация викилинков, авто-архивация логов |
| P5: Будущее | 🟡 В планах | Telegram-бот · классификация фич · `/project-upgrade` · closed-loop в dv-hub |
| P6: Порт M Code → TUI | ✅ Завершено (итерация 1) | replay budget · doom-loop · санитизация · Playwright · verify-кэш · peers |
| P7: Параллельность (2026-10-05) | 🟡 В работе | parallel-sessions / peer-comms (proposed) · idea-graph (146/168/2) · decision-queue · tree-cop · TASKS 11 active / 1 blocked / 69 planned / 87 done |

Подробнее → [DEVELOPMENT-ROADMAP.md](DEVELOPMENT-ROADMAP.md)

---

## Структура репозитория

```
opencode-vault/
├── 00-INDEX.md            # Дашборд: таблица проектов, методов, быстрый вход
├── VibeOS.md              # Глубокий концептуальный документ (философия, методы, рост)
├── AGENTS.md              # Правила для librarian
├── Architecture.md        # Описание OKF-структуры
├── TASKS.md               # Трекер задач
├── DEVELOPMENT-ROADMAP.md # Дорожная карта
├── opencode.json          # Конфигурация OpenCode для волта
│
├── 01-Reference/          # Справочник по OpenCode
│   ├── agents.md · commands.md · config.md · memory.md
│   ├── permissions.md · plugins.md
│
├── 02-Methods/            # Методы вайбкодинга (13 файлов)
│   ├── context-as-docs.md · distill-pattern.md
│   ├── memory-management.md · model-routing.md
│   ├── closed-loop.md · verifier-pattern.md
│   ├── multi-agent-pipeline.md · capability-routing.md
│   ├── tool-integration-pattern.md · git-worktree-isolation.md
│   ├── parallel-sessions.md · peer-comms.md · promo-provider-protocol.md
│
├── 03-Projects/           # Карточки проектов
│   ├── SERPlux.md · dv-hub.md · dotfiles.md · vault.md
│   ├── recruiting-hr.md · AndroidOS.md · ChaT.md
│   ├── rudra-ai.md · rudra-phone.md · prod-monitor.md
│
├── 04-Memory/             # Память сессий (OKF-подбандл)
│   ├── active-context.md · facts.md · session-log/
│
├── 05-Templates/          # Шаблоны для быстрого старта
│
└── 99-Inbox.md            # Сырые заметки на обработку
```

---

## Для кого это

- **Вайбкодеры**, которые хотят перейти от хаотичных промптов к системе
- **Разработчики**, управляющие несколькими проектами через ИИ-агентов
- **Техлиды и соло-основатели**, строящие инфраструктуру вокруг AI-ассистентов
- **Все, кто устал от потери контекста** и хочет версионируемую память

---

## Связаться

Это личный проект [Max Rudra](https://github.com/atmavichara108). Если хотите обсудить
VibeOS, предложить идею или коллаборацию — открывайте issue или пишите в
Telegram: [@Atma_Vichara108](https://t.me/Atma_Vichara108).

---

## Лицензия

**GNU General Public License v3.0** — [GPL-3.0](LICENSE)

VibeOS — свободный софт. Это значит:

- ✅ **Форкай и используй** — хоть для себя, хоть для коммерции
- ✅ **Продавай** — можешь брать деньги за свою версию VibeOS
- ✅ **Изменяй** — адаптируй под свои проекты, добавляй методы
- ⚠️ **Оставайся свободным** — если распространяешь изменённую версию,
  она должна оставаться под GPL-3.0. Закрывать форк нельзя.

Коротко: **делай что хочешь, но не отнимай свободу у других.**

Полный текст → [LICENSE](LICENSE)

---

### 🏗️ Фонд инженера (в планах)

Когда VibeOS вырастет, я планирую создать **Инженерный фонд** —
некоммерческую структуру для сбора донатов и распределения ресурсов
на развитие открытой инфраструктуры вайбкодинга.

Средства пойдут на:
- Хостинг и инфраструктуру (VPS, API)
- Разработку open-source инструментов
- Поддержку сообщества
- Документацию и переводы

Подробности появятся, когда фонд станет реальностью. Следи за обновлениями.

---

**VibeOS** — версия [v0.4](VibeOS.md#v04-2026-10-05) · Лицензия: [GPL-3.0](LICENSE)
