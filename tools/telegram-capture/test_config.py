"""Тесты config.py — проверка констант и маппингов."""
import config


def test_emoji_map_has_all_categories():
    expected = {"ingested", "error", "dotfiles", "serplux", "dv-hub", "vibeos", "new"}
    assert expected == set(config.EMOJI_MAP.keys())


def test_emoji_map_values_unique():
    assert len(set(config.EMOJI_MAP.values())) == len(config.EMOJI_MAP)


def test_emoji_map_known_emojis():
    assert config.EMOJI_MAP["ingested"] == "👍"
    assert config.EMOJI_MAP["error"] == "🤔"
    assert config.EMOJI_MAP["dotfiles"] == "👨‍💻"
    assert config.EMOJI_MAP["serplux"] == "🔥"
    assert config.EMOJI_MAP["dv-hub"] == "🤝"
    assert config.EMOJI_MAP["vibeos"] == "🏆"
    assert config.EMOJI_MAP["new"] == "🎉"


def test_processed_reactions_is_set_of_values():
    assert config.PROCESSED_REACTIONS == set(config.EMOJI_MAP.values())


def test_processed_reactions_contains_ingested():
    assert "👍" in config.PROCESSED_REACTIONS


def test_topic_names_count():
    assert len(config.TOPIC_NAMES) == 11


def test_topic_names_contains_expected():
    for name in [
        "Приложения", "Софт", "Вайб", "#General", "Смарт",
        "Графика", "красота", "сайтостроение", "Обучалки", "ИИ", "Питонизм",
    ]:
        assert name in config.TOPIC_NAMES


def test_default_limit_is_10():
    assert config.DEFAULT_LIMIT == 10


def test_chat_username():
    assert config.CHAT_USERNAME == "inbox_tools"
