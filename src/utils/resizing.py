# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Any, TypedDict

from src.utils import Page
from src.utils.settings import UISettings


class MenuResizeValues(TypedDict):
    item_size: int
    item_height: int
    inside_size: int
    inside_height: int
    banner_height: int
    total_height: int
    label_size: int
    icon_size: int
    label_spacing: int
    label_visible: bool


def get_safe_page_size(page: Page) -> tuple[int, int]: # -> (width, height)
    # Get page width and height if available, return fallback values otherwise
    current_width: float = page.width or UISettings.MAX_APP_WIDTH
    current_height: float = page.height or UISettings.MAX_APP_HEIGHT

    # Make sure width and height don't exceed max values
    safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
    safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)

    return safe_width, safe_height


def scale_width(page_width: int, design_width: int) -> int:
    return int(page_width * design_width / UISettings.MAX_APP_WIDTH)


def scale_height(page_height: int, design_height: int) -> int:
    return int(page_height * design_height / UISettings.MAX_APP_HEIGHT)


def is_supported_page_size(page: Page) -> bool:
    return (
        (page.width is None or page.width >= UISettings.MIN_SUPPORTED_WIDTH)
        and (page.height is None or page.height >= UISettings.MIN_SUPPORTED_HEIGHT)
    )


def get_menu_resize_values(page_width: int, menu: Any) -> MenuResizeValues:
    item_size = page_width // menu.items_count
    item_height = 48 if item_size < 48 else item_size
    banner_height = (
        menu.BANNER_HEIGHT
        if menu.ad_banner is not None and page_width >= menu.BANNER_WIDTH
        else 0
    )
    return {
        "item_size": item_size,
        "item_height": item_height,
        "inside_size": item_size * 5 // 6,
        "inside_height": item_height * 5 // 6,
        "banner_height": banner_height,
        "total_height": item_height + banner_height,
        "label_size": 8 if item_size < 48 else 10,
        "icon_size": 18 if item_size < 48 else 20,
        "label_spacing": 2 if item_size < 48 else 4,
        "label_visible": item_size >= 48,
    }
