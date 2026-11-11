# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import json
import os
import re
from pathlib import Path

import flet as ft

from src.logger import Logger
from src.pages.common import Menu
from src.pages.lesson_editor.components import EditorToolbar, PropertiesTabs, SlideSidebarLayout
from src.pages.lesson_editor.logic import CANVAS_DESIGN_HEIGHT, CANVAS_DESIGN_WIDTH, DEFAULT_ELEMENT_POSITION, DEFAULT_ELEMENT_SCALE, DEFAULT_ELEMENT_WIDTH, DEFAULT_TEXT_SIZE, ENTRANCE_EFFECTS, ENTRANCE_IDS, EXIT_EFFECTS, EXIT_IDS, ElementData, LogicController, calculate_pan_position, safe_float
from src.utils import Color, Data, MenuResizeValues, Page, Text, create_text, get_menu_resize_values, get_safe_page_size, scale_width

Logger.info("Loading Lesson Editor page...")

PAGE_CONTENT_DESIGN_WIDTH = 392
EDITOR_CONTENT_DESIGN_WIDTH = 352
SIDEBAR_CONTENT_DESIGN_WIDTH = 372
AVAILABLE_PAGE_HEIGHT_RATIO = 0.9
EDITOR_CANVAS_HEIGHT_RATIO = 0.55
FLOAT_REGEX = Data().get_regex_string("float")

class LessonEditorView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE CONTROLLER
        self.logic = LogicController()

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.lesson_id_input = ft.TextField(
            label=self.lang["lesson_editor.lesson_id"],
            value="1",
            width=100,
            color=Color.DEFAULT_TEXT
        )
        self.title_input = ft.TextField(
            label=self.lang["lesson_editor.lesson_title"],
            color=Color.DEFAULT_TEXT,
            expand=True
        )
        self.subtitle_input = ft.TextField(
            label=self.lang["lesson_editor.lesson_subtitle"],
            color=Color.DEFAULT_TEXT,
            expand=True
        )
        self.cover_image_input = ft.TextField(
            label=self.lang["lesson_editor.cover_image"],
            color=Color.DEFAULT_TEXT,
            expand=True
        )
        self.slide_number_title = Text.MEDIUM(
            f"{self.lang['lesson_editor.slide']} {self.logic.current_slide_index + 1}",
            weight=ft.FontWeight.BOLD
        )

        self.sidebar_column = ft.Column(
            spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
        )
        self.canvas_stack = ft.Stack(expand=True)
        self.canvas_container = ft.Container(
            content=self.canvas_stack,
            width=CANVAS_DESIGN_WIDTH,
            height=CANVAS_DESIGN_HEIGHT,
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        self.element_properties = ft.Column(
            spacing=15, scroll=ft.ScrollMode.AUTO, expand=True
        )
        self.animation_pane = ft.Column(
            spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
        )
        self.audio_pane = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.properties_tabs = PropertiesTabs(
            self._page,
            self.lang,
            self.element_properties,
            self.animation_pane,
            self.audio_pane
        )

        self.toolbar = EditorToolbar(
            self._page,
            self.lang,
            self.add_element_handler,
            self.add_element_handler,
            self.add_element_handler,
            self.add_element_handler
        )
        self.slide_sidebar = SlideSidebarLayout(
            self._page,
            self.lang,
            self.sidebar_column,
            self.add_slide_handler,
            self.move_slide_up_handler,
            self.move_slide_down_handler,
            self.delete_slide_handler
        )

        self.center_editor = ft.Column(
            [
                ft.Row(
                    [self.slide_number_title, self.toolbar],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row([self.canvas_container], alignment=ft.MainAxisAlignment.CENTER)
            ],
            expand=True
        )
        self.center_panel = ft.Container(
            content=self.center_editor,
            padding=20,
            expand=True
        )
        self.properties_panel = ft.Container(
            content=self.properties_tabs,
            width=320,
            padding=10,
            border=ft.Border(left=ft.BorderSide(1, Color.INPUT_BORDER)),
            bgcolor=Color.CARD_BACKGROUND
        )

        self.editor_layout = ft.Container(
            content=ft.Column(
                [
                    self.slide_sidebar,
                    self.center_panel,
                    self.properties_panel
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO
            ),
            height=CANVAS_DESIGN_HEIGHT,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=10,
            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND
        )

        page_content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.lesson_id_input,
                            self.title_input,
                            self.subtitle_input,
                            self.cover_image_input
                        ],
                        spacing=15
                    ),
                    self.editor_layout
                ],
                expand=True
            ),
            expand=True,
            padding=20
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[page_content]),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

        super().__init__(
            route="/lesson-editor",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True, controls=[self.main_container, self.menu]
                )
            )
        )

        self._page.on_resize = self._resize_page
        self._resize_page()
        self.refresh_editor()

    async def save_file(self, e: ft.ControlEvent) -> None:
        path = await ft.FilePicker().save_file(
            allowed_extensions=["json"], file_name="new_lesson.json"
        )
        if path:
            try:
                lesson_id = int(self.lesson_id_input.value)
            except TypeError, ValueError:
                lesson_id = 1

            data = self.logic.get_save_data(
                lesson_id,
                (self.title_input.value or "").strip(),
                (self.subtitle_input.value or "").strip(),
                (self.cover_image_input.value or "").strip()
            )
            try:
                serialized_data = json.dumps(data, ensure_ascii=False, indent=2)
                await asyncio.to_thread(Path(path).write_text, serialized_data, encoding="utf-8")
            except (OSError, TypeError, ValueError) as ex:
                Logger.error(f"{self.lang['lesson_editor.failed_to_save']}: {ex}")

    async def load_file(self, e: ft.ControlEvent) -> None:
        files = await ft.FilePicker().pick_files(allowed_extensions=["json"])
        if not files or not files[0].path:
            return

        try:
            serialized_data = await asyncio.to_thread(
                Path(files[0].path).read_text, encoding="utf-8"
            )
            data = json.loads(serialized_data)
            self.lesson_id_input.value = str(data.get("lesson_id", 1))
            self.title_input.value = data.get(
                "title", self.lang["lesson_editor.no_title"]
            )
            self.subtitle_input.value = data.get(
                "subtitle", self.lang["lesson_editor.no_subtitle"]
            )
            self.logic.process_loaded_data(data)
            self.refresh_editor()
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, AttributeError) as ex:
            Logger.error(f"{self.lang['lesson_editor.failed_to_load']}: {ex}")

    async def pick_image(self, e: ft.ControlEvent, text_field: ft.TextField, key: str) -> None:
        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "gif", "webp", "svg"]
        )
        if not files or not files[0].path:
            return

        new_path = files[0].path
        text_field.value = new_path
        selected_element_index = self.logic.selected_element_index
        if selected_element_index is None:
            return
        self.logic.slides_data[self.logic.current_slide_index]["elements"][
            selected_element_index
        ][key] = new_path
        self.render_canvas()
        self._page.update()

    async def pick_audio_element(self, e: ft.ControlEvent, text_field: ft.TextField, element_index: int) -> None:
        files = await ft.FilePicker().pick_files(
            allow_multiple=False, allowed_extensions=["mp3", "wav", "ogg"]
        )
        if not files or not files[0].path:
            return

        new_path = files[0].path
        text_field.value = new_path
        self.logic.slides_data[self.logic.current_slide_index]["elements"][
            element_index
        ]["content"] = new_path
        self._page.update()

    def refresh_editor(self) -> None:
        self.slide_number_title.value = f"Slide {self.logic.current_slide_index + 1}"
        self.render_sidebar()
        self.render_canvas()
        self.render_panes()
        self._page.update()

    def update_borders(self) -> None:
        elements = self.logic.elements_list()
        for pos_container in self.canvas_stack.controls:
            if isinstance(pos_container, ft.Container) and isinstance(
                pos_container.content, ft.GestureDetector
            ):
                gesture_detector = pos_container.content
                el_ref = gesture_detector.data
                if isinstance(gesture_detector.content, ft.Container):
                    outer_box = gesture_detector.content
                    is_selected = el_ref in elements and (
                        elements.index(el_ref) == self.logic.selected_element_index
                    )
                    outer_box.border = ft.Border.all(
                        2, ft.Colors.BLUE if is_selected else ft.Colors.TRANSPARENT
                    )
                    outer_box.update()
        self.canvas_stack.update()

    def select_element_by_index(self, element_index: int) -> None:
        if self.logic.selected_element_index == element_index:
            return
        self.logic.selected_element_index = element_index
        self.update_borders()
        self.render_panes()
        self.properties_tabs.tab_view.update()

    def select_element(self, e: ft.ControlEvent, element: ElementData) -> None:
        elements = self.logic.elements_list()
        if element in elements:
            self.select_element_by_index(elements.index(element))

    def move_layer_handler(self, direction: str) -> None:
        if self.logic.move_layer(direction):
            self.render_canvas()
            self.render_panes()
            self._page.update()

    @staticmethod
    def handle_pan(e: ft.DragUpdateEvent, control: ft.Container, element: ElementData) -> None:
        new_x, new_y = calculate_pan_position(element, e.local_delta.x, e.local_delta.y)
        element["x"] = new_x
        element["y"] = new_y
        control.left = new_x
        control.top = new_y
        control.update()

    def render_canvas(self) -> None:
        self.canvas_stack.controls.clear()
        elements = self.logic.elements_list()

        for element_index, element in enumerate(elements):
            if element.get("type") == "audio":
                continue

            is_selected = element_index == self.logic.selected_element_index
            is_text = element["type"] == "text"
            is_divider = element["type"] == "divider"

            if is_text:
                raw_text = element.get("content", "")
                display_text = (
                    re.sub(r"\{pause:[\d.]+}", "", raw_text)
                    or self.lang["lesson_editor.empty_text"]
                )
                element_width = safe_float(element.get("width"), DEFAULT_ELEMENT_WIDTH)
                font_size = int(element.get("size")) or int(DEFAULT_TEXT_SIZE)
                visual = ft.Container(
                    content=create_text(
                        display_text, size=font_size, color=Color.DEFAULT_TEXT
                    ),
                    width=element_width
                )
            elif is_divider:
                element_width = safe_float(element.get("width"), DEFAULT_ELEMENT_WIDTH)
                visual = ft.Container(
                    content=ft.Divider(thickness=2, color=Color.DEFAULT_TEXT),
                    width=element_width,
                    height=20,
                    alignment=ft.Alignment.CENTER
                )
            else:
                image_scale = safe_float(element.get("scale"), DEFAULT_ELEMENT_SCALE)
                final_width = DEFAULT_ELEMENT_WIDTH * image_scale
                image_source = element.get("content", "").strip()
                if image_source and (
                    os.path.isfile(image_source) or image_source.startswith("http")
                ):
                    visual = ft.Image(
                        src=image_source,
                        fit=ft.BoxFit.CONTAIN,
                        width=final_width,
                        filter_quality=ft.FilterQuality.LOW,
                        gapless_playback=True
                    )
                else:
                    visual = ft.Container(
                        content=ft.Icon(
                            ft.Icons.IMAGE,
                            color=Color.SECONDARY_TEXT,
                            size=24 * image_scale
                        ),
                        bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
                        border_radius=5,
                        width=100 * image_scale,
                        height=100 * image_scale,
                        alignment=ft.Alignment.CENTER
                    )

            pos_container = ft.Container(
                left=safe_float(element.get("x"), DEFAULT_ELEMENT_POSITION),
                top=safe_float(element.get("y"), DEFAULT_ELEMENT_POSITION)
            )
            draggable_wrapper = ft.GestureDetector(
                data=element,
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_update=lambda event, item=element, control=pos_container: (
                    self.handle_pan(event, control, item)
                ),
                on_tap=lambda event, item=element: self.select_element(event, item),
                content=ft.Container(
                    content=visual,
                    border=ft.Border.all(
                        2, ft.Colors.BLUE if is_selected else ft.Colors.TRANSPARENT
                    ),
                    padding=2
                )
            )
            pos_container.content = draggable_wrapper
            self.canvas_stack.controls.append(pos_container)

    def _update_selected_element_property(self, event: ft.ControlEvent, property_name: str, needs_canvas_update: bool = False, rebuild_ui: bool = False, value_map: dict[str, int] | None = None) -> None:
        selected_element_index = self.logic.selected_element_index
        elements = self.logic.elements_list()
        if selected_element_index is None or not 0 <= selected_element_index < len(
            elements
        ):
            return

        property_value = event.control.value
        if value_map is not None:
            property_value = value_map.get(property_value, 0)
        elements[selected_element_index][property_name] = property_value
        if needs_canvas_update:
            self.render_canvas()
        if rebuild_ui:
            self.render_panes()
        self._page.update()

    def _update_audio_element_property(self, event: ft.ControlEvent, property_name: str, element_index: int) -> None:
        elements = self.logic.elements_list()
        if not 0 <= element_index < len(elements):
            return
        elements[element_index][property_name] = event.control.value
        self._page.update()

    def render_panes(self) -> None:
        self.element_properties.controls.clear()
        self.animation_pane.controls.clear()
        self.audio_pane.controls.clear()

        elements = self.logic.elements_list()
        selected_element_index = self.logic.selected_element_index
        float_filter = ft.InputFilter(allow=True, regex_string=FLOAT_REGEX)

        # Audio Pane Loop
        audio_elements = [
            (i, el) for i, el in enumerate(elements) if el.get("type") == "audio"
        ]
        if not audio_elements:
            self.audio_pane.controls.append(
                Text.MEDIUM("No audio tracks added.", color=Color.SECONDARY_TEXT)
            )
        else:
            for orig_idx, el in audio_elements:
                path_tf = ft.TextField(
                    label="Audio Path",
                    value=el.get("content", ""),
                    expand=True,
                    color=Color.DEFAULT_TEXT,
                    on_change=lambda e, i=orig_idx: self._update_audio_element_property(
                        e, "content", i
                    )
                )
                delay_tf = ft.TextField(
                    label="Delay In (s)",
                    value=str(el.get("timer_in", "")),
                    width=100,
                    color=Color.DEFAULT_TEXT,
                    tooltip="Time to wait before playing",
                    input_filter=float_filter,
                    on_change=lambda e, i=orig_idx: self._update_audio_element_property(
                        e, "timer_in", i
                    )
                )
                del_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    tooltip="Delete Track",
                    on_click=lambda e, i=orig_idx: self.delete_element_handler(i)
                )
                browse_button = ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN,
                    icon_color=Color.SECONDARY_TEXT,
                    tooltip="Browse File",
                    on_click=lambda e, tf=path_tf, i=orig_idx: self._page.run_task(
                        self.pick_audio_element, e, tf, i
                    )
                )
                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([path_tf, browse_button]),
                            ft.Row(
                                [delay_tf, del_button],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ]
                    ),
                    padding=10,
                    border=ft.Border.all(1, Color.INPUT_BORDER),
                    border_radius=8,
                    bgcolor=Color.CARD_BACKGROUND
                )
                self.audio_pane.controls.append(card)

        # Animations Pane Loop
        visual_elements = [el for el in elements if el.get("type") != "audio"]
        if not visual_elements:
            self.animation_pane.controls.append(
                Text.MEDIUM("No visual elements.", color=Color.SECONDARY_TEXT)
            )
        else:
            for i, el in enumerate(elements):
                if el.get("type") == "audio":
                    continue
                is_sel = i == self.logic.selected_element_index
                el_type = el.get("type", "unknown")
                if el_type == "text":
                    preview, icon_name = (
                        el.get("content", "")[:15] or "[Empty Text]",
                        ft.Icons.TEXT_FIELDS
                    )
                elif el_type == "divider":
                    preview, icon_name = "Text Divider", ft.Icons.HORIZONTAL_RULE
                else:
                    preview, icon_name = (
                        os.path.basename(el.get("content", ""))
                        if el.get("content", "")
                        else "[Empty Image]",
                        ft.Icons.IMAGE
                    )
                ent = ENTRANCE_EFFECTS.get(el.get("entrance", 0), "None")
                has_anim = (
                    (ent != "None")
                    or (EXIT_EFFECTS.get(el.get("exit", 0), "None") != "None")
                    or el.get("timer_in")
                )
                anim_desc = (
                    f"Delay: {el.get('timer_in', 0)}s | In: {ent}"
                    if has_anim
                    else "No animation assigned"
                )
                anim_item = ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                icon_name,
                                size=18,
                                color=Color.NAVIGATION_ACTIVE_ICON
                                if is_sel
                                else Color.SECONDARY_TEXT
                            ),
                            ft.Column(
                                [
                                    Text.MEDIUM(
                                        f"{preview}",
                                        weight=ft.FontWeight.BOLD
                                        if is_sel
                                        else ft.FontWeight.NORMAL,
                                        color=Color.NAVIGATION_ACTIVE_TEXT
                                        if is_sel
                                        else Color.DEFAULT_TEXT
                                    ),
                                    Text.MEDIUM(anim_desc, color=Color.SECONDARY_TEXT)
                                ],
                                spacing=2,
                                expand=True
                            ),
                            ft.Icon(
                                ft.Icons.STAR,
                                size=14,
                                color=Color.WARNING_COLOR
                                if has_anim
                                else Color.TRANSPARENT
                            )
                        ]
                    ),
                    padding=10,
                    bgcolor=Color.NAVIGATION_ACTIVE_BACKGROUND
                    if is_sel
                    else Color.CARD_BACKGROUND,
                    border=ft.Border.all(
                        1,
                        Color.NAVIGATION_ACTIVE_ICON if is_sel else Color.INPUT_BORDER
                    ),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, i_idx=i: self.select_element_by_index(i_idx)
                )
                self.animation_pane.controls.append(anim_item)

            if (
                selected_element_index is not None
                and elements[selected_element_index].get("type") != "audio"
            ):
                selected_element = elements[selected_element_index]
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(
                    Text.MEDIUM(
                        "Delays", weight=ft.FontWeight.BOLD, color=Color.PRIMARY_TEXT
                    )
                )
                self.animation_pane.controls.append(
                    ft.Row(
                        [
                            ft.TextField(
                                label="Delay In (s)",
                                value=str(selected_element.get("timer_in", "")),
                                expand=True,
                                on_change=lambda e: (
                                    self._update_selected_element_property(
                                        e, "timer_in"
                                    )
                                ),
                                color=Color.DEFAULT_TEXT,
                                input_filter=float_filter
                            ),
                            ft.TextField(
                                label="Delay Out (s)",
                                value=str(selected_element.get("timer_out", "")),
                                expand=True,
                                on_change=lambda e: (
                                    self._update_selected_element_property(
                                        e, "timer_out"
                                    )
                                ),
                                color=Color.DEFAULT_TEXT,
                                input_filter=float_filter
                            )
                        ]
                    )
                )
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(
                    Text.MEDIUM(
                        "Entrance Animation",
                        weight=ft.FontWeight.BOLD,
                        color=Color.PRIMARY_TEXT
                    )
                )
                self.animation_pane.controls.append(
                    ft.Dropdown(
                        label="Entrance Effect",
                        value=ENTRANCE_EFFECTS.get(
                            selected_element.get("entrance", 0), "None"
                        ),
                        on_select=lambda e: self._update_selected_element_property(
                            e, "entrance", rebuild_ui=True, value_map=ENTRANCE_IDS
                        ),
                        options=[
                            ft.dropdown.Option(x)
                            for x in list(ENTRANCE_EFFECTS.values())[:5]
                        ],
                        color=Color.DEFAULT_TEXT
                    )
                )
                self.animation_pane.controls.append(
                    ft.TextField(
                        label="Duration (s)",
                        value=str(
                            selected_element.get(
                                "duration_in", selected_element.get("duration", "")
                            )
                        ),
                        expand=True,
                        on_change=lambda e: self._update_selected_element_property(
                            e, "duration_in"
                        ),
                        tooltip="e.g., 0.5",
                        color=Color.DEFAULT_TEXT,
                        input_filter=float_filter
                    )
                )
                self.animation_pane.controls.append(ft.Divider())
                self.animation_pane.controls.append(
                    Text.MEDIUM(
                        "Exit Animation",
                        weight=ft.FontWeight.BOLD,
                        color=Color.PRIMARY_TEXT
                    )
                )
                self.animation_pane.controls.append(
                    ft.Dropdown(
                        label="Exit Effect",
                        value=EXIT_EFFECTS.get(selected_element.get("exit", 0), "None"),
                        on_select=lambda e: self._update_selected_element_property(
                            e, "exit", rebuild_ui=True, value_map=EXIT_IDS
                        ),
                        options=[ft.dropdown.Option(x) for x in EXIT_EFFECTS.values()],
                        color=Color.DEFAULT_TEXT
                    )
                )
                self.animation_pane.controls.append(
                    ft.TextField(
                        label="Duration (s)",
                        value=str(
                            selected_element.get(
                                "duration_out", selected_element.get("duration", "")
                            )
                        ),
                        expand=True,
                        on_change=lambda e: self._update_selected_element_property(
                            e, "duration_out"
                        ),
                        tooltip="e.g., 0.5",
                        color=Color.DEFAULT_TEXT,
                        input_filter=float_filter
                    )
                )

        # Properties Pane
        if (
            selected_element_index is None
            or not elements
            or elements[selected_element_index].get("type") == "audio"
        ):
            self.element_properties.controls.append(
                Text.MEDIUM(
                    "Select a visual element to edit properties.",
                    color=Color.SECONDARY_TEXT
                )
            )
            return

        selected_element = elements[selected_element_index]
        self.element_properties.controls.append(
            Text.MEDIUM(
                "Element Properties",
                weight=ft.FontWeight.BOLD,
                color=Color.PRIMARY_TEXT
            )
        )
        if selected_element["type"] == "text":
            self.element_properties.controls.append(
                ft.TextField(
                    label="Text",
                    multiline=True,
                    value=selected_element.get("content", ""),
                    on_change=lambda e: self._update_selected_element_property(
                        e, "content", needs_canvas_update=True
                    ),
                    color=Color.DEFAULT_TEXT
                )
            )
            self.element_properties.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="Width (px)",
                            value=str(
                                selected_element.get("width", DEFAULT_ELEMENT_WIDTH)
                            ),
                            on_change=lambda e: self._update_selected_element_property(
                                e, "width", needs_canvas_update=True
                            ),
                            color=Color.DEFAULT_TEXT,
                            input_filter=float_filter,
                            expand=True
                        ),
                        ft.TextField(
                            label="Font Size",
                            value=str(selected_element.get("size", DEFAULT_TEXT_SIZE)),
                            on_change=lambda e: self._update_selected_element_property(
                                e, "size", needs_canvas_update=True
                            ),
                            color=Color.DEFAULT_TEXT,
                            input_filter=float_filter,
                            expand=True
                        )
                    ]
                )
            )
        elif selected_element["type"] == "divider":
            self.element_properties.controls.append(
                ft.TextField(
                    label="Width (px)",
                    value=str(selected_element.get("width", DEFAULT_ELEMENT_WIDTH)),
                    on_change=lambda e: self._update_selected_element_property(
                        e, "width", needs_canvas_update=True
                    ),
                    color=Color.DEFAULT_TEXT,
                    input_filter=float_filter
                )
            )
        else:
            path_tf = ft.TextField(
                label="Image Path",
                expand=True,
                value=selected_element.get("content", ""),
                on_change=lambda e: self._update_selected_element_property(
                    e, "content", needs_canvas_update=True
                ),
                color=Color.DEFAULT_TEXT
            )
            self.element_properties.controls.append(
                ft.Row(
                    [
                        path_tf,
                        ft.IconButton(
                            icon=ft.Icons.FOLDER_OPEN,
                            tooltip="Browse Computer",
                            icon_color=Color.SECONDARY_TEXT,
                            on_click=lambda e: self._page.run_task(
                                self.pick_image, e, path_tf, "content"
                            )
                        )
                    ]
                )
            )

    def render_sidebar(self) -> None:
        self.sidebar_column.controls.clear()
        for i, slide in enumerate(self.logic.slides_data):
            is_selected = i == self.logic.current_slide_index
            item = ft.Container(
                content=Text.MEDIUM(
                    f"Slide {i + 1}",
                    weight=ft.FontWeight.BOLD,
                    color=Color.NAVIGATION_ACTIVE_TEXT
                    if is_selected
                    else Color.DEFAULT_TEXT
                ),
                padding=10,
                bgcolor=Color.NAVIGATION_ACTIVE_BACKGROUND
                if is_selected
                else Color.CARD_BACKGROUND,
                border=ft.Border.all(2, Color.NAVIGATION_ACTIVE_ICON)
                if is_selected
                else ft.Border.all(1, Color.INPUT_BORDER),
                border_radius=8,
                ink=True,
                on_click=lambda e, idx=i: self.select_slide(idx)
            )
            self.sidebar_column.controls.append(item)

    def select_slide(self, slide_index: int) -> None:
        self.logic.current_slide_index = slide_index
        self.logic.selected_element_index = None
        self.properties_tabs.selected_index = 0
        self.refresh_editor()

    def add_element_handler(self, element_type: str) -> None:
        self.logic.add_element(element_type)
        self.properties_tabs.selected_index = 2 if element_type == "audio" else 0
        self.refresh_editor()

    def delete_element_handler(self, element_index: int) -> None:
        self.logic.delete_element_by_index(element_index)
        self.refresh_editor()

    def add_slide_handler(self, e: ft.ControlEvent) -> None:
        self.logic.add_slide()
        self.refresh_editor()

    def delete_slide_handler(self, e: ft.ControlEvent) -> None:
        if self.logic.delete_slide():
            self.refresh_editor()

    def move_slide_up_handler(self, e: ft.ControlEvent) -> None:
        self.logic.move_slide_up()
        self.refresh_editor()

    def move_slide_down_handler(self, e: ft.ControlEvent) -> None:
        self.logic.move_slide_down()
        self.refresh_editor()

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
            # Get page size
            page_width, page_height = get_safe_page_size(page=self._page)

            menu_resize_values: MenuResizeValues = get_menu_resize_values(
                page_width, self.menu
            )
            self.menu.resize(
                width=page_width,
                **menu_resize_values
            )
            self.main_container.margin.bottom = self.menu.reserved_height

            available_height = int(page_height * AVAILABLE_PAGE_HEIGHT_RATIO)
            content_width = scale_width(page_width, PAGE_CONTENT_DESIGN_WIDTH)
            canvas_height = int(available_height * EDITOR_CANVAS_HEIGHT_RATIO)
            self.editor_layout.height = available_height
            self.editor_layout.width = page_width
            self.slide_sidebar.resize(
                content_width,
                scale_width(page_width, SIDEBAR_CONTENT_DESIGN_WIDTH)
            )
            self.center_panel.width = content_width
            editor_content_width = scale_width(page_width, EDITOR_CONTENT_DESIGN_WIDTH)
            self.center_editor.width = editor_content_width
            self.toolbar.resize(editor_content_width)
            self.properties_panel.width = content_width
            self.properties_tabs.resize(
                scale_width(page_width, SIDEBAR_CONTENT_DESIGN_WIDTH)
            )
            self.canvas_container.width = editor_content_width
            self.canvas_container.height = canvas_height

            return 0

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")
            return 1

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")
            return 2
        else:
            return 0

def get_lesson_editor_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Lesson Editor page...")
    return LessonEditorView(page, lang, user_info)
