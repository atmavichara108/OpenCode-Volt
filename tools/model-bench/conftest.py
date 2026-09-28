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

import config  # noqa: E402


@pytest.fixture(autouse=True)
def _hermetic_config(monkeypatch, tmp_path):
    """Герметичность тестов: подменяет пути конфигов/ключей на tmp.

    CONFIG_PATHS → tmp opencode.jsonc (anymodel + amd-radeon с baseURL);
    AUTH_JSON_PATH → tmp пустой auth.json; VAULT_ROOT → tmp (нет .env); env
    ключей провайдеров обнуляются. Никаких чтений реального ~/.config.
    """
    cfg = tmp_path / "opencode.jsonc"
    cfg.write_text(
        '{"provider": {'
        '"anymodel": {"options": {"baseURL": "https://anymodel.test/v1"},'
        ' "models": {"am/free": {}, "cx/gpt-6-astra": {}}},'
        '"amd-radeon": {"options": {"baseURL": "https://amd.test/v1"},'
        ' "models": {"DeepSeek-V4-Flash": {}}}'
        '}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "CONFIG_PATHS", [cfg])
    auth = tmp_path / "auth.json"
    auth.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(config, "AUTH_JSON_PATH", auth)
    monkeypatch.setattr(config, "VAULT_ROOT", tmp_path)
    for var in ("ANYMODEL_API_KEY", "AMD_RADEON_API_KEY",
                "LINALIAPI_API_KEY", "APINEX_API_KEY"):
        monkeypatch.setenv(var, "")
    return cfg


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
