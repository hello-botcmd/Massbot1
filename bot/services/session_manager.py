from telethon import TelegramClient
from telethon.sessions import StringSession

from config import API_HASH, API_ID


class SessionError(Exception):
    pass


async def validate(session_str):
    session_str = session_str.strip()
    if not session_str:
        raise SessionError("Empty session string.")
    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise SessionError("Session is not logged in / expired.")
        me = await client.get_me()
        if getattr(me, "bot", False):
            raise SessionError("Bot sessions are not allowed, user accounts only.")
        return me
    finally:
        await client.disconnect()
