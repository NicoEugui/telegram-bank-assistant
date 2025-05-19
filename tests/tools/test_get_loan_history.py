import pytest
from bot.tools.get_loan_history import get_loan_history
from bot.services.redis_service import redis_service

USER_ID = "test-loan-history"
AUTH_KEY = f"auth:{USER_ID}"
LOAN_KEY = f"loan_history:{USER_ID}"

MOCK_LOANS = [
    {
        "monto_solicitado": 50000.0,
        "plazo_en_meses": 12,
        "valor_cuota": 4500.0,
        "total_a_pagar": 54000.0,
        "monto_de_intereses": 4000.0,
        "fecha_de_simulacion": "2025-05-01",
    },
    {
        "monto_solicitado": 30000.0,
        "plazo_en_meses": 6,
        "valor_cuota": 5300.0,
        "total_a_pagar": 31800.0,
        "monto_de_intereses": 1800.0,
        "fecha_de_simulacion": "2025-05-02",
    },
    {
        "monto_solicitado": 100000.0,
        "plazo_en_meses": 24,
        "valor_cuota": 4800.0,
        "total_a_pagar": 115200.0,
        "monto_de_intereses": 15200.0,
        "fecha_de_simulacion": "2025-05-03",
    },
    {
        # this one should be ignored in the test
        "monto_solicitado": 20000.0,
        "plazo_en_meses": 4,
        "valor_cuota": 5100.0,
        "total_a_pagar": 20400.0,
        "monto_de_intereses": 400.0,
        "fecha_de_simulacion": "2025-05-04",
    },
]


@pytest.mark.asyncio
async def test_requires_authentication():
    await redis_service.clear_authenticated(USER_ID)
    result = await get_loan_history.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "autentique" in result.lower()


@pytest.mark.asyncio
async def test_no_loan_history_returns_fallback():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.delete(LOAN_KEY)
    result = await get_loan_history.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "no se encontraron préstamos" in result.lower()


@pytest.mark.asyncio
async def test_returns_latest_three_loans_formatted():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.set_json(LOAN_KEY, MOCK_LOANS)

    result = await get_loan_history.ainvoke({"user_id": USER_ID})

    assert isinstance(result, str)
    assert "🧾 historial de prestamos simulados" in result.lower()
    assert result.count("Prestamo") == 3
    assert "💰 Monto" in result
    assert "📅 Fecha de simulación" in result


@pytest.mark.asyncio
async def test_handles_invalid_json():
    await redis_service.set_authenticated(USER_ID)
    await redis_service.set(LOAN_KEY, "not-a-json")

    result = await get_loan_history.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "error interno" in result.lower()
