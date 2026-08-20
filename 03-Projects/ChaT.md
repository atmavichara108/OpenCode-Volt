---
type: project
repo: /home/rudra/Projects/ChaT
kind: knowledge-operations
stack: Markdown / Obsidian / OpenCode
description: Новая территория, документируемая через интервью и knowledge-operations; старый ChaT/Notion учитывается только как legacy-источник концепций.
---
# ChaT

> Новая территория и её контекст собираются через интервью. Старый ChaT/Notion — legacy-референс, не модель текущего проекта.

**Статус:** planning

## Источники
- [[/home/rudra/Projects/ChaT/README|README]]
- [[/home/rudra/Projects/ChaT/AGENTS|AGENTS]]
- [[/home/rudra/Projects/ChaT/docs/project-map|Карта проекта]]
- [[/home/rudra/Projects/ChaT/docs/active-context|Активный контекст]]
- [[/home/rudra/Projects/ChaT/registers/facts|Реестр фактов]]
- [[/home/rudra/Projects/ChaT/registers/participants|Участники]]
- [[/home/rudra/Projects/ChaT/registers/hypotheses|Гипотезы]]
- [[/home/rudra/Projects/ChaT/registers/decisions|Решения]]
- [[/home/rudra/Projects/ChaT/registers/questions|Вопросы]]
- [[/home/rudra/Projects/ChaT/.opencode/agents/curator|Curator]]
- [[/home/rudra/Projects/ChaT/legacy/notion-reference|Legacy: Notion-референс]]

## Агенты (.opencode/agents/)
| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| chat-librarian | primary | opencode-go/gpt-5.6-luna | Координация знаний, интервью, решения и memory flush |
| development-manager | subagent | opencode-go/gpt-5.6-luna | Приоритеты, зависимости и delivery |
| tea-master | subagent | opencode-go/gpt-5.6-luna | Технология чая и качество партий |
| chat-reviewer | subagent | opencode-go/deepseek-v4-flash | Read-only проверка согласованности |
| community-architect | subagent | opencode-go/deepseek-v4-flash | Сообщество, обучение и гостеприимство |
| product-market | subagent | opencode-go/deepseek-v4-flash | Продуктовые и рыночные гипотезы |
| tea-scientist | subagent | opencode-go/deepseek-v4-flash | Проверяемые чайные эксперименты |
| velisov-steward | subagent | opencode-go/deepseek-v4-flash | Операции и вопросы Велисова Ковчега |
| regeneration-designer | subagent | opencode-go/deepseek-v4-flash | Регенеративные инициативы и устойчивость |

`chat-librarian` заменил `curator` в рамках текущей bootstrap-структуры; существующие новые agent-файлы сохраняются.

## Команды
Команды проекта не добавлены; потребность в них ещё не оценивалась.

## Плагины (.opencode/plugins/)
—

## Конфиг
Собственного `opencode.json` нет. Используется глобальный stow-конфиг с fallback `opencode-go/gpt-5.6-luna`; role-specific overrides заданы в agent frontmatter.

## Временная модельная политика
До capability-routing: primary/сложные роли используют `opencode-go/gpt-5.6-luna`, а дешёвые read-only/review/research роли — `opencode-go/deepseek-v4-flash`.

## Состояние методов
Методы проекта минимальны и ещё не оценивались отдельно.

## Лог изменений
- 2026-08-14: bootstrap ChaT и синхронизация карточки проекта в vault.
- 2026-08-17: roster синхронизирован с bootstrap-структурой; зафиксирована временная модельная политика до capability-routing.
