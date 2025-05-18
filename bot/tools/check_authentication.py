from langchain.tools import tool
from bot.services.redis_service import redis_service

import redis
import logging

logger = logging.getLogger(__name__)


@tool
async def check_authentication(user_id: str) -> dict:
    """
    Verifica si el usuario tiene una sesión activa en Redis.
    Devuelve {"is_authenticated": True} si la sesión es válida, False en caso contrario.
    """

    if not user_id or not isinstance(user_id, str):
        logger.warning("[Auth] Invalid or missing user_id.")
        return {"is_authenticated": False, "error": "invalid_user_id"}

    try:
        is_authenticated = await redis_service.is_authenticated(user_id)
        logger.info(f"[Auth] Auth status for {user_id}: {is_authenticated}")
        return {"is_authenticated": is_authenticated}
    except Exception as e:
        logger.exception(
            f"[Auth] Error while checking authentication for user {user_id}: {e}"
        )
        return {"is_authenticated": False, "error": "redis_unavailable"}
