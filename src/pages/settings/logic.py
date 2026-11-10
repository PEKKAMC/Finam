# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
from pathlib import Path
from typing import Any

from src.database import db
from src.logger import Logger
from src.pages.common.logic import get_user_currency
from src.utils import Data, ThemeRegistry, get_asset_path


class LogicController:
    def __init__(self, user_info: dict[str, str]) -> None:
        self.user_info = user_info

    @staticmethod
    def get_currencies() -> list[str]:
        return Data().get_currencies()

    @staticmethod
    def get_initial_settings(username: str) -> dict[str, Any]:
        language_files = sorted(Path(get_asset_path("lang")).glob("*.json"))
        if not language_files:
            raise FileNotFoundError("No language files found in assets/lang")

        language_name_to_code: dict[str, str] = {}
        for language_file in language_files:
            with language_file.open("r", encoding="utf-8-sig") as file:
                language_name = json.load(file)["language"]
            language_name_to_code[language_name] = language_file.stem

        return {
            "language": db.users.get_language(username),
            "currency": get_user_currency(username),
            "theme": db.app_settings.get_theme(),
            "digit_separator": db.app_settings.get_digit_separator(),
            "decimal_separator": db.app_settings.get_decimal_separator(),
            "app_lock": db.app_security.is_app_lock_enabled(),
            "language_name_to_code": language_name_to_code,
            "theme_names": (*ThemeRegistry.names(), "system"),
            "currencies": Data().get_currencies(),
        }

    @staticmethod
    def save_settings(username: str, language: str, currency: str, theme: str, digit_separator: str, decimal_separator: str) -> int:
        if digit_separator and digit_separator == decimal_separator:
            return 1
        if not db.app_settings.set_theme(theme):
            Logger.error("Failed to save app theme setting")
            return -1
        if not db.app_settings.set_digit_separator(digit_separator):
            Logger.error("Failed to save digit separator setting")
            return -2
        if not db.app_settings.set_decimal_separator(decimal_separator):
            Logger.error("Failed to save decimal separator setting")
            return -3
        if not db.users.set_language(username, language):
            Logger.error("Failed to save user language setting")
            return -4
        if not db.app_settings.set_starter_language(language):
            Logger.error("Failed to save starter language setting")
            return -5
        if not db.users.set_currency(username, currency):
            Logger.error("Failed to save user currency setting")
            return -6
        return 0

    @staticmethod
    def is_app_lock_enabled() -> bool:
        return db.app_security.is_app_lock_enabled()

    @staticmethod
    def disable_app_lock() -> None:
        db.app_security.disable_app_lock()

    @staticmethod
    def save_app_lock_pin(pin: str, confirmation: str) -> int:
        if len(pin) != 4 or not pin.isascii() or not pin.isdigit():
            return 1
        if pin != confirmation:
            return 2
        if not db.app_security.set_app_lock_pin(pin):
            return -1
        return 0
