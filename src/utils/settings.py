# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import locale
import os


def _detect_default_language() -> str:
    system_locale = locale.getlocale()[0]
    return language_for_device_locale(system_locale)


def language_for_device_locale(language_code: str | None) -> str:
    """Map the device's primary language to one of the app's supported languages."""
    normalized_language = (language_code or "").strip().lower()
    return "vi" if normalized_language.startswith(("vi", "vietnamese")) else "en"


class DefaultSettings:
    USERNAME: str = "Admin"
    THEME: str = "system"
    CURRENCY: str = "VND (đ)"
    LANGUAGE: str = _detect_default_language()
    APP_LOCK: bool = False
    DIGIT_SEPARATOR: str = ","
    DECIMAL_SEPARATOR: str = "."


class UISettings:
    MAX_APP_WIDTH: int = 432
    MAX_APP_HEIGHT: int = 960
    MIN_SUPPORTED_WIDTH: int = 250
    MIN_SUPPORTED_HEIGHT: int = 650
    CARD_BORDER_RADIUS: int = 28
    CARD_PADDING: int = 20
    METRIC_PILL_BORDER_RADIUS: int = 16
    METRIC_PILL_PADDING: int = 8
    TOP_NAVIGATION_HEIGHT: int = 50
    SHADOW_BLUR: int = 10
    SHADOW_SPREAD: int = 1
