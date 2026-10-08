from langchain_core.tools import tool


@tool
def get_places(location:str) -> str:
    """
    A tool to get places for a given location.
    """
   
    return f"Places in {location} include Central Park, Statue of Liberty, and Times Square."