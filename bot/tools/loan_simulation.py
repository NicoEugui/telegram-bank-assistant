from langchain.tools import tool
from decimal import Decimal, ROUND_HALF_UP
from config import (
    REDIS_HOST,
    REDIS_PORT,
    DEFAULT_LOAN_RATE,
)
import redis
import json

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@tool
def simulate_loan(user_id: str, loan_amount: float, term_months: int, annual_rate: float = DEFAULT_LOAN_RATE) -> dict:
    """
    Simula un préstamo personal con tasa fija. Calcula cuota mensual, total a pagar e información del perfil crediticio.
    """
    # convertion of inputs to Decimal for precision
    amount = Decimal(str(loan_amount))
    months = Decimal(str(term_months))
    monthly_rate = Decimal(str(annual_rate)) / Decimal("12") / Decimal("100")

    # calculate monthly payment using the formula for an annuity
    numerator = monthly_rate * (1 + monthly_rate) ** months
    denominator = (1 + monthly_rate) ** months - 1
    monthly_payment = amount * numerator / denominator

    monthly_payment = monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_payment = (monthly_payment * months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    result = {
        "monto_solicitado": float(amount),
        "plazo_meses": int(months),
        "tasa_anual": float(annual_rate),
        "cuota_mensual": float(monthly_payment),
        "total_a_pagar": float(total_payment),
        "observaciones": "Simulación basada en tasa fija. Sujeto a evaluación crediticia real.",
    }

    r.set(f"loan_simulation:{user_id}", json.dumps(result))
    return result
