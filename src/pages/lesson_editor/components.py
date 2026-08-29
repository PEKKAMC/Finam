# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class TopNavigationBar(ft.Row):
    def __init__(self, page: ft.Page, lang: dict, on_load, on_save):
        self._page = page
        self.lang = lang
        self.main_container = ft.Row(
            controls=[
                Text.MEDIUM("Lesson Editor", scale=0.06, min_size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900, expand=True),
                ft.Row([
                    ft.IconButton(ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_GREY_700, tooltip="Load JSON", on_click=on_load),
                    ft.Button("Save", icon=ft.Icons.SAVE, bgcolor="#1d7333", color=Color.WHITE, on_click=on_save),
                ], spacing=5)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        super().__init__(controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def resize(self, width: int) -> None:
        self.main_container.width = width


class EditorToolbar(ft.Row):
    def __init__(self, page: ft.Page, lang: dict, on_add_text, on_add_divider, on_add_image, on_add_audio):
        self._page = page
        self.lang = lang
        self.main_container = ft.Row(
            controls=[
                ft.Button("Add Text", icon=ft.Icons.TEXT_SNIPPET, on_click=lambda _: on_add_text("text") if on_add_text else None),
                ft.Button("Add Divider", icon=ft.Icons.HORIZONTAL_RULE, on_click=lambda _: on_add_divider("divider") if on_add_divider else None),
                ft.Button("Add Image", icon=ft.Icons.IMAGE, on_click=lambda _: on_add_image("image") if on_add_image else None),
                ft.Button("Add Audio", icon=ft.Icons.AUDIO_FILE, on_click=lambda _: on_add_audio("audio") if on_add_audio else None)
            ],
            spacing=10
        )
        super().__init__(controls=[self.main_container], spacing=10)

    def resize(self, width: int) -> None:
        self.main_container.width = width


class PropertiesTabs(ft.Tabs):
    def __init__(self, page: ft.Page, lang: dict, element_properties: ft.Column, animation_pane: ft.Column, audio_pane: ft.Column):
        self._page = page
        self.lang = lang
        self.tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label="Properties"),
                ft.Tab(label="Animations"),
                ft.Tab(label="Audio")
            ]
        )
        self.tab_view = ft.TabBarView(
            expand=True,
            controls=[element_properties or ft.Column(), animation_pane or ft.Column(), audio_pane or ft.Column()]
        )
        self.main_container = ft.Column(expand=True, controls=[self.tab_bar, self.tab_view])
        super().__init__(
            length=3,
            selected_index=0,
            animation_duration=200,
            expand=True,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class SlideSidebarLayout(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, sidebar_column: ft.Column, on_add_slide, on_move_up, on_move_down, on_delete_slide):
        self._page = page
        self.lang = lang
        self.main_container = ft.Column([
            Text.MEDIUM("Slides", weight=ft.FontWeight.BOLD, scale=0.06, min_size=14),
            ft.Divider(),
            ft.Button("New Slide", icon=ft.Icons.ADD, on_click=on_add_slide),
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_UPWARD, tooltip="Move Up", on_click=on_move_up, icon_size=18),
                ft.IconButton(icon=ft.Icons.ARROW_DOWNWARD, tooltip="Move Down", on_click=on_move_down, icon_size=18),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="Delete Slide", icon_color=ft.Colors.RED, on_click=on_delete_slide, icon_size=18)
            ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            sidebar_column or ft.Column()
        ])
        super().__init__(content=self.main_container, width=170, padding=10, border=ft.Border(right=ft.BorderSide(1, ft.Colors.GREY_300)))

    def resize(self, width: int) -> None:
        self.main_container.width = width