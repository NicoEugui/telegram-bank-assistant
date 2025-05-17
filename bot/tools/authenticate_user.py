from langchain.tools import tool
from datetime import datetime, timedelta
from decimal import Decimal


from config import (
    REDIS_HOST,
    REDIS_PORT,
    AUTH_TTL_SECONDS,
    PIN_CODE,
    INITIAL_BALANCE_MIN,
    INITIAL_BALANCE_MAX,
    TRANSACTION_MIN,
    TRANSACTION_MAX,
    TRANSACTION_COUNT_MIN,
    TRANSACTION_COUNT_MAX,
    CREDIT_SCORE_MIN,
    CREDIT_SCORE_MAX,
    INCOME_MIN,
    INCOME_MAX,
    DEBT_RATIO_MIN,
    DEBT_RATIO_MAX,
    CREDIT_LEVELS,
    CREDIT_RISK_LEVELS,
)

import redis
import random
import json
import logging

logger = logging.getLogger(__name__)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def authenticate_user(user_id: str, pin: str) -> dict:
    """
    Verifica si el PIN ingresado por el usuario es correcto y, en ese caso,
    lo autentica y genera sus datos financieros simulados si aún no existen.
    """
    if pin != PIN_CODE:
        return {"is_authenticated": False}

    r.setex(f"auth:{user_id}", AUTH_TTL_SECONDS, "true")

    if not r.exists(f"balance:{user_id}"):
        balance = round(
            Decimal(random.uniform(INITIAL_BALANCE_MIN, INITIAL_BALANCE_MAX)), 2
        )
        r.set(f"balance:{user_id}", str(balance))

        templates = {
            "ingreso": [
                "Transferencia recibida",
                "Deposito en efectivo",
                "Reintegro de compra",
            ],
            "egreso": [
                "Compra supermercado",
                "Pago servicio UTE",
                "Debito automatico Spotify",
                "Extraccion en cajero",
            ],
        }

        txns = []
        today = datetime.now()
        for i in range(random.randint(TRANSACTION_COUNT_MIN, TRANSACTION_COUNT_MAX)):
            type = random.choices(["egreso", "ingreso"], weights=[0.75, 0.25])[0]
            desc = random.choice(templates[tipo])
            amount = round(Decimal(random.uniform(TRANSACTION_MIN, TRANSACTION_MAX)), 2)
            txns.append(
                {
                    "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "description": desc,
                    "type": type,
                    "amount": str(amount),
                }
            )
        r.set(f"transactions:{user_id}", json.dumps(txns))

        profile = {
            "score": random.randint(CREDIT_SCORE_MIN, CREDIT_SCORE_MAX),
            "level": random.choice(CREDIT_LEVELS),
            "monthly_income": random.randint(INCOME_MIN, INCOME_MAX),
            "income_debt_ratio": round(
                random.uniform(DEBT_RATIO_MIN, DEBT_RATIO_MAX), 2
            ),
            "risk": random.choice(CREDIT_RISK_LEVELS),
        }
        r.set(f"credit_profile:{user_id}", json.dumps(profile))

        logger.info(f"[Auth] User {user_id} authenticated.")
        logger.info(f"[Auth] Balance: {balance}")
        logger.info(f"[Auth] Transactions: {json.dumps(txns, indent=2)}")
        logger.info(f"[Auth] Credit profile: {json.dumps(profile, indent=2)}")

    return {"is_authenticated": True}
