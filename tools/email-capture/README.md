# email-capture — письма Gmail → интенты вайбкодинга → idea-graph

Ручной точечный CLI: читает папки Gmail по IMAP, ищет письма по контрольным
фразам, классифицирует их по интентам (исследование / внедрение / коррекция /
проекты / подписки) и идемпотентно дописывает новые интенты в append-only
`04-Memory/idea-graph`.

- Спека: `docs/specs/email-capture.md`
- Research-основа: `06-Audits/2026-10-08-email-capture-research.md`
- Эталон паттерна: `tools/telegram-capture/`

**Anti-goals (спека):** не демон и не таймер (запускает человек); не Gmail API
(только IMAP); не наложение Gmail-меток и не реакции на письма; не коммиты —
инструмент пишет только append-only в idea-graph и свой gitignored state.

## Установка

```bash
cd tools/email-capture
python -m venv .venv          # уже сделано в этом каталоге
.venv/bin/pip install -e .    # deps: python-dotenv (+ pytest для тестов)
cp .env.example .env          # и заполнить IMAP_USER / IMAP_PASS
direnv allow                  # optional: активирует .venv при входе в каталог
.venv/bin/python capture.py --help
```

Конвенция волта: `.envrc` содержит `source .venv/bin/activate`, зависимости
живут в `.venv`, глобально ничего не ставится.

## Gmail: включить IMAP и app password [проверить]

Шаги требуют подтверждения: research 2026-10-08 не фетчил страницу поддержки,
поэтому приведённый ниже порядок — рабочая памятка, перепроверь по источнику
<https://support.google.com/mail/answer/185833> [проверить].

1. Включить 2FA (Google Account → Security → 2-Step Verification) — app password
   доступен только при включённой 2FA [проверить].
2. Создать app password (Google Account → Security → App passwords)
   [проверить]: 16 символов, подставляется в `IMAP_PASS` как есть, без пробелов [проверить].
3. В Gmail: Settings → See all settings → Forwarding and POP/IMAP →
   **Enable IMAP** [проверить].
4. Без 2FA fallback — OAuth + Gmail API (вне MVP, см. спеку).

## Примеры запуска

```bash
# посмотреть, что уйдёт в граф (read-only: ни state, ни idea-graph не трогает)
.venv/bin/python capture.py --folder INBOX --dry-run

# все папки, включая [Gmail]/All Mail (архив)
.venv/bin/python capture.py --all --dry-run --limit 20

# рабочий прогон: дописать новые интенты в idea-graph + пометить state
.venv/bin/python capture.py --all --limit 50

# только письма с даты
.venv/bin/python capture.py --folder INBOX --since 2026-10-01 --dry-run
```

Флаги: `--folder` (одна папка, дефолт `FOLDERS` из `.env`), `--all` (все папки
из `LIST`), `--limit N` (общий бюджет на прогон, дефолт `DEFAULT_LIMIT`),
`--since YYYY-MM-DD`, `--dry-run`.

Конвенция вывода: JSON писем/сводка — **stdout**, логи и ошибки — **stderr**
(поэтому `... --dry-run > mails.json` собирается чисто). Пустая выборка → `[]`,
exit 0; ошибка подключения/логина → дружелюбное сообщение в stderr, exit 1.

Поведение обычного (не dry-run) прогона:

1. выборка → дедуп → фильтр state (`state.filter_new`);
2. классификация;
3. интенты из пяти рабочих категорий дописываются в idea-graph;
4. после записи гоняется `node tools/idea-graph/validate.mjs` — **FAIL =
   сообщение об ошибке, без автоотката** (append-only, разбор вручную);
5. все новые письма (включая `error`/`default`) помечаются в state.

## Интенты и контрольные фразы

Канон фраз живёт в `config.py` (`INTENT_PHRASES`), переопределяется env'ом
`PHRASES_<INTENT>` (CSV). Каскад: **error/noise → интенты → default**, матч
`re.IGNORECASE` по нормализованному `subject + body` (снятые HTML/markdown).

| Интент | Фразы (дефолт) |
|---|---|
| `error` (шум, высший приоритет) | unsubscribe, спам, реклама, promo, выписка, квитанци, no-reply, notifications@ |
| `research` | исследование, research, изучить, сравнить, обзор, тренды, benchmark, state of, landscape |
| `implementation` | внедрение, реализация, implement, портировать, интеграция, подключить, адаптировать, roadmap, спека, spec |
| `correction` | коррекция, исправить, отменить, канон-коррекция, уточнить, вердикт, ратифицировать, пересмотреть, correct, revert, amend |
| `projects` | проект, project, VibeOS, OpenCode, dotfiles, SERPlux, dv-hub, репо, github.com/ |
| `subscriptions` | подписка, subscribe, newsletter, рассылка, digest, weekly, follow, notify |
| `default` | ничего не совпало — в граф не пишется |

`error`/`default` в idea-graph не попадают (в stdout при этом видны с полем
`intent`). Дубли снимаются по `Message-ID` и по text-signature (первые 200
символов нормализованного текста).

## Запись в idea-graph

Append-only две строки на интент (схема: `04-Memory/idea-graph/README.md`):

- **узел** `stream-intent-NNN`: `graph=stream`, `kind=intent`, `status=candidate`,
  `provenance{source:"email:gmail", observed_at:"YYYY-MM-DD", scope, basis}`,
  `projection`, доменные поля `essence` и `resolution` ∈
  `accepted|deferred|implemented` (дефолт `deferred`);
- **ребро** `e-NNNN`: `graph=stream`, `from=stream-intent-NNN`,
  `to=world-source-email-gmail` (узел-источник уже существует в графе),
  `type=announces` (тип `emits` вне taxonomy), `status`, `provenance`.

Свободные номера читаются из хвоста `nodes.jsonl` / `edges.jsonl` — существующие
id не дублируются. Запись идёт под flock + fsync. Проверка:

```bash
node tools/idea-graph/validate.mjs     # из корня волта; exit 0 = PASS
```

## Идемпотентность (state)

`STATE_PATH` (дефолт `.state/processed.jsonl`, gitignored) — JSONL строк вида
`{message_id, digest(sha256), processed_at}`. Append под эксклюзивным flock
(по образцу `tools/telegram-capture/inbox_queue.py`), чтение уже
обработанного — внутри лока, поэтому параллельные запуски не задублируют файл.
Повторный запуск одних и тех же писем не возвращает и не переписывает их.

## Тесты

```bash
.venv/bin/python -m pytest tests/ -q     # без сети и credentials
.venv/bin/python -m pytest -m smoke -q   # живой IMAP (нужен заполненный .env)
```

Обычный прогон не ходит в сеть: IMAP замокан, тесты схемы графа пишут только в
sandbox `/tmp/opencode/email-capture-tests/` и валидируют его в sandbox-режиме
валидатора — прод-граф 04-Memory/idea-graph тесты не трогают. Живые тесты
помечены `smoke` и дополнительно skip'аются без `IMAP_USER`/`IMAP_PASS`.

## Безопасность

- `.env` (логин/app password) и `.state/` — в `.gitignore` этого каталога, в
  git не попадают; `.env.example` — только плейсхолдеры.
- Письма читаются через `BODY.PEEK[]` в `SELECT ... readonly` — ящик не мутируется
  (нет ни флага `\Seen`, ни изменений папок).
- Никаких сетевых вызовов кроме IMAP; тесты сети не требуют.

## Открытые вопросы

1. Шаги app password / включения IMAP — требуют подтверждения по источнику
   support.google.com/mail/answer/185833 `[проверить]`; без 2FA — fallback
   OAuth + Gmail API (вне MVP).
2. Список фраз минимальный — расширяется по живым прогонам (канон в `config.py`).
3. При FAIL валидатора state **не** помечается (намеренно: не терять интент),
   но повторный запуск дописал бы те же письма с новыми id — сначала разобрать
   FAIL, потом решать, что со state.
