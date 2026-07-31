from telegram import Update
from telegram.ext import ContextTypes

from ..services.db import repo
from ..services.telegram_client import connected_count
from ..utils.decorators import authorized


@authorized
async def status_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await repo.count()
    online = await repo.accounts.count_documents({"keep_online": True})
    m1 = await repo.accounts.count_documents({"mode": "1"})
    m2 = await repo.accounts.count_documents({"mode": "2"})
    m3 = await repo.accounts.count_documents({"mode": "3"})
    await update.message.reply_text(
        f"📊 Total accounts added: {total}\n"
        f"🟢 Active (connected now): {connected_count()}\n"
        f"🔁 Keep-online (all online): {online}\n"
        f"🎛 Mode1: {m1} | Mode2: {m2} | Mode3: {m3}")
