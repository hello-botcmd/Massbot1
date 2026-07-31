import asyncio

from telethon import functions
from telethon.errors import FloodWaitError

from config import ONLINE_CHECK_INTERVAL
from .db import repo
from .telegram_client import get_client


async def keeper_loop():
    """Keeps every keep_online account online forever."""
    while True:
        try:
            async for acc in repo.accounts.find({"keep_online": True}):
                try:
                    cl = await get_client(acc)
                    await cl(functions.account.UpdateStatusRequest(offline=False))
                except FloodWaitError as e:
                    await asyncio.sleep(min(e.seconds, 60))
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(ONLINE_CHECK_INTERVAL)
