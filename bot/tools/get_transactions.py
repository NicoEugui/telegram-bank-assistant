from langchain.tools import tool
from datetime import datetime
from decimal import Decimal
from config import REDIS_HOST, REDIS_PORT
import redis
import json

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def get_transactions(user_id: str) -> str:
    """
    Retrieve and format the user's last simulated banking transactions grouped by date.
    The output includes emojis for visual clarity and mimics the layout of a homebanking app.
    """
    transactions_key = f"transactions:{user_id}"
    raw_data = r.get(transactions_key)

    if raw_data is None:
        return "No se encontraron movimientos en su cuenta. Por favor, autentíquese nuevamente."

    try:
        transactions = json.loads(raw_data)
    except json.JSONDecodeError:
        return "Hubo un problema al procesar sus movimientos. Intente nuevamente más tarde."

    def format_amount_string(value: str) -> str:
        return (
            f"$ {Decimal(value):,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def format_transaction_line(transaction: dict) -> str:
        emoji = "⬆️" if transaction.get("type") == "ingreso" else "⬇️"
        return f"{emoji} {transaction['description']} · {format_amount_string(transaction['amount'])}"

    transactions.sort(key=lambda t: t["date"], reverse=True)

    grouped_by_date = {}
    for transaction in transactions[:10]:
        formatted_date = datetime.strptime(transaction["date"], "%Y-%m-%d").strftime(
            "%d/%m/%Y"
        )
        grouped_by_date.setdefault(formatted_date, []).append(
            format_transaction_line(transaction)
        )

    output_lines = ["🧾 Últimos movimientos:\n"]
    for date in sorted(grouped_by_date.keys(), reverse=True)[:5]:
        output_lines.append(f"📅 {date}")
        output_lines.extend(grouped_by_date[date])
        output_lines.append("")

    return "\n".join(output_lines).strip()
