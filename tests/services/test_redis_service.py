import pytest
from bot.services.redis_service import redis_service

TEST_USER_ID = "testuser:redis"
TEST_KEY = "test:key"
TEST_JSON_KEY = "test:json"
TEST_DATA = {"foo": "bar", "count": 3}


@pytest.fixture(autouse=True)
async def cleanup_redis_keys():
    await redis_service.delete(TEST_KEY)
    await redis_service.delete(TEST_JSON_KEY)
    await redis_service.clear_authenticated(TEST_USER_ID)
    await redis_service.clear_pending_intent(TEST_USER_ID)
    await redis_service.reset_interaction_count(TEST_USER_ID)
    yield
    await redis_service.delete(TEST_KEY)
    await redis_service.delete(TEST_JSON_KEY)
    await redis_service.clear_authenticated(TEST_USER_ID)
    await redis_service.clear_pending_intent(TEST_USER_ID)
    await redis_service.reset_interaction_count(TEST_USER_ID)


@pytest.mark.asyncio
async def test_authentication_flow():
    await redis_service.set_authenticated(TEST_USER_ID, ttl=10)
    assert (
        await redis_service.is_authenticated(TEST_USER_ID) is True
    ), "User should be authenticated"

    await redis_service.clear_authenticated(TEST_USER_ID)
    assert (
        await redis_service.is_authenticated(TEST_USER_ID) is False
    ), "User should no longer be authenticated"


@pytest.mark.asyncio
async def test_pending_intent_flow():
    await redis_service.set_pending_intent(TEST_USER_ID, "simular", ttl=10)
    assert (
        await redis_service.get_pending_intent(TEST_USER_ID) == "simular"
    ), "Intent should match set value"

    await redis_service.clear_pending_intent(TEST_USER_ID)
    assert (
        await redis_service.get_pending_intent(TEST_USER_ID) is None
    ), "Intent should be cleared"


@pytest.mark.asyncio
async def test_interaction_tracking():
    await redis_service.reset_interaction_count(TEST_USER_ID)
    assert (
        await redis_service.get_interaction_count(TEST_USER_ID) == 0
    ), "Initial interaction count must be 0"

    count = await redis_service.increment_interaction_count(TEST_USER_ID)
    assert count == 1, "First increment should return 1"
    assert (
        await redis_service.get_interaction_count(TEST_USER_ID) == 1
    ), "Count after first increment must be 1"


@pytest.mark.asyncio
async def test_set_get_delete_string():
    await redis_service.set(TEST_KEY, "test-value")
    result = await redis_service.get(TEST_KEY)
    assert result == "test-value", f"Expected 'test-value', got {result}"

    exists = await redis_service.exists(TEST_KEY)
    assert exists in [True, 1], "Key should exist"

    await redis_service.delete(TEST_KEY)
    assert await redis_service.get(TEST_KEY) is None, "Key should be deleted"


@pytest.mark.asyncio
async def test_set_get_json():
    await redis_service.set_json(TEST_JSON_KEY, TEST_DATA)
    result = await redis_service.get_json(TEST_JSON_KEY)

    assert result == TEST_DATA, f"Expected {TEST_DATA}, got {result}"

    await redis_service.delete(TEST_JSON_KEY)
    assert (
        await redis_service.get_json(TEST_JSON_KEY) is None
    ), "JSON key should be deleted"
