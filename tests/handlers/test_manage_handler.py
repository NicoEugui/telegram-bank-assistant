import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, Message, User, Chat
from bot.handlers.message_handler import handle_text_message


@pytest.mark.asyncio
@patch("bot.handlers.message_handler.ResponseHumanizer")
@patch("bot.handlers.message_handler.ConversationAgent")
async def test_handle_text_message_success(agent_mock, humanizer_mock):
    user_id = "123456"
    message_text = "Hola, ¿cuánto tengo?"

    # mock update
    mock_user = User(id=user_id, is_bot=False, first_name="TestUser")
    mock_chat = Chat(id=user_id, type="private")
    mock_message = Message(message_id=1, from_user=mock_user, chat=mock_chat, date=None, text=message_text)
    mock_update = Update(update_id=1, message=mock_message)

    mock_context = MagicMock()
    mock_update.message.reply_text = AsyncMock()

    # simulate conversation response
    agent_instance = AsyncMock()
    agent_instance.run.return_value = "Simulación terminada"
    agent_mock.return_value = agent_instance

    # simulate humanized parts
    humanizer_mock.return_value.rewrite.return_value = {
        "parte_1": "Hola, este es su saldo.",
        "parte_2": "Son 25.000 pesos.",
        "parte_3": "",
        "parte_4": "",
    }

    await handle_text_message(mock_update, mock_context)

    mock_update.message.reply_text.assert_any_await("Hola, este es su saldo.")
    mock_update.message.reply_text.assert_any_await("Son 25.000 pesos.")
    assert mock_update.message.reply_text.await_count == 2


@pytest.mark.asyncio
@patch("bot.handlers.message_handler.ResponseHumanizer")
@patch("bot.handlers.message_handler.ConversationAgent")
async def test_handle_text_message_empty_response(agent_mock, humanizer_mock):
    # mocks
    mock_update = MagicMock()
    mock_update.effective_user.id = "123"
    mock_update.message.text = "Test"
    mock_update.message.reply_text = AsyncMock()

    mock_context = MagicMock()

    agent_instance = AsyncMock()
    agent_instance.run.return_value = "Texto sin partes útiles"
    agent_mock.return_value = agent_instance

    humanizer_mock.return_value.rewrite.return_value = {
        "parte_1": "",
        "parte_2": "",
        "parte_3": "",
        "parte_4": "",
    }

    await handle_text_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_not_awaited()


@pytest.mark.asyncio
@patch("bot.handlers.message_handler.ConversationAgent")
async def test_handle_text_message_exception(agent_mock):
    # mocks
    mock_update = MagicMock()
    mock_update.effective_user.id = "123"
    mock_update.message.text = "Hola"
    mock_update.message.reply_text = AsyncMock()

    mock_context = MagicMock()

    # force error
    agent_mock.side_effect = Exception("Boom")

    await handle_text_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        "Lo siento, ocurrio un error al procesar su mensaje."
    )