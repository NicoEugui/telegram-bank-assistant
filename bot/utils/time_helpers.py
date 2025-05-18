from datetime import datetime

"""
Returns a greeting in Spanish based on the current hour in the specified timezone.

Args:
    timezone (str): The timezone to use for determining the current hour. Defaults to "America/Montevideo".

Returns:
    str: A greeting message ("Buenos días", "Buenas tardes", or "Buenas noches") appropriate for the time of day.
"""
import pytz


def get_greeting_by_hour(timezone: str = "America/Montevideo") -> str:
    now = datetime.now(pytz.timezone(timezone))
    hour = now.hour

    if 6 <= hour < 12:
        return "Buenos días"
    elif 12 <= hour < 19:
        return "Buenas tardes"
    else:
        return "Buenas noches"
