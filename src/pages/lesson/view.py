# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Text
from src.logger import Logger
from src.pages.global_components import SideMenu
from src.pages.lesson.logic import LogicController
from src.pages.lesson.components import MilestoneCard, StatisticsCard, CategoryTabs, LessonItemCard

Logger.info("Initializing Lesson page...")


class LessonView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state
        self.controller = LogicController(user_state["current_user"])

        self.user_statistics = {}
        self.available_lessons = []

        self.main_container = None
        self.menu = None
        self.header_text = None
        self.top_navigation_bar = None
        self.lesson_components = []

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

        Logger.info("Loading lesson and statistics data...")
        self.user_statistics = self.controller.get_user_statistics()
        self.available_lessons = self.controller.load_available_lessons()

    def create_ui_components(self):
        Logger.info("Rendering UI for Lesson page...")
        self.menu = SideMenu(self._page, self.lang, self.user_state)

        search_bar = ft.TextField(
            hint_text=self.lang["lessons.search"],
            color=ft.Colors.GREY_900,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.TRANSPARENT,
            height=40,
            expand=True,
            content_padding=10,
            text_size=14
        )

        self.top_navigation_bar = ft.Row(
            controls=[
                ft.Container(content=self.menu.menu_button, alignment=ft.Alignment.CENTER),
                search_bar
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.header_text = ft.Column(
            spacing=5,
            controls=[
                Text.H1(self.lang["lessons.title"], color=ft.Colors.BLUE_GREY_900),
            ]
        )

        dashboard_row = ft.Row(
            spacing=20,
            controls=[
                MilestoneCard(self.lang, self.user_statistics),
                StatisticsCard(self.lang, self.user_statistics)
            ]
        )

        categories = [self.lang["lessons.category_all"]]
        tabs_row = CategoryTabs(categories)

        self.lesson_components = [
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

        lessons_list = ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=self.lesson_components
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=25,
                controls=[
                    self.top_navigation_bar,
                    self.header_text,
                    dashboard_row,
                    tabs_row,
                    lessons_list
                ]
            ),
            padding=20
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[self.main_container]
                                )
                            ]
                        ),
                        expand=True,
                        padding=0
                    ),
                    self.menu.view
                ]
            )
        ]

    def on_page_resize(self, event=None):
        current_width = self._page.width if event is None else event.width
        if not current_width: current_width = UISettings.MAX_APP_WIDTH
        safe_width = int(min(current_width, UISettings.MAX_APP_WIDTH))

        self.main_container.width = safe_width
        self.top_navigation_bar.width = safe_width * 0.9

        header_text_size = max(24, int(safe_width * 0.035))
        if self.header_text.controls:
            self.header_text.controls[0].size = header_text_size

        lesson_card_width = max(300, safe_width * 0.85)
        for card in self.lesson_components:
            card.width = lesson_card_width
            if card.content.controls[0]:
                card.content.controls[0].width = lesson_card_width * 0.5

        try:
            from src.utils import apply_responsive_text
            apply_responsive_text(self.main_container, safe_width)
        except Exception as e:
            Logger.debug(f"Skipped text resizing: {e}")

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Skipped updating during resize: {e}")


def get_lesson_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return LessonView(page, lang, user_state)