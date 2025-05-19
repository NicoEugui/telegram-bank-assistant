from telegram import Update
from telegram.ext import ContextTypes
from types import SimpleNamespace

from bot.utils.audio_converter import convert_ogg_to_wav
from bot.services.whisper_transcriber import transcribe_audio
from bot.handlers.message_handler import handle_text_message

import os
import logging
import tempfile

logger = logging.getLogger(__name__)


async def handle_audio_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message or not update.message.voice:
        return

    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        logger.info(f"[Audio] Downloading from {file.file_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            ogg_path = os.path.join(tmpdir, "input.ogg")
            wav_path = os.path.join(tmpdir, "output.wav")

            await file.download_to_drive(ogg_path)
            logger.info(f"[Audio] Downloaded to {ogg_path}")

            convert_ogg_to_wav(ogg_path, wav_path)
            logger.info(f"[Audio] Converted to {wav_path}")

            text = transcribe_audio(wav_path)
            logger.info(f"[Audio] Transcribed: {text}")

            if not text:
                await update.message.reply_text("No se pudo transcribir el audio.")
                return

            fake_update = SimpleNamespace(
                effective_user=update.effective_user,
                message=SimpleNamespace(
                    text=text,
                    chat_id=update.effective_chat.id,
                    reply_text=update.message.reply_text,
                ),
            )
            await handle_text_message(fake_update, context)

    except Exception as e:
        logger.error(f"[Audio] Error processing audio: {e}")
        await update.message.reply_text("Ocurrió un error al procesar el audio.")
