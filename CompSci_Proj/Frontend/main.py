"""
Main Drafter application for Achievement Hub.

This module controls the website's routes, page content, navigation,
Steam game searches, achievement retrieval, and user interactions.

It connects the Drafter frontend to a separate FastAPI backend.
The backend communicates with Steam to retrieve game and achievement data.
"""

# Import Drafter components and functions used to build the website.
from drafter import *

# Import requests to communicate with the FastAPI backend.
import requests

# Import the application's data models and helper functions.
from models import (
    Achievement,
    Game,
    State,
    add_game_to_library,
    game_completion_percentage,
    refresh_completed_game_count
)

# Import reusable navigation and page-heading functions.
from design import navigation, page_heading


# URL of the deployed FastAPI backend.
# Change this value if the backend is moved to another address.
BACKEND_URL = "https://achievement-hub-backend.onrender.com"


def get_achievements_from_backend(appid: int) -> list:
    """
    Retrieve achievement definitions for a Steam game.

    Sends a request to the FastAPI backend using the game's Steam App ID.
    The backend retrieves the achievement definitions from Steam.

    Args:
        appid: The unique Steam Application ID of the game.

    Returns:
        A list of achievement dictionaries returned by the backend.

    Raises:
        requests.exceptions.RequestException:
            If the backend request fails.
        ValueError:
            If the response cannot be decoded as JSON.
    """

    # Send a GET request to the game's achievement endpoint.
    response = requests.get(
        BACKEND_URL + "/games/" + str(appid) + "/achievements",
        timeout=20
    )

    # Raise an exception if the server returns an unsuccessful status.
    response.raise_for_status()

    # Convert the JSON response into a Python dictionary.
    data = response.json()

    # Return the achievement list, or an empty list if it is missing.
    return data.get("achievements", [])


def page_start(title: str, subtitle: str) -> list:
    """
    Create the shared beginning of a website page.

    Combines the navigation menu with a page heading and subtitle.
    This prevents every route from needing to recreate those elements.

    Args:
        title: The main heading displayed on the page.
        subtitle: A short explanation displayed beneath the heading.

    Returns:
        A list containing the navigation and heading components.
    """

    # Get the shared navigation menu.
    content = navigation()

    # Add the page title and subtitle.
    content.extend(page_heading(title, subtitle))

    return content


@route
def index(state: State) -> Page:
    """
    Display the website's starting page.

    This is the main entry route and directs visitors to the homepage.

    Args:
        state: The application's current State object.

    Returns:
        The homepage as a Drafter Page.
    """

    return Home(state)


@route
def Home(state: State) -> Page:
    """
    Display the homepage and a summary of the user's library.

    Shows the username, number of saved games, completed-game count,
    navigation buttons, and the five most recently added games.

    Args:
        state: The application's current State object.

    Returns:
        The homepage as a Drafter Page.
    """

    # Create the shared navigation and page heading.
    content = page_start(
        "Welcome to Achievement Hub",
        "Your personal place to organize and track video game achievements."
    )

    # Add the user's information and progress summary.
    content.extend([
        "Welcome, " + state.Username + "!",
        Header("Your Progress", 2),
        "Games in your library: " + str(len(state.Games)),
        "Fully completed games: " + str(state.Total_completed_games),
        Button("Browse games", "library"),
        Button("View achievements", "view_Achievements"),
        Header("Recently Added Games", 2)
    ])

    # Display recently added games if the library contains any.
    if state.Games:

        # Reverse the list so the newest games appear first.
        for game in state.Games[-5:][::-1]:

            # Calculate the game's achievement completion percentage.
            percent = game_completion_percentage(
                game.name, state.Achievements
            )

            # Display the game's name and completion percentage.
            content.append(
                game.name + " — " + str(percent) + "% complete"
            )

            # Add a button that opens the selected game.
            content.append(
                Button(
                    "Open " + game.name,
                    "individual_game",
                    [Argument("appid", game.appid)]
                )
            )

    else:
        # Display a message when the library is empty.
        content.append(
            "You have not added any games yet. "
            "Visit Browse Games to begin."
        )

    return Page(state, content)


@route
def Profile(state: State) -> Page:
    """
    Display the user's profile editing page.

    Provides input fields for the username, profile description,
    and gaming consoles.

    Args:
        state: The application's current State object.

    Returns:
        The profile page as a Drafter Page.
    """

    # Create the shared page heading and navigation.
    content = page_start(
        "Your Profile",
        "Edit the information shown on your Achievement Hub profile."
    )

    # Create input fields containing the user's current information.
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
    """
    Save the information submitted through the profile form.

    Updates the username, profile description, and list of consoles.
    Console names are separated using commas.

    Args:
        state: The application's current State object.
        username: The username entered by the user.
        description: The profile description entered by the user.
        consoles: A comma-separated string of console names.

    Returns:
        The updated profile page.
    """

    # Update the username only if the submitted value is not empty.
    if username.strip():
        state.Username = username.strip()

    # Remove unnecessary spaces from the profile description.
    state.Profile_description = description.strip()

    # Split the console names at commas and remove extra whitespace.
    state.Consoles_played = [
        console.strip()
        for console in consoles.split(",")
        if console.strip()
    ]

    # Store a confirmation message in the application State.
    state.Message = "Your profile has been updated."

    return Profile(state)


@route
def Settings(state: State) -> Page:
    """
    Display the user's game-sorting settings.

    Allows the user to choose how games should be ordered
    in their personal library.

    Args:
        state: The application's current State object.

    Returns:
        The settings page as a Drafter Page.
    """

    # Create the shared page heading and navigation.
    content = page_start(
        "Settings",
        "Choose how games should be ordered in your collection."
    )

    # Display the sorting dropdown and save button.
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
    """
    Save the selected game-sorting preference.

    Args:
        state: The application's current State object.
        sort_order: The sorting option selected by the user.

    Returns:
        The updated settings page.
    """

    # Update the selected sorting preference.
    state.Sort_order = sort_order

    # Display a confirmation message.
    state.Message = "Your settings have been saved."

    return Settings(state)


@route
def library(state: State) -> Page:
    """
    Display the Steam game search page.

    Allows users to search for games, choose a priority,
    review matching search results, and add games to their library.

    Args:
        state: The application's current State object.

    Returns:
        The game search page as a Drafter Page.
    """

    # Create the shared page heading and navigation.
    content = page_start(
        "Game Library",
        "Search Steam, choose a matching game, and add it to your collection."
    )

    # Add the search box, priority selector, and search button.
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

    # Display the search results if any games were found.
    if state.Search_results:

        for result in state.Search_results:

            # Display the game's name.
            content.append(result["name"])

            # Add a button that passes the selected game's information
            # to the add_game route.
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

        # Encourage the user to try another search.
        content.append("Try another title.")

    return Page(state, content)


@route
def search_games(state: State, search_name: str = "", priority: int = 3) -> Page:
    """
    Search Steam for games through the FastAPI backend.

    Sends the search term to the backend, receives matching games,
    and saves the results in the application's State.

    Args:
        state: The application's current State object.
        search_name: The game title entered by the user.
        priority: The priority selected for the game.

    Returns:
        The game library page with updated search results or an error message.
    """

    # Save the selected priority as an integer.
    state.Search_priority = int(priority)

    # Check that the search box contains text.
    if not search_name.strip():
        state.Search_results = []
        state.Message = "Please enter a game name."
        return library(state)

    try:
        # Send the search term to the backend.
        response = requests.get(
            BACKEND_URL + "/games/search",
            params={"name": search_name.strip()},
            timeout=20
        )

        # Check whether the backend request was successful.
        response.raise_for_status()

        # Extract the game list from the JSON response.
        state.Search_results = response.json().get("games", [])

        # Display an appropriate message depending on the results.
        if state.Search_results:
            state.Message = (
                "Select the correct game from these results."
            )
        else:
            state.Message = "No matching games were found."

    except requests.exceptions.RequestException:

        # Handle connection problems and unsuccessful HTTP responses.
        state.Search_results = []
        state.Message = (
            "Could not contact the Steam backend. "
            "Check that FastAPI is running on port 8000."
        )

    except (ValueError, KeyError):

        # Handle unexpected or incorrectly formatted response data.
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
    """
    Add a selected Steam game to the user's library.

    Creates a Game object using the information passed from the search
    results and checks for duplicates before adding it.

    Args:
        state: The application's current State object.
        appid: The Steam Application ID of the selected game.
        game_name: The selected game's title.
        image: The URL of the game's image.

    Returns:
        The game library page with a success or duplicate message.
    """

    # Create a Game object using the selected game's information.
    new_game = Game(
        name=game_name,
        appid=appid,
        image=image,
        priority=state.Search_priority
    )

    # Use the helper function to prevent duplicate games.
    if add_game_to_library(state, new_game):
        state.Message = game_name + " was added to your library."
    else:
        state.Message = game_name + " is already in your library."

    return library(state)


@route
def individual_game(state: State, appid: int) -> Page:
    """
    Display an individual game's information and achievements.

    Finds the selected game in the user's library. If its achievements
    have not already been loaded, requests them from the backend.

    Args:
        state: The application's current State object.
        appid: The Steam Application ID of the selected game.

    Returns:
        The individual game's page.
    """

    # Start with no selected game.
    selected_game = None

    # Search the user's library for the matching App ID.
    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    # Return to the game list if the game cannot be found.
    if selected_game is None:
        state.Message = "That game is not in your library."
        return view_Games(state)

    # Find achievements already stored for this game.
    known_achievements = [
        achievement
        for achievement in state.Achievements
        if achievement.Game_name == selected_game.name
    ]

    # Load achievements if this game has none saved yet.
    if not known_achievements:
        try:
            # Request the achievement definitions from the backend.
            steam_achievements = get_achievements_from_backend(appid)

            # Convert each returned dictionary into an Achievement object.
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

                # Save the new achievement in the application State.
                state.Achievements.append(new_achievement)

            # Update the total number of fully completed games.
            refresh_completed_game_count(state)

            # Display a message describing the retrieval result.
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

            # Handle problems communicating with the backend.
            state.Message = (
                "Backend request failed: " + str(error)
            )

        except (KeyError, TypeError, ValueError) as error:

            # Handle problems converting the returned data.
            state.Message = (
                "Achievement data could not be processed: "
                + str(error)
            )

    # Calculate the game's current completion percentage.
    percent = game_completion_percentage(
        selected_game.name,
        state.Achievements
    )

    # Create the individual game's page.
    content = page_start(
        selected_game.name,
        "Achievements and completion progress for this game."
    )

    # Display the latest status message.
    content.append(state.Message)

    # Display a completion message or the current percentage.
    if percent == 100:
        content.append("✓ Completed!")
    else:
        content.append("Completion: " + str(percent) + "%")

    # Provide a button for editing this game's achievements.
    content.append(
        Button(
            "Edit achievement completion",
            "edit_game_achievements",
            [Argument("appid", selected_game.appid)]
        )
    )

    # Track whether any achievements were found for this game.
    found = False

    # Display every achievement associated with the selected game.
    for achievement in state.Achievements:
        if achievement.Game_name == selected_game.name:
            found = True

            # Determine which status label should be displayed.
            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            content.append(
                achievement.name + " — " + status
            )

            # Display the description when one is available.
            if achievement.Description:
                content.append(achievement.Description)

            # Display the achievement category.
            content.append(
                "Category: " + achievement.achievement_type
            )

    # Display a message if the game has no available achievements.
    if not found:
        content.append(
            "No achievement definitions were returned for this game."
        )

    # Add a button to return to the user's game collection.
    content.append(
        Button("Back to My Games", "view_Games")
    )

    return Page(state, content)


@route
def edit_game_achievements(state: State, appid: int) -> Page:
    """
    Display an editing form for one game's achievements.

    Finds the selected game and creates a dropdown containing only
    achievements associated with that game.

    Args:
        state: The application's current State object.
        appid: The Steam Application ID of the selected game.

    Returns:
        The achievement editing page for the selected game.
    """

    # Find the selected game in the user's library.
    selected_game = None

    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    # Return to the game list if the game does not exist.
    if selected_game is None:
        state.Message = "Game not found."
        return view_Games(state)

    # Create the page heading.
    content = page_start(
        selected_game.name + " Achievements",
        "Update the completion status of this game's achievements."
    )

    # Store matching achievements along with their original list indexes.
    game_achievements = []

    for index, achievement in enumerate(state.Achievements):
        if achievement.Game_name == selected_game.name:
            game_achievements.append((index, achievement))

    # Check whether the selected game has any achievements.
    if not game_achievements:
        content.append("No achievements are available for this game.")

    else:

        # Display the current status of each achievement.
        for index, achievement in game_achievements:
            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            content.append(achievement.name + " — " + status)

        # Build the dropdown choices using the original list indexes.
        choices = []

        for index, achievement in game_achievements:
            choices.append(
                str(index) + " - " + achievement.name
            )

        # Add the editing controls to the page.
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

    # Add a button to return to the selected game's page.
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
    """
    Display all games saved in the user's library.

    Copies the game list and sorts it according to the user's settings.
    Each game displays its priority, completion percentage, and buttons
    for opening or removing it.

    Args:
        state: The application's current State object.

    Returns:
        The user's game collection page.
    """

    # Create the shared navigation and page heading.
    content = page_start(
        "My Games",
        "All video games you have added to your collection."
    )

    # Copy the game list so sorting does not directly reorder State.Games.
    games = state.Games[:]

    # Sort from highest to lowest priority.
    if state.Sort_order == "Highest Priority":
        games.sort(
            key=lambda game: game.priority,
            reverse=True
        )

    # Sort from lowest to highest priority.
    elif state.Sort_order == "Lowest Priority":
        games.sort(key=lambda game: game.priority)

    # Use alphabetical order for any other sorting option.
    else:
        games.sort(key=lambda game: game.name.lower())

    # Display a message if the library is empty.
    if not games:
        content.append("Your library is empty.")

    else:

        # Display each game and its current progress.
        for game in games:
            percent = game_completion_percentage(
                game.name, state.Achievements
            )

            content.append(
                game.name
                + " | Priority: " + str(game.priority)
                + " | Completion: " + str(percent) + "%"
            )

            # Identify games with all known achievements completed.
            if percent == 100:
                content.append("✓ Completed!")

            # Add a button to open the game's individual page.
            content.append(
                Button(
                    "Open Game",
                    "individual_game",
                    [Argument("appid", game.appid)]
                )
            )

            # Add a button to remove the game from the library.
            content.append(
                Button(
                    "Remove Game",
                    "remove_game",
                    [Argument("appid", game.appid)]
                )
            )

    # Add a button for searching and adding more games.
    content.append(Button("Add More Games", "library"))

    return Page(state, content)


@route
def remove_game(state: State, appid: int) -> Page:
    """
    Remove a game and its associated achievements.

    Finds the game using its Steam App ID, removes it from the library,
    and removes all achievements associated with that game.

    Args:
        state: The application's current State object.
        appid: The Steam Application ID of the game to remove.

    Returns:
        The updated game collection page.
    """

    # Start with an empty game name.
    game_name = ""

    # Find the game that matches the supplied App ID.
    for game in state.Games:
        if game.appid == appid:
            game_name = game.name
            break

    # Return to the game list if no matching game exists.
    if not game_name:
        state.Message = "That game could not be found."
        return view_Games(state)

    # Create a new game list without the removed game.
    state.Games = [
        game for game in state.Games
        if game.appid != appid
    ]

    # Remove achievements associated with the deleted game.
    state.Achievements = [
        achievement for achievement in state.Achievements
        if achievement.Game_name != game_name
    ]

    # Recalculate the number of fully completed games.
    refresh_completed_game_count(state)

    # Display a confirmation message.
    state.Message = game_name + " was removed."

    return view_Games(state)


@route
def view_Achievements(state: State) -> Page:
    """
    Display all achievements and provide a completion editing form.

    Achievements are displayed newest-first. The user can select an
    achievement and change its completion status.

    Args:
        state: The application's current State object.

    Returns:
        The achievement overview page.
    """

    # Create the shared navigation and page heading.
    content = page_start(
        "My Achievements",
        "Review your achievements and update which ones you have earned."
    )

    # Check whether any achievements have been loaded.
    if not state.Achievements:
        content.append(
            "No achievements have been loaded yet. "
            "Open a game from My Games to retrieve its achievements."
        )

    else:

        # Display achievements in reverse order.
        for achievement in state.Achievements[::-1]:

            # Determine the achievement's completion label.
            status = (
                "✓ Completed"
                if achievement.Completed
                else "Not completed"
            )

            # Display the game name, achievement name, and status.
            content.append(
                achievement.Game_name + " — " + achievement.name
                + " — " + status
            )

            # Display the description if it exists.
            if achievement.Description:
                content.append(achievement.Description)

            # Display the achievement category.
            content.append(
                "Category: " + achievement.achievement_type
            )

        # Create a heading for the editing controls.
        content.append(Header("Update an Achievement", 2))

        # Build a dropdown containing every achievement.
        choices = []

        for index, achievement in enumerate(state.Achievements):
            choices.append(
                str(index) + " - " + achievement.Game_name
                + ": " + achievement.name
            )

        # Add the selection dropdown and completion checkbox.
        content.extend([
            "Choose an achievement:",
            SelectBox("achievement_choice", choices),
            "Check this box if the achievement is completed:",
            CheckBox("completed", False),

            # NOTE: This button currently does not pass the required
            # appid argument to save_achievement.
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
    """
    Update the completion status of a selected achievement.

    Finds the game using its Steam App ID, extracts the selected
    achievement's original list index, and updates its Completed value.

    Args:
        state: The application's current State object.
        appid: The Steam Application ID of the game.
        achievement_choice: The selected dropdown value containing
            the achievement's list index and name.
        completed: Whether the achievement should be marked completed.

    Returns:
        The achievement editing page for the selected game.
    """

    # Find the game associated with the supplied App ID.
    selected_game = None

    for game in state.Games:
        if game.appid == appid:
            selected_game = game
            break

    # Return to the game list if the game cannot be found.
    if selected_game is None:
        state.Message = "Game not found."
        return view_Games(state)

    try:
        # Extract the original achievement index from the dropdown value.
        achievement_index = int(
            achievement_choice.split(" - ", 1)[0]
        )

        # Confirm the index is valid and belongs to the selected game.
        if (
            0 <= achievement_index < len(state.Achievements)
            and state.Achievements[achievement_index].Game_name
            == selected_game.name
        ):

            # Update the selected achievement's completion status.
            state.Achievements[achievement_index].Completed = completed
            state.Message = "Achievement status updated."

        else:
            state.Message = "Please select a valid achievement."

    except (ValueError, IndexError):

        # Handle invalid dropdown selections or indexes.
        state.Message = "Please select a valid achievement."

    # Recalculate the completed-game total after the update.
    refresh_completed_game_count(state)

    # Return to the selected game's achievement editing page.
    return edit_game_achievements(state, appid)


# --------------------------------------------------
# Website configuration
# --------------------------------------------------

# Set the title displayed for the website.
set_website_title("Achievement Hub")

# Provide information about the website and its sources.
set_site_information(
    author="Dinesh Goswami",
    description=(
        "Achievement Hub allows users to search for video games, "
        "organize their personal library, and track achievements."
    ),
    sources=(
        "Steam Store Search API, Steam Web API, Drafter, and FastAPI."
    ),
    planning=["planning_document.md"],
    links=[
        "https://github.com/dingos-afk/Achievement-Hub"
    ]
)

# Hide Drafter's debugging information from the website.
hide_debug_information()

# Disable the framed website layout.
set_website_framed(False)

# Start the Drafter application with an initial State object.
# The initial username is "Player".
# The website runs on port 8001.
start_server(
    State("Player"),
    site_title="Achievement Hub",
    port=8001
)
