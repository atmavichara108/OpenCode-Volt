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
- `config.py` — конфигурация (env, темы, карта эмодзи).

## Безопасность

`.env` (credentials) и `*.session` (авторизационная сессия) внесены в
`.gitignore` репозитория. **Не коммитить.**

## Связь

- Метод: [[02-Methods/tool-integration-pattern]]
- Направление: R-006 Linux UX Lab
- Команда: `/capture`
- Потребитель: [[99-Inbox]]