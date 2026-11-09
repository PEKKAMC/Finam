# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.logger import Logger
from src.pages.common.logic import add_user, change_user, delete_user, get_all_users
from src.utils import Data

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
