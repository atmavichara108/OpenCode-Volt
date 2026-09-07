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

**Порт в TUI (2026-09-06):** `tools/verify-cache/verify.py` (stdlib) — tree-hash кэш
детерминированных гейтов волта (пустые `.md` + битые викилинки), `--force`/`--json`,
кэш в `generated/` (gitignored). Резолвер викилинков выровнен с pre-commit hook +
игнор литер в code-span. Гейты зелёные, кэш-хит подтверждён. Команда `/verify`.

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

## Секрет экономии токенов (verified в app.asar, 2026-09-05)

Расход сессии — центы. Причина не одна фича, а стек контекстной гигиены на replay.
В TUI 1.18.5 этих механизмов НЕТ (strings-проверка бинаря: 0 совпадений).

### Replay budget — главное (портится в TUI)
При отправке истории модели **старые tool-результаты пережимаются**:
- `TOOL_OUTPUT_MAX_CHARS = 2000` — каждый старый tool-результат режется до
  2000 символов (head 75% + tail 25%, длинные строки — middle-elision).
  Тул не «врёт»: маркер `[mcode: replay budget — omitted ...]` честно
  показывает, что срезано и как дочитать (resume offset).
- `REPLAY_PROTECTED_CHARS = 40000` — бюджет защиты с конца: последние
  tool-результаты суммарно до 40 KB едут целиком; всё старше 40 KB и >2000
  символов — капится.
- `PRUNED_INPUT_MIN_CHARS = 120` — длинные строки в старых **входах** тулов
  (>120 симв., кроме keep-полей) заменяются на `[N characters cleared...]`.
- Reasoning старых ходов не переигрывается (только подписанный Anthropic
  или текущий turn).
- `IMAGE_BUDGET = 5` — из старых сообщений держится ≤5 картинок.
- `[Old tool result content cleared]` — уже компактированные пары чисто.
- Красacted-входы: секреты вычищаются при replay (`redactWith`).

**Порт в TUI (2026-09-06):** точка инъекции найдена в рантайм-бинаре 1.18.5 —
хук плагина `experimental.chat.messages.transform` диспатчится в main-loop
(`yield*d.trigger("experimental.chat.messages.transform",{},{messages:C})`) прямо
перед `toModelMessagesEffect(C,Z)`, который в TUI шлёт полные выводы. Заслан
плагин `replay-budget.ts` (helpers + smoke 14/14 в волте); live hook-fire после
рестарта TUI `[проверить]`.

### Остальные рычаги
- Compaction: `buffer 20000 / keep 8000 tokens`, summary ≤4096 output tokens.
- Потолки tool_output: read ≤50 KB, bash >2000 строк → полный вывод в файл
  (искать grep'ом, не тащить в контекст).
- Skills лениво: тело грузится только при match; skip — без загрузки.
- verify-кэш по tree-hash — повторный typecheck не ест токены.
- memory-стор — не перечитывать файлы ради фактов; recall вместо этого.
- Doom-loop detector (THRESHOLD/BURST) — убивает зацикливание (главный
  жрец токенов в агентных сессиях).
- Модель: сессия на `opencode-go/glm-5.3-flash` (flash-класс) — цена за
  токен на порядки ниже премиальных; дирижёру хватает.
- peers: «polling is done by reading» — peer_read дешевле wake (wake =
  платный turn).

### Формула экономии
`flash-модель × replay budget 2000/40KB × pruning входов × кэши × doom-loop guard`
— каждый множитель мал, вместе дают центы.

## Второй проход по app.asar — кандидаты на порт (2026-09-05)

### Doom-loop guard (портировать обязательно)
`THRESHOLD = 3, BURST = 9, CAPACITY = 512` (LRU по сессиям). Тот же вызов тула
с **байт-идентичными аргументами** ≥3 раз подряд → turn останавливается
`DoomLoopBurstError` с педагогическим текстом: «перечитай, что вернули ранние
вызовы; повтор тех же аргументов не даст другого ответа». Главный убийца
зацикливаний и жечь токенов.

**Порт в TUI (2026-09-06):** детектор уже нативен в бинаре 1.18.5 (`ya=3`,
byte-identical `JSON.stringify(input)===JSON.stringify(H)`), разница только в
реакции — TUI шлёт `r.ask(permission:"doom_loop")` (вопрос юзеру), не авто-стоп.
Авто-стоп включается конфигом `"doom_loop":"deny"` (permission-ключ,
`"ask"|"allow"|"deny"`). Внесение в canonical jsonc — за Rudra (red-line на правку
`opencode.jsonc`).

### No-op turn guard
`NO_OP_OUTPUT_THRESHOLD = 200, NO_OP_RETRY_LIMIT = 3, NO_OP_NUDGE` — turn,
закончившийся без ответа и без вызова тула (<200 output tokens), не считается
работой: model получает нудж «сделай работу или скажи одной фразой, что
блокирует». Ловит молчаливые сгоревшие ходы.

**Порт в TUI (2026-09-06):** в бинаре 1.18.5 отсутствовал полностью. Написан
плагин `noop-guard.ts` + helpers `noop-guard-helpers.js` (event `session.idle` →
`session.messages` прочитать последний assistant → `session.promptAsync` нудж,
retry limit 3, debounce по messageID). Smoke 9/9. Live hook-fire `[проверить]`
после рестарта TUI.

### Auto-compaction с continuation summary
`DEFAULT_TOKEN_THRESHOLD = 100000` — при переполнении контекст заменяется
continuation-summary («structured, concise, actionable… resume work in a
future context window»); `filterCompacted` реплеит только summary + хвост
(`tail_start_id`), пре-компактные пары → `[Old tool result content cleared]`.
Buffer 20000 / keep 8000 tokens, summary ≤4096 output tokens.

### Secret redaction service
`redactWith(part, PRUNED_INPUT_KEEP)` на **каждом** чтении частей из БД и на
replay. `PRUNED_INPUT_KEEP = {filePath, path, command, pattern, description,
subagent_type, name, url, offset, limit}` — что переживает pruning старых
входов. Секреты не попадают в контекст → нет leak-инцидентов и ретраев.

**Порт в TUI (2026-09-06):** replay-redaction отсутствовала полностью.
Плагин `input-security.ts` (`experimental.chat.messages.transform` → `redactText`,
pattern-based: sk-/ghp-/AKIA/AWS/PRIVATE KEY/bearer; `secrets.expose` в TUI не
настроен). Smoke 14/14.

### Playwright-CLI — полный браузерный тул (обогащает T-134)
Не просто «браузер»: embed CLI с сессиями — open/goto/click/fill/snapshot/eval,
dialog handling, tabs, **storage state** (state-load/state-save = персистентная
логин-сессия), network мок (`route`), console-логи, tracing, video-запись,
PDF. Снапшот → element ref: модель кликает по ref'ам, не по скриншотам
(дешевле, чем vision).

**Порт в TUI (2026-09-06):** `tools/playwright-browser/browser.py` (Playwright 1.62
python, chromium 1234 в ~/.cache/ms-playwright). goto/eval/click/fill/state-save/load,
read-only default, JSON на stdout. Снапшот `aria_snapshot(mode=ai)` даёт `[ref=eN]`;
click/fill по aria-ref (сеется после снапшота на том же page-instance). Живой smoke
PASS (7 подкоманд). Venv-нюанс: под GUI M Code direnv не подхватывает `.venv`
(`sys.executable`→AppImage), запуск через `PYTHONPATH=.venv/lib/python3.14/site-packages`.

### Санитизация ввода (security)
- `SYSTEM_REMINDER_RE` — system-reminder блоки из вставленного текста
  вычленяются и не подделываются как системные.
- `TRANSPORT_MARKUP` — теги `<input>/<output>/<thinking>/<system-reminder>/…`
  из пользовательского текста экранируются → prompt-injection через markup
  затруднён.

**Порт в TUI (2026-09-06):** `SYSTEM_REMINDER_RE` в бинаре 1.18.5 есть, но только
в `extractGoalFromPrompt` (не для санитизации ввода); `TRANSPORT_MARKUP` отсутствует.
Плагин `input-security.ts` (`chat.message` → `sanitizeText`: strip system-reminder
+ escape markup). Smoke 14/14. Live hook-fire `[проверить]`.

### Мелкое, но полезное
- `subagent_depth` — глубина вложенности субагентов (default 1): рекурсивный
  фан-аут ограничен по умолчанию.
- `tokens_cache_read` — per-session учёт кэш-прочтений в БД → честная
  статистика расхода (наш «проверил центы» стал возможен).
- `LARGE_FILE_THRESHOLD = 10 MB` — гард больших файлов.
- `replayElision` маркеры с `resume` — портируя budget, сохранить формат
  маркера: линия резюма позволяет дочитать файл без перечитки.

## Что это меняет для workflows волта
1. **[[.opencode/command/audit]] → параллельный fan-out:** `task(explore)` по проектам
   вместо последовательного git pull-обхода.
2. **verifier-pattern:** машиностроимые гейты — `verify` с кэшем; acceptance — verify-subagent по diff.
3. **Orchestration protocol:** `peer_role` claims вместо переговоров; контроль хопов встроен.
4. **Decision queue:** permission-события M Code — сверить `permission.ask` payload с
   плагином T-132 [проверить].
5. **session-flush плагин:** проверить событие session.idle в рантайме M Code [проверить].
