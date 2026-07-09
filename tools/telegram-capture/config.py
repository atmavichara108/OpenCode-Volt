"""Конфигурация модуля telegram-capture.

Загружает .env через python-dotenv и определяет:
- credentials/session для Telethon,
- список тем группы @inbox_tools,
- карту эмодзи категорий и набор «уже обработанных» реакций.
"""
import os

from dotenv import load_dotenv

# Загружаем .env из директории скрипта (tools/telegram-capture/.env),
# не полагаясь на текущий рабочий каталог запускающего.
load_dotenv()


API_ID = os.getenv("TELEGRAM_API_ID", "")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
CHAT_USERNAME = os.getenv("TELEGRAM_CHAT_USERNAME", "inbox_tools")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "vibeos_capture")

# SOCKS5 proxy (Tor) — обход блокировки Telegram.
# Telethon использует PySocks. Если PROXY_HOST пустой — proxy не используется.
PROXY_HOST = os.getenv("TELEGRAM_PROXY_HOST", "")
PROXY_PORT = int(os.getenv("TELEGRAM_PROXY_PORT", "9050"))
# Формат для Telethon: ('socks5', host, port) или None
PROXY = ("socks5", PROXY_HOST, PROXY_PORT) if PROXY_HOST else None

# Темы (topics) группы @inbox_tools. Точное совпадение по имени (case-sensitive для русских).
TOPIC_NAMES = [
    "Приложения",
    "Софт",
    "Вайб",
    "#General",
    "Смарт",
    "Графика",
    "красота",
    "сайтостроение",
    "Обучалки",
    "ИИ",
    "Питонизм",
]

# Карта категорий → эмодзи. Двухуровневая маркировка.
# Эмодзи выбраны из 73 доступных реакций Telegram (GetAvailableReactionsRequest).
# 📥⚠️🐧🤖🌐🧠🎯 НЕ доступны — заменены на семантически близкие.
EMOJI_MAP = {
    "ingested": "👍",      # обработан (Thumbs Up)
    "error": "🤔",          # ошибка/требует внимания (Thinking Face)
    "dotfiles": "👨‍💻",     # dotfiles / Linux UX (Man Technologist)
    "serplux": "🔥",        # SERPlux (Fire — горячие позиции)
    "dv-hub": "🤝",         # dv-hub (Handshake — связи/хаб)
    "vibeos": "🏆",         # VibeOS / метод (Trophy)
    "new": "🎉",            # новый проект (Party Popper)
}

# Любая из этих реакций на посте = «уже обработан», пропускам при извлечении.
PROCESSED_REACTIONS = set(EMOJI_MAP.values())

DEFAULT_LIMIT = 10