# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text, UISettings

class TopNavigationBar(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, current_user: str = ""):
        self._page = page
        self.lang = lang
        self.current_user = current_user
        self.logo = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(
                    src="assets/icon.png",
                    height=26,
                    width=26,
                    border_radius=8
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                Text.H3("FINAM", color=Color.PRIMARY_TEXT)
                            ],
                            spacing=5
                        ),
                        Text.H5("Quản lý tài chính & Chi tiêu thông minh", color=Color.SECONDARY_TEXT)
                    ],
                    spacing=0
                )
            ]
        )

        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=self.on_clicking_setting,
            alignment=ft.Alignment.CENTER
        )

        self.main_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.logo,
                    self.settings_button
                ],
                height=UISettings.TOP_NAVIGATION_HEIGHT,
                spacing=10,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.Padding(16, 8, 16, 8),
            border=ft.Border.only(bottom=ft.BorderSide(1, Color.DEFAULT_BORDER))
        )

        super().__init__(
            padding=0,
            bgcolor=Color.NAVIGATION_BACKGROUND,
            content=self.main_container,
            width=UISettings.MAX_APP_WIDTH,
        )

    async def on_clicking_setting(self):
        if self._page:
            await self._page.push_route("/settings")

    def resize(self, width: int) -> None:
        self.main_container.width = width