# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft
from src.logger import Logger
from src.utils import Color, Text, UISettings


class LoginHeader(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, on_close: Callable):
        self._page = page
        self.lang = lang
        self.on_close = on_close
        self.main_container = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.PEOPLE_ALT, color="#1A4734", size=22),
                            bgcolor="#DAF1DE",
                            padding=10,
                            border_radius=14
                        ),
                        Text.H3("Quản Lý Hồ Sơ Người Dùng", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=Color.SECONDARY_TEXT,
                    icon_size=20,
                    on_click=on_close
                )
            ]
        )
        super().__init__(content=self.main_container)

    def resize(self, width: int) -> None:
        self.main_container.width = width


class UserList(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, current_user: str, on_select_callback, on_delete_callback):
        self._page = page
        self.lang = lang
        self.current_user = current_user
        self.on_select = on_select_callback
        self.on_delete = on_delete_callback

        self.list_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
        self.main_container = ft.Container(
            content=self.list_column,
            height=240,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        super().__init__(content=self.main_container)

    def refresh(self, current_users: list, current_user: str = ""):
        self.current_user = current_user
        self.list_column.controls.clear()

        if not current_users:
            self.list_column.controls.append(
                Text.P(self.lang["login.no_user"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
            )
        else:
            for username in current_users:
                self.list_column.controls.append(self.create_user_box(username))

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def create_user_box(self, username: str):
        is_active = (username == self.current_user)
        initial = username[0].upper() if username else "U"

        def handle_select(e, name=username):
            self.on_select(name)
            return e

        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            padding=14,
            border=ft.Border.all(2 if is_active else 1, "#1A4734" if is_active else Color.INPUT_BORDER),
            ink=True,
            on_click=handle_select,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.Container(
                                content=Text.MEDIUM(initial, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor="#1A4734",
                                width=40,
                                height=40,
                                border_radius=14,
                                alignment=ft.Alignment.CENTER
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.MEDIUM(username, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                    Text.SMALL("Tạo ngày 2026-01-01 08:00", color=Color.SECONDARY_TEXT)
                                ]
                            )
                        ]
                    ),
                    *(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PERSON_PIN, color="#1A4734", size=20),
                                padding=4
                            )
                        ] if is_active else []
                    )
                ]
            )
        )

    def resize(self, height: int):
        pass


class AddUserField(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, on_submit_callback):
        self._page = page
        self.lang = lang
        self.on_submit_callback = on_submit_callback

        self.input_field = ft.TextField(
            hint_text="Tên người dùng...",
            bgcolor=ft.Colors.SLATE_50 if hasattr(ft.Colors, 'SLATE_50') else "#F8FAFC",
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True,
            expand=True,
            on_submit=self._handle_submit
        )
        self.error_message = Text.SMALL("", color=Color.ERROR_TEXT)
        self.submit_button = ft.Button(
            content=ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.ADD, color="#DAF1DE", size=16),
                    Text.MEDIUM("Tạo", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ],
                tight=True
            ),
            bgcolor="#1A4734",
            on_click=self._handle_submit,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=16
            )
        )
        self.main_container = ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        self.input_field,
                        self.submit_button
                    ]
                ),
                self.error_message
            ]
        )

        super().__init__(content=self.main_container)

    def _handle_submit(self, e=None):
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
        pass


class DeleteUserDialog:
    def __init__(self, page: ft.Page, lang: dict, on_confirm_callback):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm_callback
        self.selected_user: str = ""
        self.main_container = ft.AlertDialog(
            modal=True,
            bgcolor=Color.WHITE,
            title=Text.H3(self.lang["login.confirm_delete_user_title"], color=Color.PRIMARY_TEXT),
            content=Text.P(self.lang["login.confirm_delete_user_content"], color=Color.SECONDARY_TEXT),
            actions=[
                ft.TextButton(Text.BUTTON("Hủy", color=Color.SECONDARY_TEXT), on_click=lambda e: self.close()),
                ft.TextButton(Text.BUTTON("Xóa", color=ft.Colors.RED_600), on_click=lambda e: self.confirm()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.dialog = self.main_container

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
        if self._page:
            self._page.update()

    def confirm(self):
        if self.selected_user and self.on_confirm:
            self.on_confirm(self.selected_user)
        self.close()

    def resize(self, width: int) -> None:
        self.main_container.width = width