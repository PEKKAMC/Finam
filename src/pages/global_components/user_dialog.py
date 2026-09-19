# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Dialog, Text

class UserManagementCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, user_list, add_form, on_close_callback: Callable):
        self._page = page
        self.lang = lang
        self._close_dialog = on_close_callback

        self.main_container = ft.Column(
            height=375,
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=Color.SECONDARY_TEXT,
                            tooltip=self.lang["generic.close"],
                            on_click=self._close_dialog
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.PEOPLE_ALT, color=Color.PRIMARY, size=22),
                                    bgcolor=Color.LIGHT_ACCENT,
                                    padding=10,
                                    border_radius=14
                                ),
                                Text.H5(self.lang["user_management.header_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ]
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        Text.SMALL(self.lang["user_management.select_account"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        user_list
                    ]
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        Text.SMALL(self.lang["user_management.add_new_user"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        add_form
                    ]
                )
            ]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=0,
            content=self.main_container
        )

    def resize(self, width: int):
        self.main_container.width = width

class UserManagementDialog(Dialog):
    def __init__(self, page: ft.Page, lang: dict, user_list: UserList, add_form, on_close_callback: Callable):
        self.card = UserManagementCard(
            page=page,
            lang=lang,
            user_list=user_list,
            add_form=add_form,
            on_close_callback=on_close_callback
        )
        super().__init__(dialog_content=self.card, color=Color.WHITE)


class UserList(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, current_user: str, on_select_callback, on_delete_callback):
        self._page = page
        self.lang = lang
        self.current_user = current_user
        self.on_select = on_select_callback
        self.on_delete = on_delete_callback

        self.list_column = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            height=160
        )
        self.main_container = ft.Container(
            content=self.list_column,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        super().__init__(content=self.main_container)

    def refresh(self, current_users: list, current_user: str = ""):
        self.current_user = current_user
        self.list_column.controls.clear()

        if not current_users:
            self.list_column.controls.append(
                Text.P(self.lang["user_management.no_user"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
            )
        else:
            for username in current_users:
                self.list_column.controls.append(self.create_user_box(username))

    def create_user_box(self, username: str):
        is_active = (username == self.current_user)
        initial = username[0].upper() if username else ""
        created_prefix = self.lang["user_management.created_date"]

        def handle_select(e, name=username):
            self.on_select(name)
            return e

        return ft.Container(
            bgcolor=Color.WHITE,
            border_radius=20,
            padding=14,
            border=ft.Border.all(2 if is_active else 1, Color.PRIMARY if is_active else Color.INPUT_BORDER),
            ink=True,
            on_click=handle_select,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=Text.MEDIUM(initial, color=Color.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=Color.PRIMARY,
                                width=40,
                                height=40,
                                border_radius=14,
                                alignment=ft.Alignment.CENTER
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.MEDIUM(username, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                    Text.SMALL(f"{created_prefix} 2026-01-01 08:00", color=Color.SECONDARY_TEXT)
                                ]
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            *(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.PERSON_PIN, color=Color.PRIMARY, size=20),
                                        padding=4
                                    )
                                ] if is_active else []
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=Color.DELETE_ACTION,
                                icon_size=18,
                                on_click=lambda e, u=username: self.on_delete(u),
                                tooltip="Xóa người dùng"
                            )
                        ]
                    )
                ]
            )
        )

    def resize(self, height: int):
        pass