# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.lesson.components import LessonGrid, LessonSummaryBanner
from src.pages.lesson.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, UISettings

Logger.info("Initializing Lesson page...")


class LessonView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])

        # LOAD LESSON DATA
        self.available_lessons = []
        self.load_data()
        stats = self.controller.get_user_statistics(self.available_lessons)

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.summary_banner = LessonSummaryBanner(
            page=self._page,
            lang=self.lang,
            total_lessons=stats["total_lessons"],
            completed_lessons=stats["completed_lessons"],
            total_minutes=stats["total_minutes"],
            completion_pct=stats["completion_percentage"]
        )

        self.lesson_grid = LessonGrid(
            page=self._page,
            lang=self.lang,
            lessons=self.available_lessons
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=20,
                            expand=True,
                            controls=[
                                self.summary_banner,
                                self.lesson_grid
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/lessons",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def load_data(self):
        Logger.info("Loading lesson data...")
        self.available_lessons = self.controller.load_available_lessons()

    def on_page_resize(self, e=None) -> None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        self.main_container.width = page_width

        self.menu.resize(
            width=page_width
        )

        return e


def get_lesson_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    return LessonView(page, lang, user_info)