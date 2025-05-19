from langchain.tools import tool
from bot.tools.check_authentication import check_authentication
from bot.services.redis_service import redis_service

import json
import logging

logger = logging.getLogger(__name__)


@tool
async def get_loan_history(user_id: str) -> str:
    """
    Devuelve una lista legible de hasta 3 prestamos simulados asociados al usuario,
    siempre que este autenticado. Si no hay historial o se produce un error,
    se devuelve un mensaje apropiado.
    """
    if not user_id or not isinstance(user_id, str):
        return "Identificador de usuario invalido. No se puede mostrar el historial"

    auth_result = await check_authentication.ainvoke({"user_id": user_id})
    if not auth_result.get("is_authenticated"):
        return "Por razones de seguridad, necesitamos que se autentique antes de mostrar su historial de prestamos"

    key = f"loan_history:{user_id}"

    try:
        raw_data = await redis_service.get(key)
        loans = json.loads(raw_data) if raw_data else []
    except json.JSONDecodeError:
        logger.exception(f"[Loan] Invalid JSON in loan history for {user_id}")
        return "No se pudo acceder al historial de préstamos por un error interno."
    except Exception as e:
        logger.exception(f"[Loan] Redis error when getting history for {user_id}: {e}")
        return "No se pudo acceder al historial de préstamos por un error interno."

    if not loans:
        return "No se encontraron préstamos simulados en su historial."

    logger.info(
        f"[Loan] Retrieved loan history for user {user_id} - count: {len(loans)}"
    )

    lines = ["🧾 Historial de prestamos simulados:\n"]
    for idx, loan in enumerate(loans[:3], start=1):

        monto = loan.get("monto_solicitado")
        plazo = loan.get("plazo_en_meses")
        cuota = loan.get("valor_cuota")
        total = loan.get("total_a_pagar")
        fecha = loan.get("fecha_de_simulacion")

        if None in (monto, plazo, cuota, total, fecha):
            logger.warning(f"[Loan] Incomplete registration in idx {idx}: {loan}")
            continue

        lines.append(
            f"Prestamo {idx}:\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📆 Plazo: {plazo} meses\n"
            f"🧾 Cuota mensual: ${cuota:,.2f}\n"
            f"🔢 Total a pagar: ${total:,.2f}\n"
            f"📅 Fecha de simulación: {fecha}\n"
        )

        if len(lines) == 1:
            return "No se encontraron préstamos simulados en su historial."

    return "\n".join(lines).strip()
