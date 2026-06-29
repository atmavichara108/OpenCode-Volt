---
type: Reference
title: OpenCode — Права (permissions)
description: Ключи прав, значения (allow/ask/deny), тонкая настройка, skills, doom_loop.
tags: [opencode, permissions]
timestamp: 2026-06-29
---
# OpenCode: Права (permissions)

> Выжимка из opencode.ai/docs/agents#permissions и opencode.ai/docs/skills. Проверено: 2026-06-29.

## Значения
- `"allow"` — без подтверждения
- `"ask"` — спросить перед выполнением
- `"deny"` — запретить инструмент

## Ключи прав
| Ключ                   | Что гейтит                                            |
| ---------------------- | ----------------------------------------------------- |
| read                   | read                                                  |
| edit                   | write, edit, apply_patch                              |
| glob / grep / list     | поиск                                                 |
| bash                   | bash                                                  |
| task                   | вызов subagent через task                             |
| external_directory     | ЛЮБОЙ доступ к файлам вне корня проекта               |
| todowrite              | todo                                                  |
| webfetch / websearch   | сеть                                                  |
| lsp                    | LSP-серверы                                           |
| skill                  | загрузка SKILL.md (режим: allow/deny/ask + glob)      |
| question               | вопрос пользователю                                   |
| doom_loop              | recovery-промпты когда агент зациклился               |

## Тонкая настройка
- `read, edit, glob, grep, list, bash, task, external_directory, lsp, skill` — принимают либо строку, либо объект glob→action.
- Остальные — только строку.
- bash по командам: последнее совпадение побеждает, поэтому `"*"` ставить ПЕРВЫМ, частные правила после.

## Skills (механизм переиспользуемых инструкций)

Skills — SKILL.md-файлы с YAML frontmatter, которые агент может загружать по мере необходимости через встроенный инструмент `skill`.

**Где ищутся:**
- Проект: `.opencode/skills/<name>/SKILL.md`
- Глобально: `~/.config/opencode/skills/<name>/SKILL.md`
- Совместимость с Claude Code: `.claude/skills/<name>/SKILL.md` (если не отключено)

**Формат SKILL.md:**
```yaml
---
name: my-skill          # 1–64 символов, lowercase + дефисы
description: Что делает  # 1–1024 символа
license: MIT            # опционально
compatibility: opencode # опционально
---
Инструкции для агента...
```

**Контроль доступа (permission.skill):**
```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

| Значение | Поведение |
|----------|-----------|
| `allow`  | Скилл загружается сразу |
| `deny`   | Скилл скрыт от агента |
| `ask`    | Запрос подтверждения перед загрузкой |

**Полное отключение:** `tools: { skill: false }` для конкретного агента.
**В волте:** skills не используются (librarian'у хватает прямых инструкций).

## doom_loop — защита от зацикливания

Разрешение на recovery-промпты, которые OpenCode отправляет агенту, когда тот повторяет одни и те же действия (зациклился).

| Значение | Поведение |
|----------|-----------|
| `allow`  | Recovery-промпты работают — агент может получить подсказку для выхода из цикла |
| `deny`   | Recovery отключён — агент может навсегда зависнуть |
| `ask`    | Спрашивать пользователя |

**Важно:** `doom_loop` детектит повторяющиеся tool calls в рамках **одной** сессии. Он НЕ защищает от рекурсивного спавна subagent'ов через `task` — каждый новый subagent получает свежую сессию.
**В волте:** `doom_loop: allow` (librarian).

## Важно для волта
- librarian → `doom_loop: allow`, `external_directory: allow` (только чтение репозиториев).
- sysop (в dotfiles) → `external_directory: allow` + `edit` почти весь deny.
- verifier → `edit: deny`, bash только проверочные команды.
