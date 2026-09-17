# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re

import flet as ft

from logger import Logger
from src.utils.color import Color

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

    def _is_in_overlay(self, page: ft.Page) -> bool:
        try:
            return self in page.overlay
        except Exception as e:
            Logger.error(f"Error checking if dialog is in overlay: {e}")
            return False

    def add_to_overlay(self, page: ft.Page) -> int:
        try:
            if not self._is_in_overlay(page):
                page.overlay.append(self)
                return 0

            Logger.warn("Dialog already in overlay")
            return 1

        except Exception as e:
            Logger.error(f"Error adding dialog to overlay: {e}")
            return -1

    def remove_from_overlay(self, page: ft.Page) -> int:
        try:
            if self._is_in_overlay(page):
                page.overlay.remove(self)
                return 0

            Logger.warn("Dialog not in overlay")
            return 1

        except Exception as e:
            Logger.error(f"Error removing dialog from overlay: {e}")
            return -1

    def show(self, page: ft.Page) -> int:
        try:
            if not self.open:
                page.show_dialog(self)
                return 0
            else:
                Logger.warn("Dialog is already opened")
                return 1

        except Exception as e:
            Logger.error(f"Error showing dialog: {e}")
            return -1

    @staticmethod
    def close_most_recent_dialog(page: ft.Page) -> int:
        try:
            page.pop_dialog()
            return 0

        except Exception as e:
            Logger.error(f"Error closing most recent dialog: {e}")
            return -1