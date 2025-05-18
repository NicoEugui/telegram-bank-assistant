from langchain.tools import tool
from datetime import datetime
from bot.services.redis_service import redis_service
from bot.tools.check_authentication import check_authentication
from config import DEFAULT_LOAN_RATE

import json
import logging

logger = logging.getLogger(__name__)


@tool
async def simulate_loan(user_id: str, amount: float, term_months: int) -> dict:
    """
    Simula un préstamo en base al monto solicitado y el plazo en meses.
    Calcula la cuota mensual, el total a pagar y los intereses.
    Persiste el resultado en Redis como historial de préstamos del usuario.
    Adjunta un breve resumen del perfil crediticio del usuario.
    """

    if not user_id or not isinstance(user_id, str):
        return {"error": "Identificador de usuario inválido."}

    if not isinstance(amount, (int, float)) or amount <= 0:
        return {"error": "El monto debe ser un número mayor a cero."}

    if not isinstance(term_months, int) or term_months <= 0:
        return {"error": "El plazo debe ser un número entero mayor a cero."}

    auth_result = await check_authentication.ainvoke({"user_id": user_id})
    if not auth_result.get("is_authenticated"):
        return {"error": "Debe autenticarse para simular un prestamo"}

    rate = DEFAULT_LOAN_RATE / 100 / 12
    monthly_payment = (
        (amount * rate) / (1 - (1 + rate) ** -term_months)
        if rate
        else amount / term_months
    )
    total_payment = monthly_payment * term_months
    interest = total_payment - amount

    result = {
        "monto_solicitado": round(amount, 2),
        "plazo_en_meses": term_months,
        "valor_cuota": round(monthly_payment, 2),
        "total_a_pagar": round(total_payment, 2),
        "monto_de_intereses": round(interest, 2),
        "fecha_de_simulacion": datetime.now().strftime("%Y-%m-%d"),
    }

    # profile summary
    profile_summary = ""
    try:
        profile = await redis_service.get_json(f"credit_profile:{user_id}")
        if profile:
            level = profile.get("level", "desconocido")
            income = profile.get("monthly_income", 0)
            risk = profile.get("risk", "no evaluado")
            profile_summary = (
                f"Segun su perfil, usted califica como cliente de riesgo {risk.lower()} "
                f"con ingresos mensuales estimados en ${income:,} y un nivel crediticio '{level}'"
            )
    except Exception as e:
        logger.warning(
            f"[Loan] No se pudo recuperar el perfil crediticio de {user_id}: {e}"
        )

    try:
        previous = await redis_service.get_json(f"loan_history:{user_id}")
        history = previous if previous else []
        history.insert(0, result)
        await redis_service.set_json(f"loan_history:{user_id}", history)
    except Exception as e:
        logger.exception(f"[Loan] History could not be saved for {user_id}: {e}")
        return {
            "error": "No se pudo guardar la simulacion. Intente nuevamente mas tarde"
        }

    logger.info(f"[Loan] Simulated loan for user {user_id}")
    logger.info(f"[Loan] Stored loan record: {json.dumps(result, indent=2)}")

    result["resumen_perfil"] = profile_summary
    return result
