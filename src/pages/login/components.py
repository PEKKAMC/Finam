# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.utils import Color, Text, UISettings


class LoginHeader(ft.Column):
    def __init__(self, lang: dict):
        self.user_icon = ft.Icon(ft.Icons.PEOPLE_ALT, color=Color.DEFAULT_TEXT)
        self.select_user_text = Text.H2(lang["login.select_user"], color=Color.DEFAULT_TEXT)

        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.user_icon,
                self.select_user_text
            ]
        )

    def resize(self, width: int):
        self.user_icon.size = max(60, int(width * 0.12))


class AddUserField(ft.Column):
    def __init__(self, lang: dict, on_submit_callback):
        self.on_submit_callback = on_submit_callback

        self.input_field = ft.TextField(
            label=Text.H4(lang["login.add_user"]),
            color=Color.DEFAULT_TEXT,
            expand=True,
            on_submit=self._handle_submit
        )
        self.error_message = Text.SMALL("", color=Color.ERROR_TEXT)
        self.submit_button = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=Color.WHITE,
            bgcolor=Color.DEFAULT_BUTTON,
            icon_size=self.input_field.height,
            on_click=self._handle_submit
        )

        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            controls=[
                ft.Row(
                    [
                        self.input_field,
                        self.submit_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                self.error_message
            ]
        )

    def _handle_submit(self):
        input_username = self.input_field.value.strip()
        self.on_submit_callback(input_username)

    def show_error(self, message: str):
        self.error_message.value = message
        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def clear(self):
        self.input_field.value = ""
        self.error_message.value = ""
        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def resize(self, width: int):
        self.input_field.width = min(width * 0.8, 350)


class UserList(ft.Container):
    def __init__(self, lang: dict, on_select_callback, on_delete_callback):
        self.lang = lang
        self.on_select = on_select_callback
        self.on_delete = on_delete_callback

        self.list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        super().__init__(
            content=self.list_column,
            border=ft.Border.all(1, Color.DEFAULT_CONTAINER_BACKGROUND),
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=10
        )

    def refresh(self, current_users: list):
        self.list_column.controls.clear()

        if not current_users:
            self.list_column.controls.append(
                Text.P(self.lang["login.no_user"], color=Color.BLAND_TEXT, text_align=ft.TextAlign.CENTER)
            )
        else:
            for username in current_users:
                self.list_column.controls.append(self.create_user_box(username))

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def create_user_box(self, username: str):
        def handle_select(e, name=username):
            self.on_select(name)
            return e

        def handle_delete(e, name=username):
            self.on_delete(name)
            return e

        return ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, color=Color.DEFAULT_TEXT),
                    Text.H2(username, color=Color.DEFAULT_TEXT),
                ]),
                bgcolor=Color.USER_TILE_BACKGROUND,
                padding=10,
                border_radius=UISettings.CARD_BORDER_RADIUS,
                ink=True,
                expand=True,
                on_click=handle_select
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=Color.DELETE_ACTION,
                tooltip=self.lang["login.delete_user_tooltip"],
                on_click=handle_delete
            )
        ])

    def resize(self, height: int):
        self.height = height * 0.45

class DeleteUserDialog:
    def __init__(self, page: ft.Page, lang: dict, on_confirm_callback):
        self._page = page
        self.on_confirm = on_confirm_callback

        self.selected_user: str = ""

        self.dialog = ft.AlertDialog(
            modal=True,
            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
            title=Text.H3(lang["login.confirm_delete_user_title"], color=Color.DEFAULT_TEXT),
            content=Text.P(lang["login.confirm_delete_user_content"], color=Color.DEFAULT_TEXT),
            actions=[
                ft.TextButton(Text.BUTTON(lang["generic.cancel"], color=Color.DEFAULT_TEXT), on_click=self.close),
                ft.TextButton(Text.BUTTON(lang["generic.delete"], color=Color.DELETE_ACTION), on_click=self.confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def show(self, username: str):
        self.selected_user = username
        if self.dialog not in self._page.overlay:
            self._page.overlay.append(self.dialog)
        self.dialog.open = True
        try:
            self._page.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def close(self):
        self.dialog.open = False
        self._page.update()

    def confirm(self):
        if self.selected_user:
            self.on_confirm(self.selected_user)
        self.close()

