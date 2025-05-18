import pytest
from bot.services.interaction_tracker import InteractionTracker
from bot.services.redis_service import redis_service

USER_ID = "test-interaction-user"
KEY = f"interactions:{USER_ID}"


@pytest.mark.asyncio
async def test_interaction_starts_at_zero():
    await redis_service.delete(KEY)
    total = await InteractionTracker.get_total(USER_ID)
    assert total == 0


@pytest.mark.asyncio
async def test_increment_interaction_once():
    await redis_service.delete(KEY)
    count = await InteractionTracker.increment(USER_ID)
    assert count == 1

    total = await InteractionTracker.get_total(USER_ID)
    assert total == 1


@pytest.mark.asyncio
async def test_increment_interaction_multiple_times():
    await redis_service.delete(KEY)

    for i in range(5):
        count = await InteractionTracker.increment(USER_ID)

    total = await InteractionTracker.get_total(USER_ID)
    assert total == 5
    assert count == 5
