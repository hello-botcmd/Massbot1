from telegram import Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from ..services import controls
from ..services.db import repo
from ..services.joiner import join_all
from ..states import St
from ..utils.validators import clean_chat_input, parse_int
from .add_account import cancel


async def j_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send channel/group link or username\n"
        "(public or private: https://t.me/+hash, t.me/joinchat/hash, @username):")
    return St.JOIN_LINK


async def j_link_got(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["join_link"] = clean_chat_input(update.message.text)
    await update.message.reply_text("How many accounts to join?")
    return St.JOIN_COUNT


async def j_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = parse_int(update.message.text)
    if not n or n < 1:
        await update.message.reply_text("Enter a valid number:")
        return St.JOIN_COUNT
    context.user_data["join_count"] = n
    await update.message.reply_text("Enter MIN delay in seconds (e.g. 1):")
    return St.JOIN_MIN


async def j_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    v = parse_int(update.message.text)
    if v is None:
        await update.message.reply_text("Enter a number:")
        return St.JOIN_MIN
    context.user_data["join_min"] = v
    await update.message.reply_text("Enter MAX delay in seconds (e.g. 8):")
    return St.JOIN_MAX


async def j_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    v = parse_int(update.message.text)
    if v is None:
        await update.message.reply_text("Enter a number:")
        return St.JOIN_MAX
    d = context.user_data
    accounts = (await repo.all())[:d["join_count"]]
    if not accounts:
        await update.message.reply_text("❌ No accounts added yet.")
        return ConversationHandler.END
    await update.message.reply_text(
        f"🚀 Joining {len(accounts)} accounts to {d['join_link']}\n"
        f"delays alternate {d['join_min']}s / {v}s → account1 at {d['join_min']}s, "
        f"account2 at {v}s, account3 at {d['join_min']}s…\n/stop to cancel")

    async def progress(text):
        await update.message.reply_text(text)

    controls.track(join_all(accounts, d["join_link"], d["join_min"], v, progress))
    return ConversationHandler.END


join_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📢 Join$"), j_link)],
    states={
        St.JOIN_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, j_link_got)],
        St.JOIN_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, j_count)],
        St.JOIN_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, j_min)],
        St.JOIN_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, j_max)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="join",
)
