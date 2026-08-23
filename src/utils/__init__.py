# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Utils package - Default settings, text utilities, and asset helpers."""

# Import from defaults module
from src.utils.settings import DefaultSettings, UISettings

# Import from assets module
from src.utils.assets import get_asset_path, get_language, TranslationDict

# Import from text module
from src.utils.text import (
    Text,
    TEXT_STYLES,
    create_text
)

# Import from color module
from src.utils.color import Color

__all__ = [
    # Defaults
    "DefaultSettings",
    "UISettings",
    # Assets
    "get_asset_path",
    "get_language",
    "TranslationDict",
    # Text
    "Text",
    "TEXT_STYLES",
    "create_text",
    # Color
    "Color",
]
