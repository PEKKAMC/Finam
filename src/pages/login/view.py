# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.utils import Color, Text
from src.pages.login.logic import LogicController
from src.pages.login.components import LoginHeader, AddUserField, UserList, DeleteUserDialog

Logger.info("Initializing Login page...")


class LoginView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(page, lang, user_info)
        self.controller.set_view(self)

        # INITIALIZE PAGE COMPONENTS
        self.add_form = AddUserField(self.lang, on_submit_callback=self.controller.handle_add_user)
        self.delete_dialog = DeleteUserDialog(self._page, self.lang, on_confirm_callback=self.controller.handle_delete_confirm)
        self.header = LoginHeader(self.lang, on_close=lambda e: self._page.go("/home") if self.user_info.get("username") else None)
        self.user_list = UserList(self.lang, self.user_info.get("username", ""), on_select_callback=self.controller.login_user, on_delete_callback=self.controller.handle_delete_prompt)

        # Modal Card Container matching reference layout
        modal_card = ft.Container(
            width=520,
            bgcolor=Color.WHITE,
            border_radius=32,
            padding=24,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=24, color=Color.SHADOW),
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Column(
                spacing=20,
                controls=[
                    self.header,
                    ft.Divider(height=1, color=Color.INPUT_BORDER),
                    ft.Column(
                        spacing=10,
                        controls=[
                            Text.SMALL("CHỌN TÀI KHOẢN ĐANG LÀM VIỆC", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                            self.user_list
                        ]
                    ),
                    ft.Divider(height=1, color=Color.INPUT_BORDER),
                    ft.Column(
                        spacing=10,
                        controls=[
                            Text.SMALL("THÊM NGƯỜI DÙNG MỚI", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                            self.add_form
                        ]
                    ),
                    ft.Divider(height=1, color=Color.INPUT_BORDER),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            Text.SMALL("Khôi phục dữ liệu mẫu ban đầu", color=Color.SECONDARY_TEXT),
                            ft.TextButton(
                                content=ft.Row(
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.REFRESH, color=ft.Colors.RED_600, size=14),
                                        Text.SMALL("Khôi phục mẫu", color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD)
                                    ],
                                    tight=True
                                ),
                                on_click=lambda e: None
                            )
                        ]
                    )
                ]
            )
        )

        self.main_container = ft.Container(
            content=modal_card,
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=20
        )

        Logger.info("Rendering UI for login page...")

        super().__init__(
            route="/login",
            padding=0,
            bgcolor="#FAFAF8",
            controls=[self.main_container],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()
        self.user_list.refresh(self.controller.get_all_users(), self.user_info.get("username", ""))

    def on_page_resize(self, e=None):
        try:
            self.update()
        except RuntimeError as ex:
            Logger.debug(f"Render skipped: {ex}")
        return e


def get_login_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return LoginView(page, lang, user_info)