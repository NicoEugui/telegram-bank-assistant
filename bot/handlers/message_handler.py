from telegram import Update
from telegram.ext import ContextTypes
from bot.agent.conversation_agent import ConversationAgent
from bot.services.response_humanizer import ResponseHumanizer

import logging
import asyncio

logger = logging.getLogger(__name__)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    logger.info(f"[User {user_id}] Input received: {user_message}")

    try:
        agent = ConversationAgent(user_id)
        raw_response = await agent.run(user_message)

        humanizer = ResponseHumanizer(raw_response)
        parts = humanizer.rewrite()

        if not any(parts.values()):
            logger.info(f"[User {user_id}] No output parts returned from humanizer.")
            return

        for key in ["parte_1", "parte_2", "parte_3", "parte_4"]:
            if parts.get(key):
                await update.message.reply_text(parts[key])
                await asyncio.sleep(1.2)

    except Exception as e:
        logger.exception(f"[Handler] Error processing message from {user_id}: {e}")
        await update.message.reply_text(
            "Lo siento, ocurrio un error al procesar su mensaje."
        )
