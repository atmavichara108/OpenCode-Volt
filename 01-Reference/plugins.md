---
type: Reference
title: OpenCode — Плагины
description: Plugin SDK (@opencode-ai/plugin), lifecycle-хуки, реестр плагинов проектов.
tags: [opencode, plugins]
timestamp: 2026-07-03
---
# OpenCode: Плагины

> Выжимка из opencode.ai/docs/plugins. Проверено: 2026-06-29.

## Что это
Плагины расширяют OpenCode через хуки на события. Бывают:
- **Локальные** — `.js`/`.ts` файлы в `.opencode/plugins/` (проект) или `~/.config/opencode/plugins/` (глобально)
- **npm-пакеты** — указываются в `opencode.json` → `plugin: ["package-name"]`

Установка: npm-плагины ставятся автоматически через Bun при старте. Локальные — подгружаются напрямую.

Порядок загрузки: глобальный config → проектный config → глобальные plugins/ → проектные plugins/.

## Plugin SDK (@opencode-ai/plugin)

[проверить] Установлен в волте (`.opencode/package.json`) и в проектах.

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // хуки
  }
}
```

**Контекст плагина:**
- `project` — информация о проекте
- `directory` — текущая директория
- `worktree` — git worktree path
- `client` — SDK-клиент для взаимодействия с AI
- `$` — Bun shell API для выполнения команд

**Типы:** для TypeScript — `import type { Plugin } from "@opencode-ai/plugin"`

## Доступные хуки (events)

### Команды
- `command.executed`

### Файлы
- `file.edited` · `file.watcher.updated`

### LSP
- `lsp.client.diagnostics` · `lsp.updated`

### Сессия
- `session.created` · `session.compacted` · `session.deleted` · `session.diff`
- `session.error` · `session.idle` · `session.status` · `session.updated`

### Инструменты (ключевое!)
- `tool.execute.before` — перед выполнением инструмента (можно прервать)
- `tool.execute.after` — после выполнения

### Shell
- `shell.env` — внедрение переменных окружения

### Установка
- `installation.updated`

### Сообщения
- `message.*` — создание/удаление/обновление сообщений в сессии

### Разрешения
- `permission.asked` · `permission.replied`

### TUI
- `tui.prompt.append` · `tui.command.execute` · `tui.toast.show`

### Компакция (экспериментальное)
- `experimental.session.compacting` — кастомизация промпта компакции

## Кастомные инструменты из плагинов

Плагин может добавлять свои инструменты:

```typescript
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "Мой инструмент",
        args: {
          foo: tool.schema.string(),
        },
        async execute(args, context) {
          return `Hello ${args.foo}`
        },
      }),
    },
  }
}
```

Если имя инструмента совпадает со встроенным — плагин переопределяет его.

## Плагины в моих проектах

| Плагин | Где | Назначение |
|--------|-----|-----------|
| env-guard | SERPlux (.js), dv-hub (.ts) | блокирует доступ агента к .env / секретам (`tool.execute.before`) |
| commit-guard | SERPlux (.js) | перехватывает `git commit` через `tool.execute.before`, запускает pytest (вывод захвачен через `.quiet()`), блокирует если FAIL. В TUI — только итог: "✅ N tests passed" или "❌ FAILED" |
| notify | SERPlux (.js), dv-hub (.ts) | уведомления (звук/сообщение) о событиях (`session.*`) |
| compaction | dv-hub (.ts) | управление сжатием длинного контекста (`experimental.session.compacting`) |
| session-flush | глобальный (.ts) | копит `file.edited`, при `session.idle` дописывает в `04-Memory/session-log/YYYY-MM-DD.md`. Детерминированный, агентов не вызывает |

## Заметки
- В SERPlux плагины на `.js`, в dv-hub на `.ts` — стоит унифицировать [проверить какой формат предпочтительнее].
- Содержимое самих плагинов в волт не копируем — живёт в репо. Здесь только реестр.
- Для npm-зависимостей в локальных плагинах нужен `package.json` в `.opencode/` с `dependencies`.
- Логирование: `client.app.log({ body: { service, level, message } })` вместо `console.log`.
