import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram bot token (from @BotFather) ──────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ── Owner / Admins (edit directly, or override via .env) ──
OWNER_IDS = [int(i) for i in os.getenv("OWNER_IDS", "123456789").split(",") if i]
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i]

# ── MongoDB (motor) ────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "telegram_manager")

# ── Telethon API credentials (my.telegram.org) ─────────
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")

# ── Behaviour tuning ───────────────────────────────────
MODE2_SECONDS = 120            # mode-2: online duration before going offline
MODE_CHECK_INTERVAL = 25       # mode enforcer loop interval (seconds)
ONLINE_CHECK_INTERVAL = 40     # keep-online loop interval (seconds)
BOOST_PROGRESS_EVERY = 5       # progress message every N boosts
