# OpenCode Vault — Dashboard

> Справочник по OpenCode и моим проектам. Веду по ходу.
> Reference = факты об OpenCode. Methods = мои приёмы. Projects = состояние каждого проекта.

## Быстрый вход
- Спросить базу → `/ask "..."`
- Разгрести инбокс → `/capture`
- Сводка по проекту → `/project <имя>`

## Проекты
| Проект | Тип | Стек | OpenCode-агент особый | Карточка |
|--------|-----|------|----------------------|----------|
| SERPlux | коммерция | Python | collector-dev, reviewer | [[SERPlux]] |
| dv-hub | волонтёрский | TS / Hono | plan, build, reviewer, researcher, infra | [[dv-hub]] |
| dotfiles | система | shell/configs | **sysop** (ходит по системе) | [[dotfiles]] |
| vault | справочник | markdown | librarian | [[vault]] |

## Reference (возможности OpenCode)
[[agents]] · [[commands]] · [[config]] · [[permissions]] · [[plugins]]

## Methods (мои приёмы)
[[closed-loop]] · [[verifier-pattern]] · [[memory-management]]

## Конвенции
- Метод описывается ОДИН раз в `02-Methods/`. Карточки только ссылаются [[wikilink]].
- Карточка = реальное состояние репо (агенты/команды/скрипты/окружение), не копия кода.
- Новое знание → `99-Inbox.md` → оформляется через `/capture`.
- Статусы внедрения: ❌ нет · 🟡 частично · ✅ внедрено
- Неподтверждённые факты по OpenCode помечать `[проверить]`.
- Reference — выжимка, источник правды доки opencode.ai (с датой проверки).
