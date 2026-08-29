# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color


class SettingsButton(ft.Container):
    async def on_clicking_setting(self):
        if self._page:
            await self._page.push_route("/settings")

    def __init__(self, page: ft.Page, lang: dict):
        self._page = page
        self.lang = lang
        self.main_container = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=self.on_clicking_setting
        )
        super().__init__(
            content=self.main_container,
            alignment=ft.Alignment.CENTER
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width
