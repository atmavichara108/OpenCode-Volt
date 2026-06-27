---
type: Reference
title: OpenCode — Команды
description: Определение команд (opencode.json / .opencode/command/), фронтматтер, плейсхолдеры, встроенные.
tags: [opencode, commands]
timestamp: 2026-06-27
---
# OpenCode: Команды

> Выжимка из opencode.ai/docs/commands. Проверено: 2026-06-26.

## Где определять
- Глобально: `~/.config/opencode/command/*.md`
- Проект: `.opencode/command/*.md`
- Или `opencode.json` → блок `command`
- Имя файла = имя команды (`test.md` → `/test`). Вызов: `/имя`.

## Фронтматтер
```
---
description: ...        # ОБЯЗАТЕЛЬНО, показывается в TUI
agent: build|plan|...   # каким агентом исполнять (опц.)
model: provider/model   # переопределить модель (опц.)
subtask: true           # форсить вызов как subagent (не засорять основной контекст)
---
шаблон промпта
```

## Плейсхолдеры в шаблоне
- `$ARGUMENTS` — все аргументы. `/cmd Button` → Button.
- `$1`, `$2`, `$3` — позиционные аргументы.
- !`команда` — подставляет вывод bash в промпт. Напр. !`npm test`, !`git log --oneline -10`.
- `@путь/файл` — подставляет содержимое файла.

## Встроенные
`/init` · `/undo` · `/redo` · `/share` · `/help`. Свои с тем же именем переопределяют встроенные.

## Кастомные команды волта
| Команда | Агент | Назначение |
|---------|-------|-----------|
| `/ask` | librarian | Ответить на вопрос по волту |
| `/capture` | librarian | Оформить инбокс в методы/карточки |
| `/project` | librarian | Сводка по проекту |
| [`/commit`](/.opencode/command/commit.md) | librarian | Закоммитить изменения в волте (subtask) |
