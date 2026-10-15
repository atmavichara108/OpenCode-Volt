---
type: spec
project: vault
status: draft
date: 2026-10-08
kind: task
---
# Execution Spec: email-capture — Email capture для Gmail

Расширение capture-слоя VibeOS по образцу `tools/telegram-capture/`; research-основа: `06-Audits/2026-10-08-email-capture-research.md`.

## Цель

Ручной точечный CLI: читать ВСЕ папки Gmail, искать письма по контрольным фразам, классифицировать по интентам вайбкодинга (исследование / внедрение / коррекция / проекты / подписки) и идемпотентно дописывать интенты в idea-graph (append-only). Данные из писем — вход для вайбкодинга: исследование нового, внедрение, коррекция, прочие интенты касаемо системы/подписок/проектов.

## Границы

Anti-goals:
- НЕ демон (нет watch.py/systemd) — запуск человеком, точечно.
- НЕ реакции на письма (как в Telegram) — статус через папки/метки Gmail и служебный state-файл.
- НЕ Gmail API в MVP — только IMAP; API — fallback при нужности full-text `q=`-поиска (`from:`, `is:unread`, `label:`).
- НЕ наложение Gmail-меток (требует дополнительных scope/прав).
- НЕ коммиты/пуш из инструмента; пишет только append-only в idea-graph.

## Design-решения

1. **Транспорт — IMAP** (`imaplib`, stdlib, ноль зависимостей): `imap.gmail.com:993` SSL, аутентификация — app password (требует включённой 2FA). Все папки: `LIST` (иерархия, включая `[Gmail]/All Mail` = архив) → `SELECT <folder>` → `SEARCH` → `FETCH` тела → `email`-парсинг (HTML→text).
2. **Идемпотентность** — служебный state-файл (JSONL: processed message ids + digest) в gitignored-каталоге; повторный запуск не возвращает те же письма.
3. **Классификация — контрольные фразы по интентам**: приоритетный каскад (error-шум → интенты → default), матч `re.IGNORECASE` по нормализованной конкатенации `subject + body-text`:
   - research: исследование, research, изучить, сравнить, обзор, тренды, benchmark, state of, landscape
   - implementation: внедрение, реализация, implement, портировать, интеграция, подключить, адаптировать, roadmap, спека, spec
   - correction: коррекция, исправить, отменить, канон-коррекция, уточнить, вердикт, ратифицировать, пересмотреть, correct, revert, amend
   - projects: проект, project, VibeOS, OpenCode, dotfiles, SERPlux, dv-hub, репо, github.com/
   - subscriptions: подписка, subscribe, newsletter, рассылка, digest, weekly, follow, notify
   - error/noise: unsubscribe, спам, реклама, promo, выписка, квитанции, no-reply, notifications@
4. **Синхронизация с idea-graph** — append-only строки в `04-Memory/idea-graph/nodes.jsonl` + `edges.jsonl` (схема по `04-Memory/idea-graph/README.md`). Критические правила (нарушение = FAIL валидатора): тип ребра ТОЛЬКО из taxonomy — для email-intent `announces` (типа `emits` нет); `resolution` только accepted|deferred|implemented (НЕ pending) — нарушение даёт ошибку writer'а (ValueError) до записи, валидатор resolution не проверяет; обязательные поля узла: id, graph, kind, label, status, provenance{source, observed_at (YYYY-MM-DD)}, projection; id продолжает нумерацию `stream-intent-NNN` (следующий свободный — читать конец `nodes.jsonl`, не дублировать существующие); `graph` узла = `stream`; узел-источник уже существует: `world-source-email-gmail`; перед записью и после — `node tools/idea-graph/validate.mjs` должен остаться PASS.

## Структура проекта

```text
tools/email-capture/
├── .envrc + .venv/          (direnv, конвенция волта; deps в venv)
├── .env.example             (IMAP_HOST, IMAP_USER, IMAP_PASS, FOLDERS, PHRASES...)
├── .gitignore               (.env, .state/, .venv/)
├── config.py                (dotenv, дефолты, списки фраз по интентам, CHOICES)
├── capture.py               (CLI: --folder/--all, --limit, --since, --dry-run; JSON на stdout, логи на stderr)
├── classifier.py            (каскад контрольных фраз → intent, нормализация, дедуп)
├── writer.py                (append в idea-graph nodes/edges + вызов валидатора)
├── state.py                 (processed-ids JSONL, flock как в telegram-capture/inbox_queue)
├── tests/                   (pytest: classifier, writer-схема, state, dry-run)
├── pyproject.toml           (deps, pytest config)
└── README.md
```

## Шаги исполнения

### S1. Scaffold + config
`config.py`: `load_dotenv()` (из директории скрипта), env с дефолтами (IMAP_HOST/IMAP_PORT/IMAP_USER/IMAP_PASS, FOLDERS, STATE_PATH, DEFAULT_LIMIT), `INTENT_PHRASES` (интерм → фразы), `INTENT_NAMES` как CHOICES для argparse; `.env.example`, `.gitignore`, `pyproject.toml` (deps: python-dotenv; pytest marker `smoke`), `.envrc`, `tests/`.
Acceptance: `import config` даёт дефолты без `.env`; `.env.example` покрывает все переменные; `pytest --collect-only` находит `tests/`.

### S2. IMAP-клиент + CLI (capture.py)
`imaplib.IMAP4_SSL` → `login` (app password) → `LIST()` всех папок → `SELECT <folder>` → `SEARCH` (ALL / `SINCE <дата>`) → `FETCH` RFC822 → `email`-парсинг, HTML→text. CLI argparse: `--folder` / `--all` (все папки), `--limit` (default из config), `--since` (YYYY-MM-DD), `--dry-run`. JSON на stdout, логи на stderr (`logging.basicConfig(stream=sys.stderr)`); friendly-ошибки — `print(..., file=sys.stderr)` + `sys.exit(1)`.
Acceptance: `--dry-run` печатает JSON писем без записи state и без мутаций ящика; `--all` обходит все папки включая `[Gmail]/All Mail`; пустой результат → `[]`, exit 0.

### S3. classifier.py — каскад контрольных фраз
Нормализация (стрип HTML-тегов/markdown, нижний регистр), конкатенация subject+body, каскад: error/noise → интенты → default. Дедуп по `Message-ID` и по text-signature (первые 200 симв.). Детерминированный `classify(message) -> intent`.
Acceptance: письма каждого интента классифицируются верно; error-фраза (`unsubscribe`) перебивает интент-фразу в том же тексте; дубли — один результат; текст без фраз → default.

### S4. state.py — идемпотентность
JSONL state (processed message ids + digest sha256), append с `flock` (как `tools/telegram-capture/inbox_queue.py`), проверка «обработано» до выдачи. Путь default `.state/processed.jsonl`, переопределяется env, каталог gitignored.
Acceptance: повторный запуск не возвращает те же message ids; state растёт append-only; параллельные вызовы не портят файл (flock).

### S5. writer.py — запись в idea-graph + валидатор
Append в `nodes.jsonl`: `stream-intent-NNN` (graph=stream, kind=intent, status=candidate, provenance{source:"email:gmail", observed_at}, projection), следующий NNN — из хвоста `nodes.jsonl`. Append в `edges.jsonl`: `e-NNNN` (graph=stream, from=новый узел, to=`world-source-email-gmail`, type=`announces`, provenance). Доменные поля: `essence`, `resolution` (accepted|deferred|implemented). Запись атомарна; после записи — `node tools/idea-graph/validate.mjs`, FAIL → стоп с ошибкой.
Acceptance: валидатор PASS после записи; id не дублирует существующие; тип ребра `announces`; `--dry-run` writer'а ничего не пишет.

### S6. tests/ — pytest
Тесты: classifier (каскад, дедуп), writer-схема (поля узла/ребра, валидация), state (append, дедуп, flock), capture dry-run (мок imaplib). Live-прогоны — только под маркером `smoke`.
Acceptance: `pytest` зелёный без сети и credentials; `pytest -m smoke` — по флагу.

### S7. README.md
Установка (venv, `direnv allow`, `.env`), включение IMAP + app password в Gmail (support.google.com/mail/answer/185833, пометка [проверить]), примеры запуска, интенты и фразы, схема записи в idea-graph, безопасность (`.env` gitignored).
Acceptance: по инструкции воспроизводится `pip install -e .` и `python capture.py --help`.

## Acceptance criteria (DoD)

- `python capture.py --all --dry-run` → JSON писем, классифицированных по интентам, без мутаций ящика и без дублей при повторном запуске.
- `python capture.py --all --limit N` дописывает новые интенты в idea-graph; `node tools/idea-graph/validate.mjs` PASS.
- Повторный запуск не возвращает уже записанные письма (state).
- Фразы и пути — в `config.py`/`.env`, не захардкожены в логике.
- `.env` и state-каталог gitignored; credentials не попадают в репозиторий.
- Инструмент ручной: нет демонов, таймеров, наложения меток Gmail.

## Открытые вопросы

1. **App password: как включить** — шаги требуют подтверждения [проверить] (doc support.google.com/mail/answer/185833 не был fetched на момент research 2026-10-08). Без 2FA — fallback OAuth + Gmail API (вне MVP).
2. **Расширение фраз** — список минимальный; расширяется по результатам живых прогонов (канон фраз живёт в `config.py`).
