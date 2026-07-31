from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["➕ Add Account", "📢 Join"],
        ["🎛 Mode", "📊 Total Account"],
        ["❤️ Reaction", "👁 Views"],
        ["🟢 All Accounts Online"],
    ],
    resize_keyboard=True,
    is_persistent=True,
)


def inline(rows):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t, callback_data=c) for t, c in row] for row in rows]
    )
