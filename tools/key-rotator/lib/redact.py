import re

_KEY_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\brc-[a-f0-9]{20,}"),
    re.compile(r"\bmq[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)\bx-api-key[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"),
]

MASK = "***REDACTED***"


def redact(text: str, keys=None) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    for key in keys or []:
        if key and len(key) >= 8:
            text = text.replace(key, MASK)
    for pattern in _KEY_PATTERNS:
        text = pattern.sub(MASK, text)
    return text


def redact_obj(obj, keys=None):
    if isinstance(obj, str):
        return redact(obj, keys)
    if isinstance(obj, list):
        return [redact_obj(item, keys) for item in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v, keys) for k, v in obj.items()}
    return obj
