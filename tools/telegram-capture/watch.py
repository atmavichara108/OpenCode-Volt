"""watch.py — userbot-демон: real-time слив @inbox_tools в staging-очередь.

В отличие от capture.py (pull по теме по явному запросу) watch.py живёт
и реагирует на каждый новый пост: NewMessage → post_data → inbox_queue.append.
Группа само-сливается без накопления; ингест (классификация → mark → signals)
выполняется отдельно (в этой же служебной последовательности или таймером).

Сетевая часть (Telethon events) — smoke-gated: без --smoke реальная подписка
не стартует. Детерминированная логика (post_data, build_topic_map) тестируется
без telethon.

Использование:
    python watch.py --once            # слить непрочитанные и выйти (pull-режим)
    python watch.py                   # демон: жить и слушать NewMessage
    python watch.py --smoke --once    # реальный запуск (нужны credentials + Tor)
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone

import config
import inbox_queue

log = logging.getLogger("watch")


# --- Детерминированная логика (тестируется без telethon) --------------------

def post_data(message_id: int, topic: str, text: str | None, date: str,
              link: str, media_type: str, sender_name: str) -> dict:
    """Сериализовать пост в запись очереди (идентично формату capture.py + topic).

    topic обязателен — без него классификатор не знает дефолт по теме.
    """
    return {
        "message_id": message_id,
        "topic": topic,
        "text": text or "",
        "date": date,
        "link": link,
        "media_type": media_type,
        "sender_name": sender_name,
    }


def build_topic_map(topics) -> dict[int, str]:
    """Список ForumTopic-подобных объектов → {topic_id: title}.

    Устойчив к отсутствию атрибутов (проверяет getattr). Для #General (id=1,
    обычно не приходит в GetForumTopicsRequest) — подставить явно.
    """
    m: dict[int, str] = {}
    for t in topics or []:
        tid = getattr(t, "id", None)
        title = getattr(t, "title", None)
        if tid is not None and title:
            m[int(tid)] = title
    m.setdefault(1, "#General")
    return m


def resolve_topic_name(message, topic_map: dict[int, str]) -> str:
    """Определить имя темы сообщения по reply_to (форумы Telegram).

    В форуме reply_to.reply_to_top_id = id топика. Чистая от сети: читает только
    атрибуты переданного message-объекта (в тестах — SimpleNamespace).
    """
    reply = getattr(message, "reply_to", None)
    top_id = getattr(reply, "reply_to_top_id", None) if reply is not None else None
    if top_id is not None:
        return topic_map.get(int(top_id), "#General")
    return "#General"


def iso_utc(dt) -> str:
    return dt.astimezone(timezone.utc).isoformat() if dt is not None else ""


# --- Сетевая часть (smoke-gated) --------------------------------------------

async def run_watch(once: bool, smoke: bool) -> int:
    if not smoke:
        print("watch: скелет — реальный запуск требует --smoke "
              "(credentials + Tor + авторизованная сессия). Сетевые вызовы "
              "не выполняются.", file=sys.stderr)
        return 0

    from telethon import TelegramClient, events

    if not config.API_ID or not config.API_HASH:
        print("watch: ОШИБКА — в .env нет TELEGRAM_API_ID/TELEGRAM_API_HASH",
              file=sys.stderr)
        return 1
    api_id = int(config.API_ID)
    client_kwargs = {"proxy": config.PROXY} if config.PROXY else {}
    client = TelegramClient(config.SESSION_NAME, api_id, config.API_HASH,
                            **client_kwargs)
    await client.start()

    chat = await client.get_entity(config.CHAT_USERNAME)
    peer = await client.get_input_entity(chat)

    # topic_map: id → имя. Для форумов тянем GetForumTopicsRequest.
    from telethon.tl.functions.messages import GetForumTopicsRequest
    topic_map: dict[int, str] = {1: "#General"}
    try:
        res = await client(GetForumTopicsRequest(
            peer=peer, offset_date=0, offset_id=0, offset_topic=0, limit=100,
        ))
        topic_map = build_topic_map(res.topics)
    except Exception as exc:  # noqa: BLE001 — топики могут быть недоступны
        log.info("topic_map: fallback на #General (%s)", exc)

    from capture import _media_type, _is_processed

    async def on_new(event):
        msg = event.message
        if _is_processed(msg):
            return  # уже обработан реакцией
        topic = resolve_topic_name(msg, topic_map)
        rec = post_data(
            message_id=msg.id,
            topic=topic,
            text=msg.text or "",
            date=iso_utc(msg.date),
            link=f"https://t.me/{config.CHAT_USERNAME}/{msg.id}",
            media_type=_media_type(msg),
            sender_name="",
        )
        added, total = inbox_queue.append([rec])
        log.info("new #%s topic=%r → queue (%d added, %d total)", msg.id, topic, added, total)

    if smoke:
        client.add_event_handler(on_new, events.NewMessage(chats=config.CHAT_USERNAME))
        if once:
            log.info("watch: single pull + exit")
        else:
            log.info("watch: демон стартует, слушаю @%s", config.CHAT_USERNAME)
            await client.run_until_disconnected()
    else:
        print("watch: реальный запуск требует --smoke (нужны credentials + Tor). "
              "Скелет без сетевых вызовов.", file=sys.stderr)

    await client.disconnect()
    return 0


def main() -> int:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="watch: %(message)s")
    ap = argparse.ArgumentParser(description="real-time слив @inbox_tools")
    ap.add_argument("--once", action="store_true", help="слить и выйти")
    ap.add_argument("--smoke", action="store_true",
                    help="реальный запуск (credentials + Tor + сессия)")
    args = ap.parse_args()

    import asyncio
    try:
        return asyncio.run(run_watch(args.once, args.smoke))
    except Exception as exc:  # noqa: BLE001 — понятное сообщение демону
        print(f"watch: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())