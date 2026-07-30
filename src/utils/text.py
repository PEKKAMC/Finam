# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Text classification system for responsive mobile-first design."""

from enum import Enum

import flet as ft

from src.logger import Logger


class Text(Enum):
    """Text classifications."""
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    P = "p"
    LABEL = "label"
    SMALL = "small"
    BUTTON = "button"
    BADGE = "badge"

    def __call__(self, value: str, **kwargs) -> ft.Text:
        """
        Allows calling the enum member directly, e.g., Text.H1("Title").
        'self' represents the specific enum member being called.
        """
        scale, min_size, max_size, weight = TEXT_STYLES.get(self, TEXT_STYLES[Text.P])

        # Apply default weight from our styles, unless overridden in kwargs
        kwargs.setdefault("weight", weight)

        return responsive_text(value, scale=scale, min_size=min_size, max_size=max_size, **kwargs)


# Centralized styles: (scale, min_size, max_size, weight)
TEXT_STYLES = {
    Text.H1: (0.093, 18, 36, ft.FontWeight.BOLD),
    Text.H2: (0.080, 16, 32, ft.FontWeight.BOLD),
    Text.H3: (0.067, 14, 28, ft.FontWeight.BOLD),
    Text.H4: (0.057, 12, 24, ft.FontWeight.W_600),
    Text.P: (0.047, 10, 20, ft.FontWeight.NORMAL),
    Text.LABEL: (0.043, 9, 18, ft.FontWeight.W_500),
    Text.SMALL: (0.033, 8, 16, ft.FontWeight.NORMAL),
    Text.BUTTON: (0.047, 10, 20, ft.FontWeight.W_500),
    Text.BADGE: (0.037, 8, 16, ft.FontWeight.W_500),
}


def responsive_text(value: str, scale: float, min_size: int, max_size: int, **kwargs) -> ft.Text:
    """Create a flet.Text with metadata used for responsive resizing."""
    size = max(min_size, min(max_size, int(300 * scale)))
    text = ft.Text(value, size=size, **kwargs)

    # Attach metadata for apply_responsive_text
    setattr(text, "resp_scale", scale)
    setattr(text, "resp_min", min_size)
    setattr(text, "resp_max", max_size)
    return text

def apply_responsive_text(control: ft.Control, safe_width: int):
    """Recursively traverse the control tree and update Text sizes."""
    if not control:
        return

    if isinstance(control, ft.Text) and hasattr(control, "resp_scale"):
        scale = getattr(control, "resp_scale")
        min_size = getattr(control, "resp_min")
        max_size = getattr(control, "resp_max")

        new_size = min(max(min_size, int(safe_width * scale)), max_size)

        try:
            if control.size != new_size:
                control.size = new_size
        except Exception as e:
            Logger.warn(f"Failed to set size for control: {e}")

    if hasattr(control, "content") and control.content:
        apply_responsive_text(control.content, safe_width)

    if hasattr(control, "controls") and control.controls:
        for child in control.controls:
            apply_responsive_text(child, safe_width)

    for attr in ["title", "subtitle", "leading", "trailing", "actions"]:
        if hasattr(control, attr):
            val = getattr(control, attr)
            if isinstance(val, list):
                for item in val:
                    apply_responsive_text(item, safe_width)
            elif isinstance(val, ft.Control):
                apply_responsive_text(val, safe_width)

    try:
        control.update()
    except Exception as e:
        Logger.debug(f"Skipped updating control: {e}")