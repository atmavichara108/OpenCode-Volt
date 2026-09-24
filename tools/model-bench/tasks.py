"""Версионированные наборы задач для 4 гейтов capability-probe.

Каждая задача — dict с полями ``id``, ``gate``, ``prompt``, ``max_tokens`` и
данными для детерминированной проверки (``schema`` / ``tests`` /
``expected`` / ``must_contain`` / ``must_not_contain``). ``TASK_SET_HASH`` —
sha256 канонического json.dumps всех задач (sort_keys=True), первые 12 hex.
"""
import hashlib
import json

# ---------------------------------------------------------------------------
# Гейт tools — 5 задач strict JSON (schema-валидация). Порог 1.0.
# ---------------------------------------------------------------------------
TOOLS_TASKS = [
    {
        "id": "tools-01-person",
        "gate": "tools",
        "prompt": (
            "Верни СТРОГО JSON-объект (без markdown-обёртки и пояснений) с "
            "полями: \"name\" (строка), \"age\" (целое число)."
        ),
        "max_tokens": 200,
        "schema": {"name": str, "age": int},
    },
    {
        "id": "tools-02-point",
        "gate": "tools",
        "prompt": (
            "Верни СТРОГО JSON-объект (без markdown) с полями: "
            "\"x\" (число с плавающей точкой), \"y\" (число с плавающей точкой), "
            "\"label\" (строка)."
        ),
        "max_tokens": 200,
        "schema": {"x": float, "y": float, "label": str},
    },
    {
        "id": "tools-03-nested",
        "gate": "tools",
        "prompt": (
            "Верни СТРОГО JSON-объект (без markdown). Внутри него поле "
            "\"user\" — объект с полями \"id\" (целое) и \"email\" (строка), "
            "и поле \"active\" (булево)."
        ),
        "max_tokens": 200,
        "schema": {
            "user": {"id": int, "email": str},
            "active": bool,
        },
    },
    {
        "id": "tools-04-array",
        "gate": "tools",
        "prompt": (
            "Верни СТРОГО JSON-объект (без markdown) с полем \"tags\" — "
            "массив строк, и полем \"count\" — целое число."
        ),
        "max_tokens": 200,
        "schema": {"tags": list, "count": int},
    },
    {
        "id": "tools-05-mixed",
        "gate": "tools",
        "prompt": (
            "Верни СТРОГО JSON-объект (без markdown) с полями: "
            "\"title\" (строка), \"items\" (массив целых чисел), "
            "\"enabled\" (булево)."
        ),
        "max_tokens": 200,
        "schema": {"title": str, "items": list, "enabled": bool},
    },
]

# ---------------------------------------------------------------------------
# Гейт build — 4 кодинг-задачи + 1 edit-задача. Порог 0.75.
# ---------------------------------------------------------------------------
BUILD_TASKS = [
    {
        "id": "build-01-add",
        "gate": "build",
        "prompt": (
            "Напиши одну Python-функцию с именем `add(a, b)`, которая "
            "возвращает сумму двух чисел. Верни ТОЛЬКО код функции, без "
            "пояснений и без markdown-обёртки."
        ),
        "max_tokens": 400,
        "tests": [((2, 3), 5), ((-1, 1), 0), ((0, 0), 0)],
    },
    {
        "id": "build-02-fib",
        "gate": "build",
        "prompt": (
            "Напиши одну Python-функцию с именем `fib(n)`, которая возвращает "
            "n-е число Фибоначчи (индексация с 0: fib(0)=0, fib(1)=1). Верни "
            "ТОЛЬКО код функции."
        ),
        "max_tokens": 400,
        "tests": [((0,), 0), ((1,), 1), ((2,), 1), ((10,), 55)],
    },
    {
        "id": "build-03-reverse",
        "gate": "build",
        "prompt": (
            "Напиши одну Python-функцию с именем `reverse_words(s)`, которая "
            "переворачивает порядок слов в строке (слова разделены пробелом). "
            "Верни ТОЛЬКО код функции."
        ),
        "max_tokens": 400,
        "tests": [
            (("hello world",), "world hello"),
            (("a b c",), "c b a"),
            (("single",), "single"),
        ],
    },
    {
        "id": "build-04-count",
        "gate": "build",
        "prompt": (
            "Напиши одну Python-функцию с именем `count_upper(s)`, которая "
            "возвращает количество заглавных букв в строке. Верни ТОЛЬКО код "
            "функции."
        ),
        "max_tokens": 400,
        "tests": [("Hello World", 2), ("ABC", 3), ("lowercase", 0)],
    },
    {
        "id": "build-05-edit",
        "gate": "build",
        "prompt": (
            "Дан код:\n"
            "```python\n"
            "def greet(name):\n"
            "    return \"Hello, \" + name\n"
            "```\n"
            "Исправь функцию так, чтобы она возвращала \"Hello, <name>!\" "
            "(с восклицательным знаком на конце). Верни ТОЛЬКО исправленный "
            "код функции."
        ),
        "max_tokens": 400,
        "must_contain": ["def greet", "return", "!"],
        "must_not_contain": ["print", "return \"Hello, \" + name\n"],
    },
]

# ---------------------------------------------------------------------------
# Гейт reasoning — 4 задачи с детерминированным ответом. Порог 0.70.
# ---------------------------------------------------------------------------
REASONING_TASKS = [
    {
        "id": "reasoning-01-math",
        "gate": "reasoning",
        "prompt": (
            "Ответь только итоговым значением (одним числом, без пояснений): "
            "сколько будет 17 * 6?"
        ),
        "max_tokens": 300,
        "expected": "102",
    },
    {
        "id": "reasoning-02-decompose",
        "gate": "reasoning",
        "prompt": (
            "Ответь только итоговым значением (одним числом, без пояснений): "
            "сколько раз буква «е» встречается в слове «переселение»?"
        ),
        "max_tokens": 300,
        "expected": "5",
    },
    {
        "id": "reasoning-03-trap",
        "gate": "reasoning",
        "prompt": (
            "Ответь только итоговым значением (одним словом, без пояснений): "
            "У фермера было 15 овец. Все, кроме 8, умерли. Сколько овец "
            "осталось?"
        ),
        "max_tokens": 300,
        "expected": "8",
    },
    {
        "id": "reasoning-04-compare",
        "gate": "reasoning",
        "prompt": (
            "Ответь только итоговым значением (одним словом, без пояснений): "
            "что тяжелее — килограмм ваты или килограмм железа?"
        ),
        "max_tokens": 300,
        "expected": "одинаково",
    },
]

# ---------------------------------------------------------------------------
# Гейт fast — 3 одинаковых минимальных ping-запроса. Порога нет.
# ---------------------------------------------------------------------------
FAST_TASKS = [
    {
        "id": "fast-01-ping",
        "gate": "fast",
        "prompt": "Reply with: OK",
        "max_tokens": 16,
        "expected": "ok",
    },
    {
        "id": "fast-02-ping",
        "gate": "fast",
        "prompt": "Reply with: OK",
        "max_tokens": 16,
        "expected": "ok",
    },
    {
        "id": "fast-03-ping",
        "gate": "fast",
        "prompt": "Reply with: OK",
        "max_tokens": 16,
        "expected": "ok",
    },
]

# Пороги прохождения гейтов (fast — None, информативный).
THRESHOLDS = {"tools": 1.0, "build": 0.75, "reasoning": 0.70, "fast": None}

ALL_TASKS = TOOLS_TASKS + BUILD_TASKS + REASONING_TASKS + FAST_TASKS

TASKS_BY_GATE = {
    "tools": TOOLS_TASKS,
    "build": BUILD_TASKS,
    "reasoning": REASONING_TASKS,
    "fast": FAST_TASKS,
}


def _json_default(obj):
    """Сериализует type-объекты (str/int/float/bool/list/dict) как имена."""
    if isinstance(obj, type):
        return obj.__name__
    raise TypeError(f"Object of type {obj.__class__.__name__} is not serializable")


def task_set_hash():
    """sha256 канонического дампа всех задач → первые 12 hex-символов."""
    canonical = json.dumps(
        ALL_TASKS, sort_keys=True, ensure_ascii=False, default=_json_default
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


TASK_SET_HASH = task_set_hash()
