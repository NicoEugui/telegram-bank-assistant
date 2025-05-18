from langchain.tools import tool
from datetime import datetime, timedelta
from decimal import Decimal
from bot.services.redis_service import redis_service

import random
import json
import logging

from config import (
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


logger = logging.getLogger(__name__)


@tool
async def authenticate_user(user_id: str, pin: str) -> dict:
    """
    Verifica si el PIN ingresado por el usuario es correcto y, en ese caso,
    lo autentica y genera sus datos financieros simulados si aún no existen.
    """

    if not user_id or not isinstance(user_id, str):
        logger.warning("[Auth] Missing or invalid user_id.")
        return {"is_authenticated": False, "error": "invalid_user_id"}

    if not pin or not isinstance(pin, str) or len(pin) != 4 or not pin.isdigit():
        logger.warning(f"[Auth] Invalid PIN format for user {user_id}.")
        return {"is_authenticated": False, "error": "invalid_pin_format"}

    if pin != PIN_CODE:
        logger.warning(f"[Auth] Failed authentication attempt for user {user_id}.")
        return {"is_authenticated": False}

    await redis_service.set_authenticated(user_id)

    exists = await redis_service.exists(f"balance:{user_id}")
    if not exists:
        balance = round(
            Decimal(random.uniform(INITIAL_BALANCE_MIN, INITIAL_BALANCE_MAX)), 2
        )
        await redis_service.set(f"balance:{user_id}", str(balance))

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
            desc = random.choice(templates[type])
            amount = round(Decimal(random.uniform(TRANSACTION_MIN, TRANSACTION_MAX)), 2)
            txns.append(
                {
                    "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "description": desc,
                    "type": type,
                    "amount": str(amount),
                }
            )
        await redis_service.set_json(f"transactions:{user_id}", txns)

        profile = {
            "score": random.randint(CREDIT_SCORE_MIN, CREDIT_SCORE_MAX),
            "level": random.choice(CREDIT_LEVELS),
            "monthly_income": random.randint(INCOME_MIN, INCOME_MAX),
            "income_debt_ratio": round(
                random.uniform(DEBT_RATIO_MIN, DEBT_RATIO_MAX), 2
            ),
            "risk": random.choice(CREDIT_RISK_LEVELS),
        }
        await redis_service.set_json(f"credit_profile:{user_id}", profile)

        logger.info(f"[Auth] User {user_id} authenticated.")
        logger.info(f"[Auth] Balance: {balance}")
        logger.info(f"[Auth] Transactions: {json.dumps(txns, indent=2)}")
        logger.info(f"[Auth] Credit profile: {json.dumps(profile, indent=2)}")

    return {"is_authenticated": True}
