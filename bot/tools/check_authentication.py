from langchain.tools import tool
import redis
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@tool
def check_authentication(user_id: str) -> bool:
    """
    Check if the user is already authenticated.
    Returns True if the user has a valid active authentication session.
    """
    key = f"auth:{user_id}"
    return r.get(key) == "True"
