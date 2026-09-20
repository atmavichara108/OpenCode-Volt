---
type: Spec
title: Pip-Boy v8 — перестройка визуального представления (pipboy-v8-rethink)
description: Три варианта нового визуального геймплея Pip-Boy поверх общего backend (registry/snapshot/actions). Выбор концепции — за Rudra.
tags: [specs, vault, pip-boy, ecosystem, ui]
timestamp: 2026-09-10
---
# Pip-Boy v8 — Spec (pipboy-v8-rethink)

## 0. Контекст и границы

- База: main c8a7209 (v4–v7: NEXT/PROPOSALS/KANBAN/DEPS/ACCEPTANCE/
  COCKPIT/actions/SSE/palette), ветка `pipboy-v8-rethink`.
- **Общий backend остаётся**: `registry.json` (canonical), `observer.py`
  (детерминированный snapshot), `actions.py` (action/query-бэкенд),
  `pipboy.py` (on-demand host + SSE), custom tools `ecosystem_*`.
  Перестраивается только *визуальное представление и UX-геймплей*:
  `index.html` (+ при необходимости новый ассет-файл v8.html).
- Read-only контракт неизменен: no silent mutation, переходы — через
  librarian/approval; данные — canonical registry + snapshot, не
  real-time по данным (SSE — сигнал об изменении).
- Утверждение спеки = выбор варианта (A/B/C) Rudra; реализация — после.

## 1. Разведка (2026-09-10)

### 1.1 Из telegram-capture (signals-2026-07-12.json, 468 сигналов)

- Категории: dotfiles 216 · vibeos(vault) 204 · new 37 · SERPlux 11.
  Relevance: 9-10 у 323 сигналов, из них с GitHub-репо 323.
- Прямые UI-кандидаты из капчура (вандерлист для v8):
  - `humanplane/terminal` (TS) — веб-терминальная эстетика;
  - `pierridotite/stonks-dashboard` (JS) — dashboard-паттерн;
  - `graykode/abtop` (Rust) — top-вид;
  - `flipbit03/terminal-use` (Rust) — терминал как рабочая среда;
  - `x0rzavi/github-readme-terminal`, `HelpFreedom/TUI_bluetooth` —
    нишевые TUI-примеры;
  - `atuin` (Rust) — history-ориентированный UX (глубина истории);
  - `vidarh/rubywm` (Ruby) — оконный менеджер как метафора (окна/панели);
  - `TM9657/flow-like` (Rust) — узловой flow-редактор (visual flow);
  - `veirt/weathr`, `Jagalite/superseedr` — дашборд-виджеты;
  - `kanban-rs/kanban`, `Zaloog/kanban-tui` (Textual, «usable by
    agents»), `antopolskiy/kanban-md` (markdown-карточки для
    multi-agent loop) — управленческие паттерны.
- Из «new» (37): значимы для UX концепта PCLink/WebDeck (device-panel
  геймплей: кнопки/виджеты управления), cybermon (Svelte монитор).

Вывод: капчур подтверждает три зрелых метафоры — (1) **терминал/HUD**
(HUD-виджеты, top-панели), (2) **карточный flow/канбан как игра**
(visual flow, kanban-md с multi-agent), (3) **девайс-панель**
(WebDeck/PCLink: физическая кнопочная панель, которой можно касаться).

### 1.2 Опенсорс-ландшафт (вне капчура)

- **Textual/Ratatui** (TUI-фреймворки): зрелые, keyboard-first; для v8
  релевантны как inspiration, но Pip-Boy живёт в браузере — port нельзя.
- **nicbarker/clay** (18k★) — 1КБ immediate-mode UI-layout на C, идея
  «layout как данные» воспроизводима на JS для HUD-виджетов.
- **excalidraw** (132k★) — canvas с руками: свободное пространство,
  где можно держать что угодно; JSON-схема документа переносима.
- **Obsidian JSON Canvas** (spec obsidian-releases) — открытый формат
  canvas (nodes/edges): совместимость с vault-воркфлоу Obsidian.
- **gtop/btop-паттерны** — блочная приборная доска.
- **kabmat/kanban-tui/basilk/flow** (keyboard-first kanban) —
  vim-навигация как геймплей.

Вывод: для веб-морды наиболее перспективны два фундамента:
**canvas/пространственная доска** (excalidraw/JSON Canvas модель) и
**HUD-виджетная сетка** (clay-подход «layout как данные»), плюс
keyboard-first поверх всего.

## 2. Варианты визуального геймплея

### Вариант A — «ВОКЗАЛ» (пространственная карта экосистемы)

Canvas-мир: карточки-здания на карте, зависимости — дороги/трубы,
поломки — дым/сирены, переходы lifecycle — транспорт по дорогам.
Zoom-out: видны слои L0..L4 как кварталы; zoom-in: карточка → интерьер
(acceptance/evidence как комнаты). minimap + keyboard-first (WASD).
Геймплей: ежедневный «маршрут обхода» — трасса по готовым карточкам
(READY подсвечены как станции), дизейбл-здания (BLOCKED) требуют
«разбора завалов» с указанием причины. INGRESS — сигналы капчура
прилетают как новые стройплощадки.

- Плюсы: wow, сильная идентичность Fallout/приборка, естественные
  подсказки (дорога = зависимость), хоршая плотность.
- Минусы: дорог в разработке (force-graph уже есть, но интерьер и
  маршруты — новые), риск «красиво, но медленно».
- Реализация: d3-force (уже в проекте) + слои + интерьеры по клику.

### Вариант B — «БОРТОВАЯ ПАНЕЛЬ» (HUD-виджеты, layout как данные)

Всё — виджеты на гибкой сетке: readiness-стакан, карта сигналов,
спарклайны активности, cockpit-агентов, мини-канбан, live-фид (SSE),
мини-карта зависимостей. Каждый виджет имеет 3 режима (mini/normal/
full) и управляется palette (`Ctrl+K` уже есть). Геймплей: собери
свой HUD под задачу (пресеты «Утро»/«Фокус»/«Триаж»), виджеты
приближают ответ на «что сейчас можно делать» в один экран без
скролла (перестройка против текущих вертикальных списков).

- Плюсы: дёшево в реализации (все данные уже есть), сразу полезно,
  легко расширять, близко к Clay «layout как данные».
- Минусы: менее «вау», больше похоже на классический дашборд.
- Реализация: CSS-grid + widget registry + palette + SSE live.

### Вариант C — «ХРОНИКА» (event-sourced геймплей, time travel)

Главная поверхность — лента событий экосистемы (записи observer,
decision-notes, route-log, capture-сигналы), карточки сворачиваются
в события на таймлайне. Геймплей: «время — это путь», scrub-бар по
истории (показывает состояние экосистемы на любой момент по
git-истории snapshot/registry), диффы как события, «что изменилось с
вчера» — первый экран. Канбан/карточки уходят во второй план
(открываются из события).

- Плюсы: уникально (нет аналогов в найденных репо), идеально ложится
  на event-sourced route-log (ECO-017 direction), отлично для
  мульти-агентного мира (кто что сделал когда).
- Минусы: нужны history-данные (сейчас их нет — observer пишет
  только текущий момент); придётся сначала построить event-log
  (route-log redirection — отдельная карточка ECO-017).
- Реализация: append-only event-log (JSONL) в observer + scrub UI.

## 3. Рекомендация

- **Быстрый ценный шаг**: B («БОРТОВАЯ ПАНЕЛЬ») — 1-2 дня работы,
  немедленная польза, на том же backend; дальнейшая перестройка —
  добавлением новых виджетов (включая элементы A и C как виджеты:
  мини-карта экосистемы, мини-хроника).
- **Стратегический шаг**: A как «лицо» v8 (пространственная карта),
  с B-виджетами как HUD-оверлеи поверх карты — сочетание даёт и wow,
  и практичность.
- C — отдельная карточка ECO-017 (event-sourced), не блокирует v8.

Предлагаемая траектория: **B (быстро) → A (пространство поверх B) →
C (хроника как ECO-017 в фоне)**.

## 4. Что НЕ меняется в v8

- Canonical данные и все backend-компоненты (см. §0).
- Клавиши: `R` (refresh), `P` (AUTO), `Ctrl+K` (palette), `Shift+клик`
  (inspector), `#view` deep-links — сохраняются в новой морде.
- Read-only/no silent mutation/без external network.

## 5. Milestones (после утверждения варианта)

- M1: widget-скелет B (grid + 6 базовых виджетов + palette-интеграция).
- M2: live-фид (SSE) как виджет + панель сигналов капчура.
- M3 (если A): пространственная карта с force-layout и маршрутами
  зависимостей, zoom layers, интерьеры карточек.
- M4: пресеты HUD («Утро»/«Фокус»/«Триаж»), экспорт view в MD/JSON
  (перенос из v7), keyboard-first tour.

## 6. Ссылки

- [[07-Runbooks/ecosystem-kanban-runbook]] — текущее пользование v3–v7.
- [[docs/specs/ecosystem-registry]] — canonical schema.
- [[06-Audits/2026-08-31-ecosystem-upgrade-plan-v2]] — план v2 (gates).
- Сигналы: `tools/telegram-capture/signals-2026-07-12.json` (468),
  свежая регенерация — capture-scan action в Pip-Boy.
