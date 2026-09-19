---
type: Execution Spec
title: MODELS dashboard — переключение моделей агентов в Pip-Boy
description: Дашборд всех агентов с выпадающим списком моделей. Вкладка Pip-Boy MODELS + CLI model-router.py + команда /agents. Хендофф сессии «Плановый апгрейд Pip-Boy и Kanban».
status: handoff
owner: pipboy-agent
tags: [spec, pipboy, model-routing, interface]
timestamp: 2026-09-19
---

# MODELS dashboard — переключение моделей агентов

> Канонический хендофф. Владелец: сессия «Плановый апгрейд Pip-Boy и Kanban».
> Задача от Rudra: «простой механизм переключения моделей для любых агентов —
> дашборд всех агентов с выпадающим списком доступных моделей».

## Цель

В Pip-Boy появляется вкладка **MODELS**: таблица всех агентов (глобальные +
проектные), у каждого выпадающий список моделей; выбор пишет `model:` через
единый роутер. Список моделей — живой, из общего реестра провайдеров
(включая «абузные» провайдеры: openrouter:free, justwoker, linaliapi и т.п.).

## Ограничение (принято Rudra)

Переключение правит **конфигурацию** агента (`model:` в `.md`/`opencode.json`).
Эффект — с рестарта инструмента/новой сессии. Hot-reload модели в движке нет
(это зафиксировано и в `/prov`). Дашборд НЕ делает live-подмену активной сессии.

## Точки правды (что читать/писать)

- Глобальные агенты: `~/dotfiles/opencode-global/.config/opencode/agent/*.md`
- Проектные агенты: `<project>/.opencode/agent/*.md`
- Плюс блок `agent.<name>.model` в `opencode.json` / `opencode.jsonc`
- Модель агента = фронтматтер `model:` (первично) либо `agent`-блок конфига.

## Компоненты

### 1. `tools/ecosystem-map/model-router.py` (новый, stdlib, паттерн actions.py)

CLI, детерминированный:
- `list` → JSON всех агентов + текущая `model:` каждого (глобальные + проектные).
- `models` → объединённый список доступных моделей: `providers.json` + живой
  `opencode models` (+ абузные провайдеры).
- `apply --agent X --model Y [--global|--project P]` → точечная правка `model:`
  в нужном файле. Только строку `model:`, не переписывая файл. flock + backup
  перед записью (паттерн `tools/peers/peer_lease.py`).
- `--dry-run` — показать разницу без записи.

### 2. `tools/ecosystem-map/app/modules/ModelsModule.js` (новый модуль)

Паттерн — как `AgentModule.js` (`extends Module`, `mount`/`refresh`/`_render`/`_wire`).
- Таблица: имя агента, scope (global/project), текущая модель, `<select>` моделей.
- Выбор → действие `/action model-apply` → `model-router.py apply`.
- Тост: «агент X: старая → новая (применится после рестарта)».

### 3. `tools/ecosystem-map/actions.py` + `pipboy.py` endpoint

- Добавить подкоманды `model-list` / `model-models` / `model-apply` в actions.py.
- Зарегистрировать их в whitelist `Handler.do_ACTION` в pipboy.py.

### 4. Реестр провайдеров

- `providers.json` (единственный источник) дополнить абузными провайдерами.
- `observer.py`: добавить проекцию `agents.model` в `generated/snapshot.json`,
  чтобы дашборд читал живой срез без прямого доступа к конфигам.

### 5. Команда `/agents`

- `~/dotfiles/opencode-global/.config/opencode/command/agents.md` — открывает
  Pip-Boy на вкладке MODELS (pipboy.py open + якорь). Аналог `/prov`, визуальный вход.

### 6. Документация

- `02-Methods/model-routing.md`, `01-Reference/config-modes.md` — врезка о дашборде.
- `docs/specs/roel-manifest.md` (Layer 4 interface) — строка про ModelsModule.

## Решение по хранению карты (предложено, подтверждает Rudra при старте)

Карта «агент → модель» держится в одной секции `providers.json` (или
`registry.json`), а `model-router.py` проецирует её в `.md`/`opencode.json`
при `apply`. Так все маршруты видны и правятся в одном месте.

## Безопасность

- Записи — через flock и с бэкапом файла.
- Точечная правка `model:` без перезаписи фронтматтера.
- Ключи провайдеров живут в `auth.json` и в дашборд не попадают.

## Связанное

- Канон роутера моделей: [[02-Methods/model-routing]], [[01-Reference/config-modes]]
- Команда-предшественник (текстовый роутер): `~/dotfiles/.../command/prov.md`
- Провайдеры: [[01-Reference/providers]], [[01-Reference/provider-cards/linaliapi]]
- Дашборд: `tools/ecosystem-map/` (pipboy.py, actions.py, app/modules/*)