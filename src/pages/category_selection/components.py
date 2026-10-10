# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Page, Text, UISettings


class CategoryItem(ft.Container):
    def __init__(self, page: Page, lang: dict, name: str, icon: ft.IconData, on_click: Callable, is_selected: bool = False):
        self._page = page
        self.lang = lang
        self.category_name = name
        self.icon = icon
        self._on_click = on_click
        self.is_selected = is_selected

        self.icon_circle = ft.Container(
            width=60,
            height=60,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            bgcolor="#FFEB3B" if self.is_selected else None,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon=self.icon, color=Color.BLACK if self.is_selected else Color.PRIMARY, size=30)
        )

        self.icon_label = Text.LABEL(value=self.category_name, color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER)

        self.main_container = ft.Container(
            width=75,
            height=75,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=-10,
                controls=[
                    self.icon_circle,
                    self.icon_label
                ],
            ),
            on_click=self._on_click,
            ink=True,
            border_radius=UISettings.CARD_BORDER_RADIUS
        )

        super().__init__(
            content=self.main_container,
            expand=True,
            alignment=ft.Alignment.CENTER
        )

    def update_selection(self, selected: bool):
        self.is_selected = selected
        self.icon_circle.bgcolor = "#FFEB3B" if self.is_selected else None
        self.icon_circle.content.color = Color.BLACK if self.is_selected else Color.PRIMARY
        try:
            if self.icon_circle.page:
                self.icon_circle.update()
        except Exception:
            pass