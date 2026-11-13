"""
Data models and small logic helpers for Achievement Hub.

This module defines the dataclasses used to represent games, achievements,
and application state. It also contains helper functions for calculating
game completion percentages, updating completed-game totals, and adding
games to a user's library.
"""

# Import tools for creating dataclasses and default list values.
from dataclasses import dataclass, field


@dataclass
class Game:
    """
    Store information about a game saved in a user's library.

    Attributes:
        name: The title of the game.
        appid: The unique Steam Application ID for the game.
        image: The URL of the game's image.
        priority: The user's priority rating for the game.
    """

    name: str
    appid: int
    image: str = ""
    priority: int = 3


@dataclass
class Achievement:
    """
    Store information about an achievement and its completion status.

    Attributes:
        name: The display name of the achievement.
        Game_name: The name of the game associated with the achievement.
        achievement_type: The category or type of achievement.
        Description: A description of what the achievement represents.
        Completed: Whether the user has completed the achievement.
        steam_name: The original achievement name provided by Steam.
        icon: The URL of the achievement's image.
    """

    name: str
    Game_name: str
    achievement_type: str
    Description: str
    Completed: bool
    steam_name: str = ""
    icon: str = ""


@dataclass
class State:
    """
    Store information shared between Achievement Hub routes.

    Attributes:
        Username: The user's displayed username.
        Games: The games saved in the user's library.
        Achievements: The achievements associated with saved games.
        Total_completed_games: The number of games with all known
            achievements completed.
        Profile_description: The user's profile description.
        Consoles_played: A list of gaming consoles the user plays.
        Sort_order: The selected order for displaying games.
        Search_results: Games returned from a Steam search.
        Search_priority: The priority assigned to a newly selected game.
        Message: A message displayed to the user by the application.
    """

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
    """
    Calculate the percentage of a game's achievements completed.

    First, the function filters the achievement list to include only
    achievements belonging to the requested game. It then counts how many
    of those achievements are completed and calculates the percentage.

    Args:
        game_name: The name of the game being checked.
        achievements: The list of achievement objects to examine.

    Returns:
        The whole-number completion percentage.
        Returns 0 if the game has no achievements.
    """

    # Keep only achievements belonging to the requested game.
    game_achievements = [
        achievement for achievement in achievements
        if achievement.Game_name == game_name
    ]

    # Avoid dividing by zero when no achievements exist.
    if not game_achievements:
        return 0

    # Count the achievements marked as completed.
    completed = sum(
        1 for achievement in game_achievements
        if achievement.Completed
    )

    # Divide completed achievements by the total and convert to a percentage.
    return round(completed / len(game_achievements) * 100)


def refresh_completed_game_count(state: State) -> None:
    """
    Recalculate the number of fully completed games in the user's library.

    A game counts as completed when it has at least one achievement and
    every achievement associated with that game is marked as completed.

    Args:
        state: The application's current State object.

    Returns:
        None. Updates state.Total_completed_games directly.
    """

    # Start the completed-game count at zero.
    total = 0

    # Examine every game saved in the user's library.
    for game in state.Games:

        # Find all achievements associated with the current game.
        game_achievements = [
            achievement for achievement in state.Achievements
            if achievement.Game_name == game.name
        ]

        # Count the game only if it has achievements and all are completed.
        if game_achievements and all(
            achievement.Completed for achievement in game_achievements
        ):
            total += 1

    # Save the updated total in the application State.
    state.Total_completed_games = total


def add_game_to_library(state: State, game: Game) -> bool:
    """
    Add a game to the user's library if it is not already saved.

    The function checks Steam App IDs to prevent duplicate games.
    If the game is already present, nothing is added.

    Args:
        state: The application's current State object.
        game: The Game object that the user wants to add.

    Returns:
        True if the game was successfully added.
        False if a game with the same Steam App ID already exists.
    """

    # Check every game currently saved in the user's library.
    for saved_game in state.Games:

        # Steam App IDs uniquely identify games.
        if saved_game.appid == game.appid:
            return False

    # Add the game when no matching App ID was found.
    state.Games.append(game)

    return True
