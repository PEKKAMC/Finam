# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import copy

ENTRANCE_EFFECTS = {0: "None", 1: "Appear", 2: "Wipe", 3: "Fly in", 4: "Strips"}
EXIT_EFFECTS = {0: "None", 1: "Disappear", 2: "Dissolve out", 3: "Peek out", 4: "Blinds"}
ENTRANCE_IDS = {v: k for k, v in ENTRANCE_EFFECTS.items()}
EXIT_IDS = {v: k for k, v in EXIT_EFFECTS.items()}

def safe_float(val, default=0.0) -> float:
    try:
        return float(val) if val != "" else default
    except (ValueError, TypeError):
        return float(default)

def calculate_pan_position(el: dict, delta_x: float, delta_y: float) -> tuple[float, float]:
    current_x = safe_float(el.get("x"), 50.0)
    current_y = safe_float(el.get("y"), 50.0)

    if el.get("type") in ["text", "divider"]:
        el_width = safe_float(el.get("width"), 300.0)
        el_height = 50.0
    else:
        scale = safe_float(el.get("scale"), 1.0)
        el_width = 300.0 * scale
        el_height = 100.0 * scale

    margin = 20.0
    canvas_width, canvas_height = 550.0, 850.0

    min_x = -(el_width - margin)
    max_x = canvas_width - margin
    min_y = -(el_height - margin)
    max_y = canvas_height - margin

    new_x = max(min_x, min(max_x, current_x + delta_x))
    new_y = max(min_y, min(max_y, current_y + delta_y))

    return new_x, new_y

class EditorLogicController:
    def __init__(self):
        self.slides_data = [{"elements": []}]
        self.current_slide_index = 0
        self.selected_element_index = None

    def elements_list(self) -> list:
        return self.slides_data[self.current_slide_index].get("elements", [])

    def add_element(self, el_type: str) -> dict:
        if el_type == "audio":
            new_el = {"type": "audio", "content": "", "timer_in": ""}
        else:
            new_el = {
                "type": el_type, "content": "", "x": 50.0, "y": 50.0,
                "timer_in": "", "timer_out": "",
                "entrance": 0, "duration_in": "",
                "exit": 0, "duration_out": ""
            }
            if el_type in ["text", "divider"]:
                new_el["width"] = 300.0
                if el_type == "text":
                    new_el["size"] = 16.0
            else:
                new_el["scale"] = 1.0

        self.slides_data[self.current_slide_index]["elements"].append(new_el)
        self.selected_element_index = len(self.slides_data[self.current_slide_index]["elements"]) - 1
        return new_el

    def delete_element_by_index(self, idx: int):
        elements = self.elements_list()
        if idx is not None and 0 <= idx < len(elements):
            elements.pop(idx)
            if self.selected_element_index == idx:
                self.selected_element_index = None
            elif self.selected_element_index is not None and self.selected_element_index > idx:
                self.selected_element_index -= 1

    def add_slide(self):
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

    def move_slide_up(self):
        if self.current_slide_index > 0:
            self.slides_data[self.current_slide_index], self.slides_data[self.current_slide_index - 1] = \
                self.slides_data[self.current_slide_index - 1], self.slides_data[self.current_slide_index]
            self.current_slide_index -= 1
            self.selected_element_index = None

    def move_slide_down(self):
        if self.current_slide_index < len(self.slides_data) - 1:
            self.slides_data[self.current_slide_index], self.slides_data[self.current_slide_index + 1] = \
                self.slides_data[self.current_slide_index + 1], self.slides_data[self.current_slide_index]
            self.current_slide_index += 1
            self.selected_element_index = None

    def move_layer(self, direction: str) -> bool:
        idx = self.selected_element_index
        if idx is None: return False
        elements = self.elements_list()

        if direction == "forward" and idx < len(elements) - 1:
            elements[idx], elements[idx + 1] = elements[idx + 1], elements[idx]
            self.selected_element_index = idx + 1
            return True
        elif direction == "backward" and idx > 0:
            elements[idx], elements[idx - 1] = elements[idx - 1], elements[idx]
            self.selected_element_index = idx - 1
            return True
        return False

    def get_save_data(self, lesson_id: int, title: str, subtitle: str, cover_image: str) -> dict:
        saved_content = copy.deepcopy(self.slides_data)
        for slide in saved_content:
            for el in slide.get("elements", []):
                if el.get("type") == "audio":
                    for key in ["x", "y", "width", "scale", "entrance", "exit", "duration_in", "duration_out"]:
                        el.pop(key, None)
        return {
            "lesson_id": lesson_id, "title": title, "subtitle": subtitle,
            "cover_image": cover_image, "content": saved_content
        }

    def process_loaded_data(self, data: dict):
        self.slides_data.clear()
        for item in data.get("content", []):
            if isinstance(item, str):
                self.slides_data.append({"elements": [
                    {"type": "text", "content": item, "x": 50.0, "y": 50.0, "entrance": 0, "exit": 0, "width": 300.0}
                ]})
            elif "elements" in item:
                for i, el in enumerate(item["elements"]):
                    if el.get("type") == "audio":
                        for key in ["x", "y", "width", "scale", "entrance", "exit"]:
                            el.pop(key, None)
                    else:
                        if "x" not in el: el["x"] = 50.0
                        if "y" not in el: el["y"] = 50.0 + (i * 60)
                        if el.get("type") in ["text", "divider"]:
                            if "width" not in el: el["width"] = 300.0
                        else:
                            if "scale" not in el: el["scale"] = 1.0
                            if "width" in el: del el["width"]
                self.slides_data.append(item)

        if not self.slides_data:
            self.slides_data.append({"elements": []})

        self.current_slide_index = 0
        self.selected_element_index = None