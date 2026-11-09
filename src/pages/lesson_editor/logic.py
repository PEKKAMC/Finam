# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import copy
from typing import Any

CANVAS_DESIGN_WIDTH = 550.0
CANVAS_DESIGN_HEIGHT = 850.0
CANVAS_ELEMENT_MARGIN = 20.0
DEFAULT_ELEMENT_POSITION = 50.0
DEFAULT_ELEMENT_WIDTH = 300.0
DEFAULT_ELEMENT_HEIGHT = 100.0
DEFAULT_TEXT_ELEMENT_HEIGHT = 50.0
DEFAULT_ELEMENT_SCALE = 1.0
DEFAULT_TEXT_SIZE = 16.0
LOADED_ELEMENT_VERTICAL_SPACING = 60.0

ENTRANCE_EFFECTS = {0: "None", 1: "Appear", 2: "Wipe", 3: "Fly in", 4: "Strips"}
EXIT_EFFECTS = {
    0: "None",
    1: "Disappear",
    2: "Dissolve out",
    3: "Peek out",
    4: "Blinds",
}
ENTRANCE_IDS = {v: k for k, v in ENTRANCE_EFFECTS.items()}
EXIT_IDS = {v: k for k, v in EXIT_EFFECTS.items()}


ElementData = dict[str, Any]
SlideData = dict[str, list[ElementData]]


def safe_float(value: object, default: float = 0.0) -> float:
    if not isinstance(value, (str, int, float)) or value == "":
        return float(default)
    try:
        return float(value)
    except ValueError:
        return float(default)


def calculate_pan_position(element: ElementData, delta_x: float, delta_y: float) -> tuple[float, float]:
    current_x = safe_float(element.get("x"), DEFAULT_ELEMENT_POSITION)
    current_y = safe_float(element.get("y"), DEFAULT_ELEMENT_POSITION)

    if element.get("type") in {"text", "divider"}:
        element_width = safe_float(element.get("width"), DEFAULT_ELEMENT_WIDTH)
        element_height = DEFAULT_TEXT_ELEMENT_HEIGHT
    else:
        scale = safe_float(element.get("scale"), DEFAULT_ELEMENT_SCALE)
        element_width = DEFAULT_ELEMENT_WIDTH * scale
        element_height = DEFAULT_ELEMENT_HEIGHT * scale

    margin = CANVAS_ELEMENT_MARGIN

    min_x = -(element_width - margin)
    max_x = CANVAS_DESIGN_WIDTH - margin
    min_y = -(element_height - margin)
    max_y = CANVAS_DESIGN_HEIGHT - margin

    new_x = max(min_x, min(max_x, current_x + delta_x))
    new_y = max(min_y, min(max_y, current_y + delta_y))

    return new_x, new_y


class LogicController:
    def __init__(self) -> None:
        self.slides_data: list[SlideData] = [{"elements": []}]
        self.current_slide_index = 0
        self.selected_element_index: int | None = None

    def elements_list(self) -> list[ElementData]:
        return self.slides_data[self.current_slide_index].get("elements", [])

    def add_element(self, element_type: str) -> ElementData:
        if element_type == "audio":
            new_element = {"type": "audio", "content": "", "timer_in": ""}
        else:
            new_element = {
                "type": element_type,
                "content": "",
                "x": DEFAULT_ELEMENT_POSITION,
                "y": DEFAULT_ELEMENT_POSITION,
                "timer_in": "",
                "timer_out": "",
                "entrance": 0,
                "duration_in": "",
                "exit": 0,
                "duration_out": "",
            }
            if element_type in {"text", "divider"}:
                new_element["width"] = DEFAULT_ELEMENT_WIDTH
                if element_type == "text":
                    new_element["size"] = DEFAULT_TEXT_SIZE
            else:
                new_element["scale"] = DEFAULT_ELEMENT_SCALE

        self.slides_data[self.current_slide_index]["elements"].append(new_element)
        self.selected_element_index = (
            len(self.slides_data[self.current_slide_index]["elements"]) - 1
        )
        return new_element

    def delete_element_by_index(self, element_index: int) -> None:
        elements = self.elements_list()
        if 0 <= element_index < len(elements):
            elements.pop(element_index)
            if self.selected_element_index == element_index:
                self.selected_element_index = None
            elif (
                self.selected_element_index is not None
                and self.selected_element_index > element_index
            ):
                self.selected_element_index -= 1

    def add_slide(self) -> None:
        self.slides_data.insert(self.current_slide_index + 1, {"elements": []})
        self.current_slide_index += 1
        self.selected_element_index = None

    def delete_slide(self) -> bool:
        if len(self.slides_data) > 1:
            self.slides_data.pop(self.current_slide_index)
            if self.current_slide_index >= len(self.slides_data):
                self.current_slide_index = len(self.slides_data) - 1
            self.selected_element_index = None
            return True
        return False

    def move_slide_up(self) -> None:
        if self.current_slide_index > 0:
            (
                self.slides_data[self.current_slide_index],
                self.slides_data[self.current_slide_index - 1],
            ) = (
                self.slides_data[self.current_slide_index - 1],
                self.slides_data[self.current_slide_index],
            )
            self.current_slide_index -= 1
            self.selected_element_index = None

    def move_slide_down(self) -> None:
        if self.current_slide_index < len(self.slides_data) - 1:
            (
                self.slides_data[self.current_slide_index],
                self.slides_data[self.current_slide_index + 1],
            ) = (
                self.slides_data[self.current_slide_index + 1],
                self.slides_data[self.current_slide_index],
            )
            self.current_slide_index += 1
            self.selected_element_index = None

    def move_layer(self, direction: str) -> bool:
        selected_element_index = self.selected_element_index
        if selected_element_index is None:
            return False
        elements = self.elements_list()

        if direction == "forward" and selected_element_index < len(elements) - 1:
            next_index = selected_element_index + 1
            elements[selected_element_index], elements[next_index] = (
                elements[next_index],
                elements[selected_element_index],
            )
            self.selected_element_index = next_index
            return True
        if direction == "backward" and selected_element_index > 0:
            previous_index = selected_element_index - 1
            elements[selected_element_index], elements[previous_index] = (
                elements[previous_index],
                elements[selected_element_index],
            )
            self.selected_element_index = previous_index
            return True
        return False

    def get_save_data(self, lesson_id: int, title: str, subtitle: str, cover_image: str) -> dict[str, Any]:
        saved_content = copy.deepcopy(self.slides_data)
        for slide in saved_content:
            for element in slide.get("elements", []):
                if element.get("type") == "audio":
                    for key in [
                        "x",
                        "y",
                        "width",
                        "scale",
                        "entrance",
                        "exit",
                        "duration_in",
                        "duration_out",
                    ]:
                        element.pop(key, None)
        return {
            "lesson_id": lesson_id,
            "title": title,
            "subtitle": subtitle,
            "cover_image": cover_image,
            "content": saved_content,
        }

    def process_loaded_data(self, data: dict[str, Any]) -> None:
        self.slides_data.clear()
        for item in data.get("content", []):
            if isinstance(item, str):
                self.slides_data.append(
                    {
                        "elements": [
                            {
                                "type": "text",
                                "content": item,
                                "x": DEFAULT_ELEMENT_POSITION,
                                "y": DEFAULT_ELEMENT_POSITION,
                                "entrance": 0,
                                "exit": 0,
                                "width": DEFAULT_ELEMENT_WIDTH,
                            }
                        ]
                    }
                )
            elif "elements" in item:
                for element_position, element in enumerate(item["elements"]):
                    if element.get("type") == "audio":
                        for key in ["x", "y", "width", "scale", "entrance", "exit"]:
                            element.pop(key, None)
                    else:
                        element.setdefault("x", DEFAULT_ELEMENT_POSITION)
                        element.setdefault(
                            "y",
                            DEFAULT_ELEMENT_POSITION
                            + element_position * LOADED_ELEMENT_VERTICAL_SPACING,
                        )
                        if element.get("type") in {"text", "divider"}:
                            element.setdefault("width", DEFAULT_ELEMENT_WIDTH)
                        else:
                            element.setdefault("scale", DEFAULT_ELEMENT_SCALE)
                            element.pop("width", None)
                self.slides_data.append(item)

        if not self.slides_data:
            self.slides_data.append({"elements": []})

        self.current_slide_index = 0
        self.selected_element_index = None
