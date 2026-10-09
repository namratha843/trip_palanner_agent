from langchain_core.tools import tool

@tool
def calculate_total_expense(expenses: list[float]) -> str:
    """
    Calculate the totdal of a list trip expenses
    """

    if not expenses:
        raise ValueError("Expenses list cannot be empty.")

    if any(expense < 0 for expense in expenses):
        raise ValueError("Expenses cannot contain negative values.")

    total = sum(expenses)
    return f"The total expense for the trip is: ${total:.2f}"

