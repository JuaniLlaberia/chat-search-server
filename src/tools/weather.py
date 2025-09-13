import requests
from langchain_core.tools import tool

@tool
def get_weather(city: str):
    """
    Get weather information from specific city using wttr.in

    Args:
        city (str): City to retrieve weather info
    """
    try:
        url = f"http://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data['current_condition'][0]

        return {
            "city": city,
            "temperature_c": current['temp_C'],
            "temperature_f": current['temp_F'],
            "condition": current['weatherDesc'][0]['value'],
            "humidity": current['humidity'],
            "wind_speed_kmh": current['windspeedKmph'],
            "feels_like_c": current['FeelsLikeC'],
            "visibility": current['visibility']
        }
    except Exception as e:
        return {"error": f"Weather request failed: {str(e)}"}