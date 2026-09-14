---
type: Research Note
title: TUI plugin /pipboy — подтверждённый API + блокер сборки
status: blocked-pending-smoke-test
date: 2026-09-15
owner: rudra
related: "[[06-Specs/Vault/pipboy-v8-rethink]]"
tags: [spec, vault, pipboy, tui, plugin]
---

# TUI plugin `/pipboy` — разведка API (2026-09-15)

## Вывод

Native TUI route `/pipboy` в OpenCode/M-Code **подтверждён как возможный** —
API реально присутствует в установленном SDK — но собрать/проверить плагин из
этого репозитория сейчас **нельзя**: JSX-поверхность рендера хост-приватна.

## Что подтверждено (installed `@opencode-ai/plugin@1.18.5`, `dist/tui.d.ts`)

`TuiPluginModule = { id?, tui: TuiPlugin }` — плагин экспортирует `tui`.

`TuiPlugin = (api, options, meta) => Promise<void>`, где `api`:
- `route.register([{ name, render }])` + `route.navigate(name, params)` — **кастомные TUI routes**
- `route.current` — текущий route (`home` | `session` | произвольный)
- `ui.Slot`, `ui.Dialog`, `ui.DialogAlert`, `ui.DialogConfirm`, `ui.DialogPrompt`,
  `ui.DialogSelect`, `ui.Prompt`, `ui.toast`, `ui.dialog`
- `keymap` (registerLayer/dispatchCommand), `mode` (push/pop mode)
- `kv` (persistent KV), `state` (session/mcp/lsp/vcs/part)
- `client` (OpencodeClient), `event` (EventBus), `renderer` (CliRenderer)
- `slots.register`, `plugins`, `lifecycle`, `theme`, `attention`

## Блокер

- `route.render` возвращает `JSX.Element` из **`@opentui/solid`** (`SolidPlugin`).
- `@opentui/core`, `@opentui/solid`, `@opentui/keymap` **не в `.opencode/node_modules`**
  — их инжектит TUI-хост на рантайме, поверхность компонентов (Box/Text/…) из репо не видна.
- Следствие: TUI-плагин нельзя typecheck/собрать/проверить отсюда; нужен controlled
  smoke-test **внутри живого TUI** (как и заявлено в spec §9).

## Путь вперёд (когда TUI доступен)

1. Минимальный `.tsx` плагин, экспорт `tui`, `api.route.register([{ name: "pipboy", render }])`.
2. Render читает состояние через уже готовый backend (`GET http://127.0.0.1:8123/…` или
   `api.client`) и рисует проекты + READY/BLOCKED.
3. `api.keymap` добавляет slash-команду `/pipboy` → `route.navigate("pipboy")`.
4. Зарегистрировать в `opencode.json` (`plugin` → путь к файлу) и проверить вживую.

## Рабочая альтернатива уже сейчас

Pip-Boy уже открывается из TUI/GUI одним действием: `pipboy.py open` (rofi-хоткей
`pipboy-rofi open`). Это тот же URL `http://127.0.0.1:8123/`, что и будущий TUI-route.
