# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Lesson Player page - Play and take financial lessons."""

from src.pages.lesson_player.components import LessonControls, LessonHeader, PresentationBoard, SlideCanvas, TopNavigationMenu
from src.pages.lesson_player.logic import ENTRANCE_EFFECTS, EXIT_EFFECTS, AnimationController, AudioController, LogicController, generate_timeline
from src.pages.lesson_player.view import LessonPlayerView, get_lesson_player_view

__all__ = [
    "TopNavigationMenu",
    "SlideCanvas",
    "LessonHeader",
    "LessonControls",
    "PresentationBoard",
    "ENTRANCE_EFFECTS",
    "EXIT_EFFECTS",
    "generate_timeline",
    "AudioController",
    "LogicController",
    "AnimationController",
    "LessonPlayerView",
    "get_lesson_player_view",
]