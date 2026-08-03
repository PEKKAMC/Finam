# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, responsive_text


class TopNavigationMenu(ft.Row):
    def __init__(self, on_return_click):
        self.return_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=Color.BLACK,
            icon_size=30,
            on_click=on_return_click
        )

        super().__init__(
            controls=[
                ft.Container(
                    content=self.return_button,
                    alignment=ft.Alignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


class SlideCanvas(ft.Container):
    def __init__(self):
        self.canvas_stack = ft.Stack(expand=True)

        super().__init__(
            content=self.canvas_stack,
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


class LessonHeader(ft.Row):
    def __init__(self, default_title: str):
        self.title_display = responsive_text(default_title, scale=0.08, min_size=14, max_size=21, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
        self.progress_display = responsive_text("0 / 0", scale=0.04, min_size=10, max_size=15, color=ft.Colors.GREY_600)

        super().__init__(
            controls=[self.title_display, self.progress_display],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_header_information(self, title: str, current_index: int, total_slides: int, lang: dict):
        self.title_display.value = title
        self.progress_display.value = f"{lang['lesson_player.slide']} {current_index + 1} / {total_slides}"


class LessonControls(ft.Row):
    def __init__(self, lang: dict, on_previous_click, on_next_click):
        self.button_previous = ft.Button(lang["lesson_player.previous"], icon=ft.Icons.ARROW_BACK, on_click=on_previous_click, disabled=True)
        self.button_next = ft.Button(lang["lesson_player.next"], icon=ft.Icons.ARROW_FORWARD, on_click=on_next_click, disabled=True)

        super().__init__(
            controls=[self.button_previous, self.button_next],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_button_states(self, has_previous_slide: bool, has_next_slide: bool):
        self.button_previous.disabled = not has_previous_slide
        self.button_next.disabled = not has_next_slide


class PresentationBoard(ft.Container):
    def __init__(self, lesson_header: LessonHeader, lesson_controls: LessonControls, slide_canvas: SlideCanvas):
        super().__init__(
            content=ft.Column(
                controls=[
                    lesson_header,
                    lesson_controls,
                    ft.Row([slide_canvas], alignment=ft.MainAxisAlignment.CENTER)
                ],
                expand=True, scroll=ft.ScrollMode.AUTO
            ),
            padding=25, bgcolor=ft.Colors.WHITE, border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            height=850
        )