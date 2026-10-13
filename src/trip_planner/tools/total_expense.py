
from langchain_core.tools import tool


@tool
def calculate_total_expense(expenses: list[float]) -> str:
    """
    Calculate the total of a list of expenses.
    All expenses must be in the same currency.

    Example:
        expenses = [5000, 3000, 2000]
    """

    if not expenses:
        return "Please provide at least one expense."

    if any(amount < 0 for amount in expenses):
        return "Expenses cannot be negative."

    total = sum(expenses)

    return (
        f"Expense breakdown: {expenses}\n"
        f"Total expense: {total:.2f}\n"
        "Note: All amounts are assumed to be in the same currency."
    )
