"""Data models and small logic helpers for Achievement Hub."""

from dataclasses import dataclass, field


@dataclass
class Game:
    """Store a game saved in a user's library."""

    name: str
    appid: int
    image: str = ""
    priority: int = 3


@dataclass
class Achievement:
    """Store one achievement definition and the user's completion status."""

    name: str
    Game_name: str
    achievement_type: str
    Description: str
    Completed: bool
    steam_name: str = ""
    icon: str = ""


@dataclass
class State:
    """Store the information shared by the Achievement Hub routes."""

    Username: str
    Games: list[Game] = field(default_factory=list)
    Achievements: list[Achievement] = field(default_factory=list)
    Total_completed_games: int = 0
    Profile_description: str = ""
    Consoles_played: list[str] = field(default_factory=list)
    Sort_order: str = "Highest Priority"
    Search_results: list[dict] = field(default_factory=list)
    Search_priority: int = 3
    Message: str = ""


def game_completion_percentage(
    game_name: str,
    achievements: list[Achievement]
) -> int:
    """Return the whole-number completion percentage for one game."""

    game_achievements = [
        achievement for achievement in achievements
        if achievement.Game_name == game_name
    ]

    if not game_achievements:
        return 0

    completed = sum(
        1 for achievement in game_achievements
        if achievement.Completed
    )
    return round(completed / len(game_achievements) * 100)


def refresh_completed_game_count(state: State) -> None:
    """Recalculate how many library games have all known achievements."""

    total = 0

    for game in state.Games:
        game_achievements = [
            achievement for achievement in state.Achievements
            if achievement.Game_name == game.name
        ]

        if game_achievements and all(
            achievement.Completed for achievement in game_achievements
        ):
            total += 1

    state.Total_completed_games = total


def add_game_to_library(state: State, game: Game) -> bool:
    """Add a game unless its Steam App ID is already in the library."""

    for saved_game in state.Games:
        if saved_game.appid == game.appid:
            return False

    state.Games.append(game)
    return True
