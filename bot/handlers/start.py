from telegram import Update
from telegram.ext import ContextTypes

from ..utils.decorators import authorized
from ..utils.keyboard import MAIN_MENU


@authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Telegram Manager Bot\n\n"
        "Use the menu below:\n"
        "➕ Add Account · 📢 Join · 🎛 Mode · 📊 Total · ❤️ Reaction · 👁 Views · 🟢 Online\n"
        "Commands: /stop (stop processes) · /remove <chat id> (leave a chat)",
        reply_markup=MAIN_MENU,
    )
