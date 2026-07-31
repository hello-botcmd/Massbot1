import asyncio

from telethon import functions, types
from telethon.errors import FloodWaitError

from . import controls
from .telegram_client import get_client, name


async def boost(accounts, chat, msg_id, reactions, progress):
    ok = fail = 0
    for acc in accounts:
        if controls.is_stopped():
            break
        try:
            cl = await get_client(acc)
            peer = await cl.get_entity(chat)
            msg = await cl.get_messages(peer, ids=msg_id)
            if msg is None:
                raise ValueError("Post not found")
            await cl(functions.messages.SendReactionRequest(
                peer=peer,
                msg_id=msg_id,
                reaction=[types.ReactionEmoji(emoticon=r) for r in reactions],
                add_to_recent=False,
            ))
            ok += 1
        except FloodWaitError as e:
            fail += 1
            await progress(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(min(e.seconds, 300))
        except Exception as e:
            fail += 1
            await progress(f"❌ {name(acc)}: {str(e)[:70]}")
        await asyncio.sleep(1)  # 1s gap between each reaction
    await progress(f"📊 Reactions done → ✅ {ok} | ❌ {fail}")
