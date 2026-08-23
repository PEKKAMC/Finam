# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
from collections.abc import Callable

import flet as ft

from src.utils import Color, Text


class Menu(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self.app_page = page
        self.lang = lang
        self.user_info = user_info

        self.nav_items = [
            self.build_nav_item(ft.Icons.HOME_ROUNDED, self.lang.get("generic.home", "Home"), self.navigate_to("/home"), is_active=True),
            self.build_nav_item(ft.Icons.MENU_BOOK_ROUNDED, self.lang.get("generic.lesson", "Lesson"), self.navigate_to("/lessons"), is_active=False),
            self.build_nav_item(ft.Icons.SAVINGS_ROUNDED, self.lang.get("generic.saving", "Savings"), self.navigate_to("/saving"), is_active=False),
            self.build_nav_item(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, self.lang.get("generic.spending", "Spending"), self.navigate_to("/spending"), is_active=False),
            self.build_nav_item(ft.Icons.AUTO_AWESOME_ROUNDED, self.lang.get("generic.purchase_scanner", "Scanner"), self.navigate_to("/purchase_scanner"), is_active=False),
            self.build_nav_item(ft.Icons.LOGOUT_ROUNDED, self.lang.get("generic.change_user", "Log out"), self.change_user, is_active=False),
        ]

        if os.getenv("ENABLE_EDITOR") == "1":
            self.nav_items.append(
                self.build_nav_item(ft.Icons.EDIT_NOTE_ROUNDED, "editor", self.navigate_to("/lesson-editor"), is_active=False)
            )

        nav_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=self.nav_items,
        )

        self.navigation_bar = ft.Container(
            width=360,
            height=72,
            bgcolor=Color.WHITE,
            border_radius=20,
            padding=ft.Padding(10, 10, 10, 10),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=Color.SHADOW),
            content=nav_row,
        )

        super().__init__(
            content=self.navigation_bar,
            padding=0,
            bgcolor=Color.TRANSPARENT,
            bottom=0,
            left=0,
            right=0,
            width=420,
            height=86,
            alignment=ft.Alignment.CENTER,
        )

    def navigate_to(self, route: str):
        async def handler(e=None):
            await self.app_page.push_route(route)
            return e
        return handler

    async def change_user(self, e=None):
        await self.app_page.push_route("/login")
        self.user_info["username"] = None
        return e

    @staticmethod
    def build_nav_item(icon: ft.IconData, title_text: str, on_click: Callable, is_active: bool):
        active_bg = Color.LIGHT_ACCENT if is_active else Color.TRANSPARENT
        active_text = Color.PRIMARY_TEXT if is_active else Color.SECONDARY_TEXT
        active_icon = Color.PRIMARY if is_active else Color.SECONDARY_TEXT

        return ft.Container(
            width=52,
            height=52,
            border_radius=16,
            ink=True,
            on_click=on_click,
            bgcolor=active_bg,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Icon(icon, size=20, color=active_icon),
                    Text.SMALL(title_text, color=active_text),
                ],
            ),
        )

    def resize(self, page_width: int):
        self.width = max(page_width, 0)
        self.navigation_bar.width = min(max(page_width - 24, 320), 420)