"""
Achievement Hub Design Components

This module contains reusable visual components for the
Achievement Hub website.

It provides functions for creating the website's navigation
menu and standardized page headings. These functions help
maintain a consistent layout across different website pages.

Functions:
- navigation(): Creates the main navigation menu.
- page_heading(): Creates a page title and subtitle.
"""

from drafter import *


def navigation() -> list:
    """
    Create the main navigation menu for Achievement Hub.

    This function creates a list of Drafter components that
    display the website title and clickable links to the
    different sections of the website.

    The navigation menu is reused across multiple pages so
    users can move between sections without returning to
    the homepage.

    Returns:
        list: A list of Drafter components containing:
            - Header: Displays the Achievement Hub website name.
            - Link: Creates clickable links to website routes.
            - HorizontalRule: Separates the navigation menu
              from the rest of the page.
    """

    return [
        # Display the website name at the top of the menu.
        Header("ACHIEVEMENT HUB"),

        # Create a link to the homepage.
        Link("Home", "index"),

        # Add a separator between navigation links.
        " | ",

        # Create a link to the user's profile.
        Link("Profile", "Profile"),

        " | ",

        # Create a link to the website settings.
        Link("Settings", "Settings"),

        " | ",

        # Create a link to the user's saved game library.
        Link("My Library", "view_Games"),

        " | ",

        # Create a link to the Steam game search page.
        Link("Browse Games", "library"),

        " | ",

        # Create a link to the user's achievement list.
        Link("My Achievements", "view_Achievements"),

        # Add a horizontal divider below the navigation menu.
        HorizontalRule()
    ]


def page_heading(title: str, subtitle: str) -> list:
    """
    Create a standardized heading for a website page.

    This function displays a large page title followed by
    a subtitle explaining the purpose of that page.

    It also adds a horizontal divider underneath the heading
    to visually separate it from the page's main content.

    Args:
        title (str): The main heading displayed on the page.
        subtitle (str): A short description displayed below
        the main heading.

    Returns:
        list: A list of Drafter components containing:
            - Header: Displays the page title.
            - str: Displays the subtitle.
            - HorizontalRule: Separates the heading from
              the remaining page content.
    """

    return [
        # Display the page title as a level-one heading.
        Header(title, 1),

        # Display the subtitle underneath the title.
        subtitle,

        # Add a divider below the heading.
        HorizontalRule()
    ]
