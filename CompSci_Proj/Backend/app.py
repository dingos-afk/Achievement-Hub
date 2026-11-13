"""
Achievement Hub Backend

This module creates the FastAPI backend for Achievement Hub.
It handles requests from the frontend and communicates with
Steam through functions imported from steam.py.

Available endpoints:
- /: Checks whether the backend is running.
- /games/search: Searches Steam for games by name.
- /games/{appid}/achievements: Retrieves achievement definitions
  for a specific Steam game.
"""

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import functions that communicate directly with Steam.
from steam import (
    search_steam_games,
    get_game_achievements
)

# Create the FastAPI application.
app = FastAPI()

# Configure Cross-Origin Resource Sharing (CORS).
# This allows the frontend website to send GET requests
# to the backend from a different website address.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    """
    Display the backend homepage.

    This endpoint checks whether the backend is running.
    It returns a simple message confirming that the
    Achievement Hub backend is available.

    Returns:
        dict: A message identifying the backend.
    """

    return {"message": "Achievement Hub Steam Backend"}


@app.get("/games/search")
def search_games(name: str):
    """
    Search Steam for games matching a name.

    Receives a game name from the frontend and passes it
    to the search_steam_games function in steam.py.

    An error is returned if the search name is empty or
    if Steam cannot be reached.

    Args:
        name (str): The name of the game to search for.

    Returns:
        dict: A dictionary containing a list of matching games.

    Raises:
        HTTPException: Status 400 if the search name is empty.
        HTTPException: Status 502 if the Steam request fails.
    """

    # Check whether the user entered a search term.
    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a game name."
        )

    try:
        # Request matching games from the Steam search function.
        games = search_steam_games(name)

        # Return the search results as a dictionary.
        return {"games": games}

    except requests.exceptions.RequestException:
        # Return an error if the request to Steam fails.
        raise HTTPException(
            status_code=502,
            detail="Unable to search Steam games."
        )


@app.get("/games/{appid}/achievements")
def game_achievements(appid: int):
    """
    Retrieve achievement definitions using a Steam App ID.

    Receives a game's Steam App ID and requests its achievement
    information from the get_game_achievements function in steam.py.

    Each achievement is converted into a dictionary containing
    its identifier, display name, description, and icon URL.

    Args:
        appid (int): The unique Steam application ID of the game.

    Returns:
        dict: A dictionary containing the App ID, achievement list,
        and total number of achievements returned.

    Raises:
        HTTPException: Status 502 if the Steam request fails.
    """

    try:
        # Retrieve the achievement information from Steam.
        game_list = get_game_achievements(appid)

        # Create an empty list to store formatted achievements.
        achievements = []

        # Loop through each achievement returned by Steam.
        for achievement in game_list:

            # Extract the relevant information and add it
            # to the achievements list.
            achievements.append({
                "id": achievement.get("name", ""),
                "name": achievement.get("displayName", ""),
                "description": achievement.get("description", ""),
                "icon": achievement.get("icon", "")
            })

        # Return the game ID, formatted achievements,
        # and the total number of achievements.
        return {
            "appid": appid,
            "achievements": achievements,
            "total": len(achievements)
        }

    except requests.exceptions.RequestException:
        # Return an error if Steam cannot provide the information.
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve achievements from Steam."
        )
