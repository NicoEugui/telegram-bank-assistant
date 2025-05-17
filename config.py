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

# --- Auth PIN ---
PIN_CODE="1234"

INITIAL_BALANCE_MIN = 25000
INITIAL_BALANCE_MAX = 300000

TRANSACTION_MIN = -5000
TRANSACTION_MAX = 8000
TRANSACTION_COUNT_MIN = 5
TRANSACTION_COUNT_MAX = 10
TRANSACTION_DATE = "2025-05-16"

# -- Credit Profile Simulation ---
CREDIT_SCORE_MIN = 600
CREDIT_SCORE_MAX = 850
INCOME_MIN = 25000
INCOME_MAX = 90000
DEBT_RATIO_MIN = 0.15
DEBT_RATIO_MAX = 0.4

CREDIT_LEVELS = ["high", "medium", "low"]
CREDIT_RISK_LEVELS = ["low", "moderate", "high"]

# --- Loans ---
DEFAULT_LOAN_RATE = 22.0