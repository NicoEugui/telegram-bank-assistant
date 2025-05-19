import pytest
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

    result = await simulate_loan.ainvoke(
        {"user_id": USER_ID, "amount": 50000, "term_months": 12}
    )
    assert isinstance(result, dict)
    assert result["is_simulated"] is False
    assert "autenticarse" in result["error"].lower()


@pytest.mark.asyncio
async def test_invalid_input_values():
    await redis_service.set_authenticated(USER_ID)

    result_1 = await simulate_loan.ainvoke(
        {"user_id": USER_ID, "amount": -5000, "term_months": 12}
    )
    assert isinstance(result_1, dict)
    assert result_1["is_simulated"] is False
    assert "monto debe ser" in result_1["error"].lower()

    result_2 = await simulate_loan.ainvoke(
        {"user_id": USER_ID, "amount": 5000, "term_months": 0}
    )
    assert isinstance(result_2, dict)
    assert result_2["is_simulated"] is False
    assert "plazo debe ser" in result_2["error"].lower()


@pytest.mark.asyncio
async def test_simulates_and_persists_loan():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.delete(LOAN_KEY)

    result = await simulate_loan.ainvoke(
        {"user_id": USER_ID, "amount": 100000, "term_months": 12}
    )

    assert isinstance(result, dict)
    assert result["monto_solicitado"] == 100000
    assert result["plazo_en_meses"] == 12
    assert result["total_a_pagar"] > 100000
    assert "fecha_de_simulacion" in result
    assert result["is_simulated"] is True

    history = await redis_service.get_json(LOAN_KEY)
    assert isinstance(history, list)
    assert history[0]["monto_solicitado"] == 100000


@pytest.mark.asyncio
async def test_includes_credit_profile_summary():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.set_json(
        PROFILE_KEY,
        {
            "score": 720,
            "level": "high",
            "monthly_income": 80000,
            "income_debt_ratio": 0.25,
            "risk": "moderado",
        },
    )

    result = await simulate_loan.ainvoke(
        {"user_id": USER_ID, "amount": 60000, "term_months": 6}
    )

    assert isinstance(result, dict)
    assert "resumen_perfil" in result
    assert "moderado" in result["resumen_perfil"].lower()
