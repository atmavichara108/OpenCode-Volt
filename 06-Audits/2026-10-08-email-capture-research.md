---
type: research
title: Email capture — research-основа
date: 2026-10-08
status: draft
---
# Email capture — research-основа (2026-10-08)

## 1. Паттерн telegram-capture

**Структура** (`tools/telegram-capture/`): `capture.py` (извлечение), `mark.py` (категорийная реакция), `classify.py` (детерминированный классификатор), `config.py` (конфиг), `pipeline.py` (intake→signals), `inbox_queue.py` (JSONL+flock очередь), `watch.py` (демон), `.env.example`, `pyproject.toml` (deps: telethon, python-dotenv; pytest marker `smoke`).

**Reusable-паттерны для email-версии:**
- **config.py**: `python-dotenv` (`load_dotenv()` — загрузка `.env` из директории скрипта, не cwd), env-переменные с дефолтами, `CHOICES`-списки (`TOPIC_NAMES`), карта `EMOJI_MAP` категорий, `PROCESSED_REACTIONS = set(EMOJI_MAP.values())`, `DEFAULT_LIMIT`.
- **CLI** (`capture.py`): argparse с `--topic` (required, choices), `--limit` (default из config), `--dry-run` (store_true), `--all`; JSON на stdout, логи на stderr (`logging.basicConfig(stream=sys.stderr)`); friendly-ошибки через `print(..., file=sys.stderr)` + `sys.exit(1)`; fetch с запасом 3x, фильтр обработанных, slice `[:limit]`.
- **Идемпотентность**: после извлечения сразу «помечает» (📥), чтобы повторный запуск не возвращал то же; FloodWait обрабатывается с остановкой/паузой.
- **mark.py**: `--message-ids` (nargs="+"), `--category` (choices EMOJI_MAP); итог в stdout «помечено: X/Y».
- **classify.py**: приоритетный каскад правил (error → CORE → topic-override → new → GENERIC → dotfiles → serplux → topic-default → final); нормализация (`normalize` убирает футер `=====`, markdown-разметка для `\b`); извлечение title/repo/lang; дедуп по repo и по text-signature (первые 200 симв.).
- **pipeline.py**: чистый детерминированный переход вход→выход с `input_digest` (sha256), read-only гарантии.
- **Безопасность**: `.env` и `*.session` в `.gitignore`; `.env.example` обязателен.

**Не копировать слепо**: в Gmail нет «реакций» — аналог «обработано» = собственный state-файл (messageId → processed) или Gmail label; Telegram-топики заменяются на labels/папки Gmail.

## 2. Gmail API vs IMAP

**Рекомендация для ручного CLI-инструмента: IMAP (imaplib + XOAUTH2/app-password).** Обоснование:
- Gmail API требует Google Cloud project + OAuth consent screen + OAuth 2.0 Client ID (Desktop), `credentials.json`; первый запуск — `InstalledAppFlow.run_local_server(port=0)` (локальный веб-сервер + браузер), refresh в `token.json`. Это тяжёлый онбординг для точечного ручного инструмента.
- scopes: для чтения нужен `gmail.readonly` (restricted scope), `gmail.metadata` тоже restricted. Для публичного приложения — верификация; для личного — режим «Testing» с test-пользователями. IMAP: включить IMAP в настройках Gmail + app password (для аккаунтов с 2FA) — проще на порядок.
- IMAP умеет все папки/метки (`LIST`/`SELECT` по иерархии, включая `[Gmail]/All Mail` = архив), поиск `SEARCH SUBJECT/body`.
- Компромисс: если нужен именно `q=`-поиск Gmail (full-text, операторы `from:`, `is:unread`, `label:`) — тогда Gmail API (`users.messages.list`).

**Gmail API — факты** (developers.google.com/gmail/api):
- Аутентификация: `InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)` → `flow.run_local_server(port=0)`; затем `Credentials.from_authorized_user_file("token.json")` + refresh. Deps: `google-api-python-client google-auth-httplib2 google-auth-oauthlib`. Prerequisite: Google Cloud project с включённым Gmail API.
- Чтение: `users.messages.list(userId="me", maxResults, pageToken, q, labelIds[], includeSpamTrash)` → только `{id, threadId}[]` + `nextPageToken`; детали — `users.messages.get` (snippet/payload). maxResults default 100, max 500. Все папки: `users.labels.list` (системные: INBOX, TRASH, SPAM, IMPORTANT; `[Gmail]/All Mail` = весь архив).
- Квоты (новые проекты от 2026-05-01): 1,200,000 units/мин/проект; 6,000 units/мин/юзер/проект; 80,000,000 units/день/проект; per-method единицы — gap. Ошибки квот — exponential backoff.
- IMAP (developers.google.com/gmail/imap/imap-smtp): `imap.gmail.com:993` SSL, SASL XOAUTH2; сессия ~24h (при OAuth — срок токена ~1h).

## 3. Контрольные фразы

**Схема матчинга**: матчить конкатенацию `subject + " " + snippet` (Gmail API) или fetched body (IMAP); каскад приоритетов: 1) error/нелевое → 2) интенты (выше приоритет) → 3) темы/категории → 4) default. Матч `re.IGNORECASE`, предварительная нормализация (стрип markdown/HTML-тегов, нижний регистр). Дедуп по `Message-ID`/`threadId`.

**Фразы по интентам (RU/EN):**
- **исследование/research**: «исследование», «research», «изучить», «сравнить», «обзор», «тренды», «benchmark», «state of», «landscape»
- **внедрение/implementation**: «внедрение», «реализация», «implement», «портировать», «интеграция», «подключить», «адаптировать», «roadmap», «спека», «spec»
- **коррекция/correction**: «коррекция», «исправить», «отменить», «канон-коррекция», «уточнить», «вердикт», «ратифицировать», «пересмотреть», «correct», «revert», «amend»
- **проекты/projects**: «проект», «project», «VibeOS», «OpenCode», «dotfiles», «SERPlux», «dv-hub», «репо», «github.com/»
- **подписки/subscriptions**: «подписка», «subscribe», «newsletter», «рассылка», «digest», «weekly», «follow», «notify»
- **error/нелевое**: «unsubscribe», «спам», «реклама», «promo», «выписка», квитанции, «no-reply», «notifications@»

## 4. Запись в idea-graph

**Обязательные поля узла** (README S2 + validate.mjs:104): `id` (формат `<graph>-<kind>-<slug>`), `graph` ∈ {world,organ,mech,tech,proto,event,quest,stream}, `kind`, `label` , `status` ∈ {raw,candidate,accepted,implemented}, `provenance` (обязательно `source` + `observed_at` YYYY-MM-DD; опц. `scope`, `basis` ∈ quoted|derived|unknown), `projection` (list). Доменные поля: `essence`, `resolution` (spec S11: accepted|deferred|implemented), `emitted`.

**Ребро** (validate.mjs:128): `id`, `graph` (должен совпадать с graph узла `from`), `from`, `to` (без dangling), `type` ∈ taxonomy (belongs_to, contains, depends_on, refines, generalizes, follows_from, prerequisite_for, example_of, contradicts, related, inspires, evolves_into, devours, synthesizes, names, announces, gates), `status`, `provenance`.

**Валидатор** (`tools/idea-graph/validate.mjs`): JSONL парсится; required fields; уникальность id; graph ∈ GRAPHS; status ∈ STATUSES; dangling → error; graph mismatch → error; edge type ∉ taxonomy → error; prod-пороги: ≥90 nodes, ≥120 edges, все 8 графов, `related` ≤40%. Sandbox: `node validate.mjs <path>` — без порогов.

**Внешний инструмент пишет append-only**: дописывает строку JSONL; валидатор не различает авторов.

## 5. Риски и открытые вопросы

1. ~~Лайв-дефект: ребро `e-email-capture-main` тип `emits` не в taxonomy~~ — исправлено 2026-10-08 (багфикс: `announces`, `resolution: deferred`).
2. Квоты Gmail API per-method единицы — gap.
3. App-password doc (support.google.com/mail/answer/185833) — не fetched, требуется подтверждение шагов.
4. OAuth vs app password: 2FA → app password; без 2FA → OAuth Cloud project (Testing-режим достаточно для личного пользования).
5. Дедуп/idempotency: собственный state-файл (JSONL `processed_ids`) для read-only CLI.
6. HTML-body: IMAP fetch → RFC822 (email-парсинг, HTML→text); Gmail API snippet — короткий обрезок, полный body — `format=full` + base64.
7. `emitted`/`resolution`/`essence` валидатор не проверяет — дисциплина на code-review.
8. Нумерация: новые записи должны продолжать нумерацию (`stream-intent-NNN`), не дублировать существующие id.
