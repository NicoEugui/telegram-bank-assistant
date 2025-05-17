from datetime import datetime, timedelta

from langchain.tools import tool
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

import random
import json
import redis
import logging

logger = logging.getLogger(__name__)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def authenticate_user(user_id: str, pin: str) -> dict:
    """
    Authenticate the user using a 4-digit PIN. If the PIN is correct,
    mark the user as authenticated and initialize financial data if needed.
    """
    if pin != PIN_CODE:
        return {"is_authenticated": False}

    auth_key = f"auth:{user_id}"
    r.setex(auth_key, AUTH_TTL_SECONDS, "true")

    balance_key = f"balance:{user_id}"
    if not r.exists(balance_key):
        balance = round(random.uniform(INITIAL_BALANCE_MIN, INITIAL_BALANCE_MAX), 2)
        r.set(balance_key, balance)

        # generate transactions
        transaction_templates = {
            "ingreso": [
                "Transferencia recibida",
                "Depósito en efectivo",
                "Reintegro de compra",
            ],
            "egreso": [
                "Compra supermercado",
                "Pago servicio UTE",
                "Débito automático Spotify",
                "Extracción en cajero",
            ],
        }

        transactions = []
        today = datetime.now()
        for i in range(random.randint(TRANSACTION_COUNT_MIN, TRANSACTION_COUNT_MAX)):
            tipo = random.choices(["egreso", "ingreso"], weights=[0.75, 0.25])[0]
            desc = random.choice(transaction_templates[tipo])
            amount = round(random.uniform(TRANSACTION_MIN, TRANSACTION_MAX), 2)
            if tipo == "egreso":
                amount = -amount
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            transactions.append({"date": date, "description": desc, "amount": amount})

        r.set(f"transactions:{user_id}", json.dumps(transactions))

        # generate credit profile
        credit_profile = {
            "score": random.randint(CREDIT_SCORE_MIN, CREDIT_SCORE_MAX),
            "level": random.choice(CREDIT_LEVELS),
            "monthly_income": random.randint(INCOME_MIN, INCOME_MAX),
            "income_debt_ratio": round(
                random.uniform(DEBT_RATIO_MIN, DEBT_RATIO_MAX), 2
            ),
            "risk": random.choice(CREDIT_RISK_LEVELS),
        }
        r.set(f"credit_profile:{user_id}", json.dumps(credit_profile))

        logger.info(f"[Auth] User {user_id} authenticated.")
        logger.info(f"[Auth] Initial balance: {balance}")
        logger.info(f"[Auth] Transactions: {json.dumps(transactions, indent=2)}")
        logger.info(f"[Auth] Credit profile: {json.dumps(credit_profile, indent=2)}")

    return {"is_authenticated": True}
