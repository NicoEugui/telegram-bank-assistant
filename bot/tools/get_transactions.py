from langchain.tools import tool
from datetime import datetime
from decimal import Decimal
from bot.tools.check_authentication import check_authentication
from config import REDIS_HOST, REDIS_PORT
import redis
import json

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@tool
def get_transactions(user_id: str) -> str:
    """
    Devuelve los últimos movimientos simulados del usuario, agrupados por fecha.
    El formato incluye emojis para representar ingresos y egresos, similar a una app de homebanking.
    """

    auth_result = check_authentication(user_id)
    if not auth_result.get("is_authenticated"):
        return {"error": "Debe autenticarse para consultar sus movimientos"}

    transactions_key = f"transactions:{user_id}"
    raw_data = r.get(transactions_key)

    if raw_data is None:
        return "No se encontraron movimientos en su cuenta. Por favor, autentiquese nuevamente"

    try:
        transactions = json.loads(raw_data)
    except json.JSONDecodeError:
        return "Hubo un problema al procesar sus movimientos. Intente nuevamente más tarde"

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

    output_lines = ["🧾 Utimos movimientos:\n"]
    for date in sorted(grouped_by_date.keys(), reverse=True)[:5]:
        output_lines.append(f"📅 {date}")
        output_lines.extend(grouped_by_date[date])
        output_lines.append("")

    return "\n".join(output_lines).strip()
