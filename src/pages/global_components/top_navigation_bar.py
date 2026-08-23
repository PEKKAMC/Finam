# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.pages.global_components.settings_button import SettingsButton
from src.utils import Color, Text, UISettings


class TopNavigationBar(ft.Container):
    def __init__(self, current_user: str):
        self.current_user = current_user
        self.logo = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(
                    src="/icon.png",
                    height=28,
                    width=28,
                    border_radius=8
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                Text.H3("FINAM", color=Color.PRIMARY_TEXT),
                                Text.H4("Free", color=Color.SECONDARY_TEXT),
                            ],
                            spacing=5
                        ),
                        Text.H5("Quản lý tài chính & Chi tiêu thông minh", color=Color.SECONDARY_TEXT)
                    ],
                    spacing=0
                )
            ]
        )

        self.settings_button = SettingsButton()

        self.main_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.logo,
                    self.settings_button
                ],
                height=50,
                spacing=10,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.Padding(16, 8, 16, 8),
            border=ft.Border.only(bottom=ft.BorderSide(1, Color.DEFAULT_BORDER))
        )

        super().__init__(
            padding=0,
            bgcolor=Color.WHITE,
            content=self.main_container,
            top=0,
            left=0,
            right=0,
            width=UISettings.MAX_APP_WIDTH,
            height=72,
        )

    def resize(self, page_width: int):
        self.width = max(0, min(page_width, UISettings.MAX_APP_WIDTH))
        self.main_container.width = self.width
        self.main_container.content.width = max(self.width - 20, 0)