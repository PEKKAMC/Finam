# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import asyncio
import re

import flet as ft

from src.utils import apply_responsive_text, Color, responsive_text
from src.pages.lesson_player.logic import LogicController, AudioController, AnimationController, ENTRANCE_EFFECTS
from src.pages.lesson_player.components import TopNavigationMenu, SlideCanvas, LessonHeader, LessonControls, PresentationBoard

class LessonPlayerView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state_information: dict, target_lesson_filename: str = ""):
        self._page = page
        self.lang = lang
        self.user_state_information = user_state_information
        self.is_constructing_slide = False

        self.audio_controller = AudioController(self._page)
        self.lesson_logic = LogicController(target_lesson_filename)
        self.animation_controller = AnimationController(self._page, self.audio_controller)

        self.top_navigation_menu = TopNavigationMenu(on_return_click=self.handle_return_click)
        self.slide_canvas = SlideCanvas()
        self.lesson_header = LessonHeader(self.lesson_logic.lesson_title)
        self.lesson_controls = LessonControls(
            self.lang,
            on_previous_click=self.handle_previous_slide,
            on_next_click=self.handle_next_slide
        )
        self.presentation_board = PresentationBoard(self.lesson_header, self.lesson_controls, self.slide_canvas)

        self.center_alignment_container = ft.Container(
            content=ft.Column(spacing=25, controls=[self.top_navigation_menu, self.presentation_board]),
            padding=20
        )

        self.main_page_content = ft.Container(
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.center_alignment_container]),
            expand=True, padding=0
        )

        routing_path = f"/lesson-player/{target_lesson_filename}" if target_lesson_filename else "/lesson-player"

        super().__init__(
            route=routing_path,
            padding=0,
            bgcolor="#FAFAF8",
            controls=[ft.Stack(controls=[self.main_page_content], expand=True)]
        )

        self._page.on_resize = self.handle_page_resize
        self.handle_page_resize(None)

        if target_lesson_filename:
            current_directory = os.path.dirname(__file__)
            project_root_directory = os.path.abspath(os.path.join(current_directory, "..", ".."))
            full_target_path = os.path.join(project_root_directory, "assets", "lessons", target_lesson_filename)
            self._page.run_task(self.initialize_lesson_from_path, full_target_path)

        self.original_route_change_event = self._page.on_route_change
        self.original_disconnect_event = self._page.on_disconnect
        self._page.on_route_change = self.cleanup_audio_resources
        self._page.on_disconnect = self.cleanup_audio_resources

    def display_snackbar_message(self, message_text: str, background_color: str):
        snackbar_control = ft.SnackBar(responsive_text(message_text, scale=0.047, min_size=12, max_size=18), bgcolor=background_color)
        self._page.overlay.append(snackbar_control)
        snackbar_control.open = True
        self._page.update()

    async def build_and_play_current_slide(self, sequence_identifier: int):
        self.slide_canvas.clear_canvas()
        current_elements = self.lesson_logic.get_current_slide_elements()
        user_interface_elements = []

        for element_data in current_elements:
            if element_data.get("type") == "audio":
                user_interface_elements.append({
                    "data": element_data, "container": None, "control": None,
                    "target_width": 0, "is_text": False
                })
                continue

            entrance_effect = ENTRANCE_EFFECTS.get(element_data.get("entrance", 0), "None")
            is_text_element = element_data.get("type") == "text"
            is_divider_element = element_data.get("type") == "divider"

            animation_duration_milliseconds = self.animation_controller.get_animation_duration(element_data, "duration_in", 0.6)

            initial_opacity = 0 if entrance_effect not in ["None", "Wipe"] else 1
            initial_offset = ft.Offset(0, 1.5) if entrance_effect == "Fly in" else ft.Offset(0, 0)
            initial_scale = ft.Scale(1, 0.01) if entrance_effect == "Strips" else ft.Scale(1, 1)

            initial_animation_object = ft.Animation(1, ft.AnimationCurve.LINEAR)

            if is_text_element:
                target_width = self.animation_controller.safe_convert_to_float(element_data.get("width"), 300.0)
                font_size = self.animation_controller.safe_convert_to_float(element_data.get("size"), 16.0)
                raw_text_content = element_data.get("content", "")
                clean_text_content = re.sub(r'\{pause:[\d.]+}', '', raw_text_content)

                try:
                    scale_from_size = max(0.02, min(0.3, float(font_size) / 300.0))
                except Exception:
                    scale_from_size = 0.047

                if entrance_effect == "Wipe":
                    visual_control = responsive_text("", scale=scale_from_size, min_size=9, max_size=14, color=Color.DEFAULT_TEXT, width=target_width)
                else:
                    visual_control = responsive_text(clean_text_content, scale=scale_from_size, min_size=9, max_size=14, color=Color.DEFAULT_TEXT, width=target_width)

            elif is_divider_element:
                target_width = self.animation_controller.safe_convert_to_float(element_data.get("width"), 300.0)
                divider_content = ft.Container(
                    content=ft.Divider(thickness=2, color=Color.DEFAULT_TEXT),
                    width=target_width, height=20, alignment=ft.Alignment.CENTER
                )

                if entrance_effect == "Wipe":
                    decoupled_layer = ft.Stack(controls=[
                        ft.Container(content=divider_content, width=target_width, alignment=ft.Alignment.TOP_LEFT)
                    ])
                    visual_control = ft.Container(
                        content=decoupled_layer, width=0.1, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        alignment=ft.Alignment.TOP_LEFT, animate=ft.Animation(animation_duration_milliseconds, ft.AnimationCurve.LINEAR)
                    )
                else:
                    visual_control = divider_content

            else:
                image_scale = self.animation_controller.safe_convert_to_float(element_data.get("scale"), 1.0)
                target_width = 300.0 * image_scale
                image_source_path = element_data.get("content", "").strip()
                final_image_source = ""

                if image_source_path:
                    if image_source_path.startswith("http"):
                        final_image_source = image_source_path
                    elif os.path.isfile(image_source_path):
                        final_image_source = image_source_path

                if final_image_source:
                    image_content = ft.Image(src=final_image_source, fit=ft.BoxFit.CONTAIN, width=target_width)
                else:
                    image_content = ft.Icon(ft.Icons.BROKEN_IMAGE, size=target_width)

                if entrance_effect == "Wipe":
                    decoupled_layer = ft.Stack(controls=[
                        ft.Container(content=image_content, width=target_width, alignment=ft.Alignment.TOP_LEFT)
                    ])
                    visual_control = ft.Container(
                        content=decoupled_layer, width=0.1, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        alignment=ft.Alignment.TOP_LEFT, animate=ft.Animation(animation_duration_milliseconds, ft.AnimationCurve.LINEAR)
                    )
                else:
                    visual_control = image_content

            position_x = self.animation_controller.safe_convert_to_float(element_data.get("x"), 50.0)
            position_y = self.animation_controller.safe_convert_to_float(element_data.get("y"), 50.0)

            animation_container = ft.Container(
                content=visual_control, left=position_x, top=position_y,
                opacity=initial_opacity, offset=initial_offset, scale=initial_scale,
                animate_opacity=initial_animation_object, animate_offset=initial_animation_object, animate_scale=initial_animation_object,
                alignment=ft.Alignment.CENTER
            )

            user_interface_elements.append({
                "data": element_data, "container": animation_container, "control": visual_control,
                "target_width": target_width, "is_text": is_text_element,
                "full_text": element_data.get("content", "") if is_text_element else ""
            })
            self.slide_canvas.add_visual_control(animation_container)

        try:
            self._page.update()
        except Exception:
            pass

        asyncio.create_task(self.animation_controller.execute_all_animations(user_interface_elements, sequence_identifier))

    async def change_slide_wrapper(self, direction_offset: int):
        if self.is_constructing_slide: return

        await self.audio_controller.pause()
        try:
            potential_new_index = self.lesson_logic.current_slide_index + direction_offset
            if 0 <= potential_new_index < self.lesson_logic.get_total_slides():
                self.is_constructing_slide = True

                if direction_offset > 0:
                    self.lesson_logic.move_to_next_slide()
                else:
                    self.lesson_logic.move_to_previous_slide()

                new_sequence_identifier = self.animation_controller.start_new_sequence()
                self.slide_canvas.clear_canvas()

                self.lesson_header.update_header_information(
                    self.lesson_logic.lesson_title,
                    self.lesson_logic.current_slide_index,
                    self.lesson_logic.get_total_slides(),
                    self.lang
                )
                self.lesson_controls.update_button_states(
                    self.lesson_logic.has_previous_slide(),
                    self.lesson_logic.has_next_slide()
                )

                self._page.update()
                await self.build_and_play_current_slide(new_sequence_identifier)
        except Exception as exception_error:
            self.display_snackbar_message(f"Navigation Error: {str(exception_error)}", ft.Colors.RED)
        finally:
            self.is_constructing_slide = False

    async def handle_next_slide(self, event):
        await self.change_slide_wrapper(1)

    async def handle_previous_slide(self, event):
        await self.change_slide_wrapper(-1)

    async def initialize_lesson_from_path(self, filepath: str):
        success = self.lesson_logic.load_lesson_data(filepath)
        if not success:
            self.lesson_header.title_display.value = "Error Loading File"
            self.lesson_header.title_display.update()
            self.display_snackbar_message("Failed to load lesson or lesson is empty.", ft.Colors.RED_700)
            return

        self.lesson_header.update_header_information(
            self.lesson_logic.lesson_title,
            self.lesson_logic.current_slide_index,
            self.lesson_logic.get_total_slides(),
            self.lang
        )
        self.lesson_controls.update_button_states(
            self.lesson_logic.has_previous_slide(),
            self.lesson_logic.has_next_slide()
        )

        initial_sequence_identifier = self.animation_controller.start_new_sequence()
        await self.build_and_play_current_slide(initial_sequence_identifier)

    async def handle_return_click(self, event=None):
        self.animation_controller.start_new_sequence()
        await self.audio_controller.pause()
        await self._page.push_route("/lessons")

    async def cleanup_audio_resources(self, event):
        self.animation_controller.start_new_sequence()
        await self.audio_controller.pause()

        if hasattr(self, 'audio_controller'):
            await self.audio_controller.pause()

            if self.audio_controller.active_audio and self.audio_controller.active_audio in self._page.services:
                self._page.services.remove(self.audio_controller.active_audio)
                self._page.update()

        if self.original_route_change_event and event.name == "route_change":
            try:
                self.original_route_change_event(event)
            except TypeError:
                self.original_route_change_event()
        elif self.original_disconnect_event and event.name == "disconnect":
            try:
                self.original_disconnect_event(event)
            except TypeError:
                self.original_disconnect_event()

        if self.audio_controller.active_audio and self.audio_controller.active_audio in self._page.services:
            self._page.services.remove(self.audio_controller.active_audio)

    def handle_page_resize(self, event) -> None:
        current_width = self._page.width if event is None else event.width
        current_height = self._page.height if event is None else event.height
        if not current_width: current_width = 650
        if not current_height: current_height = 900

        safe_width_value = min(current_width, 650)
        safe_height_value = max(600, current_height - 100)

        try:
            self.center_alignment_container.width = safe_width_value
            self.slide_canvas.width = max(400, safe_width_value * 0.9)
            self.slide_canvas.height = max(500, safe_height_value * 0.6)
            self.presentation_board.width = safe_width_value * 0.95
            self.presentation_board.height = safe_height_value

            try:
                apply_responsive_text(self.center_alignment_container, safe_width_value)
            except Exception:
                pass

            self._page.update()
        except Exception:
            pass

def get_lesson_player_view(page: ft.Page, lang: dict, user_state_information: dict, target_lesson_filename: str = None) -> ft.View:
    return LessonPlayerView(page, lang, user_state_information, target_lesson_filename)