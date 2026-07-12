"""mark.py — простановка категорийной реакции на список сообщений.

Используется librarian после классификации постов, чтобы пометить категорию
(🐧 dotfiles, 🤖 SERPlux, 🌐 dv-hub, 🧠 VibeOS, 🎯 новый проект, ⚠️ error,
📥 ingested). Категорийная реакция заменяет промежуточную 📥 на нужный эмодзи.

Использование:
    python mark.py --message-ids 12 34 56 --category dotfiles
    python mark.py --message-ids 12 --category error --topic-id 3
"""
import argparse
import asyncio
import logging
import sys
import time

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

import config

log = logging.getLogger("mark")


def parse_args() -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Поставить категорийную реакцию на список сообщений "
        "в группе @inbox_tools.",
    )
    parser.add_argument(
        "--message-ids",
        required=True,
        nargs="+",
        type=int,
        help="ID сообщений (одно или несколько).",
    )
    parser.add_argument(
        "--category",
        required=True,
        choices=list(config.EMOJI_MAP.keys()),
        help="Категория реакции (см. config.EMOJI_MAP).",
    )
    parser.add_argument(
        "--topic-id",
        type=int,
        default=None,
        help="id темы (для корректного обращения к сообщению в форуме).",
    )
    return parser.parse_args()


async def main() -> None:
    """Точка входа: проставить реакцию на каждое сообщение."""
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="mark: %(message)s",
    )

    args = parse_args()

    if not config.API_ID or not config.API_HASH:
        print(
            "mark: ОШИБКА — в .env нет TELEGRAM_API_ID/TELEGRAM_API_HASH. "
            "См. .env.example.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        api_id = int(config.API_ID)
    except ValueError:
        print(
            f"mark: ОШИБКА — TELEGRAM_API_ID должен быть числом, "
            f"получено: {config.API_ID!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    emoji = config.EMOJI_MAP[args.category]
    log.info(
        "категория=%s → эмодзи=%s, сообщений=%d, topic_id=%s",
        args.category, emoji, len(args.message_ids), args.topic_id,
    )

    client_kwargs = {}
    if config.PROXY:
        client_kwargs["proxy"] = config.PROXY
    client = TelegramClient(config.SESSION_NAME, api_id, config.API_HASH, **client_kwargs)

    try:
        await client.start()
    except Exception as exc:  # noqa: BLE001
        print(
            f"mark: ОШИБКА авторизации — {exc}. Проверь .env и/или удали "
            f"{config.SESSION_NAME}.session.",
            file=sys.stderr,
        )
        sys.exit(1)

    chat = None
    marked = 0
    failed = []
    try:
        try:
            chat = await client.get_entity(config.CHAT_USERNAME)
        except Exception as exc:  # noqa: BLE001
            print(
                f"mark: ОШИБКА — группа @{config.CHAT_USERNAME} не найдена: {exc}",
                file=sys.stderr,
            )
            sys.exit(1)

        peer = await client.get_input_entity(chat)
        for mid in args.message_ids:
            try:
                await client(SendReactionRequest(
                    peer=peer,
                    msg_id=mid,
                    reaction=[ReactionEmoji(emoticon=emoji)],
                ))
                marked += 1
            except FloodWaitError as fw:
                print(
                    f"mark: FloodWait {fw.seconds}s на msg {mid} — "
                    f"жду и продолжаю со следующим.",
                    file=sys.stderr,
                )
                time.sleep(fw.seconds + 1)
                failed.append(mid)
                continue
            except Exception as exc:  # noqa: BLE001
                print(
                    f"mark: не удалось поставить {emoji} на msg {mid}: {exc}",
                    file=sys.stderr,
                )
                failed.append(mid)

        # stdout: человеко-читаемый итог для librarian.
        print(
            f"помечено: {marked}/{len(args.message_ids)} "
            f"(категория={args.category}, эмодзи={emoji})"
        )
        if failed:
            print(f"не удалось: {','.join(str(f) for f in failed)}")
        log.info("итог: помечено %d, ошибок %d", marked, len(failed))

    finally:
        try:
            await client.disconnect()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    asyncio.run(main())