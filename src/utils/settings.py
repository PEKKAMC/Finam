# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import locale
import os

from babel.numbers import get_territory_currencies

from src.utils.data import Data


def _detect_default_language() -> str:
    system_locale = locale.getlocale()[0]
    return language_for_device_locale(system_locale)


def language_for_device_locale(language_code: str | None) -> str:
    """Map the device's primary language to one of the app's supported languages."""
    normalized_language = (language_code or "").strip().lower()
    return "vi" if normalized_language.startswith(("vi", "vietnamese")) else "en"


def _detect_default_region() -> str | None:
    system_locale = locale.getlocale()[0] or os.getenv("LANG", "")
    locale_name = system_locale.split(".", maxsplit=1)[0].split("@", maxsplit=1)[0]
    parts = locale_name.replace("-", "_").split("_")
    return next(
        (part.upper() for part in parts[1:] if len(part) == 2 and part.isalpha()),
        None,
    )


def currency_for_region(
    region_code: str | None,
    supported_currencies: list[str] | None = None,
) -> str:
    """Return the region's current standard currency from the app's supported list."""
    fallback = "USD ($)"
    if not region_code or len(region_code) != 2:
        return fallback

    try:
        currency_codes = get_territory_currencies(region_code.upper())
    except ValueError:
        return fallback

    currencies = (
        supported_currencies
        if supported_currencies is not None
        else Data().get_currencies()
    )
    for code in currency_codes:
        match = next(
            (currency for currency in currencies if currency.startswith(f"{code} (")),
            None,
        )
        if match:
            return match
    return fallback


class DefaultSettings:
    USERNAME: str = "Admin"
    THEME: str = "system"
    CURRENCY: str = currency_for_region(_detect_default_region())
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
