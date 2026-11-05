# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
from collections.abc import Callable

import flet as ft
import flet_ads as fta

from src.logger import Logger
from src.utils import Color, Page, Text


class Menu(ft.Container):
    BANNER_WIDTH = 320
    BANNER_HEIGHT = 50
    TEST_BANNER_IDS = {
        ft.PagePlatform.ANDROID: "ca-app-pub-3940256099942544/9214589741",
        ft.PagePlatform.IOS: "ca-app-pub-3940256099942544/2435281174",
    }

    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.active_icon = self.get_active_icon()
        self.ad_banner = None
        self.ad_container = None
        self.ad_banner_height = 0
        self.reserved_height = 0

        if not page.web and page.platform in self.TEST_BANNER_IDS:
            self.ad_banner = fta.BannerAd(
                unit_id=self.TEST_BANNER_IDS[page.platform or ft.PagePlatform.ANDROID],
                width=self.BANNER_WIDTH,
                height=self.BANNER_HEIGHT,
                request=fta.AdRequest(non_personalized_ads=True),
                on_load=lambda e: Logger.info("AdMob banner loaded"),
                on_error=lambda e: Logger.warning(
                    f"AdMob banner failed to load: {e.data}"
                ),
            )
            self.ad_banner_height = self.BANNER_HEIGHT
            self.ad_container = ft.Container(
                content=self.ad_banner,
                height=self.ad_banner_height,
                alignment=ft.Alignment.CENTER,
                bgcolor=Color.PAGE_BACKGROUND,
            )

        self.navigation_items = [
            self.build_nav_item(ft.Icons.HOME_ROUNDED, self.lang["generic.home"], self._page.navigate_to("/home"), is_active=self.active_icon == "home"),
            self.build_nav_item(ft.Icons.MENU_BOOK_ROUNDED, self.lang["generic.lesson"], self._page.navigate_to("/lessons"), is_active=self.active_icon == "lesson"),
            self.build_nav_item(ft.Icons.SAVINGS_ROUNDED, self.lang["generic.saving"], self._page.navigate_to("/savings"), is_active=self.active_icon == "saving"),
            self.build_nav_item(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, self.lang["generic.spending"], self._page.navigate_to("/spending"), is_active=self.active_icon == "spending"),
            self.build_nav_item(ft.Icons.AUTO_AWESOME_ROUNDED, self.lang["generic.purchase_scanner"], self._page.navigate_to("/purchase_scanner"), is_active=self.active_icon == "scanner"),
            self.build_nav_item(ft.Icons.PERSON_ROUNDED, self.lang["generic.change_user"], self._page.navigate_to("/user_management"), is_active=self.active_icon == "user_management"),
        ]

        if os.getenv("ENABLE_EDITOR") == "1":
            self.navigation_items.append(
                self.build_nav_item(ft.Icons.EDIT_NOTE_ROUNDED, "editor", self._page.navigate_to("/lesson-editor"), is_active=self.active_icon == "editor")
            )

        self.items_count = len(self.navigation_items)

        self.main_container = ft.Container(
            bgcolor=Color.NAVIGATION_BACKGROUND,
            border_radius=20,
            padding=0,
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=self.navigation_items,
            ),
        )

        menu_controls = []
        if self.ad_container is not None:
            menu_controls.append(self.ad_container)
        menu_controls.append(self.main_container)
        self.content_column = ft.Column(
            spacing=0,
            controls=menu_controls,
        )

        super().__init__(
            content=self.content_column,
            padding=0,
            bottom=0,
            left=0,
            right=0,
            alignment=ft.Alignment.CENTER,
        )

    @staticmethod
    def build_nav_item(icon: ft.IconData, title_text: str, on_click: Callable | None, is_active: bool) -> ft.Container:
        active_bg = Color.NAVIGATION_ACTIVE_BACKGROUND if is_active else Color.TRANSPARENT
        active_text = Color.NAVIGATION_ACTIVE_TEXT if is_active else Color.SECONDARY_TEXT
        active_icon = Color.NAVIGATION_ACTIVE_ICON if is_active else Color.SECONDARY_TEXT
        change_route = None if is_active else on_click

        return ft.Container(
            border_radius=16,
            ink=True,
            on_click=change_route,
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                border_radius=16,
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
            case "/savings":
                return "saving"
            case "/spending":
                return "spending"
            case "/purchase_scanner":
                return "scanner"
            case "/lesson-editor":
                return "editor"
            case _:
                return ""

    def resize(self, width: int, item_size: int, inside_size: int) -> None:
        self.width = width
        if self.ad_banner is not None:
            banner_fits = width >= self.BANNER_WIDTH
            self.ad_banner.visible = banner_fits
            self.ad_banner_height = self.BANNER_HEIGHT if banner_fits else 0
            self.ad_container.height = self.ad_banner_height
        self.height = item_size + self.ad_banner_height
        self.reserved_height = self.height
        self.content_column.width = width
        self.main_container.width = width
        self.main_container.height = item_size
        if self.ad_container is not None:
            self.ad_container.width = width

        for item in self.navigation_items:
            item.width = item_size
            item.height = item_size
            item.content.width = inside_size
            item.content.height = inside_size