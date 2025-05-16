import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT, AUTH_TTL_SECONDS, PENDING_INTENT_TTL_SECONDS


class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
        )

    # --- AUTHENTICATION ---

    async def is_authenticated(self, user_id: str) -> bool:
        value = await self.client.get(f"auth:{user_id}")
        return value == "true"

    async def set_authenticated(self, user_id: str, ttl: int = AUTH_TTL_SECONDS):
        await self.client.set(f"auth:{user_id}", "true", ex=ttl)

    async def clear_authenticated(self, user_id: str):
        await self.client.delete(f"auth:{user_id}")

    # --- PENDING INTENT ---

    async def set_pending_intent(
        self, user_id: str, intent: str, ttl: int = PENDING_INTENT_TTL_SECONDS
    ):
        await self.client.set(f"pending_intent:{user_id}", intent, ex=ttl)

    async def get_pending_intent(self, user_id: str) -> str | None:
        return await self.client.get(f"pending_intent:{user_id}")

    async def clear_pending_intent(self, user_id: str):
        await self.client.delete(f"pending_intent:{user_id}")
