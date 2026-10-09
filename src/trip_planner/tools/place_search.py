
import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

CATEGORY_PRIORITY = {
    "tourism.attraction": 1,
    "tourism.sights": 1,
    "entertainment.museum": 2,
    "entertainment.culture": 3,
    "leisure.park": 4,
}

@tool
def get_places(location: str) -> str:
    """Find sightseeing places near a destination using Geoapify."""

    location = location.strip()

    if not location:
        return "Please provide a destination."

    if not GEOAPIFY_API_KEY:
        return (
            "Place search is not configured: "
            "GEOAPIFY_API_KEY is missing."
        )

    # Resolve the destination to coordinates.
    try:
        geo_response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": location,
                "format": "jsonv2",
                "limit": 1,
            },
            headers={
                "User-Agent": "TripPlannerAgent/1.0 "
                "(personal learning project)"
            },
            timeout=10,
        )
        geo_response.raise_for_status()
        geo_results = geo_response.json()

    except requests.RequestException:
        return (
            f"Could not look up {location}. "
            "The location service may be temporarily unavailable."
        )

    if not geo_results:
        return f"No matching destination found for {location}."

    latitude = float(geo_results[0]["lat"])
    longitude = float(geo_results[0]["lon"])

    # Search a broad selection of sightseeing categories.
    params = {
        "categories": (
            "tourism.attraction,"
            "tourism.sights,"
            "entertainment.museum,"
            "entertainment.culture,"
            "leisure.park"
        ),
        "filter": (
            f"circle:{longitude},{latitude},8000"
        ),
        "bias": f"proximity:{longitude},{latitude}",
        "limit": 50,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(
            GEOAPIFY_URL,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        features = response.json().get("features", [])

    except requests.RequestException:
        return (
            f"Could not retrieve places for {location}. "
            "The places service may be temporarily unavailable."
        )

    # Deduplicate places and rank by category.
    places_by_name = {}

    for feature in features:
        properties = feature.get("properties", {})
        name = properties.get("name")

        if not name:
            continue

        categories = properties.get("categories", [])
        priority = min(
            (
                CATEGORY_PRIORITY[category]
                for category in categories
                if category in CATEGORY_PRIORITY
            ),
            default=99,
        )

        key = name.casefold()
        place = {
            "name": name,
            "category": categories,
            "address": properties.get("formatted", ""),
            "priority": priority,
        }

        existing = places_by_name.get(key)

        if existing is None or priority < existing["priority"]:
            places_by_name[key] = place

    ranked_places = sorted(
        places_by_name.values(),
        key=lambda place: (
            place["priority"],
            place["name"].casefold(),
        ),
    )[:20]

    if not ranked_places:
        return (
            f"No named sightseeing places were found near {location}. "
            "Try a different destination or search source."
        )

    results = []

    for place in ranked_places:
        line = f"- {place['name']}"

        if place["address"]:
            line += f" — {place['address']}"

        results.append(line)

    return (
        f"Places found near {location} using Geoapify:\n"
        + "\n".join(results)
        + "\nSource: Geoapify Places API; underlying map data "
        "may include OpenStreetMap contributors."
    )
