"""Тесты watch.py — детерминированная логика userbot-демона (без telethon).

Сетевые вызовы (Telethon events) — smoke-gated; здесь тестируем только
сериализацию поста, маппинг топиков и резолв имени темы.
"""
from types import SimpleNamespace

import watch


def test_post_data_serializes_all_fields():
    rec = watch.post_data(
        message_id=42, topic="Софт", text="**tui** утилита",
        date="2026-09-06T00:00:00+00:00", link="https://t.me/inbox_tools/42",
        media_type="photo", sender_name="rudra",
    )
    assert rec["message_id"] == 42
    assert rec["topic"] == "Софт"
    assert rec["text"] == "**tui** утилита"
    assert rec["media_type"] == "photo"
    assert rec["sender_name"] == "rudra"


def test_post_data_empty_text_becomes_empty_string():
    rec = watch.post_data(1, "Софт", None, "", "", "none", "")
    assert rec["text"] == ""


def test_build_topic_map_maps_id_to_title():
    topics = [
        SimpleNamespace(id=3, title="Софт"),
        SimpleNamespace(id=7, title="ИИ"),
    ]
    m = watch.build_topic_map(topics)
    assert m[3] == "Софт"
    assert m[7] == "ИИ"
    assert m[1] == "#General"  # fallback default


def test_build_topic_map_tolerates_missing_attrs():
    topics = [SimpleNamespace(), SimpleNamespace(id=5)]
    m = watch.build_topic_map(topics)
    assert m.get(5) is None
    assert m[1] == "#General"


def test_resolve_topic_name_known_topic():
    msg = SimpleNamespace(reply_to=SimpleNamespace(reply_to_top_id=7))
    m = {7: "ИИ", 1: "#General"}
    assert watch.resolve_topic_name(msg, m) == "ИИ"


def test_resolve_topic_name_falls_back_to_general():
    msg = SimpleNamespace(reply_to=SimpleNamespace(reply_to_top_id=999))
    m = {1: "#General"}
    assert watch.resolve_topic_name(msg, m) == "#General"


def test_resolve_topic_name_no_reply():
    msg = SimpleNamespace(reply_to=None)
    m = {1: "#General"}
    assert watch.resolve_topic_name(msg, m) == "#General"


def test_iso_utc_none():
    assert watch.iso_utc(None) == ""