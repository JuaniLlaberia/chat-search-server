from datetime import date
from langchain_core.tools import tool

@tool("get_date")
def get_current_date() -> date:
    """
    Tool to get current date

    Returns:
        Current date
    """
    return date.today()