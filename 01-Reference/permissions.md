# OpenCode: Права (permissions)

> Выжимка из opencode.ai/docs/agents#permissions. Проверено: 2026-06-26.

## Значения
- `"allow"` — без подтверждения
- `"ask"` — спросить перед выполнением
- `"deny"` — запретить инструмент

## Ключи прав
| Ключ                   | Что гейтит                              |
| ---------------------- | --------------------------------------- |
| read                   | read                                    |
| edit                   | write, edit, apply_patch                |
| glob / grep / list     | поиск                                   |
| bash                   | bash                                    |
| task                   | вызов subagent через task               |
| external_directory     | ЛЮБОЙ доступ к файлам вне корня проекта |
| todowrite              | todo                                    |
| webfetch / websearch   | сеть                                    |
| lsp / skill / question | соотв. инструменты                      |
| doom_loop              | recovery-промпты когда агент завис      |

## Тонкая настройка
- `read, edit, glob, grep, list, bash, task, external_directory, lsp, skill` — принимают либо строку, либо объект glob→action.
- Остальные — только строку.
- bash по командам: последнее совпадение побеждает, поэтому `"*"` ставить ПЕРВЫМ, частные правила после.


## Важно для волта
- librarian → `external_directory: deny` (наружу не ходит).
- sysop (в dotfiles) → `external_directory: allow` + `edit` почти весь deny.
- verifier → `edit: deny`, bash только проверочные команды.
