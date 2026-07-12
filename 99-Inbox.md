---
type: Inbox
title: Inbox — Планирование новой архитектуры
description: Структурированные идеи для будущих проектов. Сессия от 2026-06-30.
tags: [meta, planning, android, monitoring, ai]
timestamp: 2026-06-30
---

# Inbox — Новые направления развития

> Зафиксировано 2026-06-30. Сессия планирования.

---

## 📱 R-001: Управление проектами с телефона (Rudra Phone Remote)

**Цель:** Полноценное управление любым проектом (SERPlux, dv-hub, dotfiles, vault) с Android-телефона (Redmi Note 15 Pro).

**Ключевые сценарии:**
- Статус проектов / быстрая сводка — «что с SERPlux?»
- Запуск команд OpenCode (через реле? API?)
- Мониторинг ошибок и алертов (прод)
- Чтение логов, просмотр метрик
- В будущем — запуск агентов / пайплайнов

**Варианты архитектуры:**

### Вариант A: Telegram Bot (расширение T-015)
- Pros: уже в планах, не нужно писать UI, Telegram API зрелый, бот на Python/TS
- Cons: ограниченный UX для сложных действий, зависимость от Telegram
- Как: `/project serplux status`, `/deploy dv-hub`, `/audit all`
- Оценка: 1-2 недели

### Вариант B: Android-приложение (натив/Kotlin или Flutter)
- Pros: полный контроль, push-уведомления, офлайн-кэш, биометрия
- Cons: нужно писать и поддерживать натив, публикация в Google Play (или side-load)
- Как: WebSocket/API Gateway → проекты, Material You под Redmi Note 15 Pro
- Оценка: 1-2 месяца до MVP

### Вариант C: PWA (Progressive Web App)
- Pros: кроссплатформа, не нужно публиковать, работает в браузере
- Cons: ограниченный доступ к API телефона (но для мониторинга хватит)
- Как: Hono/Vite (как dv-hub) — дашборд + API Gateway
- Оценка: 2-3 недели

### Вариант D: SSH/termux на телефоне
- Pros: минимальные усилия, OpenCode через terminal
- Cons: UX через терминал, не для быстрых чеков
- Как: Termux + OpenCode CLI + tmux
- Оценка: 1-2 дня

**Вопросы к решению:**
- Какой вариант первичный? (предположение: Telegram Bot как первый слой, Android-приложение как эволюция)
- Нужен ли API Gateway (центральный хаб для команд)?
- Как быть с безопасностью (авторизация команд)?

### Архитектурные блоки:
```
[Telegram / Android App]
       ↓
[API Gateway] — авторизация, роутинг, кэш
       ↓
[SERPlux] [dv-hub] [dotfiles] [vault]
       ↓
[OpenCode API / CLI] — выполнение команд
```

---

## 🤖 R-002: Вайбкодинг для Android-приложений (VibeAndroid)

**Цель:** Расширить архитектуру VibeOS для создания Android-приложений через вайбкодинг.

**Проблема:** Сейчас VibeOS заточена под веб/бэкенд (Python, TS). Android имеет свою специфику:
- Kotlin/Java, Gradle, Android SDK
- Эмулятор/физическое устройство для тестов
- UI (Jetpack Compose), Lifecycle, Activities
- Google Play публикация
- ADB, logcat

**Что нужно:**
1. **Android-методы в 02-Methods/** — новые паттерны для Android-вайбкодинга:
   - `android-preview-pattern` — быстрый просмотр UI через эмулятор/ADB
   - `gradle-fast-feedback` — минимизация времени сборки
   - `compose-iterative` — итеративная разработка Jetpack Compose
   - `android-distill` — дистилляция Android-специфичных знаний

2. **OpenCode-команды для Android:**
   - `/android-build` — сборка + запуск на эмуляторе
   - `/android-preview` — скриншот UI → анализ агентом
   - `/android-deploy` — деплой на телефон через ADB

3. **Интеграция с VibeOS:**
   - Android-проекты в таблице проектов (00-INDEX)
   - Android-агенты в системе
   - Методы применимые к Android: closed-loop, context-as-docs, model-routing

**Вопросы:**
- Какой первый Android-проект? (предположение: сам AI-ассистент — eat your own dogfood)
- OpenCode под Android? (редактор на телефоне? или только десктоп?)
- Эмулятор или физическое устройство для тестов?

---

## 📊 R-003: Production Monitoring System (ProdWatch)

**Цель:** Система мониторинга продуктов на проде — SERPlux, dv-hub, будущие деплои.

**Что нужно мониторить:**
- **Uptime:** сервис жив? HTTP 200? Response time?
- **Errors:** логи ошибок, 5xx, исключения
- **Resources:** CPU, RAM, диск (если свой сервер)
- **Data:** БД соединения, очередь задач, rate limits
- **Business:** для SERPlux — объём собранных данных, для dv-hub — активные пользователи

**Стек (opensource/preferred):**
- Uptime: `uptime-kuma` (самый простой, самописный дашборд)
- Logs: `loki` + `promtail` (легковесный), или просто `journald`
- Metrics: `prometheus` + `node_exporter`
- Alerting: gotify (push на телефон), Telegram
- Dashboard: grafana (если тяжело) или самописный минималистичный

**Альтернатива (минимализм):**
- Shell-скрипты + cron + Telegram bot для алертов
- plain text logs + grep
- `healthchecks.io` (если не критично)

**Архитектура (если свой сервер):**
```
[Product Server]
  ↓ (metrics endpoint)
[Metrics Collector / Prometheus]
  ↓
[Dashboard (Grafana / simple web)]
  ↓
[Alerting → Telegram / Gotify → Redmi Note 15 Pro]
```

**План реализации:**
1. Фаза 0: Health-check скрипты + Telegram алерты (1-2 дня)
2. Фаза 1: Дашборд (read-only, веб) (1 неделя)
3. Фаза 2: Система алертов с уровнями (2 недели)
4. Фаза 3: Полная observability (logs + metrics + traces) (1 месяц)

**Вопросы:**
- Где хостинг? (свой сервер? VPS? serverless?)
- Что первым мониторить? (SERPlux уже в проде?)
- Нужна ли история метрик или только live?

---

## 🧠 R-004: AI-ассистент на Android (Rudra AI)

**Цель:** ИИ-ассистент на Android, эволюционирующий от простого планера до полноценного ассистента.

**Фазы развития:**

### Фаза 1: Planner (MVP, 1-2 недели)
- TODO-лист с приоритетами
- Интеграция с TASKS.md / проектами
- Напоминания по времени
- Простой UI (Jetpack Compose)
- Локальное хранение (SQLite/Room)

### Фаза 2: Agent-aware (2-4 недели)
- Чтение статусов проектов из волта
- Напоминание о проблемах (❌ методы)
- Интеграция с Telegram bot (бот шлёт уведомления)
- Голосовой ввод (Speech-to-Text)

### Фаза 3: Proactive (1-2 месяца)
- Анализ логов проектов → предложения действий
- Предсказание задач на день (из календаря + статусов проектов)
- Push-уведомления с контекстом («SERPlux упал, перезапустить?»)
- Локальный LLM (Gemma 2 / Phi-3 через mlc-llm или MediaPipe)

### Фаза 4: Full Assistant (3+ месяца)
- Полноценный текстовый/голосовой интерфейс
- Выполнение команд от имени пользователя
- Интеграция с календарём, контактами, файловой системой
- Multi-agent (несколько специализированных суб-агентов)
- Распознавание контекста (проектный или личный)

**Технические решения:**
- **Язык:** Kotlin (нативный Android) или Flutter (кроссплатформа)
- **UI:** Jetpack Compose (Material You, под Redmi Note 15 Pro)
- **Local LLM:** Gemma 2 (2B) через MediaPipe или mlc-llm
- **Cloud LLM:** DeepSeek API (как в VibeOS) для сложных задач
- **Хранение:** Room (локально) + Git-backed (для проектов)
- **Сеть:** Retrofit / Ktor client для API Gateway

**Вопросы:**
- Начинать как отдельное приложение или как модуль Rudra Phone Remote?
- Какой первый use case? (TODO planner как понятная точка входа)
- Offline-first или online-only?
- Нужен ли серверный компонент или всё на телефоне?

---

## 🔄 Связи между направлениями

```
R-001 (Phone Remote) ←→ R-004 (AI Assistant): Assistant как часть Phone Remote
R-002 (VibeAndroid) ←→ R-004: AI Assistant = первый Android-проект (dogfooding)
R-003 (ProdWatch) ←→ R-001: Мониторинг на телефон
R-001 ←→ R-002: Управление Android-проектами с телефона
R-003 ←→ R-004: AI анализирует метрики прода
```

Все 4 направления сходятся в одну супер-идею:
**Единая система управления → через телефон → с ИИ-помощником → для всех проектов (включая Android).**

---

## 🎛️ R-005: Оркестрация из волта всеми проектами (Project Orchestrator)

**Идея:** Волт — не только хранилище знаний, но и пульт управления всеми OpenCode-проектами.

**Триггер:** Инцидент с AGENTS.md в SERP — librarian может и должен обновлять файлы в репо проектов, если это согласовано. Не «только карточки», а полноценная оркестрация.

**Что это значит:**
- Волт знает состояние каждого проекта (через аудит: `git pull` → сверка с карточкой → обновление)
- Волт может инициировать команды в проектах (через subagent или CLI)
- Волт координирует агентов разных проектов (SERPlux/ui-dev, dv-hub/build, dotfiles/sysop)
- Волт ведёт общий лог изменений по всем проектам

**Архитектура:**
```
[Волт / Librarian]
  ├── аудит проектов (git pull, сверка, обновление карточек)
  ├── запуск команд в проектах (/interface в SERPlux, /build в dv-hub)
  ├── координация агентов (делегация задач между проектами)
  └── общий дашборд состояния (00-INDEX, TASKS.md)
        ↓
[SERPlux] [dv-hub] [dotfiles] [vault] [новые проекты...]
  ↓           ↓          ↓          ↓
[ui-dev]  [build]   [sysop]   [librarian]
```

**Связь с Android:**
- Управление оркестрацией с телефона (R-001) → «запусти /interface в SERPlux»
- Rudra AI (R-004) как голосовой интерфейс к оркестратору
- Алерты от оркестратора → push на телефон (R-003 ProdWatch)

**Что реализовать:**
1. Команда `/orchestrate` в волте — запуск команд в проектах
2. Протокол «запрос → подтверждение → выполнение» (librarian спрашивает перед действием в репо проекта)
3. Общий лог оркестрации (кто, что, когда, в каком проекте)
4. Интеграция с Telegram-ботом (удалённая оркестрация)
5. Android-приложение как UI для оркестратора

**Вопросы:**
- Как безопасно давать волту права на запись в репо проектов? (permission: external_directory)
- Нужен ли «dry-run» режим — показать что сделает, но не делать?
- Как обрабатывать конфликты (волт правит файл, агент проекта тоже)?

---

## 🐧 R-006: Linux UX Lab — систематический апгрейд UX Linux (Manjaro)

> Зафиксировано 2026-07-07. Сессия фиксации нового направления.

**Цель:** Систематический апгрейд пользовательского опыта Linux (Manjaro).
Превратить хаотичные посты из Telegram-группы в структурированные улучшения —
вайбкодинг для десктопа.

**Контекст:** Rudra кидает посты про Linux UX в открытую группу @inbox_tools
(темы: Софт, Графика, красота, Смарт, Приложения). Сейчас это просто куча
ссылок без обработки. Нужно: `/capture` извлекает → librarian классифицирует →
предложения для dotfiles.

### Связь с dotfiles
`dotfiles` = конфиги (23 пакета Stow, агенты sysop + qtile-dev + bash-dev).
**Linux UX Lab = методология поверх dotfiles:** что улучшить, зачем, как.
dotfiles — исполнитель, Linux UX Lab — исследователь/планировщик.

### Связь с VibeAndroid (R-002)
Параллель. VibeAndroid — вайбкодинг для Android. Linux UX Lab — вайбкодинг для
десктопа. Оба — расширение VibeOS на новую платформу/домен.

### Архитектурные блоки
```
[Telegram @inbox_tools, темы: Софт/Графика/красота/Смарт/Приложения]
       ↓ (/capture)
[tools/telegram-capture/ → JSON]
       ↓
[librarian: классификация → 99-Inbox или карточка dotfiles]
       ↓
[dotfiles: sysop + qtile-dev + bash-dev → реализация]
```

### Метод-водитель
[[02-Methods/tool-integration-pattern|tool-integration-pattern]] — «LLM думает,
API делает». `tools/telegram-capture/` (T-062) — первый инструмент под Linux
UX Lab.

### Вопросы к решению
- Какой первый UX-апгрейд?
- Нужно ли отдельный агент для Linux UX? (пока — librarian + dotfiles-агенты)
- Где хранить предложения — отдельный подбандл `06-Linux-UX/` или внутри 99-Inbox?

---

## 🏗️ Предварительный план работ

### Спринт 1 (ближайшие 1-2 недели)
- [ ] Telegram Bot (T-015, R-001 шлюз) — минимальный: статусы + алерты
- [ ] R-004 Фаза 1: TODO Planner на Android (первое приложение)
- [ ] R-003 Фаза 0: Health-check скрипты

### Спринт 2 (2-4 недели)
- [ ] Android-методы в 02-Methods/ (R-002)
- [ ] R-004 Фаза 2: интеграция с проектами
- [ ] R-003 Фаза 1: веб-дашборд мониторинга
- [ ] API Gateway (R-001)

### Спринт 3 (1-2 месяца)
- [ ] R-001 Android-приложение (нативный UI)
- [ ] R-004 Фаза 3: Proactive Assistant
- [ ] R-002: Первый Android-проект через вайбкодинг
- [ ] R-003 Фаза 2: алерты с уровнями

---

## 📥 Captures из Telegram

> Посты, извлечённые через `/capture` из группы @inbox_tools. Классифицированы librarian.
> Реакции в группе проставляются через `mark.py` (👍 ingested + категорийный эмодзи).

### Сессия 2026-07-08 (тема «Софт», limit=3)

#### C-001: MinerU — PDF→Markdown конвертер
- **Источник:** [t.me/inbox_tools/633](https://t.me/inbox_tools/633) (тема «Софт»)
- **Репо:** [opendatalab/mineru](https://github.com/opendatalab/mineru) (70k★)
- **Что:** PDF/Word/Excel/изображения → чистый Markdown. Таблицы в HTML, формулы в LaTeX, OCR, 109 языков. CLI/Python/веб. Локально, приватно.
- **Категория:** 🏆 VibeOS/метод
- **Применение в VibeOS:** усиление [[02-Methods/distill-pattern|distill-pattern]] и [[02-Methods/context-as-docs|context-as-docs]]. PDF-спецификации → markdown для контекста агентов. Кандидат на `tools/doc-converter/` (второй инструмент VibeOS после telegram-capture).
- **Приоритет:** P2
- **Реакция:** 🏆 (vibeos)

#### C-002: torlink — терминальный торрент-клиент
- **Источник:** [t.me/inbox_tools/621](https://t.me/inbox_tools/621) (тема «Софт»)
- **Репо:** [baairon/torlink](https://github.com/baairon/torlink)
- **Что:** CLI-утилита для поиска и загрузки торрентов. TypeScript.
- **Категория:** 👨‍💻 dotfiles / Linux UX
- **Применение:** пакет для dotfiles, кандидат на настройку через bash-dev/util-dev
- **Приоритет:** P4
- **Реакция:** 👨‍💻 (dotfiles)

#### C-003: polaris — стриминг музыки
- **Источник:** [t.me/inbox_tools/619](https://t.me/inbox_tools/619) (тема «Софт»)
- **Репо:** [agersant/polaris](https://github.com/agersant/polaris)
- **Что:** Медиа-сервер, веб-интерфейс, Subsonic, автоиндексация библиотеки. Rust.
- **Категория:** 👨‍💻 dotfiles / Linux UX
- **Применение:** медиа-пакет в dotfiles, системный сервис на Manjaro
- **Приоритет:** P4
- **Реакция:** 👨‍💻 (dotfiles)

### Сессия 2026-07-09 (массовый capture, 6 тем × 10 постов = 60)

> 60 постов из 6 тем (Софт, Приложения, Вайб, ИИ, Графика, Смарт).
> Классифицировано librarian. Реакции проставлены через mark.py.

#### Сводка по категориям

| Категория | Эмодзи | Кол-во | Описание |
|-----------|--------|--------|----------|
| dotfiles/Linux UX | 👨‍💻 | 22 | Утилиты, терминалы, файл-менеджеры, заметки |
| VibeOS/метод | 🏆 | 22 | AI-агенты, MCP, роутинг, контекст, PDF→MD |
| Новый проект | 🎉 | 10 | VibeAndroid (8!), AI-видео (2) |
| SERPlux | 🔥 | 1 | Docker security |
| error | 🤔 | 4 | Пустые посты, нерелевантные |

#### Тема: Софт (10 постов)

| ID | Название | Язык | Категория | Описание |
|----|---------|------|-----------|----------|
| 617 | Telegram-Media-Downloader | JS | 👨‍💻 | Скачивание медиа из TG-веб |
| 578 | mgrep | TS | 🏆 | Семантический поиск по коду/изображениям/PDF |
| 577 | CloudPaste | JS | 👨‍💻 | Обмен текстом/файлами, Cloudflare, WebDAV |
| 563 | elio | Rust | 👨‍💻 | Терминальный файловый менеджер, 3 панели |
| 562 | horizon | Rust | 👨‍💻 | Управление сессиями терминала, GPU |
| 560 | netwatch | Rust | 👨‍💻 | Диагностика сети в терминале |
| 551 | blackcandy | Ruby | 👨‍💻 | Самохостинг музыки |
| 543 | deskreen | TS | 👨‍💻 | Второй экран через WebRTC |
| 523 | tiptop | Python | 👨‍💻 | Мониторинг системы (top-аналог), Textual |
| 519 | tldr-pages | — | 👨‍💻 | Упрощённые мануалы команд |

#### Тема: Приложения (10 постов)

| ID | Название | Язык | Категория | Описание |
|----|---------|------|-----------|----------|
| 623 | wlctl | — | 👨‍💻 | Управление Wi-Fi/Ethernet/VPN |
| 622 | ImageGlass | C# | 👨‍💻 | Просмотрщик изображений, 90+ форматов |
| 618 | revpdf | — | 🏆 | PDF-редактор офлайн |
| 616 | note-desktop | Python | 🏆 | Заметки в стиле Telegram, P2P, шифрование |
| 596 | PdfDing | Python | 🏆 | Менеджер PDF |
| 592 | poznote | JS | 👨‍💻 | Заметки, самохостинг, Excalidraw |
| 590 | lap | Vue | 👨‍💻 | Менеджер фотографий офлайн |
| 576 | clin-rs | Rust | 🏆 | TUI-заметки, .md/.canvas (Obsidian-like) |
| 573 | clin-rs (дубль) | Rust | 🏆 | Дубликат 576 |
| 568 | alt-sendme | TS | 👨‍💻 | Передача файлов P2P, QUIC, TLS 1.3 |

#### Тема: Вайб (10 постов, 3 пустых)

| ID | Название | Категория | Описание |
|----|---------|-----------|----------|
| 666 | dockerscan | 🔥 | Docker security (Go) |
| 665 | rlm | 🏆 | RLM — Recursive Language Model, диаграммы |
| 664 | (пустой) | 🤔 | Документ без текста |
| 663 | (пустой) | 🤔 | Документ без текста |
| 662 | (пустой) | 🤔 | Документ без текста |
| 661 | RLM видео | 🏆 | Claude 1M токенов, Context Rot, RLM, agent tools |
| 660 | Claude for OSS | 🏆 | 6 месяцев Claude Max 20x для open source |
| 658 | awesome-agent-orchestrators | 🏆 | Список AI-агентов для оркестрации |
| 656 | tinyrouter | 🏆 | LLM-маршрутизатор 10k параметров |
| 655 | free-llm-api-resources | 🏆 | 100% бесплатные LLM API (25k★) |

#### Тема: ИИ (10 постов)

| ID | Название | Язык | Категория | Описание |
|----|---------|------|-----------|----------|
| 635 | OpenHuman | — | 🏆 | AI-ассистент, Super Context, 118 приложений |
| 629 | Clips | — | 🎉 | Замена Loom, agent-native видео |
| 558 | autoskills | Ruby | 🏆 | Авто-навыки для AI-агентов, 46 технологий |
| 549 | claude-blog | Python | 👨‍💻 | Блог-контент с Claude Code |
| 525 | codeburn | TS | 🏆 | Мониторинг токенов ИИ, TUI |
| 520 | llmfit | — | 🏆 | Подбор локальных LLM под железо |
| 508 | mercury-agent | TS | 🏆 | Автономный AI-агент, 40+ инструментов, TG |
| 504 | girl-agent | TS | 🤔 | Виртуальный персонаж (нерелевантно) |
| 503 | pocketpaw | Python | 🏆 | Персональный AI-агент, Command Center |
| 501 | Sourcerer MCP | — | 🏆 | Семантический поиск по коду (MCP) |

#### Тема: Графика (10 постов)

| ID | Название | Язык | Категория | Описание |
|----|---------|------|-----------|----------|
| 589 | upscayl | TS | 👨‍💻 | AI увеличение изображений |
| 565 | claude-code-video-toolkit | Python | 🏆 | Видео с Claude Code, Remotion |
| 449 | FireRed-OpenStoryline | Python | 🎉 | Агентная система видео |
| 437 | freecut | TS | 👨‍💻 | Видеоредактор в браузере |
| 436 | pointless | JS/Rust | 👨‍💻 | Рисование, бесконечный холст |
| 435 | videoeditor | TS | 🎉 | AI видеоредактор, Vibe-стиль |
| 431 | frame | — | 🏆 | AI видеоредактор, Cursor-like UI |
| 397 | DaVinci Resolve MCP | — | 🏆 | MCP для видеомонтажа |
| 396 | Background Remover | React | 👨‍💻 | Удаление фона, локально, WebGPU |
| 394 | Chandra | — | 🏆 | OCR, изображения/PDF → HTML/MD/JSON |

#### Тема: Смарт (10 постов — VibeAndroid!)

| ID | Название | Язык | Категория | Описание |
|----|---------|------|-----------|----------|
| 609 | awesome-android-root | Python | 🎉 | 400+ инструментов для root Android |
| 594 | linux-android | Shell | 🎉 | Linux на Android через Termux |
| 585 | web-to-app | Kotlin | 🎉 | URL → Android приложение |
| 556 | DeadReckoning | Java | 🎉 | Навигация без GPS (инерциальные датчики) |
| 547 | plain-app | Kotlin | 🎉 | Управление телефоном через веб (Phone Remote!) |
| 545 | mobai-mcp | TS | 🏆 | MCP для мобильных устройств |
| 524 | localsend | Dart | 👨‍💻 | Обмен файлами P2P, кроссплатформа |
| 511 | DroidDesk | Shell | 🎉 | Android → Linux десктоп |
| 471 | web-to-app (дубль) | Kotlin | 🎉 | Дубликат 585 |
| 463 | Flow | Kotlin | 🎉 | YouTube клиент для Android |

### Анализ паттернов и перспективы

#### 1. VibeAndroid (R-002) — ПОДТВЕРЖДЕНО
8 из 10 постов темы «Смарт» — Android-инструменты. Termux+Linux, web-to-app,
plain-app (прямой кандидат на R-001 Phone Remote), mobai-mcp. Направление
VibeAndroid [[99-Inbox#R-002]] получает сильное эмпирическое подтверждение.

#### 2. MCP (Model Context Protocol) — растущий тренд
3 поста: Sourcerer MCP (семантический поиск по коду), DaVinci Resolve MCP
(видеомонтаж), mobai-mcp (мобильные устройства). MCP как стандарт подключения
внешних инструментов к LLM — прямой кандидат на изучение в VibeOS. Релевантно
[[02-Methods/tool-integration-pattern]].

#### 3. PDF→Markdown — кластер инструментов
MinerU (C-001), Chandra (394), revpdf (618). Три инструмента для преобразования
документов в Markdown. Кандидат на `tools/doc-converter/` — второй инструмент
VibeOS после telegram-capture.

#### 4. model-routing — эмпирические данные
tinyrouter (656) — LLM-маршрутизатор на 10k параметров. llmfit (520) — подбор
моделей под железо. Релевантно T-049 (профили моделей под провайдера) и
[[02-Methods/model-routing]].

#### 5. RLM и контекст-менеджмент
RLM (Recursive Language Model) — 665, 661. Решает проблему Context Rot
(деградация контекста в длинных чатах). Прямо релевантно
[[02-Methods/memory-management]] и flush-протоколу.

#### 6. Бесплатные LLM API
free-llm-api-resources (655, 25k★) — Google AI Studio, Groq, Cerebras,
OpenRouter, NVIDIA NIM, Mistral. Для дешёвых агентов и тестирования.

#### 7. AI-видео — новое направление?
5 инструментов (Clips, FireRed, videoeditor, frame, claude-code-video-toolkit).
Agent-native видеопроизводство. Возможно отдельное направление или часть
[[99-Inbox#R-002]] (VibeAndroid — медиа-приложения).

#### 8. Оркестрация агентов
awesome-agent-orchestrators (658) + pocketpaw Command Center (503). Релевантно
R-005 Project Orchestrator — оркестрация из волта всеми проектами.

### Сессия 2026-07-12 (полный capture, 11 тем, 584 поста)

> Полный сбор всех постов из группы @inbox_tools (11 тем, dry-run).
> Классифицировано librarian. Реакции проставлены через mark.py (в фоне).
> Файлы: captures_all.json (647K), captures_classified.json (149K).

#### Сводка по категориям

| Категория | Эмодзи | Кол-во | % | Описание |
|-----------|--------|--------|---|----------|
| dotfiles/Linux UX | 👨‍💻 | 216 | 37% | CLI-утилиты, терминалы, файл-менеджеры, медиа |
| VibeOS/метод | 🏆 | 204 | 35% | AI-агенты, MCP, skills, LLM, контекст |
| Новый проект | 🎉 | 37 | 6% | VibeAndroid (21!), AI-видео |
| SERPlux | 🔥 | 11 | 2% | Docker, скрапинг, SSL, хостинг |
| error | 🤔 | 116 | 20% | Пустые, дубликаты, курсы, Питонизм |

#### Сводка по темам

| Тема | Постов | Доминирующая категория |
|------|--------|------------------------|
| Приложения | 89 | dotfiles + vibeos (AI-сервисы) |
| Софт | 107 | dotfiles (CLI) + vibeos (CLI AI) |
| Вайб | 70 | vibeos (skills, agents, Claude) |
| #General | 109 | vibeos (каталоги, AI-сервисы) |
| Смарт | 21 | new (VibeAndroid!) |
| Графика | 23 | new (AI-видео) + dotfiles |
| красота | 14 | dotfiles (эстетика) |
| сайтостроение | 51 | serplux (хостинг) + dotfiles |
| Обучалки | 51 | vibeos (учебники по AI) |
| ИИ | 23 | vibeos (LLM, агенты) |
| Питонизм | 26 | error (учебные посты, старое) |

#### Топ-10 паттернов (полная картина)

1. **MCP — доминирующий тренд.** 7+ MCP-серверов: Sourcerer (код), DaVinci (видео), mobai (мобайл), telegram-mcp, mcp-ssh-manager, mcp-searxng, Reversecore_MCP. MCP как стандарт подключения инструментов к LLM — подтверждён эмпирически. VibeOS должна изучить MCP как следующий шаг после tool-integration-pattern.

2. **Skills — растущий паттерн.** mattpocock/skills, reverse-skill, taste-skill, NVIDIA SkillSpector, Microsoft SkillOpt, Firecrawl Skill. Скиллы как переиспользуемые промпты-инструменты — то, что OpenCode уже поддерживает. VibeOS может дистиллировать свои скиллы (capture уже скилл!).

3. **AI-агенты и оркестрация.** SeeAct, OpenHuman, mercury-agent (40+ инструментов, TG!), pocketpaw (Command Center), AutoAgent, ai-agents-from-scratch, agent-governance-toolkit (Microsoft). Релевантно R-005 Project Orchestrator.

4. **Локальные LLM.** Ollama Web UI, AnythingLLM, Khoj, airllm, BitNet (Microsoft), nanochat (Karpathy), MiniCPM-V. Локальный инференс — альтернатива облачным. Релевантно model-routing.

5. **Memory/Context management.** mem0.ai, agentmemory, RLM, OpenHuman Super Context. Контекст-менеджмент — ключевая проблема. Релевантно memory-management и flush-протоколу.

6. **CLI AI-агенты.** Shell GPT, AIChat, tlm, Lexido, Rawdog, Yapyap, reTermAI. CLI-агенты — мост между dotfiles и vibeos. VibeOS может использовать как референсы.

7. **VibeAndroid — подтверждён.** 21 пост в теме Смарт: termux-desktop, docker-android, escrcpy, PCLink, WebDeck, DroidRun, PairDrop, ImageToolbox, HTTP Shortcuts. R-002 получает сильное подтверждение.

8. **Web scraping + клонирование.** Scraperr, Website Downloader, ai-website-cloner-template, MiroShark, PixelRAG. Релевантно serplux (SEO) и tool-integration.

9. **PDF/Doc→Markdown кластер.** Chandra, MinerU (C-001), md2html, MD-This-Page, Youtube-to-Doc. tools/doc-converter/ (T-068) — реальный кандидат. Связь с distill-pattern.

10. **Claude ecosystem.** free-claude-code, claude-usage, claude-desktop-bin, ccpocket, Claude for OSS, Claude Code skills. Claude-специфичные инструменты — отдельная экосистема.

#### Структура хранения

- `tools/telegram-capture/captures_all.json` — полный JSON 584 постов (647K)
- `tools/telegram-capture/captures_classified.json` — классифицированные (149K, message_id + category + title + repo)
- `99-Inbox.md` — этот раздел (сводка + анализ)
- Группа @inbox_tools — реакции проставлены на все 584 поста (👨‍💻🏆🎉🔥🤔)

---
