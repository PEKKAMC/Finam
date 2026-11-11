# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import json
import os
import requests
from typing import Any

from src.database import db
from src.logger import Logger
from src.pages.common.logic import add_user, change_user, delete_user, get_all_users
from src.pages.purchase_scanner.logic import LogicController as PurchaseScannerController
from src.utils import Data, get_asset_path

class LogicController:
    def __init__(self, user_info: dict[str, str]) -> None:
        self.user_info = user_info

    @staticmethod
    def get_all_users() -> list[dict[str, str]]:
        return get_all_users()

    @staticmethod
    def add_user(input_username: str, currency: str) -> int:
        status = add_user(input_username, currency)

        if status == 0:
            Logger.info(f"Created user: {input_username}, currency: {currency}")
        elif status == 1:
            Logger.error(f"Failed to create user: {input_username}\nUser already exists.")
        else:
            Logger.error(f"Failed to create user: {input_username}\nUnknown error occurred.")

        return status

    @staticmethod
    def delete_user(username: str) -> None:
        status = delete_user(username)

        if status == 0:
            Logger.info(f"Deleted user: {username}")
        elif status == 1:
            Logger.error(f"Failed to delete user: {username}\nUser does not exist.")
        else:
            Logger.error(f"Failed to delete user: {username}\nUnknown error occurred.")

    def change_user(self, username: str) -> None:
        change_user(self.user_info, username)

    @staticmethod
    def get_currencies() -> list[str]:
        return Data().get_currencies()

    @staticmethod
    def delete_all_data() -> None:
        """Deletes data.db and any associated SQLite database files."""
        db_path = db.connection.database_name
        for suffix in ["", "-wal", "-shm"]:
            file_path = f"{db_path}{suffix}"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    Logger.info(f"Deleted database file: {file_path}")
                except OSError as ex:
                    Logger.error(f"Error deleting database file {file_path}: {ex}")

    @staticmethod
    def get_google_auth_config() -> dict[str, Any]:
        with open(get_asset_path("google_auth.json"), encoding="utf-8") as file:
            config = json.load(file)
        if not isinstance(config, dict):
            raise TypeError("Google auth configuration must be a JSON object")
        return config

    @staticmethod
    async def save_google_account(firebase_id_token: str, backend_url: str, refresh_token: str) -> bool:
        def fetch_profile() -> dict[str, Any]:
            response = requests.get(
                f"{backend_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {firebase_id_token}"},
                timeout=15,
            )
            response.raise_for_status()
            return response.json()

        profile = await asyncio.to_thread(fetch_profile)
        if not isinstance(profile, dict):
            raise TypeError("Firebase returned an invalid user profile")
        google_uid = profile.get("uid", "")
        email = profile.get("email", "")
        if not google_uid or not email:
            raise RuntimeError("Firebase returned an incomplete user profile")
        return db.app_settings.set_google_account(
            google_uid,
            email,
            refresh_token,
        )

    @staticmethod
    def get_google_account_state() -> tuple[dict[str, str] | None, bool, str | None]:
        account = db.app_settings.get_google_account()
        signed_in = db.app_settings.has_google_account_session()
        cached_tier = (
            db.app_settings.get_google_account_tier(account["uid"])
            if signed_in and account
            else None
        )
        return account, signed_in, cached_tier

    def fetch_google_account_tier(self) -> tuple[str, str]:
        account = db.app_settings.get_google_account()
        if not account or not db.app_settings.has_google_account_session():
            return "", "guest"

        refresh_token = db.app_settings.get_google_refresh_token()
        tier = PurchaseScannerController(
            self.user_info["username"]
        ).get_account_tier(refresh_token or "")
        current_account = db.app_settings.get_google_account()
        if not current_account or current_account["uid"] != account["uid"]:
            return account["uid"], "guest"
        if not db.app_settings.set_google_account_tier(account["uid"], tier):
            Logger.warning("Could not cache Google account tier")
        return account["uid"], tier

    @staticmethod
    def clear_google_account() -> bool:
        return db.app_settings.clear_google_account()

    @staticmethod
    def save_starter_language_for_logout(username: str) -> bool:
        language = db.users.get_language(username)
        return db.app_settings.set_starter_language(language)