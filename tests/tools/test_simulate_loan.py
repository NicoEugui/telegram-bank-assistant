import pytest
import json
from datetime import datetime
from bot.tools.loan_simulation import simulate_loan
from bot.services.redis_service import redis_service

USER_ID = "test-loan-user"
AUTH_KEY = f"auth:{USER_ID}"
LOAN_KEY = f"loan_history:{USER_ID}"
PROFILE_KEY = f"credit_profile:{USER_ID}"


@pytest.mark.asyncio
async def test_rejects_unauthenticated_user():
    await redis_service.delete(AUTH_KEY)
    result = await simulate_loan.ainvoke({"user_id": USER_ID, "amount": 50000, "term_months": 12})
    assert "autenticarse" in result["error"]


@pytest.mark.asyncio
async def test_invalid_input_values():
    await redis_service.set_authenticated(USER_ID)

    # monto inválido
    res1 = await simulate_loan.ainvoke({"user_id": USER_ID, "amount": -5000, "term_months": 12})
    assert "monto debe ser" in res1["error"]

    # plazo inválido
    res2 = await simulate_loan.ainvoke({"user_id": USER_ID, "amount": 5000, "term_months": 0})
    assert "plazo debe ser" in res2["error"]


@pytest.mark.asyncio
async def test_simulates_and_persists_loan():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.delete(LOAN_KEY)

    result = await simulate_loan.ainvoke({"user_id": USER_ID, "amount": 100000, "term_months": 12})

    assert result["monto_solicitado"] == 100000
    assert result["plazo_en_meses"] == 12
    assert result["total_a_pagar"] > 100000
    assert "fecha_de_simulacion" in result

    history = await redis_service.get_json(LOAN_KEY)
    assert isinstance(history, list)
    assert history[0]["monto_solicitado"] == 100000


@pytest.mark.asyncio
async def test_includes_credit_profile_summary():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.set_json(PROFILE_KEY, {
        "score": 720,
        "level": "high",
        "monthly_income": 80000,
        "income_debt_ratio": 0.25,
        "risk": "moderate"
    })

    result = await simulate_loan.ainvoke({"user_id": USER_ID, "amount": 60000, "term_months": 6})
    assert "perfil" in result["resumen_perfil"]
    assert "moderado" in result["resumen_perfil"].lower()
