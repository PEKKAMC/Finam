# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.database import db
from src.logger import Logger

LAST_USER_KEY = "last_user"


async def get_last_user(preferences: ft.SharedPreferences) -> str:
    username = await preferences.get(LAST_USER_KEY)
    if isinstance(username, str) and username and db.users.get_user_id(username):
        return username
    if username and not await preferences.remove(LAST_USER_KEY):
        Logger.error("Failed to clear invalid saved user")
    return ""


async def save_last_user(
    preferences: ft.SharedPreferences, username: str
) -> bool:
    if await preferences.set(LAST_USER_KEY, username):
        return True
    Logger.error("Failed to save last selected user")
    return False


def get_user_currency(username: str) -> str:
    return db.users.get_currency(username)


def get_all_users() -> list[dict[str, str]]:
    return db.users.get_all_users()


def add_user(username: str, currency: str) -> int:
    return db.users.add_user(username, currency)


def delete_user(username: str) -> int:
    """
    :param username: Username for the user to be deleted.
    :return: int: 0 if the user was deleted successfully, 1 if the user does not exist.
    """
    return db.users.delete_user(username)


def change_user(user_info: dict[str, str], username: str) -> None:
    user_info["username"] = username
