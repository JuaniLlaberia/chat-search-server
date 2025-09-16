from datetime import date, time, datetime
from langchain_core.tools import tool

@tool("get_date")
def get_current_date() -> date:
    """
    Tool to get current date

    Returns:
        Current date
    """
    return date.today()

@tool("get_time")
def get_current_time() -> time:
    """
    Tool to get current time

    Returns:
        Current time
    """
    return datetime.now().time()