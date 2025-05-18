import pytest
from bot.services.response_humanizer import ResponseHumanizer

@pytest.mark.asyncio
async def test_response_humanizer_rewrite_valid(monkeypatch):
    # mock the chain.invoke method to simulate OpenAI response
    class MockChain:
        def invoke(self, inputs):
            return type("MockResponse", (), {
                "content": '''
                {
                    "parte_1": "Hola, bienvenido.",
                    "parte_2": "¿En qué puedo ayudarle?",
                    "parte_3": "",
                    "parte_4": ""
                }
                '''
            })()

    monkeypatch.setattr("bot.services.response_humanizer.ResponseHumanizer.prompt", MockChain())
    
    response = ResponseHumanizer("Hola").rewrite()
    
    assert response["parte_1"] == "Hola, bienvenido."
    assert response["parte_2"] == "¿En qué puedo ayudarle?"
    assert response["parte_3"] == ""
    assert response["parte_4"] == ""

@pytest.mark.asyncio
async def test_response_humanizer_rewrite_fallback(monkeypatch):
    class MockChain:
        def invoke(self, inputs):
            return type("MockResponse", (), {
                "content": "esto no es json válido"
            })()

    monkeypatch.setattr("bot.services.response_humanizer.ResponseHumanizer.prompt", MockChain())
    
    raw = "Texto crudo sin formato"
    response = ResponseHumanizer(raw).rewrite()
    
    assert response["parte_1"] == raw
    assert response["parte_2"] == ""
    assert response["parte_3"] == ""
    assert response["parte_4"] == ""
