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
        return value == "True"

    async def set_authenticated(self, user_id: str, ttl: int = AUTH_TTL_SECONDS):
        await self.client.set(f"auth:{user_id}", "True", ex=ttl)

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

    # --- INTERACTION TRACKING ---

    async def increment_interaction_count(self, user_id: str) -> int:
        return await self.client.incr(f"interactions:{user_id}")

    async def get_interaction_count(self, user_id: str) -> int:
        value = await self.client.get(f"interactions:{user_id}")
        return int(value) if value is not None else 0

    async def reset_interaction_count(self, user_id: str):
        await self.client.delete(f"interactions:{user_id}")

    # --- GENERIC OPERATIONS ---

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        await self.client.set(key, value, ex=ex)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def set_json(self, key: str, value: dict, ex: int | None = None):
        import json

        await self.set(key, json.dumps(value), ex=ex)

    async def get_json(self, key: str) -> dict | None:
        import json

        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None


redis_service = RedisService()
