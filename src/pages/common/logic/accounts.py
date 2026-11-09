# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.database import db


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
