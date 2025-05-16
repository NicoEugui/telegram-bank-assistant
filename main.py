import logging
from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN
from bot.handlers.start_handler import build_start_handler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_bot() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(build_start_handler())

    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
