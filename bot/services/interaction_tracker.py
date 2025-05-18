import logging
from bot.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class InteractionTracker:
    @staticmethod
    async def increment(user_id: str) -> int:
        key = f"interactions:{user_id}"
        try:
            await redis_service.client.incr(key)
            total = await redis_service.client.get(key)
            return int(total or 1)
        except Exception as e:
            logger.warning(
                f"[Tracker] Could not increment interactions for {user_id}: {e}"
            )
            return 1

    @staticmethod
    async def get_total(user_id: str) -> int:
        try:
            key = f"interactions:{user_id}"
            value = await redis_service.client.get(key)
            return int(value or 0)
        except Exception as e:
            logger.warning(
                f"[Tracker] Could not retrieve interaction count for {user_id}: {e}"
            )
            return 0
