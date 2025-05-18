from langchain.tools import tool
from config import REDIS_HOST, REDIS_PORT

import redis
import logging

logger = logging.getLogger(__name__)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def check_authentication(user_id: str) -> dict:
    """
    Verifica si el usuario tiene una sesion activa en Redis.
    Devuelve {"is_authenticated": True} si el TTL de la sesión es válido (> 0), False en caso contrario.
    """

    if not user_id or not isinstance(user_id, str):
        logger.warning("[Auth] Invalid or missing user_id.")
        return {"is_authenticated": False, "error": "invalid_user_id"}

    key = f"auth:{user_id}"

    try:
        ttl = r.ttl(key)
        is_authenticated = ttl > 0
        logger.info(f"[Auth] TTL for {user_id} is {ttl}")
        return {"is_authenticated": is_authenticated}
    except redis.RedisError as e:
        logger.exception(f"[Auth] Redis error while checking authentication for user {user_id}: {e}")
        return {"is_authenticated": False, "error": "redis_unavailable"}
