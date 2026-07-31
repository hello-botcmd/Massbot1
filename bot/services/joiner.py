import asyncio

from telethon import functions
from telethon.errors import FloodWaitError

from ..utils.validators import clean_chat_input, invite_hash, is_public
from . import controls
from .telegram_client import get_client, name


async def join_all(accounts, chat_input, min_d, max_d, progress):
    chat = clean_chat_input(chat_input)
    public = is_public(chat)
    hsh = invite_hash(chat)
    ok = fail = 0
    for i, acc in enumerate(accounts, start=1):
        if controls.is_stopped():
            break
        delay = min_d if i % 2 == 1 else max_d  # alternate min, max, min, max…
        try:
            cl = await get_client(acc)
            if public:
                entity = await cl.get_entity(chat)
                await cl(functions.channels.JoinChannelRequest(entity))
            else:
                await cl(functions.messages.ImportChatInviteRequest(hsh))
            ok += 1
            await progress(f"✅ {name(acc)} joined")
        except FloodWaitError as e:
            fail += 1
            await progress(f"⏳ Flood wait {e.seconds}s on {name(acc)}")
            await asyncio.sleep(min(e.seconds, 300))
        except Exception as e:
            fail += 1
            await progress(f"❌ {name(acc)}: {str(e)[:70]}")
        await asyncio.sleep(delay)
    await progress(f"📊 Join finished → ✅ {ok} | ❌ {fail}")
