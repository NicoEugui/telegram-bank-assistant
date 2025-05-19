import pytest
import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT
from bot.services.redis_service import redis_service as redis_layer


@pytest.fixture(autouse=True, scope="function")
async def clean_redis():
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_layer.client = client

    await client.flushdb()
    yield
    await client.flushdb()
    await client.close()
