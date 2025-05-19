import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bot.tools.get_transactions import get_transactions
from bot.services.redis_service import redis_service

USER_ID = "test-tx-user"
TX_KEY = f"transactions:{USER_ID}"
AUTH_KEY = f"auth:{USER_ID}"


@pytest.mark.asyncio
async def test_user_not_authenticated():
    await redis_service.delete(AUTH_KEY)

    result = await get_transactions.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "autenticarse" in result.lower()


@pytest.mark.asyncio
async def test_no_transactions_found():
    await redis_service.set(AUTH_KEY, "True", ex=60)
    await redis_service.delete(TX_KEY)

    result = await get_transactions.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "no se encontraron movimientos" in result.lower()


@pytest.mark.asyncio
async def test_transaction_list_success():
    await redis_service.set(AUTH_KEY, "True", ex=60)

    today = datetime.now()
    tx_data = [
        {
            "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "description": "Compra supermercado",
            "type": "egreso",
            "amount": str(round(Decimal("1000.00") + i, 2)),
        }
        for i in range(3)
    ]
    await redis_service.set_json(TX_KEY, tx_data)

    result = await get_transactions.ainvoke({"user_id": USER_ID})
    assert isinstance(result, str)
    assert "🧾" in result
    assert "Compra supermercado" in result
    assert result.count("⬇️") == 3
