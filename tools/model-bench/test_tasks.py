"""Тесты наборов задач: структура и детерминированный hash."""
import tasks


def test_all_tasks_nonempty():
    assert len(tasks.ALL_TASKS) > 0
    assert len(tasks.TOOLS_TASKS) == 5
    assert len(tasks.BUILD_TASKS) == 5
    assert len(tasks.REASONING_TASKS) == 4
    assert len(tasks.FAST_TASKS) == 3


def test_each_task_has_required_fields():
    for t in tasks.ALL_TASKS:
        assert t["id"] and t["gate"] and t["prompt"]
        assert isinstance(t["max_tokens"], int) and t["max_tokens"] > 0


def test_tools_tasks_have_schema():
    for t in tasks.TOOLS_TASKS:
        assert t["gate"] == "tools"
        assert isinstance(t["schema"], dict)


def test_build_tasks_have_tests_or_edit_fields():
    for t in tasks.BUILD_TASKS:
        if "tests" in t:
            assert isinstance(t["tests"], list) and t["tests"]
        else:
            assert t.get("must_contain") and t.get("must_not_contain") is not None


def test_reasoning_tasks_have_expected():
    for t in tasks.REASONING_TASKS:
        assert "expected" in t


def test_fast_tasks_minimal():
    for t in tasks.FAST_TASKS:
        assert t["max_tokens"] == 16


def test_task_set_hash_stable():
    assert tasks.task_set_hash() == tasks.TASK_SET_HASH
    assert len(tasks.TASK_SET_HASH) == 12


def test_task_set_hash_deterministic():
    assert tasks.task_set_hash() == tasks.task_set_hash()


def test_thresholds():
    assert tasks.THRESHOLDS["tools"] == 1.0
    assert tasks.THRESHOLDS["build"] == 0.75
    assert tasks.THRESHOLDS["reasoning"] == 0.70
    assert tasks.THRESHOLDS["fast"] is None
