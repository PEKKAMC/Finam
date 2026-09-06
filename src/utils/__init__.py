# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Utils package - Default settings, text utilities, and asset helpers."""

from src.utils.assets import get_asset_path, get_language, TranslationDict
from src.utils.color import Color
from utils.resizing import get_safe_page_size
from src.utils.settings import DefaultSettings, UISettings
from src.utils.text import Text, TEXT_STYLES, create_text

__all__ = [
    # Assets
    "get_asset_path",
    "get_language",
    "TranslationDict",
    # Color
    "Color",
    # Resizing
    "get_safe_page_size",
    # Settings
    "DefaultSettings",
    "UISettings",
    # Text
    "Text",
    "TEXT_STYLES",
    "create_text"
]
