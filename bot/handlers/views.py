from telegram import Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from ..services import controls
from ..services.db import repo
from ..services.view_booster import boost_many
from ..states import St
from ..utils.validators import parse_int, parse_post
from .add_account import cancel


async def v_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send post link(s) — one or multiple, separated by spaces / commas / new lines:\n"
        "https://t.me/channel/123 https://t.me/channel/456")
    return St.VIEW_LINK


async def v_link_got(update: Update, context: ContextTypes.DEFAULT_TYPE):
    posts = []
    for tok in update.message.text.replace(",", " ").split():
        chat, mid = parse_post(tok)
        if chat and mid:
            posts.append((chat, mid))
    if not posts:
        await update.message.reply_text("❌ No valid post links found. Try again:")
        return St.VIEW_LINK
    context.user_data["views"] = posts
    await update.message.reply_text(f"📄 {len(posts)} post(s) found. How many views per post?")
    return St.VIEW_COUNT


async def v_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = parse_int(update.message.text)
    if not n or n < 1:
        await update.message.reply_text("Enter a valid number:")
        return St.VIEW_COUNT
    accounts = await repo.all()
    if not accounts:
        await update.message.reply_text("❌ No accounts.")
        return ConversationHandler.END
    await update.message.reply_text(
        f"👁 Boosting {n} views on {len(context.user_data['views'])} post(s), "
        f"simultaneously, 1s gap between each view…\n/stop to cancel")

    async def progress(text):
        await update.message.reply_text(text)

    controls.track(boost_many(accounts, context.user_data["views"], n, progress))
    return ConversationHandler.END


views_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^👁 Views$"), v_link)],
    states={
        St.VIEW_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, v_link_got)],
        St.VIEW_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, v_count)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="views",
)
