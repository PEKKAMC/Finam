# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.fallback.components import NotSupportedMessageBox, ReturnButton
from src.utils import Color, UISettings

Logger.info("Initializing Fallback page...")


class FallbackView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, fallback_reason: str):
        self._page = page
        self.lang = lang
        self.fallback_reason = fallback_reason

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
            on_click=lambda e: self._page.go("/home")
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
            controls=[self.main_container]
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def get_fallback_message(self, reason) -> str:
        match reason:
            case "unsupported_os":
                return self.lang["fallback.unsupported_os"]
            case "unsupported_screen":
                return self.lang["fallback.unsupported_screen"]
            case "page_not_found":
                return self.lang["fallback.page_not_found"]
            case _:
                return self.lang["fallback.default"]

    def on_page_resize(self, e=None):
        current_width: int = int(self._page.width or UISettings.MAX_APP_WIDTH)
        current_height: int = int(self._page.height or UISettings.MAX_APP_HEIGHT)

        safe_width: int = min(current_width, UISettings.MAX_APP_WIDTH)
        safe_height: int = min(current_height, UISettings.MAX_APP_HEIGHT)

        self.main_container.width = safe_width
        self.main_container.height = safe_height
        self.message_box.resize(safe_width, safe_height)

        return e


def get_fallback_view(page: ft.Page, lang: dict, fallback_reason: str) -> ft.View:
    return FallbackView(page, lang, fallback_reason)
