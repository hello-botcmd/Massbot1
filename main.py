import asyncio
import logging
import warnings

from telegram import BotCommand, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from bot.handlers.add_account import add_account_conv
from bot.handlers.admin import remove_cmd, stop_cmd
from bot.handlers.join import join_conv
from bot.handlers.mode import mode_conv
from bot.handlers.online import online_msg
from bot.handlers.reaction import reaction_conv
from bot.handlers.start import start
from bot.handlers.status import status_msg
from bot.handlers.views import views_conv
from bot.services.mode_manager import enforcer_loop
from bot.services.online_keeper import keeper_loop
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telethon").setLevel(logging.WARNING)

# silence PTB UserWarnings that only clutter the console
warnings.filterwarnings("ignore", category=UserWarning, module="telegram.ext")

COMMANDS = [
    BotCommand("start", "Main menu"),
    BotCommand("stop", "Stop any ongoing process"),
    BotCommand("remove", "Remove joined accounts from a chat: /remove <chat id>"),
    BotCommand("cancel", "Cancel current flow"),
]


async def post_init(app):
    asyncio.create_task(keeper_loop())
    asyncio.create_task(enforcer_loop())
    await app.bot.set_my_commands(COMMANDS)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    for conv in (add_account_conv, join_conv, mode_conv, reaction_conv, views_conv):
        app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex("^📊 Total Account$"), status_msg))
    app.add_handler(MessageHandler(filters.Regex("^🟢 All Accounts Online$"), online_msg))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("remove", remove_cmd))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
