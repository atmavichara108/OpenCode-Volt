"""conftest.py — общие фикстуры и моки для тестов telegram-capture.

Telethon не установлен в окружении тестов — мокируем его через sys.modules,
чтобы capture.py / mark.py импортировались без реальной библиотеки.
Тестируем только детерминированную логику (парсинг, фильтр, маппинг).
"""
import sys
from unittest.mock import MagicMock

# Мокируем telethon и его подмодули ДО любого импорта capture/mark.
_telethon_mock = MagicMock()
sys.modules.setdefault("telethon", _telethon_mock)
sys.modules.setdefault("telethon.errors", MagicMock())
sys.modules.setdefault("telethon.tl.functions.channels", MagicMock())
sys.modules.setdefault("telethon.tl.functions.messages", MagicMock())
sys.modules.setdefault("telethon.tl.functions", MagicMock())
sys.modules.setdefault("telethon.tl.types", MagicMock())
