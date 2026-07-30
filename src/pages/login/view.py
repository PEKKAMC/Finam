# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.utils import UISettings, apply_responsive_text, Color
from src.pages.login.logic import LogicController
from src.pages.login.components import LoginHeader, AddUserField, UserList, DeleteUserDialog


Logger.info("Initializing Login page...")


class LoginView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(page, lang, user_state)
        self.controller.set_view(self)

        # INITIALIZE PAGE COMPONENTS
        self.add_form = AddUserField(self.lang, on_submit_callback=self.controller.handle_add_user)
        self.delete_dialog = DeleteUserDialog(self._page, self.lang, on_confirm_callback=self.controller.handle_delete_confirm)
        self.header = LoginHeader(self.lang)
        self.user_list = UserList(self.lang, on_select_callback=self.controller.login_user, on_delete_callback=self.controller.handle_delete_prompt)

        # INITIALIZE PAGE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.header,
                    self.add_form,
                    self.user_list
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )

        Logger.info("Rendering UI for login page...")

        super().__init__(
            route="/login",
            padding=0,
            bgcolor=Color.WHITE,
            controls=ft.Container(content=self.main_container, alignment=ft.Alignment.CENTER, expand=True),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()
        self.user_list.refresh(self.controller.get_all_users())

    def on_page_resize(self, e=None):
        current_width: int = int(self._page.width or UISettings.MAX_APP_WIDTH)
        current_height: int = int(self._page.height or UISettings.MAX_APP_HEIGHT)

        # Safe value: reference size to properly resize elements
        safe_width: int = min(current_width, UISettings.MAX_APP_WIDTH)
        safe_height: int = min(current_height, UISettings.MAX_APP_HEIGHT)

        self.main_container.width = safe_width * 0.75
        self.main_container.height = safe_height * 0.75

        self.header.resize(safe_width)
        self.add_form.resize(safe_width)
        self.user_list.resize(safe_height)

        try:
            apply_responsive_text(self.main_container, safe_width)
        except Exception as ex:
            Logger.debug(f"Skipped text resizing: {ex}")

        try:
            self.update()
        except RuntimeError as ex:
            Logger.debug(f"Render skipped: {ex}")

        return e


def get_login_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return LoginView(page, lang, user_state)

