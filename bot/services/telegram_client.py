import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import API_HASH, API_ID

_clients = {}
_lock = asyncio.Lock()


async def get_client(account):
    uid = account["user_id"]
    async with _lock:
        cl = _clients.get(uid)
        if cl is None:
            cl = TelegramClient(StringSession(account["session"]), API_ID, API_HASH)
            await cl.connect()
            _clients[uid] = cl
        elif not cl.is_connected():
            await cl.connect()
        return cl


async def close_client(uid):
    async with _lock:
        cl = _clients.pop(uid, None)
        if cl:
            try:
                await cl.disconnect()
            except Exception:
                pass


async def close_all():
    for cl in list(_clients.values()):
        try:
            await cl.disconnect()
        except Exception:
            pass
    _clients.clear()


def connected_count():
    return sum(1 for c in _clients.values() if c.is_connected())


def name(acc):
    return f"@{acc.get('username')}" if acc.get("username") else (acc.get("name") or str(acc["user_id"]))
