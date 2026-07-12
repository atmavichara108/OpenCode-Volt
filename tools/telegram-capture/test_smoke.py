"""test_smoke.py — интеграционный smoke-тест эмодзи против Telegram API.

Проверяет что все эмодзи из config.EMOJI_MAP доступны в Telegram
(через GetAvailableReactionsRequest). Ловит хардкоды недоступных реакций
ДО реального запуска capture.py/mark.py.

Маркер: @pytest.mark.smoke — не запускается по умолчанию (нужен --smoke).
Требует: .env с credentials, Tor proxy, авторизованную сессию.
"""
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Снимаем telethon-моки, установленные conftest.py — для smoke нужен реальный
# telethon, импортируемый из .venv. telethon 1.44.0 установлен в окружении.
for _mod in list(sys.modules):
    if _mod == "telethon" or _mod.startswith("telethon."):
        # noqa: снимаем только mock'и, оставляем реальные модули если уже импортированы
        if isinstance(sys.modules[_mod], MagicMock):
            del sys.modules[_mod]

from dotenv import load_dotenv

import pytest

# Загружаем .env из директории скрипта (устойчиво к смене cwd pytest'ом).
_TOOLS_DIR = Path(__file__).resolve().parent
load_dotenv(_TOOLS_DIR / ".env")

API_ID = os.getenv("TELEGRAM_API_ID", "")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PROXY_HOST = os.getenv("TELEGRAM_PROXY_HOST", "")
PROXY_PORT = int(os.getenv("TELEGRAM_PROXY_PORT", "9050"))

TOOLS_DIR = str(_TOOLS_DIR)
# Используем существующую авторилизованную сессию capture/mark, чтобы
# smoke-тест не требовал интерактивной авторизации (код из SMS).
# .env.example не содержит SESSION_NAME — берём дефолт из config.py.
SMOKE_SESSION = str(_TOOLS_DIR / "vibeos_capture")

# Без credentials smoke-тест пропускается (маркер skipif срабатывает раньше
# чем условие --smoke из pytest_collection_modifyitems, но оба совместимы).
pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(
        not API_ID or not API_HASH,
        reason="Нет TELEGRAM_API_ID/API_HASH в .env — smoke-test пропускается",
    ),
]


async def _get_available_emojis():
    """Подключается к Telegram и возвращает множество доступных эмодзи-реакций.

    Возвращает set[str] эмодзи-строк. Структура AvailableReaction в Telethon
    1.44.0: атрибут `.reaction` напрямую содержит строку-эмодзи (раньше был
    ReactionEmoji с .emoticon — поддерживаем оба варианта для устойчивости).
    """
    # Импортируем БЕЗ мока telethon — реальный импорт. Добавляем tools/ в sys.path
    # чтобы `import config` отработал как в capture.py/mark.py.
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    import config  # noqa: PLC0415 — нужен поздний импорт после снятия моков
    from telethon import TelegramClient
    from telethon.tl.functions.messages import GetAvailableReactionsRequest

    proxy = ("socks5", PROXY_HOST, PROXY_PORT) if PROXY_HOST else None
    client_kwargs = {"proxy": proxy} if proxy else {}
    client = TelegramClient(
        SMOKE_SESSION,
        int(API_ID),
        API_HASH,
        **client_kwargs,
    )
    emojis: set[str] = set()
    try:
        await asyncio.wait_for(client.connect(), timeout=30)
        if not await client.is_user_authorized():
            pytest.skip("Сессия не авторизована — smoke-test пропускается")
        res = await client(GetAvailableReactionsRequest(hash=0))
        for r in res.reactions:
            # AvailableReaction.reaction в Telethon 1.44.0 — str (emoticon).
            # На старых версиях — ReactionEmoji с .emoticon.
            val = getattr(r, "reaction", None)
            if val is None:
                val = getattr(r, "emoticon", None)
            elif hasattr(val, "emoticon"):
                val = val.emoticon
            if isinstance(val, str) and val:
                emojis.add(val)
    finally:
        try:
            await client.disconnect()
        except Exception:  # noqa: BLE001
            pass
        # Сессию vibeos_capture.session НЕ удаляем — она используется capture/mark
        # и её повторная авторизация требует интерактивного кода из SMS.
    return emojis


@pytest.mark.smoke
def test_emoji_map_all_available_in_telegram():
    """Все эмодзи из EMOJI_MAP должны быть доступны в Telegram.

    Получает список доступных реакций через GetAvailableReactionsRequest
    и проверяет что каждый эмодзи из EMOJI_MAP там есть.
    Ловит хардкоды недоступных реакций (как 📥⚠️🐧🤖🌐🧠🎯 ранее).
    """
    # Импортируем config БЕЗ мока telethon (моки сняты в начале файла).
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    import config

    available = asyncio.run(_get_available_emojis())
    assert available, (
        "Telegram вернул пустой список доступных реакций — невозможно проверить "
        "EMOJI_MAP. Проверь аккаунт/сессию/Tor."
    )

    missing = []
    for category, emoji in config.EMOJI_MAP.items():
        if emoji not in available:
            missing.append((category, emoji))

    assert not missing, (
        "Эмодзи из config.EMOJI_MAP НЕ доступны в Telegram! "
        f"Доступно {len(available)}: {' '.join(sorted(available))}. "
        f"Недоступны: {missing!r}. Замени их в config.py EMOJI_MAP."
    )