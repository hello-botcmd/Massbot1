from telegram import Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from ..services import controls
from ..services.db import repo
from ..services.mode_manager import assign
from ..states import St
from ..utils.validators import parse_int
from .add_account import cancel


async def m_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send counts as: `mode1 mode2 mode3`\n"
        "e.g. `5 10 15`\n\n"
        "🎛 Mode 1 → online forever\n"
        "🎛 Mode 2 → online 2 min, then offline (last seen x time ago)\n"
        "🎛 Mode 3 → last seen hidden (shows 'recently')\n"
        "Distribution of which accounts get which mode is random.")
    return St.MODE_COUNTS


async def m_counts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.replace(",", " ").split()
    nums = [parse_int(p) for p in parts]
    if len(nums) != 3 or any(x is None or x < 0 for x in nums):
        await update.message.reply_text("Send exactly 3 numbers (e.g. `5 10 15`):")
        return St.MODE_COUNTS
    accounts = await repo.all()
    if not accounts:
        await update.message.reply_text("❌ No accounts added yet.")
        return ConversationHandler.END
    await update.message.reply_text(
        f"🎛 Assigning → Mode1: {nums[0]} | Mode2: {nums[1]} | Mode3: {nums[2]} (random)\n"
        "/stop to cancel")

    async def progress(text):
        await update.message.reply_text(text)

    controls.track(assign(accounts, nums[0], nums[1], nums[2], progress))
    return ConversationHandler.END


mode_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🎛 Mode$"), m_start)],
    states={St.MODE_COUNTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, m_counts)]},
    fallbacks=[CommandHandler("cancel", cancel)],
    name="mode",
)
