"""Детерминированные градеры ответов модели. БЕЗ LLM-судей.

Все градеры — чистые функции (кроме ``grade_build``, который запускает код
модели в отдельном subprocess). Ни один градер не бросает наружу — при любой
ошибке возвращает ``False``.
"""
import json
import logging
import os
import subprocess
import sys
import tempfile

log = logging.getLogger("model-bench")

# Время жизни одного subprocess-прогона кода модели.
BUILD_TIMEOUT_SECONDS = 10


def _extract_json(text):
    """Достаёт JSON-объект из ответа (снимает ```json fences если есть)."""
    if text is None:
        return None
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        # Попытка вырезать первый {...} блок (на случай пояснений вокруг).
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(t[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _check_value(value, expected_type):
    """Проверяет соответствие значения ожидаемому типу/схеме."""
    if expected_type is list:
        return isinstance(value, list)
    if expected_type is dict:
        return isinstance(value, dict)
    if isinstance(expected_type, dict):
        if not isinstance(value, dict):
            return False
        return all(
            k in value and _check_value(value[k], t)
            for k, t in expected_type.items()
        )
    if expected_type is float:
        # int допустим как float (число с плавающей точкой).
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, expected_type)


def grade_tools(reply, schema):
    """Проверяет строгий JSON-ответ по схеме.

    Требует: валидный JSON, все обязательные ключи с верными типами, БЕЗ
    лишних ключей. ``bool`` — подкласс ``int``, поэтому он отсекается явно.
    """
    data = _extract_json(reply)
    if not isinstance(data, dict):
        return False
    if set(data.keys()) != set(schema.keys()):
        return False
    return all(_check_value(data[k], schema[k]) for k in schema)


def _extract_python(text):
    """Достаёт python-код из ответа: снимает fences или возвращает весь текст."""
    if text is None:
        return ""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            # снимаем язык после ```
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return t


def grade_build(reply, tests):
    """Прогоняет код модели в отдельном subprocess и проверяет пары (args, expected).

    Безопасность: код НИКОГДА не exec в текущем процессе — только в дочернем
    ``sys.executable`` с временным cwd, timeout, минимальным env без
    прокси/ключей. Любой таймаут/исключение/несовпадение → False.
    """
    code = _extract_python(reply)
    if not code:
        return False

    harness = _harness_with_function_discovery(code, tests)
    env = _minimal_env()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(tmp, "harness.py")
            with open(script, "w", encoding="utf-8") as fh:
                fh.write(harness)
            proc = subprocess.run(
                [sys.executable, script],
                cwd=tmp,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=BUILD_TIMEOUT_SECONDS,
                text=True,
            )
            return proc.returncode == 0
    except (subprocess.TimeoutExpired, OSError):  # noqa: BLE001
        return False
    except Exception:  # noqa: BLE001
        return False


def _harness_with_function_discovery(code, tests):
    lines = [
        "import sys",
        "ns = {}",
        f"exec(compile({code!r}, '<model>', 'exec'), ns)",
        "candidates = [v for k, v in ns.items() if callable(v) and k != '__builtins__']",
        "if not candidates:",
        "    sys.exit(1)",
        "func = candidates[0]",
        f"tests = {tests!r}",
        "for args, expected in tests:",
        "    if isinstance(args, tuple):",
        "        got = func(*args)",
        "    else:",
        "        got = func(args)",
        "    if got != expected:",
        "        sys.exit(1)",
        "sys.exit(0)",
    ]
    return "\n".join(lines) + "\n"


def _minimal_env():
    """Минимальное окружение для subprocess: без прокси и API-ключей."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": "/tmp",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    # Копируем только безопасные локальные настройки; *_API_KEY/*_PROXY/*
    # остаются вне окружения — код модели их не увидит.
    for k in ("LANG", "LC_ALL"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


def grade_build_edit(reply, must_contain, must_not_contain):
    """Проверяет точечную правку по golden-подстрокам."""
    code = _extract_python(reply)
    if not code:
        return False
    return all(sub in code for sub in must_contain) and not any(
        sub in code for sub in must_not_contain
    )


def _normalize(text):
    """Нормализация: strip, lower, убрать trailing точку и лишние пробелы."""
    if text is None:
        return ""
    t = str(text).strip().lower()
    t = " ".join(t.split())
    while t.endswith(".") or t.endswith("。"):
        t = t[:-1].rstrip()
    return t


def grade_reasoning(reply, expected):
    """Проверяет ответ точным совпадением после нормализации.

    Если модель вывела рассуждения, берётся последняя непустая строка.
    """
    if reply is None:
        return False
    lines = [ln.strip() for ln in reply.splitlines() if ln.strip()]
    if not lines:
        return False
    candidate = lines[-1]
    return _normalize(candidate) == _normalize(expected)
