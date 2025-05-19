import pytest
from bot.services.interaction_tracker import InteractionTracker
from bot.services.redis_service import redis_service

USER_ID = "test-interaction-user"
KEY = f"interactions:{USER_ID}"


@pytest.fixture(autouse=True)
async def reset_interactions():
    await redis_service.delete(KEY)
    yield
    await redis_service.delete(KEY)


@pytest.mark.asyncio
async def test_interaction_starts_at_zero():
    total = await InteractionTracker.get_total(USER_ID)
    assert total == 0, "Expected interaction count to start at 0"


@pytest.mark.asyncio
async def test_increment_interaction_once():
    count = await InteractionTracker.increment(USER_ID)
    assert count == 1, "Expected increment to return 1"

    total = await InteractionTracker.get_total(USER_ID)
    assert total == 1, "Expected stored count to be 1 after one increment"


@pytest.mark.asyncio
async def test_increment_interaction_multiple_times():
    expected_counts = list(range(1, 6))
    actual_counts = []

    for _ in expected_counts:
        count = await InteractionTracker.increment(USER_ID)
        actual_counts.append(count)

    total = await InteractionTracker.get_total(USER_ID)
    assert (
        actual_counts == expected_counts
    ), f"Expected counts {expected_counts}, got {actual_counts}"
    assert total == 5, f"Expected total to be 5, got {total}"
