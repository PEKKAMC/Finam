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

        # Navigation Bar Controls
        self.nav_items = [
            self.build_nav_item(ft.Icons.HOME_ROUNDED, self.lang["generic.home"], self.navigate_to("/home")),
            self.build_nav_item(ft.Icons.MENU_BOOK_ROUNDED, self.lang["generic.lesson"], self.navigate_to("/lessons")),
            self.build_nav_item(ft.Icons.SAVINGS_ROUNDED, self.lang["generic.saving"], self.navigate_to("/saving")),
            self.build_nav_item(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, self.lang["generic.spending"], self.navigate_to("/spending")),
            self.build_nav_item(ft.Icons.AUTO_AWESOME_ROUNDED, self.lang["generic.purchase_scanner"], self.navigate_to("/purchase_scanner")),
            self.build_nav_item(ft.Icons.LOGOUT_ROUNDED, self.lang["generic.change_user"], self.change_user)
        ]

        if os.getenv("ENABLE_EDITOR") == "1":
            self.nav_items.append(
                self.build_nav_item(ft.Icons.EDIT_NOTE_ROUNDED, "editor", self.navigate_to("/lesson-editor"))
            )

        self.main_container = ft.Container(
            content=ft.Row(
                controls=self.nav_items,
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            ),
            height=75,
            bgcolor=Color.WHITE,
            border=ft.Border.only(top=ft.BorderSide(1, Color.DEFAULT_BORDER)),
            padding=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color=Color.SHADOW)
        )

        super().__init__(
            padding=0,
            bgcolor=Color.MENU_BACKGROUND,
            content=self.main_container,
            bottom=0
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
    def build_nav_item(icon: ft.IconData, title_text: str, on_click: Callable):
        return ft.Container(
            expand=True,
            padding=ft.Padding(4, 6, 4, 6),
            border_radius=10,
            ink=True,
            on_click=on_click,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Icon(
                        icon,
                        color=Color.SUBTITLE_TEXT,
                        size=20
                    ),
                    Text.SMALL(
                        title_text,
                        color=Color.SUBTITLE_TEXT,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ]
            )
        )

    def resize(self, page_width: int):
        self.main_container.width = page_width