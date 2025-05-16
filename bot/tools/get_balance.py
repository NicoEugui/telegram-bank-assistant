from langchain.tools import tool
import redis
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@tool
def get_balance(user_id: str) -> str:
    """
    Retrieve the current simulated account balance of the user.
    """
    key = f"balance:{user_id}"
    balance = r.get(key)
    
    if balance is None:
        return "No se pudo encontrar el saldo asociado a su cuenta. Por favor, autentíquese nuevamente."

    return f"Su saldo actual es de {balance} pesos uruguayos."
