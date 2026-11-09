# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Page, Text


class ReturnButton(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], on_click: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static icons
        self.return_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=on_click,
        )

        # CONTAINER COMPONENTS
        self.main_container = ft.Row(
            controls=[
                ft.Container(content=self.return_button, alignment=ft.Alignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        super().__init__(
            controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


class NotSupportedMessageBox(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], message: str) -> None:
        self._page = page
        self.lang = lang
        self.message = message

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.message_text = Text.P(f"{self.lang['fallback.something_went_wrong']}: {self.message}", color=Color.PRIMARY_TEXT)

        # CONTAINER COMPONENTS
        self.message_box: ft.Container = ft.Container(
            content=ft.Column(
                controls=[self.message_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.Border.all(width=1, color=Color.DEFAULT_BORDER),
            padding=30,
        )

        self.main_container = ft.Container(
            content=self.message_box,
            alignment=ft.Alignment.CENTER,
        )

        super().__init__(
            content=self.main_container,
            alignment=ft.Alignment.CENTER,
        )

    def update_message(self, message: str) -> None:
        self.message = message
        self.message_text.value = (
            f"{self.lang['fallback.something_went_wrong']}: {message}"
        )

    def resize(self, size: int) -> None:
        self.width = size
        self.height = size
