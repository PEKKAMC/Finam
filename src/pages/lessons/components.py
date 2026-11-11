# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Any

import flet as ft

from src.utils import Color, Page, Text


class LessonItemCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], title: str, subtitle: str, cover_image: str, is_completed: bool, route: str, duration: int = 15) -> None:
        self._page = page
        self.lang = lang
        self.title = title
        self.subtitle = subtitle
        self.cover_image = cover_image
        self.is_completed = is_completed
        self.route = route
        self.duration = duration

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.completed_badge_text = Text.SMALL(self.lang["lessons.completed_badge"], color=Color.WHITE, weight=ft.FontWeight.BOLD)

        # Dynamic texts
        self.action_button_label = Text.MEDIUM(
            self.lang["lessons.review_lesson"]
            if self.is_completed
            else self.lang["lessons.start_lesson"],
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )
        self.title_text = Text.H4(self.title, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.subtitle_text = Text.SMALL(self.subtitle, color=Color.SECONDARY_TEXT)

        # Static icons
        self.completed_badge_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.WHITE, size=14)
        self.action_button_icon = ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED,color=Color.LIGHT_ACCENT, size=18)

        # CONTAINER COMPONENTS
        self.top_badges = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # ft.Container(
                #    content=Text.SMALL(f"{self.duration} {self.lang["generic.minute"]}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                #    bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
                #    padding=ft.Padding(10, 4, 10, 4),
                #    border_radius=12,
                #    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, Color.PRIMARY))
                # ),
                *(
                    [
                        ft.Container(
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    self.completed_badge_icon,
                                    self.completed_badge_text
                                ],
                                tight=True
                            ),
                            bgcolor=Color.SUCCESS_BACKGROUND,
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12
                        )
                    ]
                    if self.is_completed
                    else []
                )
            ]
        )

        self.cover_stack = ft.Stack(
            controls=[
                ft.Image(
                    src=self.cover_image.strip() if self.cover_image else "",
                    fit=ft.BoxFit.COVER,
                    width=float("inf")
                ),
                ft.Container(
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_CENTER,
                        end=ft.Alignment.BOTTOM_CENTER,
                        colors=[
                            ft.Colors.with_opacity(0.2, "#020617"),
                            ft.Colors.with_opacity(0.9, "#020617")
                        ]
                    ),
                    padding=12,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.top_badges,
                            # Dynamic texts
                            self.title_text
                        ]
                    )
                )
            ]
        )

        self.cover_container = ft.Container(
            bgcolor=Color.DARK_SURFACE,
            content=self.cover_stack,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        self.content_panel = ft.Container(
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[
                    self.subtitle_text,
                    ft.Divider(height=1, color=Color.INPUT_BORDER),
                    ft.Button(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                self.action_button_icon,
                                self.action_button_label
                            ],
                            tight=True
                        ),
                        bgcolor=Color.PRIMARY,
                        on_click=self._page.navigate_to(self.route),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=16), padding=12
                        )
                    )
                ]
            )
        )

        self.main_container = ft.Column(
            spacing=0,
            controls=[
                self.cover_container,
                self.content_panel
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            # ink=True,
            # on_click=self._page.navigate_to(self.route),
            content=self.main_container,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=0,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW)
        )

    def resize(self, width: int, cover_height: int) -> None:
        self.width = width
        self.main_container.width = width
        self.cover_container.width = width
        self.cover_container.height = cover_height
        self.cover_stack.width = width
        self.content_panel.width = width
        for control in self.cover_stack.controls:
            if isinstance(control, ft.Image):
                control.width = width
                control.height = cover_height


class LessonSummaryBanner(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], total_lessons: int, completed_lessons: int, total_minutes: int, completion_pct: int) -> None:
        self._page = page
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.academy_title_text = Text.SMALL(self.lang["lessons.academy_title"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.banner_title_text = Text.H2(self.lang["lessons.banner_title"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.banner_description_text = Text.SMALL(self.lang["lessons.banner_description"], color=Color.LIGHT_ACCENT)
        self.completed_lessons_label = Text.SMALL(self.lang["lessons.completed_count"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.accumulated_time_label = Text.SMALL(self.lang["lessons.accumulated_time"], color=Color.SAVINGS_LABEL_TEXT, weight=ft.FontWeight.BOLD)

        # Dynamic texts
        self.completed_lessons_count = Text.H3(f"{completed_lessons}/{total_lessons}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.total_minutes_text = Text.H3(f"{total_minutes} {self.lang['generic.minute']}", color=Color.SAVINGS_VALUE_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.summary_banner_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Container(
                            content=self.academy_title_text,
                            bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
                            padding=ft.Padding(12, 4, 12, 4),
                            border_radius=16,
                            border=ft.Border.all(
                                1, ft.Colors.with_opacity(0.3, Color.PRIMARY)
                            )
                        ),
                        self.banner_title_text,
                        self.banner_description_text
                    ]
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.1, Color.WHITE),
                            border=ft.Border.all(
                                1, ft.Colors.with_opacity(0.2, Color.WHITE)
                            ),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    self.completed_lessons_count,
                                    self.completed_lessons_label
                                ]
                            )
                        ),
                        ft.Container(
                            padding=12,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.1, Color.WHITE),
                            border=ft.Border.all(
                                1, ft.Colors.with_opacity(0.2, Color.WHITE)
                            ),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    self.total_minutes_text,
                                    self.accumulated_time_label
                                ]
                            )
                        )
                    ]
                )
            ]
        )

        self.progress_bar = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
            border_radius=12,
            padding=2,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, Color.PRIMARY)),
            content=ft.ProgressBar(
                value=completion_pct / 100.0 if total_lessons > 0 else 0.0,
                color=Color.LIGHT_ACCENT,
                bgcolor=Color.TRANSPARENT,
                height=8
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=24,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=ft.Column(
                spacing=20, controls=[self.summary_banner_row, self.progress_bar]
            )
        )

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.summary_banner_row.width = content_width
        self.progress_bar.width = content_width


class LessonGrid(ft.Stack):
    def __init__(self, page: Page, lang: dict[str, str], lessons: list[dict[str, Any]]) -> None:
        self._page = page
        self.lang = lang

        # CONTAINER COMPONENTS
        self.lesson_cards = [
            LessonItemCard(
                page=self._page,
                lang=self.lang,
                title=lesson["title"],
                subtitle=lesson["subtitle"],
                cover_image=lesson["cover_image"],
                is_completed=lesson["is_completed"],
                route=lesson["route"]
            )
            for lesson in lessons
        ]

        self.responsive_row = ft.ResponsiveRow(
            spacing=20,
            run_spacing=20,
            controls=[
                ft.Container(
                    content=card,
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12}
                )
                for card in self.lesson_cards
            ]
        )

        super().__init__(
            controls=[
                self.responsive_row,
                ft.Container(
                    left=0,
                    top=0,
                    right=0,
                    bottom=0,
                    blur=ft.Blur(6, 6),
                    bgcolor=ft.Colors.with_opacity(0.45, Color.DARK_SURFACE),
                    alignment=ft.Alignment.CENTER,
                    content=Text.H2("Coming soon", color=Color.WHITE, weight=ft.FontWeight.BOLD)
                )
            ]
        )

    def resize(self, width: int, card_width: int, cover_height: int) -> None:
        self.width = width
        self.responsive_row.width = width
        for card in self.lesson_cards:
            card.resize(card_width, cover_height)
