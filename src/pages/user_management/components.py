# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Text


class ProfileCard(ft.Container):
    def __init__(self, username: str, lang: dict, on_change_user: Callable):
        self.username = username
        self.lang = lang
        self.on_change_user = on_change_user

        user_display = self.username if self.username else ""
        self.user_name_text = Text.H4(user_display, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.active_user_text = Text.MEDIUM(
            self.username if self.username else "Chưa chọn người dùng",
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )

        avatar_box = ft.Stack(
            controls=[
                ft.CircleAvatar(
                    radius=26,
                    bgcolor=Color.LIGHT_ACCENT,
                    content=ft.Icon(ft.Icons.PERSON, color=Color.PRIMARY, size=32)
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, color=Color.SAVINGS_VALUE_TEXT, size=12),
                    bgcolor=Color.PRIMARY,
                    border_radius=10,
                    padding=2,
                    bottom=0,
                    right=0
                )
            ]
        )

        vip_badge = ft.Container(
            content=Text.SMALL("VIP", color=Color.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        )

        user_info = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.user_name_text, vip_badge]
                ),
                Text.SMALL("Tài khoản Cá nhân (Chính)", color=Color.LIGHT_ACCENT)
            ]
        )

        change_user_btn = ft.Container(
            content=ft.Row(
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=Color.WHITE, size=16),
                    Text.SMALL("Đổi", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.WHITE, size=16)
                ]
            ),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=16,
            on_click=lambda e: self.on_change_user(),
            ink=True
        )

        top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[avatar_box, user_info]
                ),
                change_user_btn
            ]
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=16,
            content=ft.Column(spacing=14, controls=[top_row])
        )

    def update_user(self, username: str):
        self.username = username
        self.user_name_text.value = username if username else ""
        self.active_user_text.value = username if username else "Chưa chọn người dùng"


class MenuItem(ft.Container):
    def __init__(
        self,
        icon,
        icon_color: Color,
        icon_bg_color: Color,
        title: str,
        subtitle: str,
        badge_text: str | None = None,
        badge_bg: Color | None = None,
        badge_color: Color | None = None,
        trailing: ft.Control | None = None,
        on_click: Callable | None = None
    ):
        badge_control = None
        if badge_text:
            badge_control = ft.Container(
                content=Text.SMALL(badge_text, color=badge_color or Color.PRIMARY, weight=ft.FontWeight.BOLD),
                bgcolor=badge_bg or Color.LIGHT_ACCENT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            )

        title_row_controls = [Text.MEDIUM(title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)]
        if badge_control:
            title_row_controls.append(badge_control)

        super().__init__(
            padding=ft.Padding.symmetric(vertical=14, horizontal=16),
            on_click=on_click,
            ink=True if on_click else False,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color=icon_color, size=20),
                                bgcolor=icon_bg_color,
                                padding=10,
                                border_radius=14
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=title_row_controls
                                    ),
                                    Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)
                                ]
                            )
                        ]
                    ),
                    trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SUBTITLE_TEXT, size=20)
                ]
            )
        )


class MenuSectionCard(ft.Container):
    def __init__(self, items: list[ft.Control]):
        controls = []
        for i, item in enumerate(items):
            controls.append(item)
            if i < len(items) - 1:
                controls.append(ft.Divider(height=1, color=Color.CARD_DIVIDER, thickness=1))

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=20,
            content=ft.Column(spacing=0, controls=controls)
        )
