# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
import os

from src.logger import Logger
from src.utils import get_asset_path

class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    @staticmethod
    def get_user_statistics() -> dict:
        return {
            "completion_percentage": 0,
            "completion_decimal": 0,
            "learning_hours": 0,
            "certificates_earned": 0
        }

    @staticmethod
    def load_available_lessons() -> list:
        loaded_lessons = []
        lessons_directory = get_asset_path("lessons")

        if os.path.exists(lessons_directory):
            for filename in sorted(os.listdir(lessons_directory)):
                if filename.endswith(".json"):
                    file_path = os.path.join(lessons_directory, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            lesson_data = json.load(file)
                            loaded_lessons.append({
                                "id": lesson_data.get("lesson_id", 999),
                                "title": lesson_data.get("title", filename),
                                "subtitle": lesson_data.get("subtitle", ""),
                                "cover_image": lesson_data.get("cover_image", ""),
                                "route": f"/lesson-player/{filename}",
                                "is_completed": False
                            })
                    except Exception as error:
                        Logger.error(f"Failed to load lesson {filename}: {error}")

        loaded_lessons.sort(key=lambda lesson: lesson["id"])
        return loaded_lessons