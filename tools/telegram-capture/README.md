# tools/telegram-capture — извлечение постов из Telegram

Скрипт-инструмент VibeOS. Реализация [[02-Methods/tool-integration-pattern]].
Извлекает посты из группы `@inbox_tools` по теме, фильтрует уже обработанные
(по реакциям), возвращает JSON для анализа librarian.

«LLM думает, API делает»: Telethon детерминированно тянет посты через MTProto,
librarian только классифицирует и решает, куда записать.

## Архитектура

```
[Telegram @inbox_tools, topics]
       ↓ (capture.py)
[Telethon → MTProto → посты по теме]
       ↓ (фильтр: пропускаем 👍/🤔/категории)
[JSON: message_id, text, date, link, media]
       ↓ (mark.py: 👍 на каждый извлечённый)
[librarian анализирует → 99-Inbox / карточки]
```

## Установка

Проект использует direnv + .venv (активируется автоматически при входе в корень волта).

Первичная настройка (один раз):
```bash
cd /home/rudra/Projects/OpenCode-Vault
python -m venv .venv
cp tools/telegram-capture/.env.example tools/telegram-capture/.env  # заполнить credentials
direnv allow
pip install telethon python-dotenv pytest
```

## Настройка

1. Скопировать `.env.example` → `.env`.
2. Заполнить `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` с https://my.telegram.org
   (раздел API development tools).
3. При необходимости поправить `TELEGRAM_CHAT_USERNAME` (по умолчанию `inbox_tools`)
   и `TELEGRAM_SESSION_NAME` (по умолчанию `vibeos_capture`).

## Первый запуск

```bash
python capture.py --topic Софт --limit 10
```

При первом запуске Telethon интерактивно спросит телефон и код подтверждения
(один раз), после чего создаст файл `<session_name>.session` рядом со скриптом.
Последующие запуски используют сохранённую сессию.

## Proxy (обход блокировки)

Если Telegram заблокирован провайдером, используйте SOCKS5 proxy (например, Tor):
- Установите и запустите Tor (порт 9050 по умолчанию)
- В `.env`: `TELEGRAM_PROXY_HOST=127.0.0.1`, `TELEGRAM_PROXY_PORT=9050`
- Если `TELEGRAM_PROXY_HOST` пустой — proxy не используется (прямое соединение)

## Логика фильтра

Посты с любой реакцией из `PROCESSED_REACTIONS` (👍, 🤔, 👨‍💻, 🔥, 🤝, 🏆, 🎉)
считаются уже обработанными и **пропускаются**. Берём только непомеченные.
После извлечения (если не `--dry-run`) на каждый пост ставится реакция 👍,
чтобы при следующем запуске не выдать их повторно.

Категорийные реакции (👨‍💻 dotfiles, 🔥 SERPlux, 🤝 dv-hub, 🏆 VibeOS, 🎉 новый
проект) ставит librarian через `mark.py` после классификации — они заменяют
промежуточную 👍.

## Скрипты

- `capture.py` — извлечение непомеченных постов по теме → JSON на stdout.
- `mark.py` — простановка категорийной реакции на список message_id.
- `classify.py` — классификатор (детерминированные правила + `classify_batch()`).
- `pipeline.py` — intake-контур: flatten → classify → relevance → project mapping → upgrade path → signals-артефакт (read-only, deterministic).
- `inbox_queue.py` — staging-очередь постов (JSONL + flock): append (дедуп по message_id) / remove (атомарно).
- `watch.py` — userbot-демон: NewMessage → append в очередь в real-time (smoke-gated).
- `config.py` — конфигурация (env, темы, карта эмодзи).

## Pipeline (intake → signals)

`pipeline.py` превращает сырые посты `captures_all.json` в `signals.json` —
артефакт, который читает карта экосистемы (tools/ecosystem-map) для отображения
кандидатов апгрейда по проектам.

```bash
python pipeline.py --input captures_all.json --output signals.json
python pipeline.py --input captures_all.json --dry-run   # печать, без записи
```

Фазы: классификация (`classify_batch`) → relevance scoring (0..10) → маппинг
категория→проект (dotfiles/SERPlux/dv-hub/vault/new) → upgrade path → сортировка
сигналов. `error`-категория сигнала не даёт. Артефакт несёт `input_digest`
(sha256 канонического JSON) — одинаковый вход даёт идентичный выход.

Гарантии pipeline: read-only (пишет только собственный output), no network,
no commits, мутация входов отсутствует.

## Живой слив (не накапливать группу)

Чтобы `@inbox_tools` не копила непомеченные посты, есть слои real-time и pull.
Оба пишут в staging-очередь `inbox-queue.jsonl`, откуда пост классифицируется,
помечается реакцией и удаляется за один цикл.

### Демон (real-time)

```bash
python watch.py --smoke          # слушать NewMessage и сливать в очередь
python watch.py --smoke --once   # один pull + выход
```

`watch.py` подписывается на `events.NewMessage(chats="@inbox_tools")`, каждый
непомеченный пост сериализует через `post_data()` (с `topic`) и дописывает в
очередь. Работает постоянно — под `systemd --user`, держит Tor/сессию.

### Таймер (pull, fallback)

Каждые N минут `capture.py` уже идемпотентен (ставит 👍, повторно не дёргает).
Связка для отставания: `capture.py --topic <T>` → `inbox_queue.append` →
`pipeline.py --input inbox-queue.jsonl`.

```bash
python inbox_queue.py count
python inbox_queue.py ls --limit 10
cat posts.json | python inbox_queue.py append
python inbox_queue.py remove --ids 100 101
```

`CAPTURE_QUEUE` (env) переопределяет путь очереди (для тестов/отдельных потоков).

## Безопасность

`.env` (credentials) и `*.session` (авторизационная сессия) внесены в
`.gitignore` репозитория. **Не коммитить.**

## Связь

- Метод: [[02-Methods/tool-integration-pattern]]
- Направление: R-006 Linux UX Lab
- Команда: `/capture`
- Потребитель: [[99-Inbox]]
- Пайплайн → signals: tools/ecosystem-map (панель CAPTURE / intake-сигналы)
- Живой слив: watch.py (демон) + inbox_queue.py (очередь) + systemd timer (fallback)