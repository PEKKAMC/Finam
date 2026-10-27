# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class ThemeName(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class _ColorMeta(type):
    def __getattr__(cls, name: str) -> str:
        if cls is not Color or name.startswith("__"):
            raise AttributeError(f"{cls.__name__} has no color {name!r}")
        return ThemeManager.get_color(name)

    def __instancecheck__(cls, instance: object) -> bool:
        return isinstance(instance, str) and instance in ThemeManager.get_theme().colors.values()


class Color(metaclass=_ColorMeta):
    """Names of all semantic colors, with values supplied by the active theme."""

    # BASE COLORS
    WHITE: str = "#FFFFFF"
    BLACK: str = "#000000"
    TRANSPARENT: str = "transparent"

    # PIE CHART COLORS
    PIE_CHART_RED: str = "#FF0000"
    PIE_CHART_BLUE: str = "#0000FF"
    PIE_CHART_GREEN: str = "#00FF00"
    PIE_CHART_YELLOW: str = "#FFFF00"
    PIE_CHART_TURQUOISE: str = "#00FFAA"
    PIE_CHART_PURPLE: str = "#AA00FF"

    # UI BACKGROUNDS
    PAGE_BACKGROUND: str
    NAVIGATION_BACKGROUND: str
    NAVIGATION_ACTIVE_BACKGROUND: str
    NAVIGATION_ACTIVE_TEXT: str
    NAVIGATION_ACTIVE_ICON: str
    INCOME_COLOR: str
    INCOME_BACKGROUND: str
    EXPENSE_COLOR: str
    EXPENSE_BACKGROUND: str
    WARNING_COLOR: str
    WARNING_BACKGROUND: str
    WARNING_TEXT: str
    SUCCESS_BACKGROUND: str
    CARD_BACKGROUND: str
    COMPLETED_BACKGROUND: str
    DIALOG_BACKGROUND: str
    AGGREGATE_BACKGROUND: str
    ON_TRACK_BACKGROUND: str
    ACTIVITY_BACKGROUND: str
    MENU_BACKGROUND: str
    DEFAULT_CONTAINER_BACKGROUND: str

    # BORDERS & SHADOWS
    INPUT_BORDER: str
    DEFAULT_BORDER: str
    COMPLETED_BORDER: str
    SHADOW: str

    # TEXT COLORS
    PRIMARY_TEXT: str
    SECONDARY_TEXT: str
    SUBTITLE_TEXT: str
    BODY_TEXT: str
    COMPLETED_TEXT: str
    AGGREGATE_TEXT: str
    BLAND_TEXT: str
    DEFAULT_TEXT: str
    ERROR_TEXT: str

    # ACTIONS & BUTTONS
    PRIMARY_ACTION: str
    NEGATIVE_ACTION: str
    COMPLETED_ACTION: str
    DELETE_ACTION: str
    DARK_BUTTON: str
    CONFIRM_BUTTON: str
    DEFAULT_BUTTON: str

    # PROGRESS BARS
    PROGRESS_ACTIVE: str
    PROGRESS_COMPLETED: str
    PROGRESS_BACKGROUND: str

    # ICONS
    MENU_ICON: str

    # LOGIN PAGE
    USER_TILE_BACKGROUND: str

    # HOME PAGE
    CHART_INCOME: str
    CHART_INACTIVE: str
    CHART_EXPENSE: str

    DARK_SURFACE: str
    PRIMARY: str
    LIGHT_ACCENT: str

    EXPENSE_ACTION_BACKGROUND: str
    EXPENSE_LABEL_TEXT: str
    EXPENSE_VALUE_TEXT: str

    SAVINGS_LABEL_TEXT: str
    SAVINGS_VALUE_TEXT: str

    LESSON_BANNER_BACKGROUND: str
    LESSON_ICON_BACKGROUND: str
    LESSON_ICON_COLOR: str

    GOAL_ITEM_BACKGROUND: str
    GOAL_ITEM_BORDER: str

    PROGRESS_TRACK_BACKGROUND: str
    GOAL_HEADER_ICON_BACKGROUND: str
    GOAL_HEADER_ICON_COLOR: str
    CARD_DIVIDER: str

    METRIC_PILL_BACKGROUND: str
    METRIC_PILL_BORDER: str
    SCAN_BUTTON_BORDER: str

    AI_ADVICE_BACKGROUND: str
    AI_ADVICE_BORDER: str


class LightTheme(Color):
    PAGE_BACKGROUND = "#F7FAF8"
    NAVIGATION_BACKGROUND = "#FFFFFF"
    NAVIGATION_ACTIVE_BACKGROUND = "#DAF1DE"
    NAVIGATION_ACTIVE_TEXT = "#212121"
    NAVIGATION_ACTIVE_ICON = "#1A4734"
    INCOME_COLOR = "#1A4734"
    INCOME_BACKGROUND = "#1A4734"
    EXPENSE_COLOR = "#E90C00"
    EXPENSE_BACKGROUND = "#E90C00"
    WARNING_COLOR = "#F59E0B"
    WARNING_BACKGROUND = "#FEF3C7"
    WARNING_TEXT = "#1F2937"
    SUCCESS_BACKGROUND = "#059669"
    CARD_BACKGROUND = "#FFFFFF"
    COMPLETED_BACKGROUND = "#E0E0E0"
    DIALOG_BACKGROUND = "#F8FAFC"
    AGGREGATE_BACKGROUND = "#F0F5EE"
    ON_TRACK_BACKGROUND = "#145C26"
    ACTIVITY_BACKGROUND = "#F3F5F1"
    MENU_BACKGROUND = "#FFFFFF"
    DEFAULT_CONTAINER_BACKGROUND = "#ECEFF1"
    INPUT_BORDER = "#E0E0E0"
    DEFAULT_BORDER = "#BDBDBD"
    COMPLETED_BORDER = "#9E9E9E"
    SHADOW = "#16000000"
    PRIMARY_TEXT = "#212121"
    SECONDARY_TEXT = "#757575"
    SUBTITLE_TEXT = "#9E9E9E"
    BODY_TEXT = "#424242"
    COMPLETED_TEXT = "#616161"
    AGGREGATE_TEXT = "#5A7A5D"
    BLAND_TEXT = "#9E9E9E"
    DEFAULT_TEXT = "#263238"
    ERROR_TEXT = "#FFEB3B"
    PRIMARY_ACTION = "#1D7333"
    NEGATIVE_ACTION = "#D32F2F"
    COMPLETED_ACTION = "#1976D2"
    DELETE_ACTION = "#E53935"
    DARK_BUTTON = "#1E293B"
    CONFIRM_BUTTON = "#004D40"
    DEFAULT_BUTTON = "#8C989E"
    PROGRESS_ACTIVE = "#2E7D32"
    PROGRESS_COMPLETED = "#42A5F5"
    PROGRESS_BACKGROUND = "#DCEDC8"
    MENU_ICON = "#008800"
    USER_TILE_BACKGROUND = "#F5F5F5"
    CHART_INCOME = "#4CAF50"
    CHART_INACTIVE = "#EEEEEE"
    CHART_EXPENSE = "#F44336"
    DARK_SURFACE = "#0B2B26"
    PRIMARY = "#1A4734"
    LIGHT_ACCENT = "#DAF1DE"
    EXPENSE_ACTION_BACKGROUND = "#E90C00"
    EXPENSE_LABEL_TEXT = "#FFC1C1"
    EXPENSE_VALUE_TEXT = "#FF8A8A"
    SAVINGS_LABEL_TEXT = "#FFE082"
    SAVINGS_VALUE_TEXT = "#FFD54F"
    LESSON_BANNER_BACKGROUND = "#0F172A"
    LESSON_ICON_BACKGROUND = "#DBEAFE"
    LESSON_ICON_COLOR = "#1E40AF"
    GOAL_ITEM_BACKGROUND = "#FAF5E8"
    GOAL_ITEM_BORDER = "#F3EFE0"
    PROGRESS_TRACK_BACKGROUND = "#E2E8F0"
    GOAL_HEADER_ICON_BACKGROUND = "#FEF3C7"
    GOAL_HEADER_ICON_COLOR = "#92400E"
    CARD_DIVIDER = "#F1F5F9"
    METRIC_PILL_BACKGROUND = "#14FFFFFF"
    METRIC_PILL_BORDER = "#1FFFFFFF"
    SCAN_BUTTON_BORDER = "#33FFFFFF"
    AI_ADVICE_BACKGROUND = "#E60B2B26"
    AI_ADVICE_BORDER = "#4D10B981"


class DarkTheme(Color):
    PAGE_BACKGROUND = "#0F172A"
    NAVIGATION_BACKGROUND = "#111827"
    NAVIGATION_ACTIVE_BACKGROUND = "#14532D"
    NAVIGATION_ACTIVE_TEXT = "#F0FDF4"
    NAVIGATION_ACTIVE_ICON = "#86EFAC"
    INCOME_COLOR = "#2A6734"
    INCOME_BACKGROUND = "#2A6734"
    EXPENSE_COLOR = "#C70A00"
    EXPENSE_BACKGROUND = "#C70A00"
    WARNING_COLOR = "#FBBF24"
    WARNING_BACKGROUND = "#78350F"
    WARNING_TEXT = "#FFFBEB"
    SUCCESS_BACKGROUND = "#065F46"
    CARD_BACKGROUND = "#1E293B"
    COMPLETED_BACKGROUND = "#334155"
    DIALOG_BACKGROUND = "#1E293B"
    AGGREGATE_BACKGROUND = "#1E3A32"
    ON_TRACK_BACKGROUND = "#145C26"
    ACTIVITY_BACKGROUND = "#1E293B"
    MENU_BACKGROUND = "#111827"
    DEFAULT_CONTAINER_BACKGROUND = "#1F2937"
    INPUT_BORDER = "#475569"
    DEFAULT_BORDER = "#64748B"
    COMPLETED_BORDER = "#64748B"
    SHADOW = "#66000000"
    PRIMARY_TEXT = "#F8FAFC"
    SECONDARY_TEXT = "#CBD5E1"
    SUBTITLE_TEXT = "#94A3B8"
    BODY_TEXT = "#E2E8F0"
    COMPLETED_TEXT = "#CBD5E1"
    AGGREGATE_TEXT = "#86EFAC"
    BLAND_TEXT = "#94A3B8"
    DEFAULT_TEXT = "#E2E8F0"
    ERROR_TEXT = "#FFEB3B"
    PRIMARY_ACTION = "#15803D"
    NEGATIVE_ACTION = "#D32F2F"
    COMPLETED_ACTION = "#60A5FA"
    DELETE_ACTION = "#E53935"
    DARK_BUTTON = "#334155"
    CONFIRM_BUTTON = "#047857"
    DEFAULT_BUTTON = "#8C989E"
    PROGRESS_ACTIVE = "#4ADE80"
    PROGRESS_COMPLETED = "#60A5FA"
    PROGRESS_BACKGROUND = "#334155"
    MENU_ICON = "#008800"
    USER_TILE_BACKGROUND = "#334155"
    CHART_INCOME = "#4CAF50"
    CHART_INACTIVE = "#334155"
    CHART_EXPENSE = "#F44336"
    DARK_SURFACE = "#0B2B26"
    PRIMARY = "#1A4734"
    LIGHT_ACCENT = "#BBF7D0"
    EXPENSE_ACTION_BACKGROUND = "#E90C00"
    EXPENSE_LABEL_TEXT = "#FFC1C1"
    EXPENSE_VALUE_TEXT = "#FF8A8A"
    SAVINGS_LABEL_TEXT = "#FFE082"
    SAVINGS_VALUE_TEXT = "#FFD54F"
    LESSON_BANNER_BACKGROUND = "#0F172A"
    LESSON_ICON_BACKGROUND = "#1E3A8A"
    LESSON_ICON_COLOR = "#BFDBFE"
    GOAL_ITEM_BACKGROUND = "#1E3A5F"
    GOAL_ITEM_BORDER = "#334E68"
    PROGRESS_TRACK_BACKGROUND = "#334155"
    GOAL_HEADER_ICON_BACKGROUND = "#1E3A5F"
    GOAL_HEADER_ICON_COLOR = "#93C5FD"
    CARD_DIVIDER = "#334155"
    METRIC_PILL_BACKGROUND = "#14FFFFFF"
    METRIC_PILL_BORDER = "#1FFFFFFF"
    SCAN_BUTTON_BORDER = "#33FFFFFF"
    AI_ADVICE_BACKGROUND = "#E60B2B26"
    AI_ADVICE_BORDER = "#4D10B981"


@dataclass(frozen=True)
class Theme:
    name: str
    colors: Mapping[str, str]
    dark_mode: bool

    @classmethod
    def from_color_class(
        cls,
        name: str,
        color_class: type[Color],
        dark_mode: bool,
    ) -> "Theme":
        available_colors = {
            member
            for base in color_class.__mro__
            for member in base.__dict__
        }
        missing_colors = set(Color.__annotations__).difference(available_colors)
        if missing_colors:
            raise ValueError(
                f"Theme {name!r} is missing colors: {', '.join(sorted(missing_colors))}"
            )
        return cls(
            name=name,
            colors=MappingProxyType({
                member: getattr(color_class, member)
                for member in Color.__annotations__
            }),
            dark_mode=dark_mode,
        )


class ThemeRegistry:
    """Stores named palettes; new themes can be added without changing UI components."""

    _themes: dict[str, Theme] = {}
    _color_names = frozenset(Color.__annotations__)

    @classmethod
    def register(cls, theme: Theme) -> None:
        colors = dict(theme.colors)
        missing_colors = cls._color_names.difference(colors)
        if missing_colors:
            raise ValueError(
                f"Theme {theme.name!r} is missing colors: {', '.join(sorted(missing_colors))}"
            )
        cls._themes[theme.name] = Theme(
            name=theme.name,
            colors=MappingProxyType(colors),
            dark_mode=theme.dark_mode,
        )

    @classmethod
    def get(cls, name: str) -> Theme:
        try:
            return cls._themes[name]
        except KeyError as ex:
            raise ValueError(f"Unknown theme: {name}") from ex

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(cls._themes)


class ThemeManager:
    _current_theme = ThemeName.LIGHT.value

    @classmethod
    def set_theme(cls, name: str | ThemeName) -> None:
        theme_name = str(name)
        ThemeRegistry.get(theme_name)
        cls._current_theme = theme_name

    @classmethod
    def get_theme(cls) -> Theme:
        return ThemeRegistry.get(cls._current_theme)

    @classmethod
    def get_color(cls, name: str) -> str:
        try:
            return cls.get_theme().colors[name]
        except KeyError as ex:
            raise AttributeError(f"Unknown color: {name}") from ex


ThemeRegistry.register(Theme.from_color_class(ThemeName.LIGHT.value, LightTheme, dark_mode=False))
ThemeRegistry.register(Theme.from_color_class(ThemeName.DARK.value, DarkTheme, dark_mode=True))
