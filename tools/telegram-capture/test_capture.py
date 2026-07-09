"""Тесты capture.py — детерминированная логика (парсинг, фильтр, маппинг).

Реальные API-вызовы Telethon НЕ тестируются. Telethon замокирован в conftest.py,
поэтому import capture работает без установленной библиотеки.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import capture


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

def test_parse_args_topic_required(monkeypatch):
    """Без --topic парсер падает (sys.exit)."""
    monkeypatch.setattr("sys.argv", ["capture.py"])
    with pytest.raises(SystemExit):
        capture.parse_args()


def test_parse_args_topic_invalid_choice(monkeypatch):
    """Несуществующая тема → sys.exit (choices проверяются argparse)."""
    monkeypatch.setattr("sys.argv", ["capture.py", "--topic", "НесуществующаяТема"])
    with pytest.raises(SystemExit):
        capture.parse_args()


def test_parse_args_topic_valid(monkeypatch):
    """Корректное имя темы разбирается без ошибок."""
    monkeypatch.setattr("sys.argv", ["capture.py", "--topic", "Софт"])
    args = capture.parse_args()
    assert args.topic == "Софт"


def test_parse_args_defaults(monkeypatch):
    """limit=DEFAULT_LIMIT, dry_run=False по умолчанию."""
    monkeypatch.setattr("sys.argv", ["capture.py", "--topic", "ИИ"])
    args = capture.parse_args()
    assert args.limit == 10
    assert args.dry_run is False


def test_parse_args_dry_run(monkeypatch):
    """Флаг --dry-run выставляется в True."""
    monkeypatch.setattr("sys.argv", ["capture.py", "--topic", "ИИ", "--dry-run"])
    args = capture.parse_args()
    assert args.dry_run is True


def test_parse_args_custom_limit(monkeypatch):
    """--limit 5 → args.limit == 5."""
    monkeypatch.setattr("sys.argv", ["capture.py", "--topic", "ИИ", "--limit", "5"])
    args = capture.parse_args()
    assert args.limit == 5


# ---------------------------------------------------------------------------
# _media_type
# ---------------------------------------------------------------------------

def test_media_type_photo(monkeypatch):
    """MessageMediaPhoto → 'photo'."""
    class FakePhoto:
        pass

    monkeypatch.setattr(capture, "MessageMediaPhoto", FakePhoto)
    monkeypatch.setattr(capture, "MessageMediaDocument", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaWebPage", MagicMock)
    msg = SimpleNamespace(media=FakePhoto())
    assert capture._media_type(msg) == "photo"


def test_media_type_video(monkeypatch):
    """Document с mime_type='video/mp4' → 'video'."""
    class FakeDocument:
        def __init__(self, mime_type):
            self.document = SimpleNamespace(mime_type=mime_type)

    monkeypatch.setattr(capture, "MessageMediaPhoto", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaDocument", FakeDocument)
    monkeypatch.setattr(capture, "MessageMediaWebPage", MagicMock)
    msg = SimpleNamespace(media=FakeDocument("video/mp4"))
    assert capture._media_type(msg) == "video"


def test_media_type_document(monkeypatch):
    """Document с mime_type='application/pdf' → 'document'."""
    class FakeDocument:
        def __init__(self, mime_type):
            self.document = SimpleNamespace(mime_type=mime_type)

    monkeypatch.setattr(capture, "MessageMediaPhoto", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaDocument", FakeDocument)
    monkeypatch.setattr(capture, "MessageMediaWebPage", MagicMock)
    msg = SimpleNamespace(media=FakeDocument("application/pdf"))
    assert capture._media_type(msg) == "document"


def test_media_type_webpage(monkeypatch):
    """MessageMediaWebPage → 'webpage'."""
    class FakeWebPage:
        pass

    monkeypatch.setattr(capture, "MessageMediaPhoto", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaDocument", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaWebPage", FakeWebPage)
    msg = SimpleNamespace(media=FakeWebPage())
    assert capture._media_type(msg) == "webpage"


def test_media_type_none(monkeypatch):
    """media=None → 'none'."""
    monkeypatch.setattr(capture, "MessageMediaPhoto", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaDocument", MagicMock)
    monkeypatch.setattr(capture, "MessageMediaWebPage", MagicMock)
    msg = SimpleNamespace(media=None)
    assert capture._media_type(msg) == "none"


# ---------------------------------------------------------------------------
# _reactions_emojis
# ---------------------------------------------------------------------------

def test_reactions_emojis_empty(monkeypatch):
    """reactions=None → пустое множество."""
    monkeypatch.setattr(capture, "MessageReactions", MagicMock)
    msg = SimpleNamespace(reactions=None)
    assert capture._reactions_emojis(msg) == set()


def test_reactions_emojis_multiple(monkeypatch):
    """Две реакции → множество из двух эмодзи."""
    class FakeReactions:
        def __init__(self, results):
            self.results = results

    monkeypatch.setattr(capture, "MessageReactions", FakeReactions)
    reactions = FakeReactions([
        SimpleNamespace(reaction=SimpleNamespace(emoticon="📥")),
        SimpleNamespace(reaction=SimpleNamespace(emoticon="🤖")),
    ])
    msg = SimpleNamespace(reactions=reactions)
    assert capture._reactions_emojis(msg) == {"📥", "🤖"}


def test_reactions_emojis_skips_empty_emoticon(monkeypatch):
    """Реакции без emoticon пропускаются."""
    class FakeReactions:
        def __init__(self, results):
            self.results = results

    monkeypatch.setattr(capture, "MessageReactions", FakeReactions)
    reactions = FakeReactions([
        SimpleNamespace(reaction=SimpleNamespace(emoticon=None)),
        SimpleNamespace(reaction=SimpleNamespace(emoticon="🐧")),
        SimpleNamespace(reaction=None),
    ])
    msg = SimpleNamespace(reactions=reactions)
    assert capture._reactions_emojis(msg) == {"🐧"}


# ---------------------------------------------------------------------------
# _is_processed
# ---------------------------------------------------------------------------

def test_is_processed_true_ingested(monkeypatch):
    """Реакция 👍 → обработан (True)."""
    class FakeReactions:
        def __init__(self, results):
            self.results = results

    monkeypatch.setattr(capture, "MessageReactions", FakeReactions)
    reactions = FakeReactions([
        SimpleNamespace(reaction=SimpleNamespace(emoticon="👍")),
    ])
    msg = SimpleNamespace(reactions=reactions)
    assert capture._is_processed(msg) is True


def test_is_processed_false_no_reactions(monkeypatch):
    """Нет реакций → не обработан (False)."""
    monkeypatch.setattr(capture, "MessageReactions", MagicMock)
    msg = SimpleNamespace(reactions=None)
    assert capture._is_processed(msg) is False


def test_is_processed_true_category(monkeypatch):
    """Категорийная реакция 🔥 (serplux) → обработан (True)."""
    class FakeReactions:
        def __init__(self, results):
            self.results = results

    monkeypatch.setattr(capture, "MessageReactions", FakeReactions)
    reactions = FakeReactions([
        SimpleNamespace(reaction=SimpleNamespace(emoticon="🔥")),
    ])
    msg = SimpleNamespace(reactions=reactions)
    assert capture._is_processed(msg) is True


def test_is_processed_false_unknown_emoji(monkeypatch):
    """Неизвестный эмодзи (не из PROCESSED_REACTIONS) → False."""
    class FakeReactions:
        def __init__(self, results):
            self.results = results

    monkeypatch.setattr(capture, "MessageReactions", FakeReactions)
    reactions = FakeReactions([
        SimpleNamespace(reaction=SimpleNamespace(emoticon="📥")),
    ])
    msg = SimpleNamespace(reactions=reactions)
    assert capture._is_processed(msg) is False


# ---------------------------------------------------------------------------
# _resolve_topic_id
# ---------------------------------------------------------------------------

def test_resolve_topic_id_general(monkeypatch):
    """#General — специальный топик, id=1, без вызова API."""
    client = MagicMock()
    result = asyncio.run(capture._resolve_topic_id(client, "chat_obj", "#General"))
    assert result == 1
    # API не должен вызываться для #General.
    client.assert_not_called()


def test_resolve_topic_id_not_found(monkeypatch):
    """Тема не найдена в списке → None."""
    class FakeRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(capture, "GetForumTopicsRequest", FakeRequest)

    client = MagicMock()
    # client.get_input_entity — корутина (возвращает InputPeer).
    async def _get_input_entity(*a, **kw):
        return "peer_obj"
    client.get_input_entity = _get_input_entity
    # client(...) — корутина, оборачиваем в async mock.
    async_response = SimpleNamespace(topics=[])
    async def _call(*a, **kw):
        return async_response
    client.side_effect = _call

    result = asyncio.run(capture._resolve_topic_id(client, "chat_obj", "Софт"))
    assert result is None


def test_resolve_topic_id_found(monkeypatch):
    """Тема 'Софт' найдена с id=42 → возвращаем 42."""
    class FakeRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(capture, "GetForumTopicsRequest", FakeRequest)

    client = MagicMock()
    # client.get_input_entity — корутина (возвращает InputPeer).
    async def _get_input_entity(*a, **kw):
        return "peer_obj"
    client.get_input_entity = _get_input_entity
    topic = SimpleNamespace(id=42, title="Софт")
    async_response = SimpleNamespace(topics=[topic])
    async def _call(*a, **kw):
        return async_response
    client.side_effect = _call

    result = asyncio.run(capture._resolve_topic_id(client, "chat_obj", "Софт"))
    assert result == 42


def test_resolve_topic_id_paginates(monkeypatch):
    """Если первый батч = 100 тем без нужной, а второй — с нужной, находим."""
    class FakeRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(capture, "GetForumTopicsRequest", FakeRequest)

    client = MagicMock()
    # client.get_input_entity — корутина (возвращает InputPeer).
    async def _get_input_entity(*a, **kw):
        return "peer_obj"
    client.get_input_entity = _get_input_entity
    first_batch = SimpleNamespace(topics=[
        SimpleNamespace(id=i, title=f"Тема{i}") for i in range(100)
    ])
    second_batch = SimpleNamespace(topics=[
        SimpleNamespace(id=777, title="Питонизм")
    ])
    responses = [first_batch, second_batch]
    async def _call(*a, **kw):
        return responses.pop(0)
    client.side_effect = _call

    result = asyncio.run(capture._resolve_topic_id(client, "chat_obj", "Питонизм"))
    assert result == 777
