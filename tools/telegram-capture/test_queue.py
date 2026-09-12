"""Тесты inbox_queue.py — детерминированная логика staging-очереди (дедуп, remove, flock)."""
import inbox_queue as queue


def _q(tmp_path):
    return tmp_path / "inbox-queue.jsonl"


def test_append_adds_new_and_dedups(tmp_path):
    p = _q(tmp_path)
    added, total = queue.append([
        {"message_id": 1, "topic": "Софт", "text": "a"},
        {"message_id": 2, "topic": "ИИ", "text": "b"},
    ], p)
    assert added == 2
    assert total == 2

    added, total = queue.append([
        {"message_id": 2, "topic": "ИИ", "text": "дубль"},
        {"message_id": 3, "topic": "Софт", "text": "c"},
    ], p)
    assert added == 1
    assert total == 3
    assert sorted(queue.ids(p)) == [1, 2, 3]


def test_append_preserves_order(tmp_path):
    p = _q(tmp_path)
    queue.append([
        {"message_id": 33, "topic": "Софт", "text": "x"},
        {"message_id": 12, "topic": "ИИ", "text": "y"},
        {"message_id": 7, "topic": "Софт", "text": "z"},
    ], p)
    assert [r["message_id"] for r in queue.load(p)] == [33, 12, 7]


def test_append_ignores_missing_message_id(tmp_path):
    p = _q(tmp_path)
    added, total = queue.append([
        {"topic": "Софт", "text": "без id"},
        {"message_id": 5, "topic": "Софт", "text": "с id"},
    ], p)
    assert added == 1
    assert total == 1


def test_append_adds_ingested_at(tmp_path):
    p = _q(tmp_path)
    queue.append([{"message_id": 9, "topic": "Софт", "text": "x"}], p)
    rec = queue.load(p)[0]
    assert rec["ingested_at"] is not None


def test_remove_keeps_unremoved(tmp_path):
    p = _q(tmp_path)
    queue.append([
        {"message_id": 1, "topic": "Софт", "text": "a"},
        {"message_id": 2, "topic": "ИИ", "text": "b"},
        {"message_id": 3, "topic": "Софт", "text": "c"},
    ], p)
    kept, removed = queue.remove([2], p)
    assert removed == 1
    assert kept == 2
    assert [r["message_id"] for r in queue.load(p)] == [1, 3]


def test_remove_all_deletes_file(tmp_path):
    p = _q(tmp_path)
    queue.append([{"message_id": 1, "topic": "Софт", "text": "a"}], p)
    kept, removed = queue.remove([1], p)
    assert kept == 0
    assert removed == 1
    assert not p.exists()


def test_load_missing_returns_empty(tmp_path):
    assert queue.load(_q(tmp_path)) == []


def test_load_skips_corrupt_lines(tmp_path):
    p = _q(tmp_path)
    queue.append([{"message_id": 1, "topic": "Софт", "text": "a"}], p)
    with p.open("a", encoding="utf-8") as f:
        f.write("{not json\n")
    assert [r["message_id"] for r in queue.load(p)] == [1]