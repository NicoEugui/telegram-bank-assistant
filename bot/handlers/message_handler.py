from telegram import Update
from telegram.ext import ContextTypes
from bot.agent.conversation_agent import ConversationAgent
from bot.services.response_humanizer import ResponseHumanizer

import logging
import asyncio

logger = logging.getLogger(__name__)


async def handle_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user_input = update.message.text
    user_id = str(update.effective_user.id)

    if not user_input or not user_input.strip():
        await update.message.reply_text(
            "Disculpe, no entendí el mensaje. Podría repetirlo?"
        )
        return

    logger.info(f"[User {user_id}] Input received: {user_input}")

    agent = ConversationAgent(user_id=user_id)

    try:
        raw_response = agent.run(user_input)
        humanizer = ResponseHumanizer(raw_response)
        parts = humanizer.rewrite()

        response = None

        for key in ["parte_1", "parte_2", "parte_3"]:
            if parts.get(key):

                response = await update.message.reply_text(parts[key])
                await asyncio.sleep(1.2)

        if response:
            logger.info(f"[User {user_id}] Output sent: {parts}")
        else:
            logger.info(f"[User {user_id}] No output parts returned from humanizer.")

    except Exception as e:
        logger.exception(f"[Handler] Error processing message from {user_id}: {e}")
        await update.message.reply_text(
            "Ocurrio un error al procesar su consulta. Por favor, intente nuevamente mas tarde"
        )
