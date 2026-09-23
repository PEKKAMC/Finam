# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text, UISettings


class SettingsHeader(ft.Container):
    def __init__(self, lang: dict):
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        self.title_text = Text.H2(self.lang["ui.settings.title"])
        self.desc_text = Text.P(self.lang["ui.settings.desc"], color=Color.LIGHT_ACCENT)

        # CONTAINER COMPONENTS
        self.text_column = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.title_text]
                ),
                self.desc_text
            ]
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[self.text_column]
        )

        self.main_container = ft.Container(
            content=self.main_row
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=16,
            content=self.main_container
        )

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class SettingDropdown(ft.Container):
    def __init__(self, options: list[str], active_index: int = 0):
        # DYNAMIC CONTROLS
        self.dropdown_control = ft.Dropdown(
            options=[ft.dropdown.Option(opt) for opt in options],
            value=options[active_index],
            width=130,
            border=ft.InputBorder.NONE,
            bgcolor=Color.CARD_BACKGROUND,
            text_style=ft.TextStyle(size=12, color=Color.PRIMARY_TEXT ,weight=ft.FontWeight.W_600),
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=8),
        )

        self.main_container = ft.Container(
            content=self.dropdown_control
        )

        super().__init__(
            bgcolor=Color.USER_TILE_BACKGROUND,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=8, vertical=0),
            content=self.main_container
        )


class SettingRow(ft.Container):
    def __init__(self, icon: ft.IconData, title: str, subtitle: str, control: ft.Control):
        # TEXT AND ICON COMPONENTS
        self.row_icon = ft.Icon(icon, color=Color.PRIMARY_ACTION, size=24)
        self.title_text = Text.H5(title, color=Color.PRIMARY_TEXT)
        self.subtitle_text = Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)
        self.action_control = control

        # CONTAINER COMPONENTS
        self.text_column = ft.Column(
            spacing=2,
            controls=[
                self.title_text,
                self.subtitle_text
            ]
        )

        self.left_group = ft.Row(
            spacing=15,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.row_icon,
                self.text_column
            ]
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.left_group,
                self.action_control
            ]
        )

        self.main_container = ft.Container(
            content=self.main_row
        )

        super().__init__(
            padding=ft.Padding.symmetric(vertical=6),
            content=self.main_container
        )


class SettingCard(ft.Container):
    def __init__(self, controls: list[ft.Control]):
        self.card_controls = controls

        # CONTAINER COMPONENTS
        self.main_container = ft.Container(
            content=ft.Column(
                spacing=6,
                controls=self.card_controls
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            padding=16,
            content=self.main_container
        )

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width