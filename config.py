import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram Bot Token ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# --- Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --- LangChain / Session Settings ---
SESSION_TTL_SECONDS = 300
CONTEXT_WINDOW_LENGTH = 5

# --- App-level state TTLs ---
AUTH_TTL_SECONDS = 3600
PENDING_INTENT_TTL_SECONDS = 300
