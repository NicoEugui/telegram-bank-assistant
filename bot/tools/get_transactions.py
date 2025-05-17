from langchain.tools import tool
from datetime import datetime
import redis
import json
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@tool
def get_transactions(user_id: str) -> str:
    """
    Retrieve and format the user's last simulated banking transactions grouped by date.
    The output includes emojis for visual clarity and mimics the layout of a homebanking app.
    """

    key = f"transactions:{user_id}"
    raw = r.get(key)

    if raw is None:
        return "No se encontraron movimientos en su cuenta. Por favor, autentíquese nuevamente."

    try:
        transactions = json.loads(raw)
    except json.JSONDecodeError:
        return "Hubo un problema al procesar sus movimientos. Intente nuevamente más tarde."

    def format_amount(amount: float) -> str:
        return f"$ {abs(amount):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def format_line(txn: dict) -> str:
        emoji = "⬆️" if txn.get("type") == "ingreso" else "⬇️"
        return f"{emoji} {txn['description']} · {format_amount(txn['amount'])}"

    grouped = {}
    transactions.sort(key=lambda x: x["date"], reverse=True)
    for txn in transactions[:10]:
        date = datetime.strptime(txn["date"], "%Y-%m-%d").strftime("%d/%m/%Y")
        grouped.setdefault(date, []).append(format_line(txn))

    output = ["🧾 Últimos movimientos:\n"]
    for date in sorted(grouped.keys(), reverse=True)[:5]:
        output.append(f"📅 {date}")
        output.extend(grouped[date])
        output.append("")

    return "\n".join(output).strip()
