# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class SettingsHeader(ft.Container):
    def __init__(self, lang: dict):
        self.lang = lang
        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    Text.H2(self.lang["ui.settings.title"])
                                ]
                            ),
                            Text.P(self.lang["ui.settings.desc"], color=Color.LIGHT_ACCENT)
                        ]
                    )
                ]
            )
        )


class SettingDropdown(ft.Container):
    def __init__(self, options: list[str], active_index: int = 0):
        super().__init__(
            bgcolor=Color.USER_TILE_BACKGROUND,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=8, vertical=0),
            content=ft.Dropdown(
                options=[ft.dropdown.Option(opt) for opt in options],
                value=options[active_index],
                width=130,
                border=ft.InputBorder.NONE,
                bgcolor=Color.CARD_BACKGROUND,
                text_style=ft.TextStyle(size=12, color=Color.PRIMARY_TEXT ,weight=ft.FontWeight.W_600),
                content_padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            )
        )


class SettingRow(ft.Container):
    def __init__(self, icon: ft.IconData, title: str, subtitle: str, control: ft.Control):
        super().__init__(
            padding=ft.Padding.symmetric(vertical=6),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=15,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon, color=Color.PRIMARY_ACTION, size=24),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.H5(title, color=Color.PRIMARY_TEXT),
                                    Text.SMALL(subtitle, color=Color.SECONDARY_TEXT),
                                ]
                            )
                        ]
                    ),
                    control
                ]
            )
        )


class SettingCard(ft.Container):
    def __init__(self, controls: list[ft.Control]):
        super().__init__(
            content=ft.Column(spacing=6, controls=controls),
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            padding=16,
        )