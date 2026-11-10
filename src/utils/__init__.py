# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Utils package - Default settings, text utilities, and asset helpers."""

from src.utils.assets import TranslationDict, get_asset_path, get_language
from src.utils.color import Color, DarkTheme, LightTheme, Theme, ThemeManager, ThemeName, ThemeRegistry
from src.utils.data import Data
from src.utils.number_format import format_compact_number, format_display_number, format_expression, format_number, get_decimal_separator, set_decimal_separator, set_digit_separator
from src.utils.money import Money, to_decimal
from src.utils.page import Page
from src.utils.dialog import Dialog
from src.utils.resizing import MenuResizeValues, get_menu_resize_values, get_safe_page_size, is_supported_page_size, scale_height, scale_width
from src.utils.settings import DefaultSettings, UISettings, currency_for_region, language_for_device_locale
from src.utils.text import TEXT_STYLES, Text, create_text

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
    # Number formatting
    "format_compact_number",
    "format_display_number",
    "format_expression",
    "format_number",
    "get_decimal_separator",
    "set_decimal_separator",
    "set_digit_separator",
    "Money",
    "to_decimal",
    # Page
    "Page",
    # Resizing
    "MenuResizeValues",
    "get_safe_page_size",
    "get_menu_resize_values",
    "is_supported_page_size",
    "scale_width",
    "scale_height",
    # Settings
    "DefaultSettings",
    "UISettings",
    "currency_for_region",
    "language_for_device_locale",
    # Text
    "Text",
    "TEXT_STYLES",
    "create_text"
]
