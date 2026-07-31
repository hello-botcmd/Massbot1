from telegram import Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from ..services.db import repo
from ..services.session_manager import SessionError, validate
from ..states import St
from ..utils.keyboard import inline
from ..utils.validators import parse_int


async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose add method:",
        reply_markup=inline([[("✏️ Single", "add_single"), ("📚 Bulk", "add_bulk")]]),
    )
    return St.ADD_METHOD


async def choose_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "add_single":
        await q.edit_message_text("Send the session string:")
        return St.SINGLE_SESSION
    await q.edit_message_text("How many accounts to add?")
    return St.BULK_COUNT


async def single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        me = await validate(text)
        await repo.add(text, me)
        await update.message.reply_text(f"✅ Added @{me.username or me.id}")
    except SessionError as e:
        await update.message.reply_text(f"❌ {e}\nTry again or /cancel")
        return St.SINGLE_SESSION
    return ConversationHandler.END


async def bulk_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = parse_int(update.message.text)
    if not n or n < 1 or n > 500:
        await update.message.reply_text("Enter a valid number (1–500):")
        return St.BULK_COUNT
    context.user_data["bulk"] = {"total": n, "done": 0, "ok": 0}
    await update.message.reply_text(f"Send session string 1/{n}:")
    return St.BULK_SESSION


async def bulk_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data["bulk"]
    d["done"] += 1
    try:
        me = await validate(update.message.text)
        await repo.add(update.message.text.strip(), me)
        d["ok"] += 1
        await update.message.reply_text(f"✅ {d['done']}/{d['total']} — @{me.username or me.id}")
    except SessionError as e:
        await update.message.reply_text(f"❌ {e}")
    if d["done"] >= d["total"]:
        await update.message.reply_text(
            f"📊 Bulk add finished → ✅ {d['ok']} | ❌ {d['total'] - d['ok']}")
        return ConversationHandler.END
    await update.message.reply_text(f"Send session string {d['done'] + 1}/{d['total']}:")
    return St.BULK_SESSION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END


add_account_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^➕ Add Account$"), start_add)],
    states={
        St.ADD_METHOD: [CallbackQueryHandler(choose_method, pattern="^add_(single|bulk)$")],
        St.SINGLE_SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, single)],
        St.BULK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_count)],
        St.BULK_SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_session)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="add_account",
)
