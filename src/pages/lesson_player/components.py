# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text


class TopNavigationMenu(ft.Row):
    def __init__(self, page: ft.Page, lang: dict, on_return_click):
        self._page = page
        self.lang = lang
        self.return_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=on_return_click
        )
        self.main_container = ft.Row(
            controls=[
                ft.Container(
                    content=self.return_button,
                    alignment=ft.Alignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(
            controls=[self.main_container],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class SlideCanvas(ft.Container):
    def __init__(self, page: ft.Page, lang: dict):
        self._page = page
        self.lang = lang
        self.canvas_stack = ft.Stack(expand=True)
        self.main_container = self.canvas_stack

        super().__init__(
            content=self.main_container,
            width=550,
            height=750,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.GREY_200),
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

    def clear_canvas(self):
        for old_control in self.canvas_stack.controls:
            old_control.animate_opacity = None
            old_control.animate_offset = None
            old_control.animate_scale = None
        self.canvas_stack.controls.clear()

    def add_visual_control(self, control_to_add):
        self.canvas_stack.controls.append(control_to_add)

    def resize(self, width: int, height: int):
        self.width = max(width, 0)
        self.height = max(height, 0)

class LessonHeader(ft.Row):
    def __init__(self, page: ft.Page, lang: dict, default_title: str):
        self._page = page
        self.lang = lang
        self.title_display = Text.H2(default_title, color=ft.Colors.BLUE_GREY_900)
        self.progress_display = Text.H4("0 / 0", color=ft.Colors.GREY_600)
        self.main_container = ft.Row(
            controls=[self.title_display, self.progress_display],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def update_header_information(self, title: str, current_index: int, total_slides: int, lang: dict):
        self.title_display.value = title
        self.progress_display.value = f"{lang['lesson_player.slide']} {current_index + 1} / {total_slides}"

    def resize(self, width: int) -> None:
        self.main_container.width = width


class LessonControls(ft.Row):
    def __init__(self, page: ft.Page, lang: dict, on_previous_click, on_next_click):
        self._page = page
        self.lang = lang
        self.button_previous = ft.Button(self.lang["lesson_player.previous"], icon=ft.Icons.ARROW_BACK, on_click=on_previous_click, disabled=True)
        self.button_next = ft.Button(self.lang["lesson_player.next"], icon=ft.Icons.ARROW_FORWARD, on_click=on_next_click, disabled=True)
        self.main_container = ft.Row(
            controls=[self.button_previous, self.button_next],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        super().__init__(controls=[self.main_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def update_button_states(self, has_previous_slide: bool, has_next_slide: bool):
        self.button_previous.disabled = not has_previous_slide
        self.button_next.disabled = not has_next_slide

    def resize(self, width: int) -> None:
        self.main_container.width = width


class PresentationBoard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, lesson_header, lesson_controls, slide_canvas):
        self._page = page
        self.lang = lang
        self.lesson_header = lesson_header
        self.lesson_controls = lesson_controls
        self.slide_canvas = slide_canvas
        self.main_container = ft.Column(
            controls=[
                self.lesson_header,
                self.lesson_controls,
                ft.Row([self.slide_canvas], alignment=ft.MainAxisAlignment.CENTER)
            ],
            expand=True, scroll=ft.ScrollMode.AUTO
        )

        super().__init__(
            content=self.main_container,
            padding=25, bgcolor=ft.Colors.WHITE, border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            height=850
        )

    def resize(self, width: int, height: int):
        self.width = max(width, 0)
        self.height = max(height, 0)