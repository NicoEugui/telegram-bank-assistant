import openai
from pathlib import Path

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )
    return transcript
