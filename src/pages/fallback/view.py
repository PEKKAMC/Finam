# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.fallback.components import NotSupportedMessageBox, ReturnButton
from src.utils import Color, get_safe_page_size, Page

Logger.info("Initializing Fallback page...")


class FallbackView(ft.View):
    def __init__(self, page: Page, lang: dict, fallback_reason: str):
        self._page = page
        self.lang = lang
        self.fallback_reason = fallback_reason

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE COMPONENTS
        self.message = self.get_fallback_message(
            reason=self.fallback_reason
        )

        self.message_box = NotSupportedMessageBox(
            page=self._page,
            lang=self.lang,
            message=self.message
        )

        self.return_button = ReturnButton(
            page=self._page,
            lang=self.lang,
            on_click=self._page.navigate_to("/home")
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.return_button,
                    self.message_box
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        )

        super().__init__(
            route="/fallback",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            controls=[
                self.main_container
            ]
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def get_fallback_message(self, reason: str) -> str:
        match reason:
            case "unsupported_os":
                return self.lang["fallback.unsupported_os"]
            case "unsupported_screen":
                return self.lang["fallback.unsupported_screen"]
            case "page_not_found":
                return self.lang["fallback.page_not_found"]
            case _:
                return self.lang["fallback.default"]

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
            page_width, page_height = self.get_safe_page_size(self._page)

            self.main_container.width = page_width

            self.message_box.resize(
                size=int(min(page_width, page_height) * 0.7)
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


def get_fallback_view(page: Page, lang: dict, fallback_reason: str) -> ft.View:
    Logger.info("Loading Fallback page...")
    return FallbackView(page, lang, fallback_reason)
