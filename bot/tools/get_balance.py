from langchain.tools import tool
from bot.tools.check_authentication import check_authentication
from config import REDIS_HOST, REDIS_PORT

import redis
import logging

logger = logging.getLogger(__name__)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def get_balance(user_id: str) -> str:
    """
    Devuelve el saldo actual simulado del usuario.
    """

    if not user_id or not isinstance(user_id, str):
        return "Identificador de usuario invalido. Por favor, inicie sesión nuevamente"

    auth_result = check_authentication(user_id)
    if not auth_result.get("is_authenticated"):
        return "Debe autenticarse para consultar su saldo"

    try:
        key = f"balance:{user_id}"
        balance = r.get(key)

        if balance is None:
            return "No se pudo encontrar el saldo asociado a su cuenta. Por favor, autentiquese nuevamente"

        return f"Su saldo actual es de {balance} pesos uruguayos. Hay algo mas en lo que pueda ayudarle?"

    except redis.RedisError as e:
        logger.exception(f"[Balance] Redis error for user {user_id}: {e}")
        return "Ocurrio un error interno al consultar su saldo. Intente nuevamente en unos minutos"
