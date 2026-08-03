# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


import asyncio
import json
import os
import re
import time

import flet as ft
import flet_audio as fta

from src.logger import Logger

ENTRANCE_EFFECTS = {0: "None", 1: "Appear", 2: "Wipe", 3: "Fly in", 4: "Strips"}
EXIT_EFFECTS = {0: "None", 1: "Disappear", 2: "Dissolve out", 3: "Peek out", 4: "Blinds"}

def generate_timeline(segment_length: int, segment_duration: float, frames_per_second: float):
    if segment_duration <= 0.0:
        return [{"sleep_time": 0.0, "characters_to_show": segment_length}]

    frame_duration = 1.0 / frames_per_second
    output_frames = []
    elapsed_time = 0.0

    while elapsed_time < segment_duration:
        progress = elapsed_time / segment_duration
        output_frames.append({
            "sleep_time": frame_duration,
            "characters_to_show": int(progress * segment_length)
        })
        elapsed_time += frame_duration

    output_frames.append({
        "sleep_time": 0.0,
        "characters_to_show": segment_length
    })

    return output_frames

class AudioController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.active_audio = None

    async def play(self, audio_source_path: str):
        if self.active_audio:
            old_audio = self.active_audio
            if old_audio in self.page.services:
                self.page.services.remove(old_audio)
                self.page.run_task(self._safe_pause_task, old_audio)

        flet_src = audio_source_path
        if "assets" in flet_src:
            parts = flet_src.split("assets", 1)
            flet_src = parts[1].replace("\\", "/")
            if not flet_src.startswith("/"):
                flet_src = "/" + flet_src

        self.active_audio = fta.Audio(src=flet_src, autoplay=True)
        self.page.services.append(self.active_audio)
        self.page.update()
        self.page.run_task(self._safe_play_task, self.active_audio)

    @staticmethod
    async def _safe_play_task(audio_control):
        try:
            await asyncio.wait_for(audio_control.play(), timeout=1.0)
        except Exception as e:
            Logger.debug(f"Audio play failed: {e}")

    @staticmethod
    async def _safe_pause_task(audio_control):
        try:
            await asyncio.wait_for(audio_control.pause(), timeout=0.5)
        except Exception as e:
            Logger.debug(f"Audio pause failed: {e}")

    async def pause(self):
        if self.active_audio:
            self.page.run_task(self._safe_pause_task, self.active_audio)


class LogicController:
    def __init__(self, target_lesson_filename: str = ""):
        self.target_lesson_filename = target_lesson_filename
        self.slides_data_list = []
        self.current_slide_index = 0
        self.lesson_title = "Untitled Lesson"

    def load_lesson_data(self, filepath: str) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                parsed_data = json.load(file)
                self.lesson_title = parsed_data.get("title", "Untitled Lesson")
                raw_content = parsed_data.get("content", [])
                self.slides_data_list = []

                for item in raw_content:
                    if isinstance(item, str):
                        self.slides_data_list.append(
                            {"elements": [
                                {"type": "text", "content": item, "x": 50, "y": 50, "width": 300, "entrance": 0, "exit": 0}
                            ]}
                        )
                    elif "elements" in item:
                        self.slides_data_list.append(item)

                self.current_slide_index = 0
                return len(self.slides_data_list) > 0
        except Exception as error:
            Logger.error(f"Failed to load lesson: {error}")
            return False

    def get_current_slide_elements(self) -> list:
        if not self.slides_data_list or self.current_slide_index >= len(self.slides_data_list):
            return []
        return self.slides_data_list[self.current_slide_index].get("elements", [])

    def get_total_slides(self) -> int:
        return len(self.slides_data_list)

    def has_next_slide(self) -> bool:
        return self.current_slide_index < len(self.slides_data_list) - 1

    def has_previous_slide(self) -> bool:
        return self.current_slide_index > 0

    def move_to_next_slide(self):
        if self.has_next_slide():
            self.current_slide_index += 1

    def move_to_previous_slide(self):
        if self.has_previous_slide():
            self.current_slide_index -= 1


class AnimationController:
    def __init__(self, page: ft.Page, audio_controller: AudioController):
        self.page = page
        self.audio_controller = audio_controller
        self.active_sequence_identifier = 0

    def start_new_sequence(self):
        self.active_sequence_identifier += 1
        return self.active_sequence_identifier

    def get_current_sequence(self):
        return self.active_sequence_identifier

    @staticmethod
    def safe_convert_to_float(value, default_value=0.0) -> float:
        try:
            return float(value) if value != "" else default_value
        except (ValueError, TypeError):
            return float(default_value)

    @staticmethod
    def get_animation_duration(element_data: dict, duration_key: str, default_seconds: float = 0.5) -> int:
        duration_value = element_data.get(duration_key, "")
        if not duration_value:
            duration_value = element_data.get("duration", "")
            if not duration_value:
                animation_speed = element_data.get("speed", "Normal")
                if animation_speed == "Fast": return 300
                if animation_speed == "Slow": return 1200
                return int(default_seconds * 1000)
        try:
            milliseconds = int(float(duration_value) * 1000)
            return max(milliseconds, 10)
        except ValueError:
            return int(default_seconds * 1000)

    async def interruptible_sleep(self, duration_seconds: float, sequence_identifier: int) -> bool:
        if duration_seconds <= 0:
            return self.active_sequence_identifier == sequence_identifier

        time_chunks = int(duration_seconds / 0.05)
        for _ in range(time_chunks):
            if self.active_sequence_identifier != sequence_identifier: return False
            await asyncio.sleep(0.05)

        if self.active_sequence_identifier != sequence_identifier: return False
        await asyncio.sleep(duration_seconds % 0.05)
        return self.active_sequence_identifier == sequence_identifier

    async def execute_element_animation(self, interface_item: dict, sequence_identifier: int):
        def safe_page_update(control_element):
            try:
                if self.active_sequence_identifier == sequence_identifier and control_element and control_element.page:
                    control_element.update()
            except Exception as e:
                Logger.debug(f"Page update skipped: {e}")

        if self.active_sequence_identifier != sequence_identifier: return

        element_data = interface_item["data"]
        animation_start_time = time.time()

        if element_data.get("timer_in"):
            try:
                timer_in_seconds = float(element_data["timer_in"])
                if not await self.interruptible_sleep(timer_in_seconds, sequence_identifier): return
            except ValueError:
                pass

        if self.active_sequence_identifier != sequence_identifier: return

        if element_data.get("type") == "audio":
            audio_source_path = element_data.get("content", "").strip()
            if audio_source_path:
                resolved_path = audio_source_path
                if not os.path.isabs(resolved_path):
                    current_directory = os.path.dirname(__file__)
                    project_root = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
                    possible_paths = [
                        os.path.join(os.getcwd(), audio_source_path),
                        os.path.join(project_root, audio_source_path),
                        os.path.join(project_root, "assets", "lessons", audio_source_path)
                    ]
                    for path_option in possible_paths:
                        if os.path.isfile(path_option):
                            resolved_path = path_option
                            break

                if os.path.isfile(resolved_path) or audio_source_path.startswith("http"):
                    await self.audio_controller.play(resolved_path)
                else:
                    Logger.error(f"Audio asset missing: {audio_source_path}")
            return

        animation_container = interface_item["container"]
        visual_control = interface_item["control"]
        target_width = interface_item["target_width"]
        is_text_element = interface_item["is_text"]

        entrance_effect = ENTRANCE_EFFECTS.get(element_data.get("entrance", 0), "None")
        exit_effect = EXIT_EFFECTS.get(element_data.get("exit", 0), "None")

        if entrance_effect == "Appear":
            entrance_duration_milliseconds = 0
            entrance_animation_object = None
        else:
            entrance_duration_milliseconds = self.get_animation_duration(element_data, "duration_in", 0.6)
            entrance_animation_object = ft.Animation(entrance_duration_milliseconds, ft.AnimationCurve.DECELERATE)

        duration_in_seconds = entrance_duration_milliseconds / 1000.0
        animation_container.animate_opacity = entrance_animation_object
        animation_container.animate_offset = entrance_animation_object
        animation_container.animate_scale = entrance_animation_object

        if entrance_effect == "Wipe":
            if is_text_element:
                raw_text_content = interface_item.get("full_text", "")
                text_segments = re.split(r'(\{pause:[\d.]+})', raw_text_content)

                clean_text_length = len(re.sub(r'\{pause:[\d.]+}', '', raw_text_content))
                current_displayed_text = ""

                for text_segment in text_segments:
                    if not text_segment: continue
                    if self.active_sequence_identifier != sequence_identifier: return

                    pause_match_result = re.match(r'\{pause:([\d.]+)}', text_segment)

                    if pause_match_result:
                        pause_duration_seconds = float(pause_match_result.group(1))
                        if not await self.interruptible_sleep(pause_duration_seconds, sequence_identifier):
                            return
                    else:
                        segment_character_length = len(text_segment)
                        segment_duration_seconds = duration_in_seconds * (segment_character_length / clean_text_length) if clean_text_length > 0 else 0
                        frames_per_second = 30.0
                        animation_frames = generate_timeline(segment_character_length, segment_duration_seconds, frames_per_second)

                        for frame_data in animation_frames:
                            if self.active_sequence_identifier != sequence_identifier: return

                            visual_control.value = current_displayed_text + text_segment[:frame_data["characters_to_show"]]
                            safe_page_update(visual_control)

                            if frame_data["sleep_time"] > 0:
                                if not await self.interruptible_sleep(frame_data["sleep_time"], sequence_identifier): return

                        current_displayed_text += text_segment
                        visual_control.value = current_displayed_text
                        safe_page_update(visual_control)
            else:
                visual_control.width = target_width
                safe_page_update(visual_control)
                if not await self.interruptible_sleep(duration_in_seconds, sequence_identifier): return

        elif entrance_effect != "None":
            animation_container.opacity = 1
            animation_container.offset = ft.Offset(0, 0)
            animation_container.scale = ft.Scale(1, 1)
            safe_page_update(animation_container)
            if not await self.interruptible_sleep(duration_in_seconds, sequence_identifier): return

        if element_data.get("timer_out") and exit_effect != "None":
            try:
                remaining_sleep_seconds = float(element_data["timer_out"]) - (time.time() - animation_start_time)

                if remaining_sleep_seconds > 0:
                    if not await self.interruptible_sleep(remaining_sleep_seconds, sequence_identifier): return

                default_exit_duration_seconds = 0.01 if exit_effect == "Disappear" else 0.6
                exit_duration_milliseconds = self.get_animation_duration(element_data, "duration_out", default_exit_duration_seconds)

                exit_animation_object = ft.Animation(exit_duration_milliseconds, ft.AnimationCurve.EASE_IN_OUT)
                animation_container.animate_opacity = exit_animation_object
                animation_container.animate_offset = exit_animation_object
                animation_container.animate_scale = exit_animation_object
                safe_page_update(animation_container)

                if exit_effect in ["Disappear", "Dissolve out"]:
                    animation_container.opacity = 0
                elif exit_effect == "Peek out":
                    animation_container.offset = ft.Offset(0, 1.5)
                    animation_container.opacity = 0
                elif exit_effect == "Blinds":
                    animation_container.scale = ft.Scale(1, 0.001)

                safe_page_update(animation_container)
            except ValueError:
                pass

    async def execute_all_animations(self, user_interface_elements: list, sequence_identifier: int):
        await asyncio.sleep(0.05)
        if self.active_sequence_identifier != sequence_identifier: return
        for interface_item in user_interface_elements:
            self.page.run_task(self.execute_element_animation, interface_item, sequence_identifier)