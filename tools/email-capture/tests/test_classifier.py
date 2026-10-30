"""Тесты classifier.py — каскад контрольных фраз, нормализация, дедуп."""
from __future__ import annotations

import classifier


def _msg(subject: str, body: str = "", **kw) -> dict:
    return {"subject": subject, "body": body, **kw}


INTENT_SAMPLES = {
    "research": (
        "Запрос на исследование подходов",
        "Нужно сравнить варианты и сделать обзор трендов с benchmark.",
    ),
    "implementation": (
        "План внедрения",
        "Реализация спеки в роадмапе: интеграция и подключение сервиса.",
    ),
    "correction": (
        "Канон-коррекция по пункту 3",
        "Просьба пересмотреть вердикт и ратифицировать исправление.",
    ),
    "projects": (
        "Статус проекта",
        "Обновление в репо OpenCode: commit в github.com/example/repo.",
    ),
    "subscriptions": (
        "Ваша подписка активна",
        "Еженедельная рассылка: newsletter digest и анонсы недели.",
    ),
}


def test_every_intent_classifies_correctly():
    for intent, (subject, body) in INTENT_SAMPLES.items():
        assert classifier.classify(_msg(subject, body)) == intent, intent


def test_error_phrase_overrides_intent_phrase():
    # каскад: error/noise идёт первым и перебивает интент-фразу в том же тексте
    msg = _msg("Исследование трендов недели", "Нажмите unsubscribe, чтобы отписаться.")
    assert classifier.classify(msg) == "error"


def test_default_when_no_phrases():
    assert classifier.classify(_msg("Просто приветствие", "Добрый день, держи сводку мыслей.")) == "default"


def test_empty_text_is_default():
    assert classifier.classify(_msg("")) == "default"
    assert classifier.classify_text("") == "default"


def test_match_is_case_insensitive():
    assert classifier.classify(_msg("RESEARCH roundup")) == "research"
    assert classifier.classify(_msg("UnSubscribe")) == "error"


def test_match_covers_body_not_only_subject():
    assert classifier.classify(_msg("Внутри", "нужна реализация этого")) == "implementation"


def test_dedup_by_message_id():
    # тексты и темы разные — дедуп срабатывает только по Message-ID
    a = _msg("Первая тема письма", "Совсем другой текст про репозиторий.", message_id="<1@x>")
    b = _msg("Вторая тема письма", "Иной текст про проект недели.", message_id="<1@x>")
    assert len(classifier.dedup([a, b])) == 1


def test_dedup_by_text_signature():
    long_text = ("исследование рынка идей " * 20)  # >200 символов нормализации
    a = _msg("Тема", long_text, message_id="<1@x>")
    b = _msg("Тема", long_text, message_id="<2@x>")  # другой id — дубль по подписи
    out = classifier.dedup([a, b])
    assert len(out) == 1


def test_dedup_keeps_distinct_texts():
    a = _msg("Первое письмо про проект", message_id="<1@x>")
    b = _msg("Второе письмо про репо", message_id="<2@x>")
    assert len(classifier.dedup([a, b])) == 2


def test_signature_is_first_200_normalized_chars():
    sig = classifier.text_signature(_msg("Ab", "  <b>Cd</b>*ef*   gh "))
    assert sig == "ab cd ef gh"
    assert len(sig) <= classifier.SIGNATURE_LEN


def test_normalize_strips_html_and_markdown():
    # нормализация приводит к нижнему регистру — сравниваем в нижнем
    assert classifier.normalize("**bold** _em_ `code` # H") == "bold em code h"
    assert classifier.normalize("<p>Привет<br>мир</p>") == "привет мир"


def test_html_to_text_drops_script_and_tags():
    html = "<html><style>p{color:red}</style><script>alert(1)</script><p>Текст <a href='#'>ссылка</a></p></html>"
    text = classifier.html_to_text(html)
    assert "Текст" in text and "ссылка" in text
    assert "alert" not in text and "color" not in text


def test_classify_batch_adds_intent_and_dedups():
    msgs = [
        _msg("Обзор трендов", message_id="<1@x>"),
        _msg("Обзор трендов", message_id="<1@y>"),  # дубль по подписи текста
        _msg("Отписка", "unsubscribe", message_id="<2@x>"),
    ]
    out = classifier.classify_batch(msgs)
    assert [m["intent"] for m in out] == ["research", "error"]


def test_phrases_live_in_config_not_logic():
    import config

    assert set(config.INTENT_PHRASES) == {
        *config.INTENT_NAMES,
        "error",
    }
    assert config.CHOICES[: len(config.INTENT_NAMES)] == config.INTENT_NAMES
