from src.trip_planner.tools.place_search import get_places

def test_get_places_returns_places_for_location():
    # Arrange
    location = "New York"

    # Act
    result = get_places.invoke({
        "location": location
    })

    
    assert "Central Park" in result
    assert "Statue of Liberty" in result
    assert "Times Square" in result
    