---
type: project
repo: /home/rudra/Projects/OpenCode-Vault
kind: справочник
stack: markdown + OpenCode
---
# vault (этот волт)

Дашборд-справочник по OpenCode и проектам. Сам является OpenCode-проектом.

**Запуск:** `opencode` в папке волта.
**Агент:** librarian (primary) — читает и ведёт знания, наружу НЕ ходит (external_directory: deny).

## Структура
00-INDEX (дашборд) · 01-Reference (OpenCode) · 02-Methods (приёмы) · 03-Projects (карточки) · 99-Inbox

## Агент (.opencode/agent/)
| Агент | Назначение |
|-------|-----------|
| librarian | ответы по волту, ведение заметок, разгребание инбокса |

## Команды (.opencode/command/)
/ask · /capture · /project

## Состояние
- [x] структура
- [x] librarian + команды
- [x] Reference наполнен
- [x] карточки SERPlux, dv-hub
- [ ] методы (closed-loop, verifier, memory) — наполнить
- [ ] dotfiles — после создания репо

## Лог изменений
- 2026-06-26: волт заведён и наполнен готовыми данными
