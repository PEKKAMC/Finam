# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft
import json
import os
import re

from src.pages.global_components import SideMenu
from src.utils import Color, Text, apply_responsive_text
from src.pages.lesson_editor.logic import ENTRANCE_EFFECTS, EXIT_EFFECTS, ENTRANCE_IDS, EXIT_IDS, EditorLogicController, safe_float, calculate_pan_position
from src.pages.lesson_editor.components import TopNavigationBar, EditorToolbar, PropertiesTabs, SlideSidebarLayout

class LessonEditorView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state
        self.menu = SideMenu(self._page, self.lang, self.user_state)
        self.logic = EditorLogicController()

        # Input Fields
        self.lesson_id_input = ft.TextField(label="Lesson ID", value="1", width=100, color=Color.DEFAULT_TEXT)
        self.title_input = ft.TextField(label="Lesson Title", color=Color.DEFAULT_TEXT, expand=True)
        self.subtitle_input = ft.TextField(label="Lesson Subtitle", color=Color.DEFAULT_TEXT, expand=True)
        self.cover_image_input = ft.TextField(label="Cover Image Path/URL", color=Color.DEFAULT_TEXT, expand=True)
        self.slide_number_title = Text.LABEL(f"Slide {self.logic.current_slide_index + 1}", scale=0.06, min_size=12, weight=ft.FontWeight.BOLD)

        # Core Layout Setup
        self.sidebar_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.canvas_stack = ft.Stack(expand=True)
        self.canvas_container = ft.Container(
            content=self.canvas_stack,
            width=550, height=850,
            bgcolor=Color.WHITE,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        self.element_properties = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.animation_pane = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.audio_pane = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.properties_tabs = PropertiesTabs(self.element_properties, self.animation_pane, self.audio_pane)

        self.top_nav_bar = TopNavigationBar(self.menu.menu_button, self.load_file, self.save_file)
        self.toolbar = EditorToolbar(self.add_element_handler, self.add_element_handler, self.add_element_handler, self.add_element_handler)
        self.slide_sidebar = SlideSidebarLayout(self.sidebar_column, self.add_slide_handler, self.move_slide_up_handler, self.move_slide_down_handler, self.delete_slide_handler)

        center_editor = ft.Column([
            ft.Row([self.slide_number_title, self.toolbar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.canvas_container], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True)

        self.editor_layout = ft.Container(
            content=ft.Row([
                self.slide_sidebar,
                ft.Container(content=center_editor, padding=20, expand=True),
                ft.Container(content=self.properties_tabs, width=320, padding=10, border=ft.Border(left=ft.BorderSide(1, ft.Colors.GREY_300)), bgcolor="#fafafa")
            ], expand=True),
            height=850, border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=10, bgcolor="#f9fafb"
        )

        page_content = ft.Container(
            content=ft.Column(
                [self.top_nav_bar, ft.Row([self.lesson_id_input, self.title_input, self.subtitle_input, self.cover_image_input], spacing=15), self.editor_layout],
                expand=True),
            expand=True, padding=20
        )

        super().__init__(
            route="/lesson-editor", padding=0, bgcolor="#FAFAF8",
            controls=[ft.Stack(controls=[page_content, self.menu.view], expand=True)]
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize(None)
        self.refresh_editor()

    def show_snackbar(self, message: str, color: str):
        sb = ft.SnackBar(Text.LABEL(message, scale=0.047, min_size=12), bgcolor=color)
        self._page.overlay.append(sb)
        sb.open = True
        self._page.update()

    async def save_file(self, e):
        path = await ft.FilePicker().save_file(allowed_extensions=["json"], file_name="new_lesson.json")
        if path:
            try:
                lid = int(self.lesson_id_input.value)
            except ValueError:
                lid = 1

            data = self.logic.get_save_data(
                lid, self.title_input.value.strip(),
                self.subtitle_input.value.strip(), self.cover_image_input.value.strip()
            )
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.show_snackbar("Lesson saved successfully!", ft.Colors.GREEN_700)
            except Exception as ex:
                self.show_snackbar(f"Failed to save: {ex}", ft.Colors.RED_700)

    async def load_file(self, e):
        files = await ft.FilePicker().pick_files(allowed_extensions=["json"])
        if files and len(files) > 0:
            try:
                with open(files[0].path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.lesson_id_input.value = str(data.get("lesson_id", 1))
                    self.title_input.value = data.get("title", "no title")
                    self.subtitle_input.value = data.get("subtitle", "no subtitle")
                    self.logic.process_loaded_data(data)
                    self.refresh_editor()
                    self.show_snackbar("Lesson loaded successfully!", ft.Colors.GREEN_700)
            except Exception as ex:
                self.show_snackbar(f"Failed to load: {ex}", ft.Colors.RED_700)

    async def pick_image(self, e, tf_control, key):
        files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "gif", "webp", "svg"])
        if files and len(files) > 0:
            new_path = files[0].path
            tf_control.value = new_path
            idx = self.logic.selected_element_index
            if idx is not None:
                self.logic.slides_data[self.logic.current_slide_index]["elements"][idx][key] = new_path
                self.render_canvas()
                self._page.update()

    async def pick_audio_element(self, e, tf_control, el_index):
        files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=["mp3", "wav", "ogg"])
        if files and len(files) > 0:
            new_path = files[0].path
            tf_control.value = new_path
            self.logic.slides_data[self.logic.current_slide_index]["elements"][el_index]["content"] = new_path
            self._page.update()

    def refresh_editor(self):
        self.slide_number_title.value = f"Slide {self.logic.current_slide_index + 1}"
        self.render_sidebar()
        self.render_canvas()
        self.render_panes()
        self._page.update()

    def update_borders(self):
        for pos_container in self.canvas_stack.controls:
            if isinstance(pos_container, ft.Container) and isinstance(pos_container.content, ft.GestureDetector):
                gesture_detector = pos_container.content
                el_ref = gesture_detector.data
                if isinstance(gesture_detector.content, ft.Container):
                    outer_box = gesture_detector.content
                    is_selected = (self.logic.elements_list().index(el_ref) == self.logic.selected_element_index) if el_ref in self.logic.elements_list() else False
                    outer_box.border = ft.Border.all(2, ft.Colors.BLUE if is_selected else ft.Colors.TRANSPARENT)
                    outer_box.update()
        self.canvas_stack.update()

    def select_element_by_index(self, idx: int):
        if self.logic.selected_element_index == idx: return
        self.logic.selected_element_index = idx
        self.update_borders()
        self.render_panes()
        self.properties_tabs.tab_view.update()

    def select_element(self, e, el: dict):
        elements = self.logic.elements_list()
        try:
            self.select_element_by_index(elements.index(el))
        except ValueError:
            pass

    def move_layer_handler(self, direction: str):
        if self.logic.move_layer(direction):
            self.render_canvas()
            self.render_panes()
            self._page.update()

    def handle_pan(self, e: ft.DragUpdateEvent, ctrl: ft.Container, el: dict):
        new_x, new_y = calculate_pan_position(el, e.local_delta.x, e.local_delta.y)
        el["x"] = new_x
        el["y"] = new_y
        ctrl.left = new_x
        ctrl.top = new_y
        ctrl.update()

    def render_canvas(self):
        self.canvas_stack.controls.clear()
        elements = self.logic.elements_list()

        for idx, el in enumerate(elements):
            if el.get("type") == "audio":
                continue

            is_selected = (idx == self.logic.selected_element_index)
            is_text = el["type"] == "text"
            is_divider = el["type"] == "divider"

            if is_text:
                raw_text = el.get("content", "")
                display_text = re.sub(r'\{pause:[\d.]+}', '', raw_text) or "[Empty Text]"
                w_val = safe_float(el.get("width"), 300.0)
                font_size = safe_float(el.get("size"), 16.0)
                try:
                    scale_from_size = max(0.02, min(0.3, float(font_size) / 300.0))
                except Exception:
                    scale_from_size = 0.047
                visual = ft.Container(content=Text.LABEL(display_text, scale=scale_from_size, min_size=9, color=Color.DEFAULT_TEXT), width=w_val)
            elif is_divider:
                w_val = safe_float(el.get("width"), 300.0)
                visual = ft.Container(content=ft.Divider(thickness=2, color=Color.DEFAULT_TEXT), width=w_val, height=20, alignment=ft.Alignment.CENTER)
            else:
                s_val = safe_float(el.get("scale"), 1.0)
                final_width = 300.0 * s_val
                img_src = el.get("content", "").strip()
                if img_src and (os.path.isfile(img_src) or img_src.startswith("http")):
                    visual = ft.Image(src=img_src, fit=ft.BoxFit.CONTAIN, width=final_width, filter_quality=ft.FilterQuality.LOW, gapless_playback=True)
                else:
                    visual = ft.Container(content=ft.Icon(ft.Icons.IMAGE, color=ft.Colors.GREY_500, size=24 * s_val), bgcolor=ft.Colors.GREY_200, border_radius=5, width=100 * s_val, height=100 * s_val, alignment=ft.Alignment.CENTER)

            pos_container = ft.Container(left=safe_float(el.get("x"), 50.0), top=safe_float(el.get("y"), 50.0))
            draggable_wrapper = ft.GestureDetector(
                data=el,
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_update=lambda e, el_ref=el, ctrl=pos_container: self.handle_pan(e, ctrl, el_ref),
                on_tap=lambda e, el_ref=el: self.select_element(e, el_ref),
                content=ft.Container(content=visual, border=ft.Border.all(2, ft.Colors.BLUE if is_selected else ft.Colors.TRANSPARENT), padding=2)
            )
            pos_container.content = draggable_wrapper
            self.canvas_stack.controls.append(pos_container)

    def render_panes(self):
        self.element_properties.controls.clear()
        self.animation_pane.controls.clear()
        self.audio_pane.controls.clear()

        elements = self.logic.elements_list()
        idx = self.logic.selected_element_index
        float_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$")

        def update_prop(e, key, needs_canvas_update=False, rebuild_ui=False, map_dict=None):
            if idx is not None and elements:
                val = e.control.value
                if map_dict is not None: val = map_dict.get(val, 0)
                elements[idx][key] = val
                if needs_canvas_update: self.render_canvas()
                if rebuild_ui: self.render_panes()
                self._page.update()

        def update_audio_prop(e, key, el_index):
            if elements and el_index < len(elements):
                elements[el_index][key] = e.control.value
                self._page.update()

        # Audio Pane Loop
        audio_elements = [(i, el) for i, el in enumerate(elements) if el.get("type") == "audio"]
        if not audio_elements:
            self.audio_pane.controls.append(Text.LABEL("No audio tracks added.", scale=0.033, min_size=9, color=ft.Colors.GREY_500))
        else:
            for orig_idx, el in audio_elements:
                path_tf = ft.TextField(label="Audio Path", value=el.get("content", ""), expand=True, color=Color.DEFAULT_TEXT, on_change=lambda e, i=orig_idx: update_audio_prop(e, "content", i))
                delay_tf = ft.TextField(label="Delay In (s)", value=str(el.get("timer_in", "")), width=100, color=Color.DEFAULT_TEXT, tooltip="Time to wait before playing", input_filter=float_filter, on_change=lambda e, i=orig_idx: update_audio_prop(e, "timer_in", i))
                del_btn = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, tooltip="Delete Track", on_click=lambda e, i=orig_idx: self.delete_element_handler(i))
                browse_btn = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_GREY_700, tooltip="Browse File", on_click=lambda e, tf=path_tf, i=orig_idx: self._page.run_task(self.pick_audio_element, e, tf, i))
                card = ft.Container(content=ft.Column([ft.Row([path_tf, browse_btn]), ft.Row([delay_tf, del_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]), padding=10, border=ft.Border.all(1, ft.Colors.BLUE_GREY_700), border_radius=8, bgcolor=Color.WHITE)
                self.audio_pane.controls.append(card)

        # Animations Pane Loop
        visual_elements = [el for el in elements if el.get("type") != "audio"]
        if not visual_elements:
            self.animation_pane.controls.append(Text.LABEL("No visual elements.", scale=0.033, min_size=9, color=ft.Colors.GREY_500))
        else:
            for i, el in enumerate(elements):
                if el.get("type") == "audio": continue
                is_sel = (i == self.logic.selected_element_index)
                el_type = el.get("type", "unknown")
                if el_type == "text": preview, icon_name = el.get("content", "")[:15] or "[Empty Text]", ft.Icons.TEXT_FIELDS
                elif el_type == "divider": preview, icon_name = "Text Divider", ft.Icons.HORIZONTAL_RULE
                else: preview, icon_name = os.path.basename(el.get("content", "")) if el.get("content", "") else "[Empty Image]", ft.Icons.IMAGE
                ent = ENTRANCE_EFFECTS.get(el.get("entrance", 0), "None")
                has_anim = (ent != "None") or (EXIT_EFFECTS.get(el.get("exit", 0), "None") != "None") or el.get("timer_in")
                anim_desc = f"Delay: {el.get('timer_in', 0)}s | In: {ent}" if has_anim else "No animation assigned"
                anim_item = ft.Container(content=ft.Row([ft.Icon(icon_name, size=18, color=ft.Colors.BLUE_600 if is_sel else ft.Colors.BLUE_GREY_400), ft.Column([Text.LABEL(f"{preview}", weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL, scale=0.043, min_size=11), Text.LABEL(anim_desc, scale=0.033, min_size=9, color=ft.Colors.GREY_600 if has_anim else ft.Colors.GREY_400)], spacing=2, expand=True), ft.Icon(ft.Icons.STAR, size=14, color=ft.Colors.AMBER_400 if has_anim else ft.Colors.TRANSPARENT)]), padding=10, bgcolor=ft.Colors.BLUE_50 if is_sel else ft.Colors.WHITE, border=ft.Border.all(1, ft.Colors.BLUE_400 if is_sel else ft.Colors.GREY_300), border_radius=8, ink=True, on_click=lambda e, i_idx=i: self.select_element_by_index(i_idx))
                self.animation_pane.controls.append(anim_item)

            if idx is not None and elements[idx].get("type") != "audio":
                el = elements[idx]
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(Text.LABEL("Delays", weight=ft.FontWeight.BOLD, scale=0.047, min_size=12, color=ft.Colors.BLUE_800))
                self.animation_pane.controls.append(ft.Row([ft.TextField(label="Delay In (s)", value=str(el.get("timer_in", "")), expand=True, on_change=lambda e: update_prop(e, "timer_in"), color=Color.DEFAULT_TEXT, input_filter=float_filter), ft.TextField(label="Delay Out (s)", value=str(el.get("timer_out", "")), expand=True, on_change=lambda e: update_prop(e, "timer_out"), color=Color.DEFAULT_TEXT, input_filter=float_filter)]))
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(Text.LABEL("Entrance Animation", weight=ft.FontWeight.BOLD, scale=0.047, min_size=12, color=ft.Colors.BLUE_800))
                self.animation_pane.controls.append(ft.Dropdown(label="Entrance Effect", value=ENTRANCE_EFFECTS.get(el.get("entrance", 0), "None"), on_select=lambda e: update_prop(e, "entrance", rebuild_ui=True, map_dict=ENTRANCE_IDS), options=[ft.dropdown.Option(x) for x in list(ENTRANCE_EFFECTS.values())[:5]], color=Color.DEFAULT_TEXT))
                self.animation_pane.controls.append(ft.TextField(label="Duration (s)", value=str(el.get("duration_in", el.get("duration", ""))), expand=True, on_change=lambda e: update_prop(e, "duration_in"), tooltip="e.g., 0.5", color=Color.DEFAULT_TEXT, input_filter=float_filter))
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(Text.LABEL("Exit Animation", weight=ft.FontWeight.BOLD, scale=0.047, min_size=12, color=ft.Colors.BLUE_800))
                self.animation_pane.controls.append(ft.Dropdown(label="Exit Effect", value=EXIT_EFFECTS.get(el.get("exit", 0), "None"), on_select=lambda e: update_prop(e, "exit", rebuild_ui=True, map_dict=EXIT_IDS), options=[ft.dropdown.Option(x) for x in EXIT_EFFECTS.values()], color=Color.DEFAULT_TEXT))
                self.animation_pane.controls.append(ft.TextField(label="Duration (s)", value=str(el.get("duration_out", el.get("duration", ""))), expand=True, on_change=lambda e: update_prop(e, "duration_out"), tooltip="e.g., 0.5", color=Color.DEFAULT_TEXT, input_filter=float_filter))

        # Properties Pane
        if idx is None or not elements or elements[idx].get("type") == "audio":
            self.element_properties.controls.append(Text.LABEL("Select a visual element to edit properties.", scale=0.033, min_size=9, color=ft.Colors.GREY_500))
            return

        el = elements[idx]
        self.element_properties.controls.append(Text.LABEL("Element Properties", weight=ft.FontWeight.BOLD, scale=0.06, min_size=12, color=ft.Colors.BLUE_GREY_900))
        if el["type"] == "text":
            self.element_properties.controls.append(ft.TextField(label="Text", multiline=True, value=el.get("content", ""), on_change=lambda e: update_prop(e, "content", needs_canvas_update=True), color=Color.DEFAULT_TEXT))
            self.element_properties.controls.append(ft.Row([ft.TextField(label="Width (px)", value=str(el.get("width", 300.0)), on_change=lambda e: update_prop(e, "width", needs_canvas_update=True), color=Color.DEFAULT_TEXT, input_filter=float_filter, expand=True), ft.TextField(label="Font Size", value=str(el.get("size", 16.0)), on_change=lambda e: update_prop(e, "size", needs_canvas_update=True), color=Color.DEFAULT_TEXT, input_filter=float_filter, expand=True)]))
        elif el["type"] == "divider":
            self.element_properties.controls.append(ft.TextField(label="Width (px)", value=str(el.get("width", 300.0)), on_change=lambda e: update_prop(e, "width", needs_canvas_update=True), color=Color.DEFAULT_TEXT, input_filter=float_filter))
        else:
            path_tf = ft.TextField(label="Image Path", expand=True, value=el.get("content", ""), on_change=lambda e: update_prop(e, "content", needs_canvas_update=True), color=Color.DEFAULT_TEXT)
            self.element_properties.controls.append(ft.Row([path_tf, ft.IconButton(icon=ft.Icons.FOLDER_OPEN, tooltip="Browse Computer", icon_color=ft.Colors.BLUE_GREY_700, on_click=lambda e: self._page.run_task(self.pick_image, e, path_tf, "content"))]))
            self.element_properties.controls.append(ft.TextField(label="Scale", value=str(el.get("scale", 1.0)), on_change=lambda e: update_prop(e, "scale", needs_canvas_update=True), color=Color.DEFAULT_TEXT, input_filter=float_filter))

        self.element_properties.controls.append(ft.Divider())
        self.element_properties.controls.append(Text.LABEL("Layer Order", weight=ft.FontWeight.BOLD, scale=0.047, min_size=12))
        self.element_properties.controls.append(ft.Row([ft.Button("Forward", icon=ft.Icons.ARROW_UPWARD, on_click=lambda e: self.move_layer_handler("forward"), expand=True), ft.Button("Backward", icon=ft.Icons.ARROW_DOWNWARD, on_click=lambda e: self.move_layer_handler("backward"), expand=True)]))
        self.element_properties.controls.append(ft.Divider())
        self.element_properties.controls.append(ft.Button("Delete Element", icon=ft.Icons.DELETE, color=ft.Colors.RED, on_click=lambda e: self.delete_element_handler(idx)))

    def render_sidebar(self):
        self.sidebar_column.controls.clear()
        for i, slide in enumerate(self.logic.slides_data):
            is_selected = (i == self.logic.current_slide_index)
            item = ft.Container(
                content=Text.LABEL(f"Slide {i + 1}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900 if is_selected else Color.DEFAULT_TEXT),
                padding=10, bgcolor=ft.Colors.BLUE_50 if is_selected else Color.WHITE,
                border=ft.Border.all(2, ft.Colors.BLUE_400) if is_selected else ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=8, ink=True, on_click=lambda e, idx=i: self.select_slide(idx)
            )
            self.sidebar_column.controls.append(item)

    def select_slide(self, idx: int):
        self.logic.current_slide_index = idx
        self.logic.selected_element_index = None
        self.properties_tabs.selected_index = 0
        self.refresh_editor()

    def add_element_handler(self, el_type: str):
        self.logic.add_element(el_type)
        self.properties_tabs.selected_index = 2 if el_type == "audio" else 0
        self.refresh_editor()

    def delete_element_handler(self, idx: int):
        self.logic.delete_element_by_index(idx)
        self.refresh_editor()

    def add_slide_handler(self, e):
        self.logic.add_slide()
        self.refresh_editor()

    def delete_slide_handler(self, e):
        if self.logic.delete_slide():
            self.refresh_editor()
            self.show_snackbar("Slide deleted.", ft.Colors.BLUE_GREY_700)
        else:
            self.show_snackbar("Cannot delete the last slide.", ft.Colors.RED_700)

    def move_slide_up_handler(self, e):
        self.logic.move_slide_up()
        self.refresh_editor()

    def move_slide_down_handler(self, e):
        self.logic.move_slide_down()
        self.refresh_editor()

    def on_page_resize(self, e) -> None:
        w = self._page.width if e is None else e.width
        h = self._page.height if e is None else e.height
        if not w or not h: return

        available_height = max(500, h - 130)
        self.editor_layout.height = available_height
        self.canvas_container.width = min(550, w * 0.35)
        self.canvas_container.height = available_height * 0.75

        try:
            apply_responsive_text(self.canvas_container, int(w))
            self._page.update()
        except Exception:
            pass

def get_lesson_editor_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return LessonEditorView(page, lang, user_state)