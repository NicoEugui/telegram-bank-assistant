from telegram import Update
from telegram.ext import ContextTypes
from config import OPENAI_API_KEY, REDIS_HOST, REDIS_PORT
from bot.agent.conversation_agent import ConversationAgent

import logging

logger = logging.getLogger(__name__)
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    user_id = str(update.effective_user.id)

    agent = ConversationAgent(
        user_id=user_id,
        redis_url=f"redis://{REDIS_HOST}:{REDIS_PORT}",
        openai_api_key=OPENAI_API_KEY,
    )

    try:
       response = agent.run(user_input)
    except Exception as e:
        logger.exception(f"[Handler] Error processing message from {user_id}: {e}")
        response = "Ocurrio un error, por favor intenta mas tarde"
    await update.message.reply_text(response)
