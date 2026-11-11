# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Page, Text


class TopNavigationBar(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], on_load: Callable[[ft.ControlEvent], object], on_save: Callable[[ft.ControlEvent], object]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.save_button_label_text = Text.BUTTON(
            self.lang["lesson_editor.save"], color=Color.WHITE
        )
        self.title_text = Text.MEDIUM(
            self.lang["lesson_editor.title"],
            weight=ft.FontWeight.BOLD,
            color=Color.PRIMARY_TEXT,
            expand=True
        )
        # Static icons
        self.save_button_icon = ft.Icon(ft.Icons.SAVE, color=Color.WHITE)

        self.main_container = ft.Row(
            controls=[
                self.title_text,
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.FOLDER_OPEN,
                            icon_color=Color.SECONDARY_TEXT,
                            tooltip=self.lang["lesson_editor.load_json"],
                            on_click=on_load
                        ),
                        ft.Button(
                            content=ft.Row(
                                controls=[
                                    self.save_button_icon,
                                    self.save_button_label_text
                                ],
                                spacing=6
                            ),
                            bgcolor=Color.PRIMARY_ACTION,
                            on_click=on_save
                        )
                    ],
                    spacing=5
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        super().__init__(
            controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width


class EditorToolbar(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], on_add_text: Callable[[str], None], on_add_divider: Callable[[str], None], on_add_image: Callable[[str], None], on_add_audio: Callable[[str], None]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.add_text_label = Text.BUTTON(self.lang["lesson_editor.add_text"])
        self.add_divider_label = Text.BUTTON(self.lang["lesson_editor.add_divider"])
        self.add_image_label = Text.BUTTON(self.lang["lesson_editor.add_image"])
        self.add_audio_label = Text.BUTTON(self.lang["lesson_editor.add_audio"])
        # Static icons
        self.add_text_icon = ft.Icon(ft.Icons.TEXT_SNIPPET)
        self.add_divider_icon = ft.Icon(ft.Icons.HORIZONTAL_RULE)
        self.add_image_icon = ft.Icon(ft.Icons.IMAGE)
        self.add_audio_icon = ft.Icon(ft.Icons.AUDIO_FILE)

        self.main_container = ft.Row(
            controls=[
                ft.Button(
                    content=ft.Row(controls=[self.add_text_icon, self.add_text_label]),
                    on_click=lambda _: on_add_text("text") if on_add_text else None
                ),
                ft.Button(
                    content=ft.Row(
                        controls=[self.add_divider_icon, self.add_divider_label]
                    ),
                    on_click=lambda _: (
                        on_add_divider("divider") if on_add_divider else None
                    )
                ),
                ft.Button(
                    content=ft.Row(controls=[self.add_image_icon, self.add_image_label]),
                    on_click=lambda _: on_add_image("image") if on_add_image else None
                ),
                ft.Button(
                    content=ft.Row(controls=[self.add_audio_icon, self.add_audio_label]),
                    on_click=lambda _: on_add_audio("audio") if on_add_audio else None
                )
            ],
            spacing=10,
            wrap=True
        )
        super().__init__(controls=[self.main_container], spacing=10)

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width


class PropertiesTabs(ft.Tabs):
    def __init__(self, page: Page, lang: dict[str, str], element_properties: ft.Column, animation_pane: ft.Column, audio_pane: ft.Column) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label=self.lang["lesson_editor.properties"]),
                ft.Tab(label=self.lang["lesson_editor.animations"]),
                ft.Tab(label=self.lang["lesson_editor.audio"])
            ]
        )
        self.tab_view = ft.TabBarView(
            expand=True,
            controls=[
                element_properties or ft.Column(),
                animation_pane or ft.Column(),
                audio_pane or ft.Column()
            ]
        )
        self.main_container = ft.Column(
            expand=True, controls=[self.tab_bar, self.tab_view]
        )
        super().__init__(
            length=3,
            selected_index=0,
            animation_duration=200,
            expand=True,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width


class SlideSidebarLayout(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], sidebar_column: ft.Column, on_add_slide: Callable[[ft.ControlEvent], object], on_move_up: Callable[[ft.ControlEvent], object], on_move_down: Callable[[ft.ControlEvent], object], on_delete_slide: Callable[[ft.ControlEvent], object]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.new_slide_label = Text.BUTTON(self.lang["lesson_editor.new_slide"])
        self.slides_title_text = Text.MEDIUM(
            self.lang["lesson_editor.slides"],
            weight=ft.FontWeight.BOLD
        )
        # Static icons
        self.new_slide_icon = ft.Icon(ft.Icons.ADD)
        self.main_container = ft.Column(
            [
                self.slides_title_text,
                ft.Divider(),
                ft.Button(
                    content=ft.Row(
                        controls=[self.new_slide_icon, self.new_slide_label]
                    ),
                    on_click=on_add_slide
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_UPWARD,
                            tooltip=self.lang["lesson_editor.move_up"],
                            on_click=on_move_up,
                            icon_size=18
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_DOWNWARD,
                            tooltip=self.lang["lesson_editor.move_down"],
                            on_click=on_move_down,
                            icon_size=18
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip=self.lang["lesson_editor.delete_slide"],
                            icon_color=ft.Colors.RED,
                            on_click=on_delete_slide,
                            icon_size=18
                        )
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                sidebar_column or ft.Column()
            ]
        )
        super().__init__(
            content=self.main_container,
            padding=10,
            border=ft.Border(right=ft.BorderSide(1, Color.INPUT_BORDER)),
            bgcolor=Color.CARD_BACKGROUND
        )

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
