from functools import wraps
from config import OWNER_IDS, ADMIN_IDS

AUTHORIZED = set(OWNER_IDS) | set(ADMIN_IDS)


def authorized(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if user is None or user.id not in AUTHORIZED:
            await update.effective_message.reply_text("⛔ Unauthorized.")
            return None
        return await func(update, context, *args, **kwargs)
    return wrapper
