# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar

import flet as ft
import flet_ads as fta

from src.logger import Logger
from src.pages.common.menu.logic import get_active_menu_item
from src.utils import Color, Page, Text


class Menu(ft.Container):
    BANNER_WIDTH = 320
    BANNER_HEIGHT = 50
    BANNER_IDS: ClassVar[dict[ft.PagePlatform, str]] = {
        ft.PagePlatform.ANDROID: "ca-app-pub-6347435898633316~7597886932",
        ft.PagePlatform.IOS: "ca-app-pub-6347435898633316~7597886932",
    }

    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, Any]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.active_icon = self.get_active_icon()
        self.ad_banner = None
        self.ad_container = None
        self.ad_banner_height = 0
        self.reserved_height = 0

        # TEXT AND ICON COMPONENTS
        # NavigationItem owns each navigation label and icon.
        if not page.web and page.platform in self.BANNER_IDS:
            self.ad_banner = fta.BannerAd(
                unit_id=self.BANNER_IDS[page.platform or ft.PagePlatform.ANDROID],
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

        self.navigation_items: list[NavigationItem] = [
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
    def build_nav_item(icon: ft.IconData, title_text: str, on_click: Callable[..., Any] | None, is_active: bool) -> NavigationItem:
        return NavigationItem(icon, title_text, on_click, is_active)

    def get_active_icon(self) -> str:
        return get_active_menu_item(self._page.route)

    def resize(self, width: int, item_size: int, item_height: int, inside_size: int, inside_height: int, banner_height: int, total_height: int, label_size: int, icon_size: int, label_spacing: int, label_visible: bool) -> None:
        self.width = width
        if self.ad_banner is not None:
            self.ad_banner.visible = banner_height > 0
            self.ad_banner_height = banner_height
            self.ad_container.height = self.ad_banner_height
        self.height = total_height
        self.reserved_height = total_height
        self.content_column.width = width
        self.main_container.width = width
        self.main_container.height = item_height
        if self.ad_container is not None:
            self.ad_container.width = width

        for item in self.navigation_items:
            item.width = item_size
            item.height = item_height
            item.resize(
                inside_size,
                inside_height,
                icon_size,
                label_size,
                label_spacing,
                label_visible,
            )


class NavigationItem(ft.Container):
    def __init__(self, icon: ft.IconData, title_text: str, on_click: Callable[..., Any] | None, is_active: bool) -> None:
        active_text_color = Color.NAVIGATION_ACTIVE_TEXT if is_active else Color.SECONDARY_TEXT
        active_icon_color = Color.NAVIGATION_ACTIVE_ICON if is_active else Color.SECONDARY_TEXT
        active_background = Color.NAVIGATION_ACTIVE_BACKGROUND if is_active else Color.TRANSPARENT

        # TEXT AND ICON COMPONENTS
        # Static icons
        self.icon = ft.Icon(icon, size=20, color=active_icon_color)

        # Dynamic texts
        self.label = Text.SMALL(title_text, color=active_text_color)
        self.content_column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[self.icon, self.label],
        )

        super().__init__(
            border_radius=16,
            ink=True,
            on_click=None if is_active else on_click,
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                border_radius=16,
                bgcolor=active_background,
                alignment=ft.Alignment.CENTER,
                content=self.content_column,
            ),
        )

    def resize(self, width: int, height: int, icon_size: int, label_size: int, spacing: int, label_visible: bool) -> None:
        self.content.width = width
        self.content.height = height
        self.content_column.spacing = spacing
        self.icon.size = icon_size
        self.label.size = label_size
        self.label.visible = label_visible