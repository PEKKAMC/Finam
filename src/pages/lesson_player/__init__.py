# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Lesson Player page - Play and take financial lessons."""

from src.pages.lesson_player.components import (
    LessonControls,
    LessonHeader,
    PresentationBoard,
    SlideCanvas,
    TopNavigationMenu,
)
from src.pages.lesson_player.logic import (
    ENTRANCE_EFFECTS,
    EXIT_EFFECTS,
    AnimationController,
    AudioController,
    LogicController,
    generate_timeline,
)
from src.pages.lesson_player.view import LessonPlayerView, get_lesson_player_view

__all__ = [
    "ENTRANCE_EFFECTS",
    "EXIT_EFFECTS",
    "AnimationController",
    "AudioController",
    "LessonControls",
    "LessonHeader",
    "LessonPlayerView",
    "LogicController",
    "PresentationBoard",
    "SlideCanvas",
    "TopNavigationMenu",
    "generate_timeline",
    "get_lesson_player_view",
]
