"""conftest.py — общие фикстуры для тестов model-bench.

Все тесты ОФЛАЙН: ``client.chat`` мокается. Smoke-тесты (маркер
``@pytest.mark.smoke``) требуют реального провайдера и снимают мок — они не
запускаются без флага ``--smoke``.
"""
import sys
from pathlib import Path

import pytest

# tools/model-bench в sys.path, чтобы `import config/tasks/...` работал.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def pytest_addoption(parser):
    """--smoke: включить интеграционные smoke-тесты с реальным провайдером."""
    parser.addoption(
        "--smoke",
        action="store_true",
        default=False,
        help="Запустить интеграционные smoke-тесты (реальный провайдер).",
    )


def pytest_collection_modifyitems(config, items):
    """Без --smoke smoke-тесты пропускаются."""
    if config.getoption("--smoke"):
        return
    skip_marker = pytest.mark.skip(reason="Нужен флаг --smoke для smoke-тестов")
    for item in items:
        if "smoke" in item.keywords:
            item.add_marker(skip_marker)
