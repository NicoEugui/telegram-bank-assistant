import pytest
from bot.tools.get_balance import get_balance
from bot.services.redis_service import redis_service


USER_ID = "test-balance-user"


@pytest.mark.asyncio
async def test_get_balance_authenticated(monkeypatch):
    # mock autenticación exitosa
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication.ainvoke",
        lambda _: {"is_authenticated": True},
    )

    await redis_service.set(f"balance:{USER_ID}", "123456.78")
    result = await get_balance.ainvoke({"user_id": USER_ID})
    assert "123456.78" in result
    assert "pesos uruguayos" in result


@pytest.mark.asyncio
async def test_get_balance_not_authenticated(monkeypatch):
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication.ainvoke",
        lambda _: {"is_authenticated": False},
    )
    result = await get_balance.ainvoke({"user_id": USER_ID})
    assert "Debe autenticarse" in result


@pytest.mark.asyncio
async def test_get_balance_missing_in_redis(monkeypatch):
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication.ainvoke",
        lambda _: {"is_authenticated": True},
    )

    await redis_service.delete(f"balance:{USER_ID}")
    result = await get_balance.ainvoke({"user_id": USER_ID})
    assert "No se pudo encontrar el saldo" in result


@pytest.mark.asyncio
async def test_get_balance_invalid_user_id():
    result = await get_balance.ainvoke({"user_id": None})
    assert "Identificador de usuario invalido" in result
