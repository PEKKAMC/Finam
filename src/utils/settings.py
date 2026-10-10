# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

class DefaultSettings:
    USERNAME: str = "Admin"
    THEME: str = "light"
    CURRENCY: str = "VND (đ)"
    LANGUAGE: str = "vi"

    @classmethod
    def get_language(cls, username: str = "Admin") -> str:
        """Get the language setting for a user from the database."""
        try:
            from src.database import db
            return db.users.get_language(username)
        except:
            return cls.LANGUAGE

    @classmethod
    def get_currency(cls, username: str = "Admin") -> str:
        """Get the currency setting for a user from the database."""
        try:
            from src.database import db
            return db.users.get_currency(username)
        except:
            return cls.CURRENCY


def get_user_currency(username: str = "Admin") -> str:
    """Return the saved currency for the current user."""
    try:
        from src.database import db
        return db.users.get_currency(username)
    except Exception:
        return DefaultSettings.CURRENCY


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
    MENU_HEIGHT: int = 72
    SHADOW_BLUR: int = 10
    SHADOW_SPREAD: int = 1
