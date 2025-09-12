from fastapi import APIRouter
from src.tools.date_tools import get_current_date
from src.tools.search_tools import tavily_search

helper_router = APIRouter()

tools = [
    get_current_date,
    tavily_search
]

@helper_router.get("/health", status_code=200)
async def health_check():
    """
    Endpoint to check server heath status
    """
    return {"status": "healthy"}

@helper_router.get("/debug/tools", status_code=200)
async def debug_tools():
    """
    Endpoint to see all available tools
    """
    tools_info = []

    for tool in tools:
        tools_info.append({
            "name": getattr(tool, "name", "unkown"),
            "type": str(type(tool)),
            "args_schema": str(getattr(tool, "args_schema", None))
        })

    return {"tools": tools_info}
