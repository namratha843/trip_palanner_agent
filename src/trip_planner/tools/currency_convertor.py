
import requests
from langchain_core.tools import tool

FRANKFURTER_URL = "https://api.frankfurter.dev/v2/rate"


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """Convert an amount between currencies using Frankfurter reference rates."""

    if amount < 0:
        return "Amount cannot be negative."

    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    if not from_currency or not to_currency:
        return "Please provide both currency codes, such as USD and INR."

    if from_currency == to_currency:
        return f"{amount:.2f} {from_currency} = {amount:.2f} {to_currency}"

    try:
        response = requests.get(
            f"{FRANKFURTER_URL}/{from_currency}/{to_currency}",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        rate = float(data["rate"])
        rate_date = data["date"]
        converted_amount = amount * rate

        return (
            f"Currency conversion (Frankfurter reference rate):\n"
            f"- From: {amount:.2f} {from_currency}\n"
            f"- To: {converted_amount:.2f} {to_currency}\n"
            f"- Exchange rate: 1 {from_currency} = "
            f"{rate} {to_currency}\n"
            f"- Rate date: {rate_date}\n"
            "- Note: This is a reference rate, not a guaranteed "
            "transaction or card rate."
        )

    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return (
                f"Could not find a supported reference rate for "
                f"{from_currency} to {to_currency}."
            )
        return "Currency conversion failed because the rate service returned an error."

    except requests.RequestException:
        return "Currency conversion failed because the rate service is unavailable."

    except (KeyError, TypeError, ValueError):
        return "Currency conversion failed because the rate response was invalid."
