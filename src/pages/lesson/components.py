# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Text

class MilestoneCard(ft.Container):
    def __init__(self, lang: dict, user_statistics: dict):
        super().__init__(
            expand=2,
            bgcolor="#287b35",
            border_radius=15,
            height=200,
            padding=20,
            content=ft.Column(
                spacing=15,
                controls=[
                    Text.H2(lang["lessons.previous_lesson_head"], color=ft.Colors.WHITE),
                    Text.P(lang["lessons.previous_lesson"], color=ft.Colors.WHITE_70),
                    ft.Container(height=10),
                    ft.Column(
                        spacing=5,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    Text.LABEL(lang["lessons.overall_completion"], color=ft.Colors.BLACK_87),
                                    ft.Row(
                                        controls=[
                                            Text.LABEL(f"{user_statistics['completion_percentage']}%", color=ft.Colors.WHITE),
                                            ft.Container(width=20),
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    )
                                ]
                            ),
                            ft.ProgressBar(
                                value=user_statistics["completion_decimal"],
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.WHITE_30,
                                height=6
                            )
                        ]
                    )
                ]
            )
        )

class StatisticsCard(ft.Container):
    def __init__(self, lang: dict, user_statistics: dict):
        super().__init__(
            expand=1,
            bgcolor="#E8F0E6",
            border_radius=15,
            height=200,
            padding=15,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.TIMER, color=ft.Colors.BLUE_800, size=20),
                                bgcolor="#D1E4FA", padding=10, border_radius=10
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    Text.SMALL(lang["lessons.learning_time"], color=ft.Colors.GREY_600),
                                    Text.H3(f"{user_statistics['learning_hours']} {lang['generic.hours']}", color=ft.Colors.BLUE_GREY_900)
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.VERIFIED, color=ft.Colors.GREEN_800, size=20),
                                bgcolor="#CDE5D0",
                                padding=10,
                                border_radius=10
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    Text.SMALL(lang["lessons.certificates"], color=ft.Colors.GREY_600),
                                    Text.H3(str(user_statistics["certificates_earned"]), color=ft.Colors.BLUE_GREY_900)
                                ]
                            )
                        ]
                    )
                ]
            )
        )

class CategoryTabs(ft.Row):
    def __init__(self, categories: list):
        super().__init__(spacing=10)
        self.controls = [
            ft.Container(
                content=Text.P(
                    category,
                    color=ft.Colors.WHITE if category == categories[0] else ft.Colors.BLUE_GREY_600,
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=ft.Colors.GREEN_800 if category == categories[0] else ft.Colors.GREY_200,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                border_radius=20,
            ) for category in categories
        ]

class LessonItemCard(ft.Container):
    def __init__(self, page: ft.Page, title: str, subtitle: str, cover_image: str, is_completed: bool, route: str):
        text_content = ft.Container(
            padding=ft.Padding.only(left=20, top=20, bottom=20, right=270),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text.H3(
                                title,
                                color=ft.Colors.GREY_700 if is_completed else ft.Colors.BLACK_87,
                                expand=True
                            ),
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_500, visible=is_completed)
                        ]
                    ),
                    Text.P(subtitle, color=ft.Colors.GREY_800),
                ]
            )
        )

        card_stack = ft.Stack()

        if cover_image:
            cover_image = cover_image.strip()
            image_layer = ft.Container(
                right=0,
                top=0,
                bottom=0,
                width=250,
                content=ft.ShaderMask(
                    content=ft.Image(
                        src=cover_image,
                        fit=ft.BoxFit.COVER,
                    ),
                    blend_mode=ft.BlendMode.DST_IN,
                    shader=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[ft.Colors.TRANSPARENT, ft.Colors.BLACK],
                        stops=[0.0, 0.6]
                    )
                )
            )
            card_stack.controls.append(image_layer)

        card_stack.controls.append(text_content)

        super().__init__(
            width=500,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.GREY_500 if is_completed else ft.Colors.GREY_400),
            ink=True,
            on_click=lambda event: page.go(route),
            content=card_stack,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=0
        )