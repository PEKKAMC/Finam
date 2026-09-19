# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
from collections.abc import Callable

import flet as ft

from src.utils import Color, Page, Text


class Menu(ft.Container):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.active_icon = self.get_active_icon()

        self.navigation_items = [
            self.build_nav_item(ft.Icons.HOME_ROUNDED, self.lang["generic.home"], self._page.navigate_to("/home"), is_active=self.active_icon == "home"),
            self.build_nav_item(ft.Icons.MENU_BOOK_ROUNDED, self.lang["generic.lesson"], self._page.navigate_to("/lessons"), is_active=self.active_icon == "lesson"),
            self.build_nav_item(ft.Icons.SAVINGS_ROUNDED, self.lang["generic.saving"], self._page.navigate_to("/saving"), is_active=self.active_icon == "saving"),
            self.build_nav_item(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, self.lang["generic.spending"], self._page.navigate_to("/spending"), is_active=self.active_icon == "spending"),
            self.build_nav_item(ft.Icons.AUTO_AWESOME_ROUNDED, self.lang["generic.purchase_scanner"], self._page.navigate_to("/purchase_scanner"), is_active=self.active_icon == "scanner"),
            self.build_nav_item(ft.Icons.PERSON_ROUNDED, self.lang["generic.change_user"], self._page.navigate_to("/user_management"), is_active=self.active_icon == "user_management"),
        ]

        if os.getenv("ENABLE_EDITOR") == "1":
            self.navigation_items.append(
                self.build_nav_item(ft.Icons.EDIT_NOTE_ROUNDED, "editor", self._page.navigate_to("/lesson-editor"), is_active=self.active_icon == "editor")
            )

        self.main_container = ft.Container(
            width=360,
            height=72,
            bgcolor=Color.NAVIGATION_BACKGROUND,
            border_radius=20,
            padding=ft.Padding(10, 10, 10, 10),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=self.navigation_items,
            ),
        )

        super().__init__(
            content=self.main_container,
            padding=0,
            bottom=0,
            height=72,
            alignment=ft.Alignment.CENTER,
        )

    @staticmethod
    def build_nav_item(icon: ft.IconData, title_text: str, on_click: Callable | None, is_active: bool) -> ft.Container:
        active_bg = Color.LIGHT_ACCENT if is_active else Color.TRANSPARENT
        active_text = Color.PRIMARY_TEXT if is_active else Color.SECONDARY_TEXT
        active_icon = Color.PRIMARY if is_active else Color.SECONDARY_TEXT
        change_route = None if is_active else on_click

        return ft.Container(
            width=52,
            height=52,
            border_radius=16,
            ink=True,
            on_click=change_route,
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

    def get_active_icon(self) -> str:
        current_route = self._page.route

        match current_route:
            case "/user_management":
                return "user_management"
            case "/home":
                return "home"
            case "/lessons" | "/lesson-player":
                return "lesson"
            case "/saving":
                return "saving"
            case "/spending":
                return "spending"
            case "/purchase_scanner":
                return "scanner"
            case "/lesson-editor":
                return "editor"
            case _:
                return ""

    def resize(self, width: int) -> None:
        self.main_container.width = width