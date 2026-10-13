
import requests
from langchain_core.tools import tool

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    95: "Thunderstorm",
}


@tool
def get_weather_info(location: str) -> str:
    """Get current weather conditions for a city or destination."""

    location = location.strip()
    if not location:
        return "Please provide a destination."

    try:
        # Step 1: Resolve the location to coordinates.
        geo_response = requests.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )
        geo_response.raise_for_status()
        locations = geo_response.json().get("results", [])

        if not locations:
            return f"No matching location found for {location}."

        place = locations[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        # Step 2: Fetch current weather.
        weather_response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,weather_code,wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        data = weather_response.json()

        current = data.get("current")
        if not current:
            return f"Current weather data is unavailable for {location}."

        code = current["weather_code"]
        condition = WEATHER_CODES.get(code, f"Weather code {code}")

        return (
            f"Current weather for {place['name']}, "
            f"{place.get('country', '')}:\n"
            f"- Condition: {condition}\n"
            f"- Temperature: {current['temperature_2m']}°C\n"
            f"- Feels like: {current['apparent_temperature']}°C\n"
            f"- Humidity: {current['relative_humidity_2m']}%\n"
            f"- Wind speed: {current['wind_speed_10m']} km/h\n"
            f"- Observation time: {current['time']}\n"
            "Source: Open-Meteo."
        )

    except requests.RequestException:
        return (
            f"Could not retrieve weather for {location}. "
            "The weather service may be temporarily unavailable."
        )
    except (KeyError, TypeError, ValueError):
        return f"The weather service returned unexpected data for {location}."

