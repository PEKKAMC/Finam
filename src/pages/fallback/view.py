# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.fallback.components import NotSupportedMessageBox
from src.utils import apply_responsive_text, Color, UISettings

Logger.info("Initializing Fallback page...")


class FallbackView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, fallback_reason: str):
        self._page = page
        self.lang = lang
        self.fallback_reason = fallback_reason

        # INITIALIZE PAGE COMPONENTS
        self.message_box = NotSupportedMessageBox(self.fallback_reason, self.lang)

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.message_box
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )

        super().__init__(
            route="/fallback",
            padding=0,
            bgcolor=Color.WHITE,
            controls=ft.Container(content=self.main_container, alignment=ft.Alignment.CENTER, expand=True)
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def on_page_resize(self, e=None):
        current_width: int = int(self._page.width or UISettings.MAX_APP_WIDTH)
        current_height: int = int(self._page.height or UISettings.MAX_APP_HEIGHT)

        # Safe value: reference size to properly resize elements
        safe_width: int = min(current_width, UISettings.MAX_APP_WIDTH)
        safe_height: int = min(current_height, UISettings.MAX_APP_HEIGHT)

        self.main_container.width = safe_width
        self.main_container.height = safe_height

        apply_responsive_text(self.main_container, safe_width)

        try:
            apply_responsive_text(self.main_container, safe_width)
        except Exception as ex:
            Logger.debug(f"Skipped text resizing: {ex}")

        try:
            self.update()
        except RuntimeError as ex:
            Logger.debug(f"Render skipped: {ex}")

        return e


def get_fallback_view(page: ft.Page, lang: dict, fallback_reason: str) -> ft.View:
    return FallbackView(page, lang, fallback_reason)
