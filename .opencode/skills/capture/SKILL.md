---
name: capture
description: Извлечение постов из Telegram-группы @inbox_tools по теме и их классификация. Использовать когда пользователь просит "достань посты", "вытащи из группы", "покажи что нового в теме X", "заскрапи Telegram", "capture тему Y". Параметры скрапинга (тема, limit, dry-run) определяет пользователь в запросе.
---

# Скилл: Telegram Capture

Извлекает посты из Telegram-группы @inbox_tools (открытая группа Rudra для сбора
идей по софту, подходам, инструментам) и классифицирует их для VibeOS.

Реализация метода [[02-Methods/tool-integration-pattern|tool-integration-pattern]]:
скрипт `tools/telegram-capture/capture.py` (Telethon + Tor SOCKS5 proxy)
детерминированно тянет посты из нужной темы, фильтрует уже помеченные реакцией
(👍/🤔/👨‍💻/🔥/🤝/🏆/🎉) и отдаёт JSON для анализа librarian.

## Когда активируется

Используй этот скилл КОГДА пользователь просит:
- «достань посты из темы X» / «вытащи из группы» / «покажи что нового в теме»
- «заскрапи Telegram» / «capture тему Y»
- «что есть в теме [название]?»
- Любой запрос на извлечение контента из группы @inbox_tools

НЕ используй для: обработки 99-Inbox (это команда `/inbox`), общих вопросов о Telegram.

## Параметры скрапинга (определяет пользователь)

| Параметр | Значение | Default |
|----------|----------|---------|
| `topic` | Название темы группы | (обязательный) |
| `limit` | Сколько постов извлечь | 10 |
| `dry-run` | Только показать, не помечать | false |

### Доступные темы (topics) группы @inbox_tools
- **Приложения** — десктопные приложения
- **Софт** — утилиты, CLI-инструменты
- **Вайб** — подходы к вайбкодингу, AI-инструменты
- **#General** — общее (id=1, special topic)
- **Смарт** — смартфон-связанное
- **Графика** — графические инструменты
- **красота** — эстетика UI/UX
- **сайтостроение** — веб-разработка (старое)
- **Обучалки** — обучающие материалы (старое)
- **ИИ** — AI/ML инструменты
- **Питонизм** — Python-экосистема (очень старое)

## Как запустить

Librarian НЕ может запускать python напрямую (bash ограничен read-only).
Делегируй через task-агента (general):

```bash
cd /home/rudra/Projects/OpenCode-Vault
python tools/telegram-capture/capture.py --topic "<тема>" --limit <N> [--dry-run]
```

direnv автоматически активирует `.venv` (Telethon + python-socks + pytest).
Tor SOCKS5 proxy (127.0.0.1:9050) настроен в `.env` — обход блокировки Telegram.
Авторизация пройдена (vibeos_capture.session) — при повторных запусках код не нужен.

## Что делает скрипт (capture.py)

1. Подключается к Telegram через Tor (SOCKS5 proxy)
2. Находит группу @inbox_tools
3. Получает список тем (GetForumTopicsRequest), находит topic_id по имени
4. Запрашивает сообщения из темы (limit×3 с запасом для фильтра)
5. **Фильтр:** пропускает посты с любой реакцией из PROCESSED_REACTIONS
   (👍 ingested, 🤔 error, 👨‍💻 dotfiles, 🔥 serplux, 🤝 dv-hub, 🏆 vibeos, 🎉 new)
6. Берёт первые `limit` непомеченных
7. Выводит JSON в stdout: `[{message_id, text, date, link, media_type, sender_name}]`
8. Если НЕ dry-run — ставит 👍 на каждый извлечённый (через SendReactionRequest)

## Что делает librarian после получения JSON

1. **Прочитай JSON** (из stdout task-агента)
2. **Проанализируй каждый пост:**
   - Что это? (софт, метод, подход, инструмент)
   - К какому проекту? (SERPlux, dv-hub, dotfiles, VibeOS, новый)
   - Категория для реакции: 👨‍💻 dotfiles / 🔥 serplux / 🤝 dv-hub / 🏆 vibeos / 🎉 new
   - Стоит ли внедрять? (приоритет P1-P5, сложность)
   - Куда записать? (99-Inbox → Captures, карточка проекта, 02-Methods)
3. **Запиши в `99-Inbox.md`** — раздел «📥 Captures из Telegram», формат:
   ```
   #### C-NNN: <название>
   - **Источник:** [link](link) (тема «X»)
   - **Репо:** [url](url)
   - **Что:** краткое описание
   - **Категория:** 👨‍💻/🔥/🤝/🏆/🎉
   - **Применение:** куда/зачем в VibeOS
   - **Приоритет:** P1-P5
   - **Реакция:** эмодзи (категория)
   ```
4. **Поставь категорийную реакцию** через mark.py (делегируй task-агенту):
   ```bash
   python tools/telegram-capture/mark.py --message-ids <id1> <id2> --category <cat>
   ```
   Это пометит посты категорийным эмодзи (заменяет промежуточную 👍).
5. **Сообщи пользователю** — сводка: сколько постов, категории, рекомендации

## Схема маркировки (двухуровневая)

| Эмодзи | Категория | Назначение |
|--------|-----------|------------|
| 👍 | ingested | Обработан (default для без категории) |
| 🤔 | error | Ошибка обработки |
| 👨‍💻 | dotfiles | dotfiles / Linux UX Lab |
| 🔥 | serplux | SERPlux |
| 🤝 | dv-hub | dv-hub |
| 🏆 | vibeos | VibeOS / метод / инструмент |
| 🎉 | new | Новый проект / направление |

Любая из этих реакций на посте = «уже обработан», при следующем /capture пропускается.

## Связанные файлы

- `tools/telegram-capture/capture.py` — главный скрипт
- `tools/telegram-capture/mark.py` — простановка категорийных реакций
- `tools/telegram-capture/config.py` — конфигурация (TOPIC_NAMES, EMOJI_MAP)
- `tools/telegram-capture/README.md` — описание модуля
- `.opencode/command/capture.md` — команда /capture (альтернативный запуск)
- `99-Inbox.md` — куда записываются captures (раздел «📥 Captures из Telegram»)
- `02-Methods/tool-integration-pattern.md` — метод, реализацией которого является
- `03-Projects/vault.md` — карточка проекта

## Пример использования

Пользователь: «достань 5 постов из темы Графика»

Librarian:
1. Делегирует: `python tools/telegram-capture/capture.py --topic Графика --limit 5`
2. Получает JSON с 5 постами
3. Анализирует: «Pост 1 — GIMP плагин → 👨‍💻 dotfiles, Пост 2 — krita → 👨‍💻 dotfiles...»
4. Записывает в 99-Inbox (C-004..C-008)
5. Делегирует: `python tools/telegram-capture/mark.py --message-ids 700 701 702 703 704 --category dotfiles`
6. Сообщает: «Извлечено 5 постов из темы Графика. Все → dotfiles/Linux UX. Записаны как C-004..C-008. Реакции 👨‍💻 проставлены.»
