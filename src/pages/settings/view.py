# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar
from src.pages.settings.components import SettingsTemporaryMessageBox
from src.utils import Color, UISettings

Logger.info("Initializing Settings page...")


class SettingsView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.top_navigation_bar = TopNavigationBar(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info["username"]
        )

        # Temporary message box
        self.text_box = SettingsTemporaryMessageBox(
            page=self._page,
            lang=self.lang
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
                                self.text_box
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(top=UISettings.TOP_NAVIGATION_HEIGHT, bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/settings",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def get_safe_page_size(self) -> tuple[int, int]: # -> (width, height)
        # Get page width and height if available, return fallback values otherwise
        current_width: float = self._page.width or UISettings.MAX_APP_WIDTH
        current_height: float = self._page.height or UISettings.MAX_APP_HEIGHT

        # Make sure width and height don't exceed max values
        safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
        safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)

        return safe_width, safe_height

    def on_page_resize(self, e=None) -> None:
        page_width, page_height = self.get_safe_page_size()

        self.main_container.width = page_width

        self.menu.resize(
            width=page_width
        )

        self.top_navigation_bar.resize(
            width=page_width
        )

        self.text_box.resize(
            size=int(min(page_width, page_height) * 0.7)
        )

        return e

def get_settings_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SettingsView(page, lang, user_info)
