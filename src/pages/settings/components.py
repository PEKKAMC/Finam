# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color


class SettingsHeader(ft.Container):
    def __init__(self, on_close: Callable | None):
        super().__init__(
            padding=ft.Padding.only(bottom=5, top=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        spacing=15,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                padding=12,
                                bgcolor=Color.LIGHT_ACCENT,
                                border_radius=12,
                                content=ft.Icon(
                                    ft.Icons.SETTINGS_OUTLINED,
                                    color=Color.PRIMARY_ACTION,
                                    size=26
                                )
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Cài đặt hệ thống", size=22, weight=ft.FontWeight.W_700, color=Color.PRIMARY_TEXT),
                                    ft.Text("Tùy chỉnh ngôn ngữ, bảo mật & thông báo", size=14, color=Color.SECONDARY_TEXT),
                                ]
                            )
                        ]
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CLOSE, size=20, color=Color.PRIMARY_TEXT),
                        bgcolor=Color.USER_TILE_BACKGROUND,
                        padding=8,
                        border_radius=20,
                        on_click=on_close
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
                color=Color.PRIMARY_TEXT,
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
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
                                    ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=Color.PRIMARY_TEXT),
                                    ft.Text(subtitle, size=14, color=Color.SECONDARY_TEXT),
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