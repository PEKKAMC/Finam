# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class Username(ft.Container):
    def __init__(self, current_user: str):
        super().__init__(
            content=Text.H2(
                value=current_user,
                text_align=ft.TextAlign.CENTER,
                color=Color.BLACK
            ),
            expand=True,
            bgcolor=Color.WHITE,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, Color.BLACK)
            )
        )

