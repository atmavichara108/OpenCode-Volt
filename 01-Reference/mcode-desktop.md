---
type: Reference
title: M Code Desktop
description: Десктоп-форк OpenCode — новые органы движка, отличия от TUI, статус миграции. Проверено изнутри сессии 2026-09-05.
tags: [reference, opencode, mcode, desktop]
timestamp: 2026-09-05
---

# M Code Desktop

> Десктоп-приложение (Electron), форк OpenCode. Ниже — факты, проверенные изнутри
> сессии в волте 2026-09-05. Неподтверждённое помечено `[проверить]`.

## Идентификация
- Бинарь: `~/Applications/mcode/mcode-desktop-linux-x86_64.AppImage`; в PATH `mcode` нет.
  OpenCode TUI 1.18.5 остаётся в `/usr/bin/opencode` — сосуществуют.
- Updater: `owner: anomalyco, repo: opencode, channel: latest` → форк OpenCode
  [проверить: точка расхождения с апстримом, номер версии].
- Логи сессии: `<repo>/.mcode/logs/YYYYMMDDTHHMMSS.log` (main/renderer);
  persistence-файлы `opencode.*.dat` — legacy-имена, преемственность подтверждена.
- Провайдер сессии по умолчанию: `opencode-go/*` — та же подписка, что и в OpenCode
  (в этой сессии `opencode-go/glm-5.3-flash`).

## Конфигурация (миграция глобального слоя завершена)
- Глобальный конфиг: `~/.config/mcode/opencode.jsonc` (legacy-имя канонично).
  Профиль: bash `*`=ask + whitelist read-only + denylist (rm/curl/ssh/docker/systemctl/sudo,
  force-push, git reset/checkout/rebase); `external_directory` — только
  `~/Projects/**` + `~/dotfiles/**`, секреты deny.
- Глобальный kernel агентов перенесён: `~/.config/mcode/agent/` — meta,
  researcher, reviewer, sysop, system-ops, verifier.
- Глобальные команды: bridge, done, dream, flush, loop, spec (`~/.config/mcode/command/`).
- Плагины: `decision-queue-hook.ts`, `decision-queue-helpers.ts`, `session-flush.ts`.
- Проектный legacy `.opencode/` читается как есть: агент librarian, команды и
  skills волта подхвачены без переименования.
- Изменение конфига вступает после рестарта M Code (running sessions держат старый).

## Новые органы (отсутствуют в OpenCode TUI)

### Ring of peers — мульти-сессийная координация
| Орган | Функция |
|-------|---------|
| `peers` | реестр живых сессий проекта: id, state (busy/idle), title, role (orchestrator), holds |
| `peer_role` | claim/list/release ролей: «я беру auth-refactor» — сигнализация без блокировок |
| `peer_message` | письмо соседней сессии (показ сразу или на границе turn); 3 письма/turn |
| `peer_read` | хвост транскрипта соседа — реальная речь, до 50 сообщений |
| `peer_ask` | вопрос с ожиданием ответа (timeout 40–240 с) |
| `session_message` | запись в любую сессию инсталла + relay `on_behalf_of` (кросс-проект через глобального агента) |

Лимиты: 3 письма/turn, 1 wake/мин/сосед, 3 хопа/thread без человека. Письма не
создают задач и не авторизуют ничего — работа живёт в дереве, не в переписке.
Для librarian это прямой канал оркестрации вместо цепочек task/handoff-файлов.

### Субагенты task — fan-out с изоляцией
- Типы: `explore` (быстрый поиск кода), `general`, `verify` (проверка по evidence, не редактирует).
- `worktree: true` — child работает в git-worktree, ветка `mcode/<slug>` переживает сессию;
  незафиксированные правки child умирают.
- `background: true` — fan-out без блокировки turn; `task_status`/`task_cancel` для контроля.
- Отличие от TUI task: worktree-изоляция, фон, специализация типов, лимит времени.

### Детерминированная верификация — verify
- Кэш по `(project, kind, tree-hash)`; kind — иммутабельный версионный id
  (`core.typecheck.v1`). Повтор на неизменённом дереве → мгновенный сохранённый результат.
- Дополняет [[02-Methods/verifier-pattern]]: машиностроимые гейты (typecheck/lint/test)
  не гоняются заново; acceptance-вопросы остаются за verify-subagent.

### Кросс-сессионная память — memory
- `record`/`skip`/`recall`; факт ≤500 символов, верифицируемый, repository-stable.
- Запись не разрушает старое — не влезшее в бюджет остаётся доступно через recall.
- Слой движка поверх файловой 04-Memory/: факты волта остаются в [[04-Memory/facts]],
  memory-стор — для фактов уровня «как работает этот harness» и команд.

### Oracle — второе мнение
- Более сильная модель по break-glass запросу (архитектурный выбор, дорогая ошибка).
- Включается в Settings → Advanced → Oracle. Не рутинная проверка.

### Медиа-канал
- `ask_image` — допросить изображение (из чата, с диска или папкой до 8 файлов).
- `download` — файл с сети на диск; `send_media`/`send_file` — показать/передать
  файл пользователю прямо в чат.
- В TUI выдача файлов была текстом-путём; здесь артефакт = сообщение.

### Прочее
- `question` — структурированный вопрос пользователю с опциями и timeout.
- `todowrite`/`todoread` — план со стабильными id, owner-линк на subagent.
- `skill` — skill-система с критериями применения; slash-команды (`/review`) открыты агенту.
- bash: `background: true` (дев-серверы/билды без блокировки), env per-call, timeout.
- Manual work mode: оператор подтверждает каждое действие; пауза ≠ отказ [проверить: список режимов].

## Librarian в M Code
- `.opencode/agent/librarian.md` виден как агент (primary), но эта сессия стартовала
  с дефолтной моделью `opencode-go/glm-5.3-flash` и без авто-применения
  model/temperature/permission-профиля из librarian.md — роль «активируется»
  чтением файла + следованием протоколу [проверить: переключение агентов через UI].
- `Tab`/`switch_agent` — механика TUI; в M Code переключение через UI приложения.

## Что это меняет для workflows волта
1. **[[.opencode/command/audit]] → параллельный fan-out:** `task(explore)` по проектам
   вместо последовательного git pull-обхода.
2. **verifier-pattern:** машиностроимые гейты — `verify` с кэшем; acceptance — verify-subagent по diff.
3. **Orchestration protocol:** `peer_role` claims вместо переговоров; контроль хопов встроен.
4. **Decision queue:** permission-события M Code — сверить `permission.ask` payload с
   плагином T-132 [проверить].
5. **session-flush плагин:** проверить событие session.idle в рантайме M Code [проверить].
