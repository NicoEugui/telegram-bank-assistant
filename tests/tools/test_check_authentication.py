import pytest
from bot.tools.check_authentication import check_authentication
from bot.services.redis_service import redis_service


USER_ID = "test-auth-user"
AUTH_KEY = f"auth:{USER_ID}"


@pytest.mark.asyncio
async def test_authentication_valid_session(monkeypatch):
    await redis_service.set(AUTH_KEY, "True", ex=60)
    result = await check_authentication.ainvoke({"user_id": USER_ID})
    assert result == {"is_authenticated": True}


@pytest.mark.asyncio
async def test_authentication_expired_session(monkeypatch):
    await redis_service.delete(AUTH_KEY)
    result = await check_authentication.ainvoke({"user_id": USER_ID})
    assert result == {"is_authenticated": False}


@pytest.mark.asyncio
async def test_authentication_invalid_user_id():
    result = await check_authentication.ainvoke({"user_id": None})
    assert result["is_authenticated"] is False
    assert "invalid_user_id" in result.get("error", "")


@pytest.mark.asyncio
async def test_authentication_redis_error(monkeypatch):
    # force a error on redis.ttl
    async def fake_ttl(*_):
        raise Exception("Redis connection error")

    monkeypatch.setattr(redis_service.client, "ttl", fake_ttl)

    result = await check_authentication.ainvoke({"user_id": USER_ID})
    assert result["is_authenticated"] is False
    assert result.get("error") == "redis_unavailable"
