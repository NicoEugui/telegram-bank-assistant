from langchain.tools import tool
from datetime import datetime
from bot.tools.check_authentication import check_authentication
from config import REDIS_HOST, REDIS_PORT, DEFAULT_LOAN_RATE

import redis
import json
import logging

logger = logging.getLogger(__name__)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def simulate_loan(user_id: str, amount: float, term_months: int) -> dict:
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

    auth_result = check_authentication(user_id)
    if not auth_result.get("is_authenticated"):
        return {"error": "Debe autenticarse para simular un préstamo."}

    rate = DEFAULT_LOAN_RATE / 100 / 12
    if rate == 0:
        monthly_payment = amount / term_months
    else:
        monthly_payment = (amount * rate) / (1 - (1 + rate) ** -term_months)

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

    # obtein credit profile
    credit_key = f"credit_profile:{user_id}"
    profile_summary = ""

    try:
        profile_raw = r.get(credit_key)
        if profile_raw:
            profile = json.loads(profile_raw)
            level = profile.get("level", "desconocido")
            income = profile.get("monthly_income", 0)
            risk = profile.get("risk", "no evaluado")
            profile_summary = (
                f"Segun su perfil, usted califica como cliente de riesgo {risk.lower()} "
                f"con ingresos mensuales estimados en ${income:,} y un nivel crediticio '{level}'"
            )
    except Exception as e:
        logger.warning(f"[Loan] No se pudo recuperar el perfil crediticio de {user_id}: {e}")

    # persist loan simulation
    key = f"loan_history:{user_id}"
    try:
        previous = r.get(key)
        history = json.loads(previous) if previous else []
        history.insert(0, result)
        r.set(key, json.dumps(history))
    except Exception as e:
        logger.exception(f"[Loan] No se pudo guardar el historial para {user_id}: {e}")
        return {"error": "No se pudo guardar la simulacion. Intente nuevamente mas tarde"}

    logger.info(f"[Loan] Simulated loan for user {user_id}")
    logger.info(f"[Loan] Stored loan record: {json.dumps(result, indent=2)}")

    result["Resumen Perfil"] = profile_summary
    return result
