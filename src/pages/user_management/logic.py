# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

from src.database import db
from src.logger import Logger
from src.utils import Data

class LogicController:
    def __init__(self, user_info: dict):
        self.user_info = user_info

    @staticmethod
    def get_all_users() -> list[dict]:
        return db.users.get_all_users()

    def add_user(self, input_username: str, currency: str) -> tuple[bool, str]:
        current_users = self.get_all_users()
        if input_username not in current_users:
            db.users.add_user(input_username, currency)
            Logger.info(f"Created user: {input_username}, currency: {currency}")
            return True, ""
        return False, "user_management.user_already_exists"

    @staticmethod
    def delete_user(username: str):
        db.users.delete_user(username)
        Logger.info(f"Deleted user: {username}")

    def change_user(self, username: str):
        self.user_info["username"] = username

    @staticmethod
    def delete_all_data():
        """Deletes data.db and any associated SQLite database files."""
        db_path = db.connection.database_name
        for suffix in ["", "-wal", "-shm"]:
            file_path = f"{db_path}{suffix}"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    Logger.info(f"Deleted database file: {file_path}")
                except Exception as ex:
                    Logger.error(f"Error deleting database file {file_path}: {ex}")

    @staticmethod
    def get_currencies() -> list:
        return Data().get_currencies()

    @staticmethod
    def get_currency(username: str) -> str:
        return db.users.get_currency(username)