"""Тесты classify.py — детерминированные правила классификатора.

Покрывают точечные дефекты, найденные при калибровке на живом сборе:
голый github-URL должен быть сигналом (не error), курсы/видео — error.
"""
import classify


def _post(text, topic="Софт"):
    return {"topic": topic, "text": text, "message_id": 1}


def test_bare_github_url_is_not_error():
    p = _post("https://github.com/jnMetaCode/agency-orchestrator", topic="Вайб")
    assert classify.classify_post(p) != "error"


def test_bare_non_github_url_is_error():
    p = _post("https://telegra.ph/file/abc.jpg")
    assert classify.classify_post(p) == "error"


def test_paid_course_is_error():
    p = _post("**Курс Python** Цена: 1500 руб. Научись программировать", topic="Питонизм")
    assert classify.classify_post(p) == "error"


def test_github_repo_text_is_signal():
    p = _post("tui файловый менеджер https://github.com/foo/bar", topic="Софт")
    assert classify.classify_post(p) == "dotfiles"


def test_empty_text_is_error():
    p = _post("")
    assert classify.classify_post(p) == "error"