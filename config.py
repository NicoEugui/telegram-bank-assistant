import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ALLOWED_ENVS = {"development", "production"}


def load_environment() -> str:
    env = os.getenv("ENV")
    if not env:
        print("[Config] ENV not set, defaulting to 'development'")
        env = "development"

    env = env.lower()
    if env not in ALLOWED_ENVS:
        raise ValueError(
            f"[Config] Unknown ENV value: '{env}'. Must be one of {ALLOWED_ENVS}."
        )

    dotenv_path = ".env" if env == "development" else f".env.{env}"
    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"[Config] Missing environment file: {dotenv_path}")

    load_dotenv(dotenv_path)
    logger.info(f"[Config] Loaded environment: {env} from {dotenv_path}")
    return env


# --- Load environment ---
ENV = load_environment()

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise EnvironmentError("Missing TELEGRAM_BOT_TOKEN")

# --- OpenAI Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

if not OPENAI_API_KEY:
    raise EnvironmentError("Missing OPENAI_API_KEY")

# --- Redis Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --- LangChain Session Settings ---
SESSION_TTL_SECONDS = 300
CONTEXT_WINDOW_LENGTH = 5

# --- App TTLs ---
AUTH_TTL_SECONDS = 3600
PENDING_INTENT_TTL_SECONDS = 300

# --- PIN Configuration ---
PIN_CODE = "1234"

# --- Balance Simulation ---
INITIAL_BALANCE_MIN = 25000
INITIAL_BALANCE_MAX = 300000

# --- Transactions Simulation ---

TRANSACTION_MIN = 200
TRANSACTION_MAX = 8000
TRANSACTION_COUNT_MIN = 5
TRANSACTION_COUNT_MAX = 10

# --- Credit Profile Simulation ---
CREDIT_SCORE_MIN = 600
CREDIT_SCORE_MAX = 850
INCOME_MIN = 25000
INCOME_MAX = 90000
DEBT_RATIO_MIN = 0.15
DEBT_RATIO_MAX = 0.4

CREDIT_LEVELS = ["high", "medium", "low"]
CREDIT_RISK_LEVELS = ["low", "moderate", "high"]

# --- Loan Configuration ---
DEFAULT_LOAN_RATE = 22.0
MIN_LOAN_AMOUNT = 45000
MAX_TERM_MONTHS = 60
