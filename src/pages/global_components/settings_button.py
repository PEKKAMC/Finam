# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color


class SettingsButton(ft.Container):
    async def on_clicking_setting(self):
        await self.page.push_route("/settings")
        pass

    def __init__(self):
        super().__init__(
            content=ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=Color.BLACK,
                icon_size=30,
                on_click=self.on_clicking_setting
            ),
            alignment=ft.Alignment.CENTER
        )

