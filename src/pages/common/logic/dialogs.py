# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Protocol

import flet as ft

from src.utils import Dialog, Page


class UserListControl(Protocol):
    @property
    def main_container(self) -> ft.Control: ...

    def update_data(self, users: list[dict[str, str] | str], current_user: str = "", user_created_at: dict[str, str] | None = None) -> None: ...


def show_user_management_dialog(page: Page, user_list: UserListControl, user_dialog: Dialog, users: list[dict[str, str]], current_username: str) -> int:
    user_list.update_data(users, current_username)
    try:
        user_list.main_container.update()
        user_dialog.update()
        page.update()
    except RuntimeError:
        pass
    return user_dialog.show()


def close_user_management_dialog(user_dialog: Dialog) -> int:
    return user_dialog.dismiss()
