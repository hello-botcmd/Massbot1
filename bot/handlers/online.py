from telegram import Update
from telegram.ext import ContextTypes

from ..services.db import repo
from ..utils.decorators import authorized


@authorized
async def online_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await repo.set_all_keep_online(True)
    await update.message.reply_text(
        "🟢 All accounts will be kept online forever.\n"
        "The bot constantly re-checks so no account goes offline.\n"
        "Use /stop to turn this off.")
