"""
Steam API Integration for Achievement Hub

This module contains functions that communicate with Steam's
external APIs to retrieve video game information and achievement
definitions.

Functions:
- get_game_achievements(): Retrieves achievement definitions
  for a specific Steam game.
- search_steam_games(): Searches the Steam Store for games
  matching a user's search term.

The Steam Web API key is loaded from an environment variable
so that it does not need to be written directly into the code.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from the local .env file.
# This allows the application to access the Steam API key
# without placing the key directly in the source code.
load_dotenv()

# Retrieve the Steam Web API key from the environment.
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

# Base URL used for Steam Web API requests.
BASE_URL = "https://api.steampowered.com"


def get_game_achievements(appid: int) -> list:
    """
    Retrieve achievement information for a Steam game.

    Uses Steam's GetSchemaForGame API endpoint to request
    the achievement definitions associated with a game.

    The returned information includes achievement names,
    descriptions, internal identifiers, and icon URLs.

    Args:
        appid (int): The unique Steam application ID of the game.

    Returns:
        list: A list containing the game's achievement definitions.
        Returns an empty list if no achievement information
        is available in the response.

    Raises:
        requests.exceptions.RequestException: If the HTTP
        request fails or Steam cannot be reached.
    """

    # Construct the URL for Steam's achievement schema endpoint.
    url = BASE_URL + "/ISteamUserStats/GetSchemaForGame/v2/"

    # Prepare the parameters required by Steam's API.
    params = {
        "key": STEAM_API_KEY,
        "appid": appid,
        "l": "english"
    }

    # Send a GET request to Steam with the API parameters.
    # The timeout prevents the program from waiting indefinitely.
    response = requests.get(url, params=params, timeout=15)

    # Check whether the request was successful.
    # An HTTP error will raise an exception if it failed.
    response.raise_for_status()

    # Convert the JSON response into a Python dictionary.
    data = response.json()

    # Navigate through the returned dictionary to find
    # the achievement definitions.
    # The get() method provides an empty dictionary or list
    # if the expected information is missing.
    return data["game"].get(
        "availableGameStats", {}
    ).get("achievements", [])


def search_steam_games(game_name: str) -> list:
    """
    Search the Steam Store for games matching a name.

    Sends the user's search term to Steam's Store Search API
    and processes the returned game information.

    Each matching game is converted into a dictionary
    containing its Steam App ID, name, and image URL.

    Args:
        game_name (str): The name or search term entered
        by the user.

    Returns:
        list: A list of dictionaries representing matching games.
        Each dictionary contains:
            - appid: The unique Steam application ID.
            - name: The game's display name.
            - image: The URL of the game's thumbnail image.

        Returns an empty list if no matching games are found.

    Raises:
        requests.exceptions.RequestException: If the HTTP
        request fails or Steam cannot be reached.
    """

    # Store the URL for Steam's Store Search API.
    url = "https://store.steampowered.com/api/storesearch/"

    # Prepare the search parameters.
    params = {
        "term": game_name,
        "l": "english",
        "cc": "US"
    }

    # Send a GET request to Steam using the search parameters.
    response = requests.get(url, params=params, timeout=15)

    # Check whether Steam successfully processed the request.
    response.raise_for_status()

    # Convert the JSON response into a Python dictionary.
    data = response.json()

    # Create a list containing the relevant information
    # for every game returned by the Steam Store API.
    return [
        {
            "appid": game["id"],
            "name": game["name"],
            "image": game.get("tiny_image", "")
        }

        # Loop through the games in the API response.
        # If the response has no items, use an empty list.
        for game in data.get("items", [])
    ]
