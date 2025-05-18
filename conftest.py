import fakeredis
import pytest

@pytest.fixture(scope="session", autouse=True)
def patch_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr("bot.services.redis_service.redis_service.client", fake)
