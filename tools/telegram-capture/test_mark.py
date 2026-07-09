"""Тесты mark.py — парсинг аргументов командной строки.

Реальные API-вызовы Telethon НЕ тестируются. Telethon замокирован в conftest.py.
"""
import pytest

import mark


def test_parse_args_message_ids_required(monkeypatch):
    """Без --message-ids парсер падает (sys.exit)."""
    monkeypatch.setattr("sys.argv", ["mark.py"])
    with pytest.raises(SystemExit):
        mark.parse_args()


def test_parse_args_message_ids_multiple(monkeypatch):
    """--message-ids 12 34 56 → [12, 34, 56]."""
    monkeypatch.setattr(
        "sys.argv", ["mark.py", "--message-ids", "12", "34", "56", "--category", "dotfiles"]
    )
    args = mark.parse_args()
    assert args.message_ids == [12, 34, 56]


def test_parse_args_category_required(monkeypatch):
    """Без --category парсер падает (sys.exit)."""
    monkeypatch.setattr("sys.argv", ["mark.py", "--message-ids", "12"])
    with pytest.raises(SystemExit):
        mark.parse_args()


def test_parse_args_category_invalid(monkeypatch):
    """Несуществующая категория → sys.exit (choices проверяются argparse)."""
    monkeypatch.setattr(
        "sys.argv", ["mark.py", "--message-ids", "12", "--category", "несуществующая"]
    )
    with pytest.raises(SystemExit):
        mark.parse_args()


def test_parse_args_category_valid(monkeypatch):
    """--category dotfiles → 'dotfiles'."""
    monkeypatch.setattr(
        "sys.argv", ["mark.py", "--message-ids", "12", "--category", "dotfiles"]
    )
    args = mark.parse_args()
    assert args.category == "dotfiles"


def test_parse_args_topic_id_default_none(monkeypatch):
    """--topic-id по умолчанию None."""
    monkeypatch.setattr(
        "sys.argv", ["mark.py", "--message-ids", "12", "--category", "error"]
    )
    args = mark.parse_args()
    assert args.topic_id is None


def test_parse_args_topic_id_explicit(monkeypatch):
    """--topic-id 3 → 3."""
    monkeypatch.setattr(
        "sys.argv",
        ["mark.py", "--message-ids", "12", "--category", "error", "--topic-id", "3"],
    )
    args = mark.parse_args()
    assert args.topic_id == 3


def test_parse_args_all_categories_accepted(monkeypatch):
    """Все ключи EMOJI_MAP принимаются argparse как валидные категории."""
    import config
    for cat in config.EMOJI_MAP.keys():
        monkeypatch.setattr(
            "sys.argv", ["mark.py", "--message-ids", "1", "--category", cat]
        )
        args = mark.parse_args()
        assert args.category == cat
