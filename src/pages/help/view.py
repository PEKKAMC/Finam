# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.common import Menu
from src.pages.help.components import FaqSection, HelpForm
from src.utils import (
    Color,
    MenuResizeValues,
    Page,
    Text,
    UISettings,
    get_menu_resize_values,
    get_safe_page_size,
    scale_width,
)

Logger.info("Initializing Help page...")

CONTENT_DESIGN_WIDTH = 392
FORM_CONTENT_DESIGN_WIDTH = 352


class HelpView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info,
        )

        self.faq_section = FaqSection(
            lang=self.lang
        )

        self.help_form = HelpForm(
            page=self._page,
            lang=self.lang
        )

        # INITIALIZE MAIN CONTAINER
        self.page_heading = ft.Column(
            spacing=6,
            controls=[
                Text.H1(
                    self.lang["help.title"],
                    color=Color.PRIMARY_TEXT,
                ),
                Text.P(
                    self.lang["help.description"],
                    color=Color.SECONDARY_TEXT,
                ),
            ],
        )
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=20,
                controls=[
                    self.page_heading,
                    self.faq_section,
                    self.help_form,
                ],
            ),
        )
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_container],
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0),
        )

        super().__init__(
            route="/help",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.menu,
                    ],
                ),
            ),
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)

            # Get component size values
            menu_resize_values: MenuResizeValues = self.get_menu_resize_values(
                page_width, self.menu
            )

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            self.content_container.width = page_width
            content_width = scale_width(page_width, CONTENT_DESIGN_WIDTH)
            form_content_width = scale_width(
                page_width,
                FORM_CONTENT_DESIGN_WIDTH,
            )
            self.faq_section.resize(content_width)

            # Resizing other components
            self.menu.resize(
                width=page_width,
                **menu_resize_values,
            )
            self.main_container.margin.bottom = self.menu.reserved_height

            self.help_form.resize(
                width=content_width,
                content_width=form_content_width,
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")


def get_help_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Help page...")
    return HelpView(page, lang, user_info)
