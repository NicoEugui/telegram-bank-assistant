import pytest
from bot.agent.conversation_agent import ConversationAgent
from bot.services.redis_service import redis_service

import asyncio

USER_ID = "test-agent-user"

@pytest.mark.asyncio
async def test_conversation_agent_runs(monkeypatch):
    # patch RedisChatMessageHistory to avoid writing to real Redis
    monkeypatch.setattr("bot.agent.conversation_agent.RedisChatMessageHistory.ttl", 5)
    
    await redis_service.reset_interaction_count(USER_ID)

    agent = ConversationAgent(USER_ID)
    response = await agent.run("Hola, ¿qué tarjetas ofrecen?")

    assert isinstance(response, str)
    assert len(response) > 0
    assert "tarjetas" in response.lower() or "mastercard" in response.lower()
