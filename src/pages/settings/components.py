# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text

class SettingsTemporaryMessageBox(ft.Container):
    def __init__(self, page: ft.Page, lang: dict):
        self._page = page
        self.lang = lang

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    Text.P(f"Settings page I guess", color=Color.PRIMARY_TEXT)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            border=ft.Border.all(width=1, color=Color.DEFAULT_BORDER),
            alignment=ft.Alignment.CENTER,
        )

        super().__init__(
            content=self.main_container,
            alignment=ft.Alignment.CENTER,
        )

    def resize(self, size: int):
        self.width = size
        self.height = size