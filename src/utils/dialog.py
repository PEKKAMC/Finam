# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re

import flet as ft

from src.logger import Logger
from src.utils import Color, Page

class Dialog(ft.AlertDialog):
    def __init__(self, dialog_content: ft.Control, color: Color | ft.Colors | str, options: list | None = None, padding: int = 24):
        if not self._verify_color(color):
            color = Color.DEFAULT_CONTAINER_BACKGROUND

        self._dialog_page: Page | None = getattr(self, "_page", None)

        super().__init__(
            content=dialog_content,
            bgcolor=color,
            actions=options,
            content_padding=padding,
            modal=True
        )

    @staticmethod
    def _verify_color(color: Color | ft.Colors | str) -> bool:
        if isinstance(color, Color | ft.Colors):
            return True
        elif isinstance(color, str):
            return bool(re.match(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', color))
        else:
            return False

    def _get_page(self) -> Page:
        try:
            return self.page
        except RuntimeError:
            if self._dialog_page is None:
                raise
            return self._dialog_page

    def show(self) -> int:
        try:
            if not self.open:
                self._get_page().show_dialog(self)
            return 0

        except Exception as ex:
            Logger.error(f"Error showing dialog: {ex}")
            return -1

    def dismiss(self) -> int:
        try:
            if self.open:
                dismissed_dialog = self._get_page().pop_dialog()
                if dismissed_dialog is not self:
                    Logger.error("Attempted to dismiss a dialog that is not at the top of the dialog stack")
                    return -1
            return 0

        except Exception as ex:
            Logger.error(f"Error dismissing dialog: {ex}")
            return -1
