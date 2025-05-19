from langchain.tools import tool
from datetime import datetime
from decimal import Decimal
from bot.tools.check_authentication import check_authentication
from bot.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)


@tool
async def get_transactions(user_id: str) -> str:
    """
    Devuelve los últimos movimientos simulados del usuario, agrupados por fecha.
    El formato incluye emojis para representar ingresos y egresos, similar a una app de homebanking.
    """

    if not user_id or not isinstance(user_id, str):
        return "Identificador de usuario invalido. Por favor, autentiquese nuevamente"

    auth_result = await check_authentication.ainvoke({"user_id": user_id})
    if not auth_result.get("is_authenticated"):
        return "Debe autenticarse para consultar sus movimientos"

    key = f"transactions:{user_id}"

    try:
        transactions = await redis_service.get_json(key)
    except Exception as e:
        logger.exception(f"[Transactions] Redis error for user {user_id}: {e}")
        return "Hubo un problema al procesar sus movimientos"

    if not transactions:
        return "No se encontraron movimientos en su cuenta"

    def format_amount_string(value: str) -> str:
        return (
            f"$ {Decimal(value):,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def format_transaction_line(transaction: dict) -> str:
        emoji = "⬆️" if transaction.get("type") == "ingreso" else "⬇️"
        return f"{emoji} {transaction['description']} · {format_amount_string(transaction['amount'])}"

    try:
        transactions.sort(key=lambda t: t["date"], reverse=True)
    except Exception as e:
        logger.warning(f"[Transactions] Failed to sort transactions: {e}")

    grouped_by_date = {}
    for txn in transactions[:10]:
        try:
            formatted_date = datetime.strptime(txn["date"], "%Y-%m-%d").strftime(
                "%d/%m/%Y"
            )
            grouped_by_date.setdefault(formatted_date, []).append(
                format_transaction_line(txn)
            )
        except Exception as e:
            logger.warning(f"[Transactions] Failed to parse or group txn: {txn} - {e}")

    output_lines = ["🧾 Utimos movimientos:\n"]
    for date in sorted(grouped_by_date.keys(), reverse=True)[:5]:
        output_lines.append(f"📅 {date}")
        output_lines.extend(grouped_by_date[date])
        output_lines.append("")

    return "\n".join(output_lines).strip()
