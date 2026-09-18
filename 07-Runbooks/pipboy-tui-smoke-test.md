---
type: Runbook
title: Pip-Boy TUI plugin /pipboy — controlled smoke-test
date: 2026-09-15
owner: rudra
related: "[[docs/specs/pipboy-tui-plugin-research]]"
tags: [runbook, pipboy, tui, plugin, smoke-test]
---

# Pip-Boy TUI plugin `/pipboy` — controlled smoke-test

> Цель: проверить, что native TUI route реально работает в живом OpenCode/M-Code TUI.
> Контракт: `docs/specs/pipboy-tui-plugin-research.md`. Блокер: JSX-поверхность
> `@opentui/solid` хост-приватна — собрать/typecheck плагин из репозитория нельзя,
> проверяем только в рантайме TUI.

## Шаг 0 — предпосылки

- TUI запущен из **живого** инстанса (не под sudo, тот же пользователь `rudra`).
- `bun` доступен (`.opencode` использует bun). Проверка: `bun --version`.
- Pip-Boy хост поднят (не обязателен для smoke, но нужен для чтения данных):
  `python3 tools/ecosystem-map/pipboy.py up`.

## Шаг 1 — минимальный плагин

Создать `tools/ecosystem-map/pipboy-tui/plugin.tsx`:

```tsx
/** @jsxImportSource @opentui/solid */
import type { TuiPlugin } from "@opencode-ai/plugin/tui"

export const tui: TuiPlugin = async (api) => {
  api.route.register([
    {
      name: "pipboy",
      render: () => {
        const projects = api.state.session.count()  // dummy: заставь роут жить
        return (
          <box>
            <text>PIP-BOY route OK (sessions: {projects})</text>
          </box>
        )
      },
    },
  ])
}
```

> Компоненты `<box>/<text>` — предположительное имя из `@opentui/solid`.
> Если имена другие, TUI напечатает ошибку компиляции при загрузке плагина —
> это и есть результат smoke-теста (см. Шаг 5). Подставляй реальные примитивы
> из автокомплита, когда откроешь файл в TUI/редакторе.

## Шаг 2 — зарегистрировать плагин

В `opencode.json` добавить ключ `plugin` (путь относительно корня волта):

```json
"plugin": [
  "./tools/ecosystem-map/pipboy-tui/plugin.tsx"
]
```

Формат подтверждён SDK: `Config["plugin"] = Array<string>` (файлы или npm-спекы).

## Шаг 3 — перезапустить TUI

Полностью выйти из TUI и войти заново (hot-reload плагинов не гарантирован).

## Шаг 4 — открыть route

1. Командная палитра TUI (`Ctrl+K` / `Cmd+K`) → найти команду/route `pipboy`.
2. Или, если добавить keymap, — slash `/pipboy` (позже).
3. Альтернатива: `api.route.navigate("pipboy")` из другого плагина/консоли.

## Шаг 5 — зафиксировать результат (4 исхода)

| Исход | Значение | Дальше |
|---|---|---|
| **A. Роут открылся** | TUI plugin подтверждён, хост компилирует `@opentui/solid` JSX | Писать полноценный `render` (проекты + READY/BLOCKED из `http://127.0.0.1:8123/`) |
| **B. Ошибка импорта `@opentui/solid`** | Хост не резолвит пакет из файла-плагина → нужен другой import-path (автокомплит/доки) | Уточнить правильный `jsxImportSource` |
| **C. Ошибка `<box>/<text>` неизвестны** | Роут-механизм жив, примитивы другие | Заменить на реальные имена компонентов |
| **D. Плагин молча не загрузился** | Проверить лог TUI (`m-code-data/mcode/log/`) на `plugin`/`tui` ошибки | Смотреть `api.plugins.list()` в статусе |

## Шаг 6 — после подтверждения (A)

Расширить `render` до реального Pip-Boy:
- читать `GET http://127.0.0.1:8123/generated/snapshot.json` (fetch из TUI-процесса);
- рисовать список проектов, READY/BLOCKED, клик → inspector;
- `api.keymap` + slash `/pipboy` → `api.route.navigate("pipboy")`.

## Rollback

Удалить `plugin`-ключ из `opencode.json` и файл `pipboy-tui/`. Ничего в
canonical-данных не трогается.
