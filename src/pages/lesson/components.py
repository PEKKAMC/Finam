# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class LessonItemCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, title: str, subtitle: str, cover_image: str, is_completed: bool, route: str, duration: int = 15):
        self._page = page
        self.lang = lang
        self.title = title
        self.subtitle = subtitle
        self.cover_image = cover_image
        self.is_completed = is_completed
        self.route = route
        self.duration = duration

        self.top_badges = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    content=Text.SMALL(f"{self.duration} phút", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
                    padding=ft.Padding(10, 4, 10, 4),
                    border_radius=12,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, Color.PRIMARY))
                ),
                *(
                    [
                        ft.Container(
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.WHITE, size=14),
                                    Text.SMALL("Đã học", color=Color.WHITE, weight=ft.FontWeight.BOLD)
                                ],
                                tight=True
                            ),
                            bgcolor=ft.Colors.EMERALD_600 if hasattr(ft.Colors, 'EMERALD_600') else "#059669",
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12
                        )
                    ] if self.is_completed else []
                )
            ]
        )

        self.cover_stack = ft.Stack(
            controls=[
                ft.Image(
                    src=self.cover_image.strip() if self.cover_image else "",
                    fit=ft.BoxFit.COVER,
                    width=float("inf"),
                    height=176
                ),
                ft.Container(
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_CENTER,
                        end=ft.Alignment.BOTTOM_CENTER,
                        colors=["rgba(2, 6, 23, 0.2)", "rgba(2, 6, 23, 0.9)"]
                    ),
                    padding=12,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.top_badges,
                            Text.H4(self.title, color=Color.WHITE, weight=ft.FontWeight.BOLD)
                        ]
                    )
                )
            ]
        )

        self.cover_container = ft.Container(
            height=176,
            bgcolor=Color.DARK_SURFACE,
            content=self.cover_stack,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        self.content_panel = ft.Container(
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[
                    Text.SMALL(self.subtitle, color=Color.SECONDARY_TEXT),
                    ft.Divider(height=1, color=Color.INPUT_BORDER),
                    ft.Button(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=Color.LIGHT_ACCENT, size=18),
                                Text.MEDIUM("Ôn Lại Bài Học" if self.is_completed else "Bắt Đầu Học", color=Color.WHITE, weight=ft.FontWeight.BOLD)
                            ],
                            tight=True
                        ),
                        bgcolor=Color.PRIMARY,
                        on_click=lambda e: self._page.go(self.route) if self._page else None,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=16),
                            padding=12
                        )
                    )
                ]
            )
        )
        self.main_container = ft.Column(
            spacing=0,
            controls=[self.cover_container, self.content_panel]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            ink=True,
            on_click=lambda e: self._page.go(self.route),
            content=self.main_container,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=0,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW)
        )

    def resize(self, width: int) -> None:
        self.main_container.width = max(width, 0)