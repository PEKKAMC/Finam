# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class TopNavigationBar(ft.Row):
    def __init__(self, on_load, on_save):
        super().__init__(
            controls=[
                Text.LABEL("Lesson Editor", scale=0.06, min_size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900, expand=True),
                ft.Row([
                    ft.IconButton(ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_GREY_700, tooltip="Load JSON", on_click=on_load),
                    ft.Button("Save", icon=ft.Icons.SAVE, bgcolor="#1d7333", color=Color.WHITE, on_click=on_save),
                ], spacing=5)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


class EditorToolbar(ft.Row):
    def __init__(self, on_add_text, on_add_divider, on_add_image, on_add_audio):
        super().__init__(
            controls=[
                ft.Button("Add Text", icon=ft.Icons.TEXT_SNIPPET, on_click=lambda _: on_add_text("text")),
                ft.Button("Add Divider", icon=ft.Icons.HORIZONTAL_RULE, on_click=lambda _: on_add_divider("divider")),
                ft.Button("Add Image", icon=ft.Icons.IMAGE, on_click=lambda _: on_add_image("image")),
                ft.Button("Add Audio", icon=ft.Icons.AUDIO_FILE, on_click=lambda _: on_add_audio("audio"))
            ],
            spacing=10
        )


class PropertiesTabs(ft.Tabs):
    def __init__(self, element_properties: ft.Column, animation_pane: ft.Column, audio_pane: ft.Column):
        self.tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label="Properties"),
                ft.Tab(label="Animations"),
                ft.Tab(label="Audio")
            ]
        )
        self.tab_view = ft.TabBarView(
            expand=True,
            controls=[element_properties, animation_pane, audio_pane]
        )
        super().__init__(
            length=3,
            selected_index=0,
            animation_duration=200,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[self.tab_bar, self.tab_view]
            )
        )


class SlideSidebarLayout(ft.Container):
    def __init__(self, sidebar_column: ft.Column, on_add_slide, on_move_up, on_move_down, on_delete_slide):
        super().__init__(
            content=ft.Column([
                Text.LABEL("Slides", weight=ft.FontWeight.BOLD, scale=0.06, min_size=14),
                ft.Divider(),
                ft.Button("New Slide", icon=ft.Icons.ADD, on_click=on_add_slide),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_UPWARD, tooltip="Move Up", on_click=on_move_up, icon_size=18),
                    ft.IconButton(icon=ft.Icons.ARROW_DOWNWARD, tooltip="Move Down", on_click=on_move_down, icon_size=18),
                    ft.IconButton(icon=ft.Icons.DELETE, tooltip="Delete Slide", icon_color=ft.Colors.RED, on_click=on_delete_slide, icon_size=18)
                ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                sidebar_column
            ]),
            width=170, padding=10, border=ft.Border(right=ft.BorderSide(1, ft.Colors.GREY_300))
        )