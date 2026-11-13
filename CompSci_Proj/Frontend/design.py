
"""Shared visual elements for Achievement Hub."""

from drafter import *


def navigation() -> list:
    """Return the navigation links used on every page."""

    return [
        Header("ACHIEVEMENT HUB"),
        Link("Home", "index"),
        " | ",
        Link("Profile", "Profile"),
        " | ",
        Link("Settings", "Settings"),
        " | ",
        Link("My Library", "view_Games"),
        " | ",
        Link("Browse Games", "library"),
        " | ",
        Link("My Achievements", "view_Achievements"),
        HorizontalRule()
    ]


def page_heading(title: str, subtitle: str) -> list:
    """Return a heading and subtitle for a page."""

    return [
        Header(title, 1),
        subtitle,
        HorizontalRule()
    ]