# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Text


class ReturnButton(ft.Row):
    def __init__(self, page: ft.Page, on_return_click: Callable):
        self._page = page
        self.return_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=on_return_click
        )

        super().__init__(
            controls=[
                ft.Container(
                    content=self.return_button,
                    alignment=ft.Alignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


class NotSupportedMessageBox(ft.Container):
    def __init__(self, page: ft.Page, message: str, lang: dict):
        self._page = page
        self.lang: dict = lang
        self.message: str = message

        self.message_box: ft.Container = ft.Container(
            content=ft.Column(
                controls=[
                    Text.P(f"{self.lang["fallback.something_went_wrong"]}: {self.message}", color=Color.PRIMARY_TEXT)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            border=ft.Border.all(width=1, color=Color.DEFAULT_BORDER),
            padding=30
        )

        super().__init__(
            content=self.message_box,
            alignment=ft.Alignment.CENTER,
        )

    def resize(self, width: int, height: int):
        size: int = int(min(width, height) * 0.7)
        self.width = size
        self.height = size