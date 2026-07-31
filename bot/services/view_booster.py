import asyncio

from telethon import functions
from telethon.errors import FloodWaitError

from config import BOOST_PROGRESS_EVERY
from . import controls
from .telegram_client import get_client


async def boost_one(accounts, chat, msg_id, count, progress, tag):
    ok = fail = 0
    for n in range(count):
        if controls.is_stopped():
            break
        acc = accounts[n % len(accounts)]
        try:
            cl = await get_client(acc)
            peer = await cl.get_entity(chat)
            await cl.get_messages(peer, ids=msg_id)
            try:
                await cl(functions.messages.GetMessagesViewsRequest(
                    peer=peer, id=[msg_id], increment=True))
            except TypeError:
                await cl(functions.messages.GetMessagesViewsRequest(
                    peer=peer, id=[msg_id]))
            ok += 1
        except FloodWaitError as e:
            fail += 1
            await asyncio.sleep(min(e.seconds, 300))
        except Exception:
            fail += 1
        if (n + 1) % BOOST_PROGRESS_EVERY == 0:
            await progress(f"{tag} → {n + 1}/{count} views")
        await asyncio.sleep(1)  # 1s gap between each view
    await progress(f"{tag} → done ✅ {ok} | ❌ {fail}")


async def boost_many(accounts, posts, count, progress):
    # each post boosted simultaneously, 1s gap inside each post's loop
    await asyncio.gather(*[
        boost_one(accounts, chat, mid, count, progress, f"📄 post {i + 1}")
        for i, (chat, mid) in enumerate(posts)
    ])
