
from dataclasses import dataclass
import requests

from drafter import *


BACKEND_URL = "http://127.0.0.1:8000"


@dataclass
class State:
    search_results: list[dict]
    message: str


@route
def index(state: State) -> Page:
    """Display the Steam game search form and its results."""

    content = [
        Header("Achievement Hub - Connection Test"),
        "Search for a Steam game:",
        TextBox("game_name", placeholder="Example: Portal 2"),
        Button("Search Steam", "search_games"),
        "",
        Header("Search Results", 2),
        state.message
    ]

    for game in state.search_results:
        content.append(
            game["name"] + " (App ID: " + str(game["appid"]) + ")"
        )

    return Page(state, content)


@route
def search_games(state: State, game_name: str) -> Page:
    """Search Steam through the separate FastAPI backend."""

    if not game_name.strip():
        state.message = "Please enter a game name."
        state.search_results = []
        return index(state)

    try:
        response = requests.get(
            BACKEND_URL + "/games/search",
            params={"name": game_name},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()
        state.search_results = data["games"]

        if state.search_results:
            state.message = "Games found:"
        else:
            state.message = "No matching games were found."

    except requests.exceptions.RequestException:
        state.message = (
            "Could not connect to the backend. "
            "Make sure FastAPI is running."
        )
        state.search_results = []

    except (ValueError, KeyError):
        state.message = "The backend returned unexpected data."
        state.search_results = []

    return index(state)


start_server(
    State([], "Enter a game name to begin."),
    site_title="Achievement Hub Connection Test",
    port=8001
)