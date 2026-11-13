
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from steam import (
    search_steam_games,
    get_game_achievements
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    """Display the backend homepage."""

    return {"message": "Achievement Hub Steam Backend"}


@app.get("/games/search")
def search_games(name: str):
    """Search Steam for games matching a name."""

    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a game name."
        )

    try:
        games = search_steam_games(name)
        return {"games": games}

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to search Steam games."
        )


@app.get("/games/{appid}/achievements")
def game_achievements(appid: int):
    """Retrieve achievement definitions using a Steam App ID."""

    try:
        game_list = get_game_achievements(appid)

        achievements = []

        for achievement in game_list:
            achievements.append({
                "id": achievement.get("name", ""),
                "name": achievement.get("displayName", ""),
                "description": achievement.get("description", ""),
                "icon": achievement.get("icon", "")
            })

        return {
            "appid": appid,
            "achievements": achievements,
            "total": len(achievements)
        }

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve achievements from Steam."
        )