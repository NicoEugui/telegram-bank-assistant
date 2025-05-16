from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

CHOOSING = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text("Bienvenido a la jungla !")

    return CHOOSING
