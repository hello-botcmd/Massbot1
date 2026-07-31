from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from config import DB_NAME, MONGO_URI


class AccountRepo:
    def __init__(self):
        self._client = AsyncIOMotorClient(MONGO_URI)
        self.accounts = self._client[DB_NAME]["accounts"]

    async def add(self, session, me):
        return await self.accounts.update_one(
            {"user_id": me.id},
            {"$set": {
                "session": session,
                "phone": getattr(me, "phone", "") or "",
                "username": getattr(me, "username", "") or "",
                "name": getattr(me, "first_name", "") or "",
                "added_at": datetime.utcnow().isoformat(),
                "mode": None, "mode_expired": False, "keep_online": False,
            }},
            upsert=True,
        )

    async def all(self):
        return [a async for a in self.accounts.find()]

    async def count(self):
        return await self.accounts.count_documents({})

    async def set_mode(self, uid, mode):
        await self.accounts.update_one(
            {"user_id": uid},
            {"$set": {"mode": mode, "mode_expired": False,
                      "mode_at": datetime.utcnow().isoformat()}},
        )

    async def set_mode_expired(self, uid):
        await self.accounts.update_one({"user_id": uid}, {"$set": {"mode_expired": True}})

    async def set_all_keep_online(self, flag):
        await self.accounts.update_many({}, {"$set": {"keep_online": flag}})


repo = AccountRepo()
