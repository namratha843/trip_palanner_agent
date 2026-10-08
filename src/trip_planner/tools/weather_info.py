from langchain_core.tools import tool

@tool
def get_weather_info(location: str) -> str:
    """
    A tool to get weather information for a given location.
    """
    # Placeholder implementation. Replace with actual weather API call.
    return f"The current weather in {location} is sunny with a temperature of 25°C."