from langchain.tools import tool
from bot.tools.check_authentication import check_authentication
from config import REDIS_HOST, REDIS_PORT

import redis
import json
import logging

logger = logging.getLogger(__name__)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def get_loan_history(user_id: str) -> str:
    """
    Devuelve una lista legible de hasta 3 prestamos simulados asociados al usuario,
    siempre que este autenticado. Si no hay historial o se produce un error,
    se devuelve un mensaje apropiado.
    """
    if not user_id or not isinstance(user_id, str):
        return "Identificador de usuario invalido. No se puede mostrar el historial"

    auth_result = check_authentication(user_id)
    if not auth_result.get("is_authenticated"):
        return "Por razones de seguridad, necesitamos que se autentique antes de mostrar su historial de prestamos"

    key = f"loan_history:{user_id}"

    try:
        data = r.get(key)
    except redis.RedisError as e:
        logger.exception(f"[Loan] Redis error for user {user_id}: {e}")
        return "No se pudo acceder al historial de prestamos por un error interno"

    if not data:
        return "No se encontraron prestamos simulados en su historial"

    try:
        loans = json.loads(data)
    except json.JSONDecodeError:
        return "No se pudo acceder al historial de prestamos por un error interno"

    logger.info(f"[Loan] Retrieved loan history for user {user_id} - count: {len(loans)}")

    lines = ["🧾 Historial de prestamos simulados:\n"]
    for idx, loan in enumerate(loans[:3], start=1):
        try:
            lines.append(
                f"Prestamo {idx}:\n"
                f"💰 Monto: ${loan['monto_solicitado']:.2f}\n"
                f"📆 Plazo: {loan['plazo_en_meses']} meses\n"
                f"🧾 Cuota mensual: ${loan['valor_cuota']:.2f}\n"
                f"🔢 Total a pagar: ${loan['total_a_pagar']:.2f}\n"
                f"📅 Fecha de simulacion: {loan['fecha_de_simulacion']}\n"
            )
        except KeyError as e:
            logger.warning(f"[Loan] Missing key in loan record: {e}")
