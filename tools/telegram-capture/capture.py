"""capture.py — извлечение непомеченных постов из темы группы @inbox_tools.

Реализация [[02-Methods/tool-integration-pattern]]: Telethon через MTProto
детерминированно тянет посты из нужной темы, фильтрует уже помеченные
реакцией (📥/⚠️/категории) и отдаёт JSON на stdout для анализа librarian.
Если не передан --dry-run, на каждый извлечённый пост ставится 📥, чтобы
при следующем запуске не выдать его повторно.

Использование:
    python capture.py --topic Софт --limit 10
    python capture.py --topic ИИ --dry-run
"""
import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetForumTopicsRequest, SendReactionRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaWebPage,
    MessageReactions,
    ReactionEmoji,
)

import config

log = logging.getLogger("capture")  # лог идёт в stderr (см. basicConfig ниже)


def parse_args() -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Извлечь непомеченные посты из темы группы @inbox_tools.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        choices=config.TOPIC_NAMES,
        help="Название темы (точное совпадение, см. config.TOPIC_NAMES).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=config.DEFAULT_LIMIT,
        help=f"Сколько непомеченных постов извлечь (default {config.DEFAULT_LIMIT}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать что извлечётся, не ставить реакцию 📥.",
    )
    return parser.parse_args()


def _media_type(msg) -> str:
    """Определить тип медиа сообщения: photo / video / document / none."""
    media = msg.media
    if isinstance(media, MessageMediaPhoto):
        return "photo"
    if isinstance(media, MessageMediaDocument):
        # Документы Telegram покрывают video/video_note/voice/sticker/files.
        # Попытаемся уточнить по mime_type.
        mime = getattr(media.document, "mime_type", "") or ""
        if mime.startswith("video"):
            return "video"
        return "document"
    if isinstance(media, MessageMediaWebPage):
        return "webpage"
    return "none"


def _reactions_emojis(msg) -> set:
    """Собрать множество эмодзи реакций, проставленных на сообщении."""
    reactions = getattr(msg, "reactions", None)
    if not isinstance(reactions, MessageReactions):
        return set()
    emojis = set()
    for rc in reactions.results:
        # ReactionCount несёт .reaction (ReactionEmoji) и .count
        reaction = getattr(rc, "reaction", None)
        emoticon = getattr(reaction, "emoticon", None)
        if emoticon:
            emojis.add(emoticon)
    return emojis


def _is_processed(msg) -> bool:
    """true, если на сообщении стоит хотя бы одна «обработанная» реакция."""
    return bool(_reactions_emojis(msg) & config.PROCESSED_REACTIONS)


async def _resolve_topic_id(client, chat, topic_name: str) -> int | None:
    """Найти message_thread_id темы по точному имени.

    Для #General (special General topic) возвращаем 1, если он не пришёл в списке.
    """
    # #General — специальный топик форумов, id=1.
    if topic_name == "#General":
        return 1

    # GetForumTopicsRequest требует InputPeer, не entity.
    peer = await client.get_input_entity(chat)
    offset_id = 0
    while True:
        res = await client(GetForumTopicsRequest(
            peer=peer,
            offset_date=0,
            offset_id=offset_id,
            offset_topic=0,
            limit=100,
        ))
        for topic in res.topics:
            # ForumTopic объекты: forum_topic.id, forum_topic.title
            tid = getattr(topic, "id", None)
            title = getattr(topic, "title", None)
            if tid is not None and title == topic_name:
                return tid
        if not res.topics or len(res.topics) < 100:
            break
        offset_id = res.topics[-1].id
    return None


async def main() -> None:
    """Точка входа: извлечь посты, отдать JSON, пометить 📥."""
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="capture: %(message)s",
    )

    args = parse_args()

    # Проверка наличия credentials.
    if not config.API_ID or not config.API_HASH:
        print(
            "capture: ОШИБКА — в .env нет TELEGRAM_API_ID/TELEGRAM_API_HASH. "
            "См. .env.example.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        api_id = int(config.API_ID)
    except ValueError:
        print(
            f"capture: ОШИБКА — TELEGRAM_API_ID должен быть числом, "
            f"получено: {config.API_ID!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    client_kwargs = {}
    if config.PROXY:
        client_kwargs["proxy"] = config.PROXY
    client = TelegramClient(
        config.SESSION_NAME,
        api_id,
        config.API_HASH,
        **client_kwargs,
    )

    try:
        await client.start()
    except Exception as exc:  # noqa: BLE001 — падать с понятным сообщением
        print(
            f"capture: ОШИБКА авторизации — {exc}. Проверь .env и/или удали "
            f"{config.SESSION_NAME}.session и пройди авторизацию заново.",
            file=sys.stderr,
        )
        sys.exit(1)

    chat = None
    topic_id = None
    try:
        # 1. Найти группу по username.
        try:
            chat = await client.get_entity(config.CHAT_USERNAME)
        except Exception as exc:  # noqa: BLE001
            print(
                f"capture: ОШИБКА — группа @{config.CHAT_USERNAME} не найдена: {exc}",
                file=sys.stderr,
            )
            sys.exit(1)

        # 2. Найти id темы по имени.
        topic_id = await _resolve_topic_id(client, chat, args.topic)
        if topic_id is None:
            print(
                f"capture: ОШИБКА — тема {args.topic!r} не найдена в "
                f"@{config.CHAT_USERNAME}. Доступные: "
                f"{', '.join(config.TOPIC_NAMES)}",
                file=sys.stderr,
            )
            sys.exit(1)

        # 3. Берём сообщения с запасом (3x) — часть отфильтруем как обработанные.
        fetch_limit = max(args.limit * 3, args.limit + 10)
        log.info(
            "тема=%s topic_id=%s — запрашиваю до %d сообщений",
            args.topic, topic_id, fetch_limit,
        )
        messages = await client.get_messages(
            chat,
            reply_to=topic_id,
            limit=fetch_limit,
        )
        log.info("получено %d сообщений из темы", len(messages) if messages else 0)

        # 4. Фильтр: пропускаем сообщения с «обработанными» реакциями.
        unmarked = [m for m in (messages or []) if not _is_processed(m)]
        processed_count = (len(messages) if messages else 0) - len(unmarked)
        log.info(
            "отфильтровано %d обработанных, осталось %d непомеченных",
            processed_count, len(unmarked),
        )

        # 5. Берём первые limit непомеченных.
        selected = unmarked[: args.limit]
        log.info(
            "отбираю %d из %d непомеченных (limit=%d)",
            len(selected), len(unmarked), args.limit,
        )

        # 6. Формируем JSON-результат.
        results = []
        for m in selected:
            sender_name = ""
            try:
                sender = await m.get_sender()
                sender_name = getattr(sender, "title", None) or getattr(
                    sender, "first_name", None
                ) or getattr(sender, "username", None) or ""
            except Exception:  # noqa: BLE001 — sender опционален
                sender_name = ""
            link = f"https://t.me/{config.CHAT_USERNAME}/{m.id}"
            results.append({
                "message_id": m.id,
                "text": m.text or "",
                "date": m.date.isoformat() if m.date else "",
                "link": link,
                "media_type": _media_type(m),
                "sender_name": sender_name,
            })

        # 7. Печатаем результат в stdout (для разбора librarian).
        print(json.dumps(results, ensure_ascii=False, indent=2))

        # 8. Маркировка 📥 на каждый извлечённый пост (кроме dry-run).
        marked = 0
        if not args.dry_run and selected:
            peer = await client.get_input_entity(chat)
            for m in selected:
                try:
                    await client(SendReactionRequest(
                        peer=peer,
                        msg_id=m.id,
                        reaction=[ReactionEmoji(emoticon=config.EMOJI_MAP["ingested"])],
                    ))
                    marked += 1
                except FloodWaitError as fw:
                    print(
                        f"capture: FloodWait {fw.seconds}s — остановка маркировки.",
                        file=sys.stderr,
                    )
                    break
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"capture: не удалось поставить 📥 на msg {m.id}: {exc}",
                        file=sys.stderr,
                    )
            log.info("помечено 📥: %d", marked)
        elif args.dry_run:
            log.info("dry-run: реакции не ставятся")

    finally:
        try:
            await client.disconnect()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    asyncio.run(main())