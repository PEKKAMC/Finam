# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Page, Text


class TopNavigationMenu(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], on_return_click: Callable[[ft.ControlEvent], object]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static icons
        self.return_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=Color.PRIMARY_TEXT,
            icon_size=30,
            on_click=on_return_click
        )
        self.main_container = ft.Row(
            controls=[
                ft.Container(content=self.return_button, alignment=ft.Alignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(
            controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class SlideCanvas(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Child controls supply their own text and icon components.
        self.canvas_stack = ft.Stack(expand=True)
        self.main_container = self.canvas_stack

        super().__init__(
            content=self.main_container,
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

    def clear_canvas(self) -> None:
        for old_control in self.canvas_stack.controls:
            old_control.animate_opacity = None
            old_control.animate_offset = None
            old_control.animate_scale = None
        self.canvas_stack.controls.clear()

    def add_visual_control(self, control_to_add: ft.Control) -> None:
        self.canvas_stack.controls.append(control_to_add)

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


class LessonHeader(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], default_title: str) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.title_display = Text.H2(default_title, color=Color.PRIMARY_TEXT)
        self.progress_display = Text.H4("0 / 0", color=Color.SECONDARY_TEXT)
        self.main_container = ft.Row(
            controls=[self.title_display, self.progress_display],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(
            controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_header_information(self, title: str, current_index: int, total_slides: int, lang: dict[str, str]) -> None:
        self.title_display.value = title
        self.progress_display.value = (
            f"{lang['lesson_player.slide']} {current_index + 1} / {total_slides}"
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class LessonControls(ft.Row):
    def __init__(self, page: Page, lang: dict[str, str], on_previous_click: Callable[[ft.ControlEvent], object], on_next_click: Callable[[ft.ControlEvent], object]) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.previous_button_label = Text.BUTTON(
            self.lang["lesson_player.previous"]
        )
        self.next_button_label = Text.BUTTON(self.lang["lesson_player.next"])
        # Static icons
        self.previous_button_icon = ft.Icon(ft.Icons.ARROW_BACK)
        self.next_button_icon = ft.Icon(ft.Icons.ARROW_FORWARD)
        self.button_previous = ft.Button(
            content=ft.Row(
                controls=[self.previous_button_icon, self.previous_button_label],
                spacing=6
            ),
            on_click=on_previous_click,
            disabled=True
        )
        self.button_next = ft.Button(
            content=ft.Row(
                controls=[self.next_button_icon, self.next_button_label], spacing=6
            ),
            on_click=on_next_click,
            disabled=True
        )
        self.main_container = ft.Row(
            controls=[self.button_previous, self.button_next],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(
            controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_button_states(self, has_previous_slide: bool, has_next_slide: bool) -> None:
        self.button_previous.disabled = not has_previous_slide
        self.button_next.disabled = not has_next_slide

    def resize(self, width: int) -> None:
        self.main_container.width = width


class PresentationBoard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], lesson_header: LessonHeader, lesson_controls: LessonControls, slide_canvas: SlideCanvas) -> None:
        self._page = page
        self.lang = lang
        # TEXT AND ICON COMPONENTS
        # Child controls supply their own text and icon components.
        self.lesson_header = lesson_header
        self.lesson_controls = lesson_controls
        self.slide_canvas = slide_canvas
        self.main_container = ft.Column(
            controls=[
                self.lesson_header,
                self.lesson_controls,
                ft.Row([self.slide_canvas], alignment=ft.MainAxisAlignment.CENTER)
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        super().__init__(
            content=self.main_container,
            padding=25,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            )
        )

    def resize(self, width: int, height: int, padding: int, content_width: int) -> None:
        self.width = width
        self.height = height
        self.padding = padding
        self.main_container.width = content_width
