# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Text, Color
from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar
from src.pages.lesson.logic import LogicController
from src.pages.lesson.components import LessonItemCard

Logger.info("Initializing Lesson page...")


class LessonView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController(user_info["username"])

        self.available_lessons = []
        self.main_container = None
        self.menu = None
        self.top_navigation_bar = None
        self.lesson_grid_responsive = None

        self.load_data()

        super().__init__(
            route="/lessons",
            padding=0,
            bgcolor="#FAFAF8",
            controls=self.create_ui_components()
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def load_data(self):
        """Fetches data from the controller before rendering the UI."""
        Logger.info("Loading lesson data...")
        self.available_lessons = self.controller.load_available_lessons()

    def create_ui_components(self):
        Logger.info("Rendering UI for Lesson page...")
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(current_user=self.user_info["username"])

        # Compute completion statistics dynamically
        total_lessons = len(self.available_lessons)
        completed_lessons = sum(1 for l in self.available_lessons if l.get("is_completed", False))
        total_minutes = sum(15 for l in self.available_lessons if l.get("is_completed", False))
        completion_pct = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0

        # Header Summary Banner matching TSX layout
        summary_banner = ft.Container(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=24,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                        controls=[
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Container(
                                        content=Text.SMALL("HỌC VIỆN TÀI CHÍNH FINAM", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
                                        padding=ft.Padding(12, 4, 12, 4),
                                        border_radius=16,
                                        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, Color.PRIMARY))
                                    ),
                                    Text.H2("Tư Duy & Kiến Thức Quản Lý Tiền", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                                    Text.SMALL("Cung cấp các bài học cô đọng giúp bạn đưa ra các quyết định chi tiêu thông minh hơn", color=Color.LIGHT_ACCENT)
                                ]
                            ),
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(
                                        padding=12,
                                        border_radius=16,
                                        bgcolor=ft.Colors.with_opacity(0.1, Color.WHITE),
                                        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, Color.WHITE)),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=2,
                                            controls=[
                                                Text.H3(f"{completed_lessons}/{total_lessons}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                                Text.SMALL("BÀI HOÀN THÀNH", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=12,
                                        border_radius=16,
                                        bgcolor=ft.Colors.with_opacity(0.1, Color.WHITE),
                                        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, Color.WHITE)),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=2,
                                            controls=[
                                                Text.H3(f"{total_minutes} phút", color=ft.Colors.AMBER_300 if hasattr(ft.Colors, 'AMBER_300') else "#FCD34D", weight=ft.FontWeight.BOLD),
                                                Text.SMALL("ĐÃ TÍCH LŨY", color=ft.Colors.AMBER_200 if hasattr(ft.Colors, 'AMBER_200') else "#FDE68A", weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    )
                                ]
                            )
                        ]
                    ),
                    # Course Progress Bar matching TSX
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.8, Color.DARK_SURFACE),
                        border_radius=12,
                        padding=2,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, Color.PRIMARY)),
                        content=ft.ProgressBar(
                            value=completion_pct / 100.0,
                            color=Color.LIGHT_ACCENT,
                            bgcolor=Color.TRANSPARENT,
                            height=8
                        )
                    )
                ]
            )
        )

        # Responsive Lesson Cards Grid
        lesson_cards = [
            LessonItemCard(
                page=self._page,
                title=lesson["title"],
                subtitle=lesson["subtitle"],
                cover_image=lesson["cover_image"],
                is_completed=lesson["is_completed"],
                route=lesson["route"]
            )
            for lesson in self.available_lessons
        ]

        self.lesson_grid_responsive = ft.ResponsiveRow(
            spacing=20,
            run_spacing=20,
            controls=[
                ft.Container(content=card, col={"xs": 12, "sm": 6, "lg": 4})
                for card in lesson_cards
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=25,
                controls=[
                    summary_banner,
                    self.lesson_grid_responsive
                ]
            ),
            padding=20,
            margin=ft.Margin(left=16, top=84, right=16, bottom=88)
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        ]

    def on_page_resize(self, event=None):
        current_width = self._page.width if event is None else event.width
        if not current_width:
            current_width = UISettings.MAX_APP_WIDTH
        safe_width = int(min(current_width, UISettings.MAX_APP_WIDTH))

        self.main_container.width = max(safe_width - 32, 320)
        self.main_container.margin = ft.Margin(left=16, top=84, right=16, bottom=88)
        self.top_navigation_bar.resize(safe_width)
        self.menu.resize(safe_width)

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Skipped updating during resize: {e}")


def get_lesson_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return LessonView(page, lang, user_info)