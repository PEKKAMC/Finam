# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Text classification system."""

from enum import Enum

import flet as ft


class Text(Enum):
    """Text classifications."""
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    P = "p"
    LABEL = "label"
    MEDIUM = "medium"
    SMALL = "small"
    BUTTON = "button"
    BADGE = "badge"

    def __call__(self, value: str, **kwargs) -> ft.Text:
        """
        Allows calling the enum member directly, e.g., Text.H1("Title").
        'self' represents the specific enum member being called.
        """
        size, weight = TEXT_STYLES.get(self, TEXT_STYLES[Text.P])

        # Apply default weight from our styles, unless overridden in kwargs
        kwargs.setdefault("weight", weight)

        return create_text(value, size=size, **kwargs)


# Centralized styles: (size, weight)
TEXT_STYLES = {
    Text.H1: (32, ft.FontWeight.BOLD),
    Text.H2: (24, ft.FontWeight.BOLD),
    Text.H3: (19, ft.FontWeight.BOLD),
    Text.H4: (16, ft.FontWeight.BOLD),
    Text.H5: (13, ft.FontWeight.BOLD),
    Text.H6: (11, ft.FontWeight.BOLD),
    Text.P: (16, ft.FontWeight.NORMAL),
    Text.LABEL: (9, ft.FontWeight.W_500),
    Text.MEDIUM: (12, ft.FontWeight.NORMAL),
    Text.SMALL: (10, ft.FontWeight.NORMAL),
    Text.BUTTON: (14, ft.FontWeight.W_500),
    Text.BADGE: (12, ft.FontWeight.W_500),
}


def create_text(value: str, size: int, **kwargs) -> ft.Text:
    """Create a flet.Text with metadata."""
    text = ft.Text(value, size=size, **kwargs)
    return text