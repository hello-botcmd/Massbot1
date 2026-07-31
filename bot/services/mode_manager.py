import asyncio
import random
from datetime import datetime

from telethon import functions
from telethon.errors import FloodWaitError

from config import MODE2_SECONDS, MODE_CHECK_INTERVAL
from . import controls
from .db import repo
from .telegram_client import get_client, name


async def status(client, offline=False, hidden=None):
    kwargs = {"offline": offline}
    if hidden is not None:
        kwargs["hidden"] = hidden
    await client(functions.account.UpdateStatusRequest(**kwargs))


async def apply_mode(acc, mode):
    cl = await get_client(acc)
    # always reset old state first (unhides a previous mode-3, re-onlines a mode-2)
    await status(cl, offline=False, hidden=False)
    if mode == "1":                       # online forever
        await status(cl, offline=False, hidden=False)
    elif mode == "2":                     # online 2 min, then offline
        await status(cl, offline=False, hidden=False)
    elif mode == "3":                     # hide last seen → "last seen recently"
        await status(cl, offline=False, hidden=True)
    await repo.set_mode(acc["user_id"], mode)


async def assign(accounts, c1, c2, c3, progress):
    random.shuffle(accounts)                       # random distribution
    plan = (["1"] * c1 + ["2"] * c2 + ["3"] * c3)[:len(accounts)]
    for acc, mode in zip(accounts, plan):
        if controls.is_stopped():
            break
        try:
            await apply_mode(acc, mode)
            await progress(f"🎛 {name(acc)} → Mode {mode}")
        except FloodWaitError as e:
            await progress(f"⏳ Flood wait {e.seconds}s — pausing")
            await asyncio.sleep(min(e.seconds, 300))
        except Exception as e:
            await progress(f"❌ {name(acc)}: {str(e)[:70]}")
        await asyncio.sleep(2)
    await progress("🎛 Mode assignment finished.")


async def enforcer_loop():
    """Keeps every assigned mode enforced (mode-2 offline transition included)."""
    while True:
        try:
            async for acc in repo.accounts.find({"mode": {"$ne": None}}):
                try:
                    cl = await get_client(acc)
                    mode = acc.get("mode")
                    if mode == "1":
                        await status(cl, offline=False, hidden=False)
                    elif mode == "2" and not acc.get("mode_expired"):
                        try:
                            t = datetime.fromisoformat(acc.get("mode_at"))
                        except Exception:
                            t = datetime.utcnow()
                        if (datetime.utcnow() - t).total_seconds() >= MODE2_SECONDS:
                            await status(cl, offline=True)          # "last seen x time ago"
                            await repo.set_mode_expired(acc["user_id"])
                        else:
                            await status(cl, offline=False, hidden=False)
                    elif mode == "3":
                        await status(cl, offline=False, hidden=True)
                except FloodWaitError as e:
                    await asyncio.sleep(min(e.seconds, 60))
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(MODE_CHECK_INTERVAL)
