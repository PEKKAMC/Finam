# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils.settings import UISettings


def get_safe_page_size(page: ft.Page) -> tuple[int, int]: # -> (width, height)
    # Get page width and height if available, return fallback values otherwise
    current_width: float = page.width or UISettings.MAX_APP_WIDTH
    current_height: float = page.height or UISettings.MAX_APP_HEIGHT

    # Make sure width and height don't exceed max values
    safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
    safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)

    return safe_width, safe_height