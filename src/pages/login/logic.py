# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.database import db
from src.logger import Logger


class LogicController:
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.view = None

    def set_view(self, view):
        """Bind the view to the controller so it can trigger UI updates."""
        self.view = view

    @staticmethod
    def get_all_users() -> list:
        return db.users.get_all_users()

    def add_user(self, input_username: str) -> tuple[bool, str]:
        current_users = self.get_all_users()
        if input_username not in current_users:
            db.users.add_user(input_username)
            Logger.info(f"Created user: {input_username}")
            return True, ""
        return False, self.lang["login.user_already_exists"]

    @staticmethod
    def delete_user(username: str):
        db.users.delete_user(username)
        Logger.info(f"Deleted user: {username}")

    def login_user(self, username: str):
        self.user_info["username"] = username
        self._page.go("/home")

    def handle_add_user(self, input_username: str):
        if not input_username:
            return

        success, error_msg = self.add_user(input_username)
        if success:
            self.view.add_form.clear()
            self.view.user_list.refresh(self.get_all_users(), self.user_info.get("username", ""))
        else:
            self.view.add_form.show_error(error_msg)

    def handle_delete_prompt(self, username: str):
        self.view.delete_dialog.show(username)

    def handle_delete_confirm(self, username: str):
        self.delete_user(username)
        self.view.user_list.refresh(self.get_all_users(), self.user_info.get("username", ""))