---
type: project
repo: /home/rudra/Projects/ChaT
spec-home: /home/rudra/Projects/ChaT/docs/specs/
kind: knowledge-operations
stack: Markdown / Obsidian / OpenCode
description: Новая территория, документируемая через интервью и knowledge-operations; старый ChaT/Notion учитывается только как legacy-источник концепций.
---
# ChaT

> Новая территория и её контекст собираются через интервью. Старый ChaT/Notion — legacy-референс, не модель текущего проекта.
> Профиль пользователя: [[user-profile-contract]]. ChaT — first-class consumer: читает минимальный scoped context для интервью, решений и операций, а durable user-level изменения предлагает через global `profile-governor`. Каноническая запись только после явного approval; факты и provenance остаются в регистрах ChaT, без второй копии профиля и без auto-sync.

**Статус:** planning

## Profile integration

- **Read:** scoped profile context для интервью, контекста стартапа, приоритетов, рабочих предпочтений и operational constraints текущей задачи.
- **Write:** ChaT может сформировать proposal с полем, значением, reason, source/register, timestamp и confidence; canonical write выполняет только `profile-governor` после явного подтверждения пользователя.
- **Provenance:** проектные facts/hypotheses/decisions/participants остаются в регистрах ChaT; в профиль попадает только явно promoted user-level fact с ссылкой на источник.
- **Boundaries:** minimum necessary scope, no secrets, no silent sync, no duplicate canonical profile.

Полноценная интеграция ChaT является текущим приоритетом profile-governor; hooks/events и конкретный adapter остаются planned, а не заявляются внедрёнными.

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
- [[/home/rudra/Projects/ChaT/.mcode/agents/curator|Curator]]
- [[/home/rudra/Projects/ChaT/legacy/notion-reference|Legacy: Notion-референс]]

## Агенты (`.mcode/agents/`)

> **Миграция 2026-10 (B21):** агенты/команды/плагины переехали из `.opencode/`
> в `.mcode/`. Каталог `.mcode/` **не отслеживается git** (0 файлов в
> `git ls-files`) — объекты существуют только на диске локально.
> Evidence: [[06-Audits/2026-10-07-external-repos-pass-draft]], §B21 в
> [[06-Audits/2026-10-06-pae-evolution-roadmap-draft]], [[04-Memory/facts]].

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| curator | primary | opencode-go/gpt-5.6-luna | Координация знаний, интервью, решения и memory flush |
| development-manager | subagent | opencode-go/gpt-5.6-luna | Приоритеты, зависимости и delivery |
| tea-master | subagent | opencode-go/gpt-5.6-luna | Технология чая и качество партий |
| chat-reviewer | subagent | opencode-go/deepseek-v4-flash | Read-only проверка согласованности |
| community-architect | subagent | opencode-go/deepseek-v4-flash | Сообщество, обучение и гостеприимство |
| product-market | subagent | opencode-go/deepseek-v4-flash | Продуктовые и рыночные гипотезы |
| tea-scientist | subagent | opencode-go/deepseek-v4-flash | Проверяемые чайные эксперименты |
| velisov-steward | subagent | opencode-go/deepseek-v4-flash | Операции и вопросы Велисова Ковчега |
| regeneration-designer | subagent | opencode-go/deepseek-v4-flash | Регенеративные инициативы и устойчивость |

Статус расхождения карточка↔диск: **переоткрыто 2026-10-29** — на диске те же
9 агентов, но **`chat-librarian.md` не существует** (ни в `.mcode/`, ни в
`.opencode/`): primary — **`curator`** (слово владельца 2026-10-29, basis:
quoted: «чей primary на самом деле: curator»). Прежнее «закрыто 2026-10-07»
считалось по числу 9, состав разошёлся. Замена `curator → chat-librarian` не
выполнена и не требуется.

## Команды (`.mcode/command/` — 9)
develop · experiment · flush · interview · map · review · science · site · tea

## Наблюдение за git (сверка 2026-10-29)
- ветка `task/git-freed-b11`, последний коммит `da499c2` (07.10 23:27);
- миграция агентского слоя в `.mcode/` **не завершена**: в рабочем дереве
  deletions по `.opencode/agents/*.md`, git ещё отслеживает `.opencode/agents/`,
  `.mcode/` в git не входит (0 файлов).

## Плагины
Плагинов в ChaT нет (`.mcode/` не содержит каталога plugin/plugins).

## Конфиг
Собственного `opencode.json` нет. Используется глобальный stow-конфиг с fallback `opencode-go/gpt-5.6-luna`; role-specific overrides заданы в agent frontmatter.

## Временная модельная политика
До capability-routing: primary/сложные роли используют `opencode-go/gpt-5.6-luna`, а дешёвые read-only/review/research роли — `opencode-go/deepseek-v4-flash`.

## Состояние методов
Методы проекта минимальны и ещё не оценивались отдельно.

## Лог изменений
- 2026-08-14: bootstrap ChaT и синхронизация карточки проекта в vault.
- 2026-08-17: roster синхронизирован с bootstrap-структурой; зафиксирована временная модельная политика до capability-routing.
- 2026-10-29: сверка карточки↔репо (Служитель, по поручению владельца): фантом `chat-librarian` убран — primary подтверждён `curator` (слово владельца); расхождение переоткрыто; команды перечислены (9); миграция в `.mcode/` зафиксирована как незавершённая; добавлено наблюдение за git.
