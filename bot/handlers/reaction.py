from telegram import Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from ..services import controls
from ..services.db import repo
from ..services.reaction_booster import boost
from ..states import St
from ..utils.validators import parse_int, parse_post
from .add_account import cancel


async def r_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the post link (public or private):\nhttps://t.me/channel/123")
    return St.REACT_LINK


async def r_link_got(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, mid = parse_post(update.message.text)
    if not chat or not mid:
        await update.message.reply_text("❌ Invalid post link. Try again:")
        return St.REACT_LINK
    context.user_data["react"] = {"chat": chat, "mid": mid}
    await update.message.reply_text("How many accounts should react?")
    return St.REACT_COUNT


async def r_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = parse_int(update.message.text)
    if not n or n < 1:
        await update.message.reply_text("Enter a valid number:")
        return St.REACT_COUNT
    context.user_data["react"]["count"] = n
    await update.message.reply_text("Send reaction(s), space separated, e.g.:\n❤️ 🥰")
    return St.REACT_EMOJI


async def r_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emojis = update.message.text.split()
    if not emojis:
        await update.message.reply_text("Send at least one reaction:")
        return St.REACT_EMOJI
    d = context.user_data["react"]
    accounts = (await repo.all())[:d["count"]]
    if not accounts:
        await update.message.reply_text("❌ No accounts.")
        return ConversationHandler.END
    await update.message.reply_text(
        f"❤️ Reacting on {d['chat']}/{d['mid']} with {' '.join(emojis)}\n"
        f"1s gap between reactions · /stop to cancel")

    async def progress(text):
        await update.message.reply_text(text)

    controls.track(boost(accounts, d["chat"], d["mid"], emojis, progress))
    return ConversationHandler.END


reaction_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^❤️ Reaction$"), r_link)],
    states={
        St.REACT_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, r_link_got)],
        St.REACT_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, r_count)],
        St.REACT_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, r_emoji)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="reaction",
)
