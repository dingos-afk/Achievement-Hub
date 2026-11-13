
"""Main Drafter application for Achievement Hub."""

from drafter import *
import requests

from models import (
    Achievement,
    Game,
    State,
    add_game_to_library,
    game_completion_percentage,
    refresh_completed_game_count
)

from design import navigation, page_heading


# Local development address for the FastAPI backend.
# Change this to the deployed backend URL when hosted.
BACKEND_URL = "https://achievement-hub-backend.onrender.com"


def get_achievements_from_backend(appid: int) -> list:
    """Retrieve achievement definitions from the FastAPI backend."""

    response = requests.get(
        BACKEND_URL + "/games/" + str(appid) + "/achievements",
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    return data.get("achievements", [])

def page_start(title: str, subtitle: str) -> list:
    """Create the shared navigation and page heading."""

    content = navigation()
    content.extend(page_heading(title, subtitle))
    return content


@route
def index(state: State) -> Page:
    """Display the website's starting page."""

    return Home(state)


@route
def Home(state: State) -> Page:
    """Display the homepage and a summary of the user's library."""

    content = page_start(
        "Welcome to Achievement Hub",
        "Your personal place to organize and track video game achievements."
    )

    content.extend([
        "Welcome, " + state.Username + "!",
        Header("Your Progress", 2),
        "Games in your library: " + str(len(state.Games)),
        "Fully completed games: " + str(state.Total_completed_games),
        Button("Browse games", "library"),
        Button("View achievements", "view_Achievements"),
        Header("Recently Added Games", 2)
    ])

    if state.Games:
        for game in state.Games[-5:][::-1]:
            percent = game_completion_percentage(
                game.name, state.Achievements
            )

            content.append(
                game.name + " — " + str(percent) + "% complete"
            )

            content.append(
                Button(
                    "Open " + game.name,
                    "individual_game",
                    [Argument("appid", game.appid)]
                )
            )
    else:
        content.append(
            "You have not added any games yet. "
            "Visit Browse Games to begin."
        )

    return Page(state, content)


@route
def Profile(state: State) -> Page:
    """Show the profile and allow the user to edit profile information."""

    content = page_start(
        "Your Profile",
        "Edit the information shown on your Achievement Hub profile."
    )

    content.extend([
        "Username:",
        TextBox("username", state.Username),
        "Profile description:",
        TextArea("description", state.Profile_description),
        "Consoles played (separate entries with commas):",
        TextBox("consoles", ", ".join(state.Consoles_played)),
        Button("Save Profile", "save_profile")
    ])

    return Page(state, content)


@route
def save_profile(
    state: State,
    username: str,
    description: str,
    consoles: str
) -> Page:
    """Save the profile form values into State."""

    if username.strip():
        state.Username = username.strip()

    state.Profile_description = description.strip()

    state.Consoles_played = [
        console.strip()
        for console in consoles.split(",")
        if console.strip()
    ]

    state.Message = "Your profile has been updated."

    return Profile(state)


@route
def Settings(state: State) -> Page:
    """Display settings for sorting games in the library."""

    content = page_start(
        "Settings",
        "Choose how games should be ordered in your collection."
    )

    content.extend([
        "Game sorting:",
        SelectBox(
            "sort_order",
            [
                "Highest Priority",
                "Lowest Priority",
                "Alphabetical"
            ],
            state.Sort_order
        ),
        Button("Save Settings", "save_settings"),
        state.Message
    ])

    return Page(state, content)


@route
def save_settings(state: State, sort_order: str) -> Page:
    """Save the selected game sorting preference."""

    state.Sort_order = sort_order
    state.Message = "Your settings have been saved."

    return Settings(state)


@route
def library(state: State) -> Page:
    """Show Steam game search and games available to add."""

    content = page_start(
        "Game Library",
        "Search Steam, choose a matching game, and add it to your collection."
    )

    content.extend([
        "Search Games:",
        TextBox("search_name", placeholder="Example: Portal 2"),
        "Priority (5 is highest, 1 is lowest):",
        SelectBox(
            "priority",
            ["5", "4", "3", "2", "1"],
            str(state.Search_priority)
        ),
        Button("Search Steam", "search_games"),
        state.Message,
        Header("Search Results", 2)
    ])

    if state.Search_results:
        for result in state.Search_results:
            content.append(result["name"])

            content.append(
                Button(
                    "Add to My Games",
                    "add_game",
                    [
                        Argument("appid", result["appid"]),
                        Argument("game_name", result["name"]),
                        Argument("image", result.get("image", ""))
                    ]
                )
            )

    elif state.Message == "No matching games were found.":
        content.append("Try another title.")

    return Page(state, content)


@route
def search_games(
    state: State,
    search_name: str,
    priority: str
) -> Page:
    """Search Steam through the separate FastAPI backend."""

    state.Search_priority = int(priority)

    if not search_name.strip():
        state.Search_results = []
        state.Message = "Please enter a game name."
        return library(state)

    try:
        response = requests.get(
            BACKEND_URL + "/games/search",
            params={"name": search_name.strip()},
            timeout=20
        )

        response.raise_for_status()
        state.Search_results = response.json().get("games", [])

        if state.Search_results:
            state.Message = (
                "Select the correct game from these results."
            )
        else:
            state.Message = "No matching games were found."

    except requests.exceptions.RequestException:
        state.Search_results = []
        state.Message = (
            "Could not contact the Steam backend. "
            "Check that FastAPI is running on port 8000."
        )

    except (ValueError, KeyError):
        state.Search_results = []
        state.Message = "The backend returned unexpected data."

    return library(state)


@route
def add_game(
    state: State,
    appid: int,
    game_name: str,
    image: str
) -> Page:
    """Add the selected Steam game if it is not already in the library."""

    new_game = Game(
        name=game_name,
        appid=appid,
        image=image,
        priority=state.Search_priority
    )

    if add_game_to_library(state, new_game):
        state.Message = game_name + " was added to your library."
    else:
        state.Message = game_name + " is already in your library."

    return library(state)

@route
def individual_game(state: State, appid: int) -> Page:
    """Display a game's achievements and completion percentage."""

    selected_game = None

    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    if selected_game is None:
        state.Message = "That game is not in your library."
        return view_Games(state)

    known_achievements = [
        achievement
        for achievement in state.Achievements
        if achievement.Game_name == selected_game.name
    ]

    # Load achievements if this game has none saved yet.
    if not known_achievements:
        try:
            steam_achievements = get_achievements_from_backend(appid)

            for item in steam_achievements:
                new_achievement = Achievement(
                    name=item.get("name") or "Unnamed achievement",
                    Game_name=selected_game.name,
                    achievement_type="Unspecified",
                    Description=item.get("description", ""),
                    Completed=False,
                    steam_name=item.get("id", ""),
                    icon=item.get("icon", "")
                )

                state.Achievements.append(new_achievement)

            refresh_completed_game_count(state)

            if steam_achievements:
                state.Message = (
                    str(len(steam_achievements))
                    + " achievements loaded successfully."
                )
            else:
                state.Message = (
                    "Steam returned an empty achievement list."
                )

        except requests.exceptions.RequestException as error:
            state.Message = (
                "Backend request failed: " + str(error)
            )

        except (KeyError, TypeError, ValueError) as error:
            state.Message = (
                "Achievement data could not be processed: "
                + str(error)
            )

    percent = game_completion_percentage(
        selected_game.name,
        state.Achievements
    )

    content = page_start(
        selected_game.name,
        "Achievements and completion progress for this game."
    )

    content.append(state.Message)

    if percent == 100:
        content.append("✓ Completed!")
    else:
        content.append("Completion: " + str(percent) + "%")

    content.append(
    Button(
        "Edit achievement completion",
        "edit_game_achievements",
        [Argument("appid", selected_game.appid)]
    )
)
    found = False

    for achievement in state.Achievements:
        if achievement.Game_name == selected_game.name:
            found = True

            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            content.append(
                achievement.name + " — " + status
            )

            if achievement.Description:
                content.append(achievement.Description)

            content.append(
                "Category: " + achievement.achievement_type
            )

    if not found:
        content.append(
            "No achievement definitions were returned for this game."
        )

    content.append(
        Button("Back to My Games", "view_Games")
    )

    return Page(state, content)

@route
def edit_game_achievements(state: State, appid: int) -> Page:
    """Show only the selected game's achievements for editing."""

    selected_game = None

    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    if selected_game is None:
        state.Message = "Game not found."
        return view_Games(state)

    content = page_start(
        selected_game.name + " Achievements",
        "Update the completion status of this game's achievements."
    )

    game_achievements = []

    for index, achievement in enumerate(state.Achievements):
        if achievement.Game_name == selected_game.name:
            game_achievements.append((index, achievement))

    if not game_achievements:
        content.append("No achievements are available for this game.")

    else:
        for index, achievement in game_achievements:
            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            content.append(achievement.name + " — " + status)

        choices = []

        for index, achievement in game_achievements:
            choices.append(
                str(index) + " - " + achievement.name
            )

        content.extend([
            Header("Update Achievement", 2),
            "Choose an achievement:",
            SelectBox("achievement_choice", choices),
            "Check this box if the achievement is completed:",
            CheckBox("completed", False),
            Button(
                "Save Achievement Status",
                "save_achievement",
                [Argument("appid", appid)]
            )
        ])

    content.append(
        Button(
            "Back to Game",
            "individual_game",
            [Argument("appid", appid)]
        )
    )

    return Page(state, content)

@route
def view_Games(state: State) -> Page:
    """Display all games saved in the user's collection."""

    content = page_start(
        "My Games",
        "All video games you have added to your collection."
    )

    games = state.Games[:]

    if state.Sort_order == "Highest Priority":
        games.sort(
            key=lambda game: game.priority,
            reverse=True
        )

    elif state.Sort_order == "Lowest Priority":
        games.sort(key=lambda game: game.priority)

    else:
        games.sort(key=lambda game: game.name.lower())

    if not games:
        content.append("Your library is empty.")

    else:
        for game in games:
            percent = game_completion_percentage(
                game.name, state.Achievements
            )

            content.append(
                game.name
                + " | Priority: " + str(game.priority)
                + " | Completion: " + str(percent) + "%"
            )

            if percent == 100:
                content.append("✓ Completed!")

            content.append(
                Button(
                    "Open Game",
                    "individual_game",
                    [Argument("appid", game.appid)]
                )
            )

            content.append(
                Button(
                    "Remove Game",
                    "remove_game",
                    [Argument("appid", game.appid)]
                )
            )

    content.append(Button("Add More Games", "library"))

    return Page(state, content)


@route
def remove_game(state: State, appid: int) -> Page:
    """Remove a game and its associated achievements from the library."""

    game_name = ""

    for game in state.Games:
        if game.appid == appid:
            game_name = game.name
            break

    if not game_name:
        state.Message = "That game could not be found."
        return view_Games(state)

    state.Games = [
        game for game in state.Games
        if game.appid != appid
    ]

    state.Achievements = [
        achievement for achievement in state.Achievements
        if achievement.Game_name != game_name
    ]

    refresh_completed_game_count(state)
    state.Message = game_name + " was removed."

    return view_Games(state)


@route
def view_Achievements(state: State) -> Page:
    """Display achievements newest-first and a completion editing form."""

    content = page_start(
        "My Achievements",
        "Review your achievements and update which ones you have earned."
    )

    if not state.Achievements:
        content.append(
            "No achievements have been loaded yet. "
            "Open a game from My Games to retrieve its achievements."
        )

    else:
        for achievement in state.Achievements[::-1]:
            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            content.append(
                achievement.Game_name + " — " + achievement.name
                + " — " + status
            )

            if achievement.Description:
                content.append(achievement.Description)

            content.append(
                "Category: " + achievement.achievement_type
            )

        content.append(Header("Update an Achievement", 2))

        choices = []

        for index, achievement in enumerate(state.Achievements):
            choices.append(
                str(index) + " - " + achievement.Game_name
                + ": " + achievement.name
            )

        content.extend([
            "Choose an achievement:",
            SelectBox("achievement_choice", choices),
            "Check this box if the achievement is completed:",
            CheckBox("completed", False),
            Button("Save Achievement Status", "save_achievement")
        ])

    return Page(state, content)


@route
def save_achievement(
    state: State,
    appid: int,
    achievement_choice: str,
    completed: bool
) -> Page:
    """Update an achievement belonging to the selected game."""

    selected_game = None

    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    if selected_game is None:
        state.Message = "Game not found."
        return view_Games(state)

    try:
        achievement_index = int(
            achievement_choice.split(" - ", 1)[0]
        )

        if (
            0 <= achievement_index < len(state.Achievements)
            and state.Achievements[achievement_index].Game_name
            == selected_game.name
        ):
            state.Achievements[achievement_index].Completed = completed
            state.Message = "Achievement status updated."

        else:
            state.Message = "Please select a valid achievement."

    except (ValueError, IndexError):
        state.Message = "Please select a valid achievement."

    refresh_completed_game_count(state)

    return edit_game_achievements(state, appid)
    
set_site_information(
    author="Dinesh Goswami",
    description=(
        "Achievement Hub is a website for searching video games, "
        "organizing a personal game library, and tracking achievements."
    ),
    sources=(
        "Steam Store Search API, Steam Web API, Drafter, and FastAPI."
    ),
    planning="See planning_document.md in the project repository.",
    links=[]
)
    
start_server(
    State("Player"),
    site_title="Achievement Hub",
    port=8001
)
