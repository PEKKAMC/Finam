# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.database import db
from src.logger import Logger


class LogicController:
    def __init__(self, user_info: dict):
        self.user_info = user_info

    @staticmethod
    def get_all_users() -> list:
        return db.users.get_all_users()

    def add_user(self, input_username: str) -> tuple[bool, str]:
        current_users = self.get_all_users()
        if input_username not in current_users:
            db.users.add_user(input_username)
            Logger.info(f"Created user: {input_username}")
            return True, ""
        return False, "user_management.user_already_exists"

    @staticmethod
    def delete_user(username: str):
        db.users.delete_user(username)
        Logger.info(f"Deleted user: {username}")

    def change_user(self, username: str):
        self.user_info["username"] = username