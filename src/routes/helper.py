from fastapi import APIRouter
from src.tools.date_tools import get_current_date, get_current_time
from src.tools.search_tools import tavily_search
from src.tools.weather import get_weather
from src.tools.crypto_markets import get_crypto_price, get_crypto_details, get_trending_cryptos, search_crypto_coins, get_crypto_market_overview, get_top_cryptos

helper_router = APIRouter()

tools = [
    tavily_search,
    get_weather,
    get_crypto_price,
    get_crypto_details,
    get_trending_cryptos,
    search_crypto_coins,
    get_crypto_market_overview,
    get_top_cryptos,
    get_current_date,
    get_current_time
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
