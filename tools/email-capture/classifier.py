"""Классификация писем по контрольным фразам интентов (детерминированная).

Каскад (приоритет сверху вниз):
    error/noise → research → implementation → correction → projects
    → subscriptions → default

Матч — `re.IGNORECASE` по нормализованной конкатенации `subject + " " + body`.
Дедуп — по Message-ID и по text-signature (первые 200 символов нормализованного
текста). Никакой сетки и ML: только фразы из `config.INTENT_PHRASES`.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Iterable, Mapping

import config

# --- нормализация ----------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")
_MD_RE = re.compile(r"[*_`#>~\[\]()!|]")
_WS_RE = re.compile(r"\s+")


class _TextExtractor(HTMLParser):
    """HTML → видимый текст (без script/style)."""

    _SKIP = {"script", "style", "head", "title"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: D102
        if tag in self._SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:  # noqa: D102
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:  # noqa: D102
        if not self._skip_depth:
            self._chunks.append(data)

    def text(self) -> str:
        return " ".join(self._chunks)


def html_to_text(html: str) -> str:
    """Снять HTML-теги (оставив текст), не ломаясь на битой разметке."""
    if not html:
        return ""
    parser = _TextExtractor()
    try:
        parser.feed(html)
        parser.close()
        return parser.text()
    except Exception:  # noqa: BLE001 — битый HTML не должен валить классификацию
        return _TAG_RE.sub(" ", html)


def normalize(text: str) -> str:
    """Нижний регистр, без HTML/markdown-разметки, одинарные пробелы."""
    if not text:
        return ""
    text = html_to_text(text)
    text = text.replace("\xa0", " ")
    text = _MD_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip().lower()


# --- компиляция паттернов (один раз) ---------------------------------------

_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    intent: [re.compile(re.escape(phrase), re.IGNORECASE) for phrase in phrases]
    for intent, phrases in config.INTENT_PHRASES.items()
}


# --- ключи дедупа ----------------------------------------------------------

SIGNATURE_LEN = 200


def message_id_of(message: Mapping) -> str:
    """Message-ID письма (несколько источников key-названий, иначе '')."""
    for key in ("message_id", "Message-ID", "message-id", "id"):
        val = message.get(key)
        if val:
            return str(val).strip()
    return ""


def text_of(message: Mapping) -> str:
    """Сырой текст письма: отдельный `text` либо subject+body."""
    if message.get("text"):
        return str(message["text"])
    subject = message.get("subject") or ""
    body = message.get("body") or message.get("body_text") or ""
    return f"{subject}\n{body}"


def text_signature(message: Mapping) -> str:
    """Подпись текста: первые 200 символов нормализованной конкатенации."""
    return normalize(text_of(message))[:SIGNATURE_LEN]


def dedup(messages: Iterable[Mapping]) -> list[dict]:
    """Снять дубли: сначала по Message-ID, затем по text-signature.

    Порядок входа сохраняется; первый встреченный экземпляр остаётся.
    Письма без Message-ID дедупятся только по подписи текста.
    """
    out: list[dict] = []
    seen_ids: set[str] = set()
    seen_sigs: set[str] = set()
    for message in messages:
        record = dict(message)
        mid = message_id_of(record)
        if mid and mid in seen_ids:
            continue
        sig = text_signature(record)
        if sig and sig in seen_sigs:
            continue
        if mid:
            seen_ids.add(mid)
        if sig:
            seen_sigs.add(sig)
        out.append(record)
    return out


# --- классификация ---------------------------------------------------------

def classify_text(text: str) -> str:
    """Каскад контрольных фраз → intent. Детерминированно для одного текста."""
    normalized = normalize(text)
    if not normalized:
        return config.DEFAULT_INTENT
    for intent in config.CASCADE:
        for pattern in _PATTERNS.get(intent, ()):
            if pattern.search(normalized):
                return intent
    return config.DEFAULT_INTENT


def classify(message: Mapping) -> str:
    """`classify(message) -> intent` по subject + body (см. модуль)."""
    subject = str(message.get("subject") or "")
    body = str(message.get("body") or message.get("body_text") or "")
    return classify_text(f"{subject}\n{body}")


def classify_batch(messages: Iterable[Mapping]) -> list[dict]:
    """Дедуп + классификация: на выходе записи с полем `intent`."""
    return [dict(m, intent=classify(m)) for m in dedup(messages)]
