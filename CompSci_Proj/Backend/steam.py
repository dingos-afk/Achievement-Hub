
import os
import requests
from dotenv import load_dotenv

# Load Steam API key from .env
load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")

BASE_URL = "https://api.steampowered.com"


def get_game_achievements(appid: int) -> list:
    """
    Retrieves the achievement information for a Steam game.

    Args:
        appid: The Steam App ID of the game.

    Returns:
        A list containing the game's achievements.
    """

    url = BASE_URL + "/ISteamUserStats/GetSchemaForGame/v2/"

    params = {
        "key": STEAM_API_KEY,
        "appid": appid,
        "l": "english"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    return data["game"].get(
        "availableGameStats", {}
    ).get("achievements", [])


def search_steam_games(game_name: str) -> list:
    """
    Searches the Steam Store for games matching a name.

    Args:
        game_name: The name of the game to search for.

    Returns:
        A list of matching Steam games.
    """

    url = "https://store.steampowered.com/api/storesearch/"

    params = {
        "term": game_name,
        "l": "english",
        "cc": "US"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    return [
        {
            "appid": game["id"],
            "name": game["name"],
            "image": game.get("tiny_image", "")
        }
        for game in data.get("items", [])
    ]