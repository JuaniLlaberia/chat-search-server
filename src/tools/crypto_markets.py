import requests
from typing import Dict
from langchain.tools import tool
import json
from datetime import datetime

class CryptoDataTool:
    """
    Comprehensive crypto data tool using CoinGecko API
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def _make_request(endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        try:
            url = f"{CryptoDataTool.BASE_URL}{endpoint}"
            response = requests.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}

@tool
def get_crypto_price(coin_id: str, vs_currency: str = "usd") -> Dict:
    """
    Get current price for a cryptocurrency

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'cardano')
        vs_currency: Currency to compare against (default: 'usd')

    Returns:
        Dictionary with current price and basic market data
    """
    endpoint = "/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": vs_currency,
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_last_updated_at": "true"
    }

    result = CryptoDataTool._make_request(endpoint, params)

    if "error" in result:
        return result

    if coin_id not in result:
        return {"error": f"Coin '{coin_id}' not found. Use search_crypto_coins to find the correct ID."}

    data = result[coin_id]
    return {
        "coin": coin_id,
        "price": data.get(vs_currency, 0),
        "currency": vs_currency.upper(),
        "market_cap": data.get(f"{vs_currency}_market_cap", 0),
        "volume_24h": data.get(f"{vs_currency}_24h_vol", 0),
        "price_change_24h": data.get(f"{vs_currency}_24h_change", 0),
        "last_updated": datetime.fromtimestamp(data.get("last_updated_at", 0)).strftime("%Y-%m-%d %H:%M:%S") if data.get("last_updated_at") else "Unknown"
    }

@tool
def get_crypto_details(coin_id: str) -> Dict:
    """
    Get detailed information about a cryptocurrency

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')

    Returns:
        Comprehensive crypto data including market stats, supply info, etc.
    """
    endpoint = f"/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "true",
        "developer_data": "true"
    }

    result = CryptoDataTool._make_request(endpoint, params)

    if "error" in result:
        return result

    market_data = result.get("market_data", {})

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "symbol": result.get("symbol", "").upper(),
        "current_price_usd": market_data.get("current_price", {}).get("usd", 0),
        "market_cap_usd": market_data.get("market_cap", {}).get("usd", 0),
        "market_cap_rank": market_data.get("market_cap_rank", 0),
        "total_volume_usd": market_data.get("total_volume", {}).get("usd", 0),
        "price_change_24h": market_data.get("price_change_percentage_24h", 0),
        "price_change_7d": market_data.get("price_change_percentage_7d", 0),
        "price_change_30d": market_data.get("price_change_percentage_30d", 0),
        "circulating_supply": market_data.get("circulating_supply", 0),
        "total_supply": market_data.get("total_supply", 0),
        "max_supply": market_data.get("max_supply", 0),
        "all_time_high": market_data.get("ath", {}).get("usd", 0),
        "all_time_low": market_data.get("atl", {}).get("usd", 0),
        "description": result.get("description", {}).get("en", "")[:500] + "..." if result.get("description", {}).get("en", "") else "",
        "homepage": result.get("links", {}).get("homepage", [None])[0],
        "blockchain_site": result.get("links", {}).get("blockchain_site", [None])[0]
    }

@tool
def get_trending_cryptos() -> Dict:
    """
    Get currently trending cryptocurrencies

    Returns:
        List of trending crypto coins with basic info
    """
    endpoint = "/search/trending"
    result = CryptoDataTool._make_request(endpoint)

    if "error" in result:
        return result

    trending_coins = []
    for coin in result.get("coins", [])[:10]:  # Top 10
        coin_data = coin.get("item", {})
        trending_coins.append({
            "id": coin_data.get("id"),
            "name": coin_data.get("name"),
            "symbol": coin_data.get("symbol"),
            "market_cap_rank": coin_data.get("market_cap_rank"),
            "price_btc": coin_data.get("price_btc", 0)
        })

    return {
        "trending_coins": trending_coins,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@tool
def search_crypto_coins(query: str) -> Dict:
    """
    Search for cryptocurrencies by name or symbol

    Args:
        query: Search term (coin name or symbol)

    Returns:
        List of matching cryptocurrencies with their IDs
    """
    endpoint = "/search"
    params = {"query": query}
    result = CryptoDataTool._make_request(endpoint, params)

    if "error" in result:
        return result

    coins = []
    for coin in result.get("coins", [])[:10]:  # Top 10 results
        coins.append({
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol"),
            "market_cap_rank": coin.get("market_cap_rank")
        })

    return {
        "query": query,
        "results": coins,
        "total_found": len(result.get("coins", []))
    }

@tool
def get_crypto_market_overview() -> Dict:
    """
    Get global cryptocurrency market overview

    Returns:
        Global market statistics
    """
    endpoint = "/global"
    result = CryptoDataTool._make_request(endpoint)

    if "error" in result:
        return result

    data = result.get("data", {})

    return {
        "total_market_cap_usd": data.get("total_market_cap", {}).get("usd", 0),
        "total_volume_24h_usd": data.get("total_volume", {}).get("usd", 0),
        "bitcoin_dominance": data.get("market_cap_percentage", {}).get("btc", 0),
        "ethereum_dominance": data.get("market_cap_percentage", {}).get("eth", 0),
        "active_cryptocurrencies": data.get("active_cryptocurrencies", 0),
        "markets": data.get("markets", 0),
        "market_cap_change_24h": data.get("market_cap_change_percentage_24h_usd", 0),
        "updated_at": datetime.fromtimestamp(data.get("updated_at", 0)).strftime("%Y-%m-%d %H:%M:%S") if data.get("updated_at") else "Unknown"
    }

@tool
def get_top_cryptos(limit: int = 10, vs_currency: str = "usd") -> Dict:
    """
    Get top cryptocurrencies by market cap

    Args:
        limit: Number of coins to return (max 250, default 10)
        vs_currency: Currency for prices (default 'usd')

    Returns:
        List of top cryptocurrencies with market data
    """
    endpoint = "/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": min(limit, 250),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d"
    }

    result = CryptoDataTool._make_request(endpoint, params)

    if "error" in result:
        return result

    coins = []
    for coin in result:
        coins.append({
            "rank": coin.get("market_cap_rank", 0),
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "price": coin.get("current_price", 0),
            "market_cap": coin.get("market_cap", 0),
            "volume_24h": coin.get("total_volume", 0),
            "price_change_24h": coin.get("price_change_percentage_24h", 0),
            "price_change_7d": coin.get("price_change_percentage_7d", 0)
        })

    return {
        "top_cryptocurrencies": coins,
        "currency": vs_currency.upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
