from telegram.ext import Application, MessageHandler, filters
from bot.handlers.message_handler import handle_text_message
from bot.handlers.global_error_handler import global_error_handler
from config import TELEGRAM_BOT_TOKEN

import logging


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_bot() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )

    app.add_error_handler(global_error_handler)

    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
