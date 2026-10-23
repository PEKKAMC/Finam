# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re

import flet as ft

from src.logger import Logger
from src.utils import Color, Page

class Dialog(ft.AlertDialog):
    def __init__(self, dialog_content: ft.Control, color: Color | ft.Colors | str):
        self.dialog_content = dialog_content
        self.color = color

        if not self._verify_color():
            self.color = Color.WHITE

        super().__init__(
            bgcolor=color,
            content=self.dialog_content,
            modal=True
        )

    def _verify_color(self) -> bool:
        if isinstance(self.color, Color | ft.Colors):
            return True
        elif isinstance(self.color, str):
            return bool(re.match(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', self.color))
        else:
            return False

    def show(self, page: Page) -> int:
        try:
            if not self.open:
                page.show_dialog(self)
            return 0

        except Exception as ex:
            Logger.error(f"Error showing dialog: {ex}")
            return -1

    def dismiss(self, page: Page) -> int:
        try:
            if self.open:
                dismissed_dialog = page.pop_dialog()
                if dismissed_dialog is not self:
                    Logger.error("Attempted to dismiss a dialog that is not at the top of the dialog stack")
                    return -1
            return 0

        except Exception as ex:
            Logger.error(f"Error dismissing dialog: {ex}")
            return -1
