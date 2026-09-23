# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Text, UISettings


class ProfileCard(ft.Container):
    def __init__(self, username: str, lang: dict, on_change_user: Callable):
        self.username = username
        self.lang = lang
        self.on_change_user = on_change_user

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.account_type_text = Text.SMALL(self.lang["ui.personal_account"], color=Color.LIGHT_ACCENT)
        self.change_btn_text = Text.SMALL(self.lang["ui.change"], color=Color.WHITE, weight=ft.FontWeight.BOLD)

        # Static icons
        self.avatar_icon = ft.Icon(ft.Icons.PERSON, color=Color.PRIMARY, size=32)
        self.change_user_icon = ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=Color.WHITE, size=16)
        self.chevron_icon = ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.WHITE, size=16)

        # Dynamic texts
        user_display = self.username if self.username else ""
        self.user_name_text = Text.H4(user_display, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.active_user_text = Text.MEDIUM(
            self.username if self.username else self.lang["ui.no_user_selected"],
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )

        # CONTAINER COMPONENTS
        self.avatar_box = ft.Stack(
            controls=[
                ft.CircleAvatar(
                    radius=26,
                    bgcolor=Color.LIGHT_ACCENT,
                    content=self.avatar_icon
                )
            ]
        )

        self.user_info_column = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.user_name_text]
                ),
                self.account_type_text
            ]
        )

        self.change_user_button = ft.Container(
            content=ft.Row(
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.change_user_icon,
                    self.change_btn_text,
                    self.chevron_icon
                ]
            ),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=16,
            on_click=lambda e: self.on_change_user(),
            ink=True
        )

        self.top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.avatar_box,
                        self.user_info_column
                    ]
                ),
                self.change_user_button
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=14,
                controls=[
                    self.top_row
                ]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            content=self.main_container
        )

    def update_data(self, username: str):
        self.username = username
        self.user_name_text.value = username if username else ""
        self.active_user_text.value = username if username else self.lang["ui.no_user_selected"]
        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class MenuItem(ft.Container):
    def __init__(self, icon, icon_color: Color, icon_bg_color: Color, title: str, subtitle: str, badge_text: str | None = None, badge_bg: Color | None = None, badge_color: Color | None = None, trailing: ft.Control | None = None, on_click: Callable | None = None):
        # TEXT AND ICON COMPONENTS
        self.title_text = Text.MEDIUM(title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.subtitle_text = Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)
        self.main_icon = ft.Icon(icon, color=icon_color, size=20)
        self.trailing_control = trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SUBTITLE_TEXT, size=20)

        # CONTAINER COMPONENTS
        self.badge_control = None
        if badge_text:
            self.badge_control = ft.Container(
                content=Text.SMALL(badge_text, color=badge_color or Color.PRIMARY, weight=ft.FontWeight.BOLD),
                bgcolor=badge_bg or Color.LIGHT_ACCENT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            )

        self.title_row_controls = [self.title_text]
        if self.badge_control:
            self.title_row_controls.append(self.badge_control)

        self.icon_container = ft.Container(
            content=self.main_icon,
            bgcolor=icon_bg_color,
            padding=10,
            border_radius=14
        )

        self.text_column = ft.Column(
            spacing=2,
            expand=True,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.title_row_controls
                ),
                self.subtitle_text
            ]
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        self.icon_container,
                        self.text_column
                    ]
                ),
                self.trailing_control
            ]
        )

        super().__init__(
            padding=ft.Padding.symmetric(vertical=14, horizontal=16),
            on_click=on_click,
            ink=True if on_click else False,
            content=self.main_row
        )


class MenuSectionCard(ft.Container):
    def __init__(self, items: list[ft.Control]):
        self.items = items

        # CONTAINER COMPONENTS
        self.controls = []
        for i, item in enumerate(self.items):
            self.controls.append(item)
            if i < len(self.items) - 1:
                self.controls.append(ft.Divider(height=1, color=Color.CARD_DIVIDER, thickness=1))

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=0,
                controls=self.controls
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            content=self.main_container
        )

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width