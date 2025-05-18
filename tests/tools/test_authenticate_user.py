import pytest
from decimal import Decimal
from bot.tools.authenticate_user import authenticate_user
from bot.services.redis_service import redis_service
from config import PIN_CODE

USER_ID = "test-auth-user"


@pytest.mark.asyncio
async def test_authenticate_with_valid_pin(monkeypatch):
    # cleanup
    await redis_service.delete(f"auth:{USER_ID}")
    await redis_service.delete(f"balance:{USER_ID}")
    await redis_service.delete(f"transactions:{USER_ID}")
    await redis_service.delete(f"credit_profile:{USER_ID}")

    result = await authenticate_user.ainvoke({"user_id": USER_ID, "pin": PIN_CODE})
    assert result["is_authenticated"] is True

    # validate Redis persistence
    balance = await redis_service.get(f"balance:{USER_ID}")
    transactions = await redis_service.get_json(f"transactions:{USER_ID}")
    profile = await redis_service.get_json(f"credit_profile:{USER_ID}")

    assert balance is not None
    assert Decimal(balance) >= 0
    assert isinstance(transactions, list) and len(transactions) > 0
    assert isinstance(profile, dict)
    assert "score" in profile


@pytest.mark.asyncio
async def test_authenticate_with_invalid_pin():
    result = await authenticate_user.ainvoke({"user_id": USER_ID, "pin": "0000"})
    assert result["is_authenticated"] is False


@pytest.mark.asyncio
async def test_authenticate_with_missing_user_id():
    result = await authenticate_user.ainvoke({"user_id": None, "pin": PIN_CODE})
    assert result["is_authenticated"] is False
    assert result.get("error") == "invalid_user_id"


@pytest.mark.asyncio
async def test_authenticate_with_invalid_pin_format():
    result = await authenticate_user.ainvoke({"user_id": USER_ID, "pin": "abc"})
    assert result["is_authenticated"] is False
    assert result.get("error") == "invalid_pin_format"
