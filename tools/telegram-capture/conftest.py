"""conftest.py — общие фикстуры и моки для тестов telegram-capture.

Telethon не установлен в окружении тестов — мокируем его через sys.modules,
чтобы capture.py / mark.py импортировались без реальной библиотеки.
Тестируем только детерминированную логику (парсинг, фильтр, маппинг).

Smoke-тесты (test_smoke.py, маркер @pytest.mark.smoke) требуют РЕАЛЬНОГО
telethon — они снимают мок из sys.modules в начале файла.
"""
import sys
from unittest.mock import MagicMock

import pytest

# Мокируем telethon и его подмодули ДО любого импорта capture/mark.
_telethon_mock = MagicMock()
sys.modules.setdefault("telethon", _telethon_mock)
sys.modules.setdefault("telethon.errors", MagicMock())
sys.modules.setdefault("telethon.tl.functions.channels", MagicMock())
sys.modules.setdefault("telethon.tl.functions.messages", MagicMock())
sys.modules.setdefault("telethon.tl.functions", MagicMock())
sys.modules.setdefault("telethon.tl.types", MagicMock())


def pytest_addoption(parser):
    """--smoke: включить интеграционные smoke-тесты с реальным Telegram."""
    parser.addoption(
        "--smoke",
        action="store_true",
        default=False,
        help="Запустить интеграционные smoke-тесты (реальное Telegram API).",
    )


def pytest_collection_modifyitems(config, items):
    """Без явного --smoke smoke-тесты пропускаются (нужны credentials/Tor)."""
    if config.getoption("--smoke"):
        return
    skip_marker = pytest.mark.skip(reason="Нужен флаг --smoke для smoke-тестов")
    for item in items:
        if "smoke" in item.keywords:
            item.add_marker(skip_marker)
