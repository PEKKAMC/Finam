# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.pages.global_components.username import Username
from src.pages.global_components.settings_button import SettingsButton


class TopNavigationBar(ft.Row):
    def __init__(self, menu_button: ft.Control, current_user: str):
        super().__init__(
            controls=[
                ft.Container(
                    content=menu_button,
                    alignment=ft.Alignment.CENTER
                ),
                Username(current_user=current_user),
                SettingsButton()
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
