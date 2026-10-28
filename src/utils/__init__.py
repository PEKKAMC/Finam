# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Utils package - Default settings, text utilities, and asset helpers."""

from src.utils.assets import get_asset_path, get_language, TranslationDict
from src.utils.color import Color, DarkTheme, LightTheme, Theme, ThemeManager, ThemeName, ThemeRegistry
from src.utils.data import Data
from src.utils.page import Page
from src.utils.dialog import Dialog
from src.utils.resizing import get_safe_page_size
from src.utils.settings import DefaultSettings, UISettings
from src.utils.text import Text, TEXT_STYLES, create_text
from src.utils.number_format import (
    format_expression,
    format_number,
    get_decimal_separator,
    set_decimal_separator,
    set_digit_separator,
)

__all__ = [
    # Assets
    "get_asset_path",
    "get_language",
    "TranslationDict",
    # Color
    "Color",
    "LightTheme",
    "DarkTheme",
    "Theme",
    "ThemeManager",
    "ThemeName",
    "ThemeRegistry",
    # Data
    "Data",
    # Dialog
    "Dialog",
    # Page
    "Page",
    # Resizing
    "get_safe_page_size",
    # Settings
    "DefaultSettings",
    "UISettings",
    # Text
    "Text",
    "TEXT_STYLES",
    "create_text",
    # Number formatting
    "format_expression",
    "format_number",
    "get_decimal_separator",
    "set_decimal_separator",
    "set_digit_separator",
]
