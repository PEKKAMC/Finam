# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.lessons.components import LessonGrid, LessonSummaryBanner
from src.pages.lessons.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, UISettings

Logger.info("Initializing Lessons page...")


class LessonsView(ft.View):
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
        self._load_data()
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

        self.content_column = ft.Column(
            spacing=20,
            expand=True,
            controls=[
                self.summary_banner,
                self.lesson_grid
            ]
        )

        # INITIALIZE MAIN CONTAINER
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            content=self.content_column,
        )
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

        super().__init__(
            route="/lessons",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.menu
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def _load_data(self):
        Logger.info("Loading lesson data...")
        self.available_lessons = self.controller.load_available_lessons()

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self._load_data()
            stats = self.controller.get_user_statistics(self.available_lessons)
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
            self.content_column.controls = [self.summary_banner, self.lesson_grid]
            self._on_page_resize()
            self.update()
            return 0
        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_item_size = page_width // self.menu.items_count
            menu_item_height = max(48, menu_item_size)
            menu_inside_size = menu_item_size // 6 * 5
            menu_inside_height = menu_item_height // 6 * 5
            menu_label_size = 8 if menu_item_size < 48 else 10
            menu_icon_size = 18 if menu_item_size < 48 else 20
            menu_label_spacing = 2 if menu_item_size < 48 else 4
            menu_label_visible = menu_item_size >= 48
            banner_height = (
                self.menu.BANNER_HEIGHT
                if self.menu.ad_banner is not None
                and page_width >= self.menu.BANNER_WIDTH
                else 0
            )
            menu_total_height = menu_item_height + banner_height

            # Resizing main container
            self.main_container.width = page_width
            self.content_container.width = page_width

            # Resizing other components
            self.menu.resize(
                width=page_width,
                item_size=menu_item_size,
                item_height=menu_item_height,
                inside_size=menu_inside_size,
                inside_height=menu_inside_height,
                banner_height=banner_height,
                total_height=menu_total_height,
                label_size=menu_label_size,
                icon_size=menu_icon_size,
                label_spacing=menu_label_spacing,
                label_visible=menu_label_visible,
            )
            self.main_container.margin.bottom = self.menu.reserved_height
            content_width = max(0, page_width - UISettings.CARD_PADDING * 2)
            lesson_card_width = content_width
            lesson_cover_height = min(176, lesson_card_width * 3 // 4)
            self.summary_banner.resize(
                width=content_width,
                content_width=max(0, content_width - 48),
            )
            self.lesson_grid.resize(
                width=content_width,
                card_width=lesson_card_width,
                cover_height=lesson_cover_height,
            )

            return 0

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")
            return 1

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")
            return 2

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")
            return -1


def get_lessons_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Lessons page...")
    return LessonsView(page, lang, user_info)