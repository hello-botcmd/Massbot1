from telethon import functions, types
from telegram import Update
from telegram.ext import ContextTypes

from ..services import controls
from ..services.db import repo
from ..services.telegram_client import get_client
from ..utils.decorators import authorized
from ..utils.validators import clean_chat_input


def _peer(chat):
    s = str(chat)
    if s.startswith("-100"):
        return types.PeerChannel(int(s[4:]))
    if s.startswith("-"):
        return types.PeerChat(int(s[1:]))
    return None


@authorized
async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    controls.stop_all()
    await repo.set_all_keep_online(False)
    await update.message.reply_text("🛑 Stopped all ongoing processes and disabled keep-online.")


@authorized
async def remove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove <chat id | @username | t.me link>")
        return
    chat = clean_chat_input(context.args[0])
    accounts = await repo.all()
    peer = None
    try:
        peer = _peer(chat)
    except (ValueError, TypeError):
        pass
    ok = fail = 0
    for acc in accounts:
        try:
            cl = await get_client(acc)
            if peer:
                await cl(functions.channels.LeaveChannelRequest(peer))
            else:
                entity = await cl.get_entity(chat)
                try:
                    await cl(functions.channels.LeaveChannelRequest(entity))
                except Exception:
                    await cl(functions.messages.LeaveChatRequest(await cl.get_input_entity(chat)))
            ok += 1
        except Exception:
            fail += 1
    await update.message.reply_text(
        f"🗑 Removed {ok} account(s) from {chat} | ❌ failed: {fail}")
