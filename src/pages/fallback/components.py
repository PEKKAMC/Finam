# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Text


class NotSupportedMessageBox(ft.Container):
    def __init__(self, fallback_reason: str, lang: dict):
        self.fallback_reason: str = fallback_reason
        self.message: str = ""

        match self.fallback_reason:
            case "unsupported_os":
                self.message = lang["fallback.unsupported_os"]
            case "unsupported_screen":
                self.message = lang["fallback.unsupported_screen"]
            case "page_not_found":
                self.message = lang["fallback.page_not_found"]
            case _:
                self.message = lang["fallback.default"]

        super().__init__(
            content=[
                Text.H1(f"Whoops, something when wrong: {self.message}")
            ]
        )

    def resize(self, width: int, height: int):
        super().width = width * 0.8
        super().height = height * 0.4