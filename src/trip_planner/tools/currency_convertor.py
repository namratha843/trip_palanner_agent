from langchain_core.tools import tool

EXCHANGE_RATES = {
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
    ("USD", "INR"): 83.0,
    ("INR", "USD"): 1 / 83.0,
    ("EUR", "INR"): 90.0,
    ("INR", "EUR"): 1 / 90.0,
}


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """Convert an amount between supported currencies using placeholder rates."""

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    if from_currency == to_currency:
        return f"{amount:.2f} {from_currency} = {amount:.2f} {to_currency}"

    rate = EXCHANGE_RATES.get((from_currency, to_currency))

    if rate is None:
        raise ValueError(
            f"Unsupported currency pair: {from_currency} to {to_currency}"
        )

    converted_amount = amount * rate

    return (
        f"{amount:.2f} {from_currency} = "
        f"{converted_amount:.2f} {to_currency}"
    )

