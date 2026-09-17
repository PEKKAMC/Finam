# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.utils import Color, get_safe_page_size, Text, UISettings
from src.pages.global_components import Menu
from src.pages.user_management.logic import LogicController
from src.pages.user_management.components import UserManagementDialog, AddUserField, UserList, DeleteUserDialog

Logger.info("Initializing User Management page...")


class DialogManager:
    def __init__(self, page: ft.Page, lang: dict, controller: LogicController, refresh_callback):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.refresh_view = refresh_callback

        self.delete_dialog = DeleteUserDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self.handle_delete_confirm
        )

    def show_delete_prompt(self, username: str):
        self.delete_dialog.show(username)

    def handle_delete_confirm(self, username: str):
        self.controller.delete_user(username)
        self.refresh_view()


class UserManagementView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info)

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(self._page, self.lang, self.controller, self.refresh_view)

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.add_form = AddUserField(page=self._page, lang=self.lang, on_submit_callback=self.handle_add_user)

        self.user_list = UserList(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info.get("username", ""),
            on_select_callback=self.handle_change_user,
            on_delete_callback=self.dialogs.show_delete_prompt
        )

        # INITIALIZE USER MANAGEMENT DIALOG
        self.user_dialog = UserManagementDialog(
            page=self._page,
            lang=self.lang,
            user_list=self.user_list,
            add_form=self.add_form,
            on_close_callback=self._close_user_management_dialog
        )

        # ---------------------------------------------------------
        # NEW LAYOUT: LOGIN ROW (Opens User Dialog)
        # ---------------------------------------------------------
        self.login_row = ft.Container(
            padding=ft.Padding.only(top=40, bottom=20, left=20, right=20),
            on_click=lambda e: self.user_dialog.show(self._page),
            ink=True,
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.CircleAvatar(
                        radius=35,
                        bgcolor="#4A4A4A",
                        content=ft.Icon(ft.Icons.PERSON, color=Color.WHITE, size=45)
                    ),
                    ft.Column(
                        spacing=4,
                        controls=[
                            Text.H3(self.lang["user_management.select_user"], color=Color.DEFAULT_TEXT),
                        ]
                    )
                ]
            )
        )

        def create_menu_item(icon, icon_color, text, on_click=None):
            return ft.Container(
                padding=ft.Padding.symmetric(vertical=16, horizontal=20),
                border_radius=UISettings.CARD_BORDER_RADIUS,
                on_click=on_click,
                ink=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=15,
                            controls=[
                                ft.Icon(icon, color=icon_color, size=22),
                                Text.H4(text, color=Color.DEFAULT_TEXT)
                            ]
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#555555", size=24)
                    ]
                )
            )

        self.menu_items = ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            content=ft.Column(
                spacing=0,
                controls=[
                    create_menu_item(ft.Icons.WORKSPACE_PREMIUM, "#FFC107", "Thành viên Premium"),
                    ft.Divider(height=1, color="#2C2C2C", thickness=1),
                    create_menu_item(ft.Icons.THUMB_UP_OUTLINED, "#FFC107", "Giới thiệu cho bạn bè"),
                    ft.Divider(height=1, color="#2C2C2C", thickness=1),
                    create_menu_item(ft.Icons.AD_UNITS, "#FFC107", "Tắt quảng cáo"),
                    ft.Divider(height=1, color="#2C2C2C", thickness=1),
                    create_menu_item(ft.Icons.SETTINGS_OUTLINED, "#FFC107", "Cài đặt", on_click=lambda e: self._page.go("/settings")),
                    ft.Divider(height=1, color="#2C2C2C", thickness=1),
                    create_menu_item(ft.Icons.APPS, "#FFC107", "Ứng dụng của chúng tôi"),
                ]
            )
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=20,
                            expand=True,
                            controls=[
                                self.login_row,
                                self.menu_items
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/home",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

        # INITIAL DATA LOAD
        self.refresh_view()

    def _close_user_management_dialog(self):
        self.user_dialog.close_most_recent_dialog(self._page)

    def handle_add_user(self, input_username: str):
        if not input_username:
            return
        success, error_msg = self.controller.add_user(input_username)
        if success:
            self.add_form.clear()
            self.refresh_view()
        else:
            self.add_form.show_error(self.lang.get(error_msg, error_msg))

    def handle_change_user(self, username: str):
        self.controller.change_user(username)
        self._page.go("/home")

    def refresh_view(self):
        self.user_list.refresh(self.controller.get_all_users(), self.user_info.get("username", ""))
        try:
            self._page.update()
        except RuntimeError:
            pass

    def _on_page_resize(self, e = None) -> ft.PageResizeEvent | None:
        page_width, page_height = get_safe_page_size(
            page=self._page
        )

        self.main_container.width = page_width
        self.main_container.height = page_height

        self.menu.resize(
            width=page_width
        )

        return e


def get_user_management_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return UserManagementView(page, lang, user_info)