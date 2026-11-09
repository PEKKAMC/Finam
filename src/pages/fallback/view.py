# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.fallback.components import NotSupportedMessageBox, ReturnButton
from src.utils import Color, Page, UISettings, get_safe_page_size

Logger.info("Initializing Fallback page...")


class FallbackView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], fallback_reason: str) -> None:
        self._page = page
        self.lang = lang
        self.fallback_reason = fallback_reason

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE COMPONENTS
        self.message = self.get_fallback_message(reason=self.fallback_reason)

        self.message_box = NotSupportedMessageBox(
            page=self._page, lang=self.lang, message=self.message
        )

        self.return_button = ReturnButton(
            page=self._page, lang=self.lang, on_click=self._page.navigate_to("/home")
        )

        # INITIALIZE MAIN CONTAINER
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=20,
                expand=True,
                controls=[
                    self.return_button,
                    self.message_box
                ]
            )
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

        super().__init__(
            route="/home",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container
                    ]
                )
            )
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

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

    def _refresh_view(self) -> int:
        self._resize_page()
        self.message = self.get_fallback_message(self.fallback_reason)
        self.message_box.update_message(self.message)
        self.update()
        return 0

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

            # Resizing other components
            self.message_box.resize(size=int(page_width * 0.7))

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_fallback_view(page: Page, lang: dict[str, str], fallback_reason: str) -> ft.View:
    Logger.info("Loading Fallback page...")
    return FallbackView(page, lang, fallback_reason)
