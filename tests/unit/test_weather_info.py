from src.trip_planner.tools.weather_info import get_weather_info

def test_get_weather_info():
    result = get_weather_info.invoke({
        "location": "New York"
    })
    assert "New York" in result
    assert "25°C" in result