"""Тесты градеров (офлайн). build-гейт — реальный subprocess-прогон."""
import graders


# --- grade_tools ---

def test_tools_happy_plain_json():
    assert graders.grade_tools('{"name": "Ann", "age": 30}', {"name": str, "age": int})


def test_tools_happy_fenced_json():
    reply = '```json\n{"name": "Ann", "age": 30}\n```'
    assert graders.grade_tools(reply, {"name": str, "age": int})


def test_tools_fail_extra_key():
    reply = '{"name": "Ann", "age": 30, "extra": 1}'
    assert not graders.grade_tools(reply, {"name": str, "age": int})


def test_tools_fail_missing_key():
    reply = '{"name": "Ann"}'
    assert not graders.grade_tools(reply, {"name": str, "age": int})


def test_tools_fail_wrong_type():
    reply = '{"name": "Ann", "age": "thirty"}'
    assert not graders.grade_tools(reply, {"name": str, "age": int})


def test_tools_fail_bool_is_not_int():
    reply = '{"name": "Ann", "age": true}'
    assert not graders.grade_tools(reply, {"name": str, "age": int})


def test_tools_fail_invalid_json():
    assert not graders.grade_tools("not json at all", {"name": str, "age": int})


def test_tools_nested_and_array():
    assert graders.grade_tools(
        '{"user": {"id": 1, "email": "a@b.c"}, "active": true}',
        {"user": {"id": int, "email": str}, "active": bool},
    )
    assert graders.grade_tools(
        '{"tags": ["a", "b"], "count": 2}', {"tags": list, "count": int}
    )


# --- grade_build (subprocess) ---

def test_build_correct_function():
    code = "def add(a, b):\n    return a + b\n"
    assert graders.grade_build(code, [((2, 3), 5), ((-1, 1), 0)])


def test_build_fenced_correct():
    code = "```python\ndef add(a, b):\n    return a + b\n```"
    assert graders.grade_build(code, [((2, 3), 5)])


def test_build_incorrect_function():
    code = "def add(a, b):\n    return a - b\n"
    assert not graders.grade_build(code, [((2, 3), 5)])


def test_build_syntax_error():
    assert not graders.grade_build("def add(a, b):\n    return a +", [((2, 3), 5)])


def test_build_infinite_loop_timeout():
    code = "def add(a, b):\n    while True:\n        pass\n    return a + b\n"
    assert not graders.grade_build(code, [((2, 3), 5)])


def test_build_empty_reply():
    assert not graders.grade_build("", [((2, 3), 5)])


# --- grade_build_edit ---

def test_edit_happy():
    code = 'def greet(name):\n    return "Hello, " + name + "!"\n'
    assert graders.grade_build_edit(
        code, must_contain=["def greet", "!", "return"], must_not_contain=["print"]
    )


def test_edit_fail_missing():
    code = "def greet(name):\n    return 'Hi'\n"
    assert not graders.grade_build_edit(
        code, must_contain=["!"], must_not_contain=["print"]
    )


def test_edit_fail_forbidden():
    code = 'def greet(name):\n    print("x")\n    return "!"\n'
    assert not graders.grade_build_edit(
        code, must_contain=["!"], must_not_contain=["print"]
    )


# --- grade_reasoning ---

def test_reasoning_exact():
    assert graders.grade_reasoning("102", "102")


def test_reasoning_normalizes_case_dot_spaces():
    assert graders.grade_reasoning("  Одинаково. ", "одинаково")


def test_reasoning_takes_last_line():
    reply = "Шаги: 1) ... 2) ...\n8"
    assert graders.grade_reasoning(reply, "8")


def test_reasoning_fail_wrong_value():
    assert not graders.grade_reasoning("7", "8")


def test_reasoning_fail_empty():
    assert not graders.grade_reasoning("", "8")
