from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters
from bot.commands import start

CHOOSING = 1


def build_start_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start.start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start.start),
            ],
        },
        fallbacks=[],
    )
