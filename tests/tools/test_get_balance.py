import pytest
from unittest.mock import AsyncMock, patch
from bot.services.redis_service import redis_service
from bot.tools.get_balance import get_balance

USER_ID = "test-user"


@pytest.mark.asyncio
async def test_get_balance_authenticated(monkeypatch):
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication",
        AsyncMock(return_value={"is_authenticated": True}),
    )

    await redis_service.set(f"balance:{USER_ID}", "1000")
    result = await get_balance.ainvoke({"user_id": USER_ID})

    assert "1000" in result
    assert "pesos uruguayos" in result


@pytest.mark.asyncio
async def test_get_balance_not_authenticated(monkeypatch):
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication",
        AsyncMock(return_value={"is_authenticated": False}),
    )

    result = await get_balance.ainvoke({"user_id": USER_ID})
    assert "autentiquese" in result.lower()


@pytest.mark.asyncio
async def test_get_balance_missing(monkeypatch):
    monkeypatch.setattr(
        "bot.tools.get_balance.check_authentication",
        AsyncMock(return_value={"is_authenticated": True}),
    )

    await redis_service.delete(f"balance:{USER_ID}")
    result = await get_balance.ainvoke({"user_id": USER_ID})
    assert "No se pudo encontrar el saldo" in result


@pytest.mark.asyncio
async def test_get_balance_invalid_user():
    with pytest.raises(Exception):
        await get_balance.ainvoke({"user_id": None})
