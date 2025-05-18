from langchain.tools import tool
from bot.tools.check_authentication import check_authentication
from bot.services.redis_service import redis_service

import redis
import logging

logger = logging.getLogger(__name__)


@tool
async def get_balance(user_id: str) -> str:
    """
    Devuelve el saldo actual simulado del usuario,
    si el usuario está autenticado y tiene información en Redis.
    """

    if not user_id or not isinstance(user_id, str):
        return "Identificador de usuario invalido. Por favor, inicie sesión nuevamente"

    auth_result = await check_authentication.ainvoke({"user_id": user_id})
    if not auth_result.get("is_authenticated"):
        return "Debe autenticarse para consultar su saldo"

    try:
        key = f"balance:{user_id}"
        balance = await redis_service.get(key)

        if balance is None:
            return "No se pudo encontrar el saldo asociado a su cuenta. Por favor, autentiquese nuevamente"

        return f"Su saldo actual es de {balance} pesos uruguayos. Hay algo mas en lo que pueda ayudarle?"

    except redis.RedisError as e:
        logger.exception(f"[Balance] Redis error for user {user_id}: {e}")
        return "Ocurrio un error interno al consultar su saldo. Intente nuevamente en unos minutos"
