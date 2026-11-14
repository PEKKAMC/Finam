# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import flet as ft
import flet_audio as fta

from src.logger import Logger
from src.utils import Color, Data, Page, Text, format_number, scale_width

FLOAT_REGEX = Data().get_regex_string("float")


class ScannerHeaderBanner(ft.Container):
    def __init__(self, lang: dict[str, str]) -> None:
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.ai_title_text = Text.SMALL(lang["purchase_scanner.ai_title"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.title_text = Text.H2(lang["purchase_scanner.title"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.description_text = Text.MEDIUM(lang["purchase_scanner.description"], color=Color.LIGHT_ACCENT)

        # Static icons
        self.ai_title_icon = ft.Icon(
            ft.Icons.AUTO_AWESOME,
            color=Color.PROGRESS_ACTIVE,
            size=14
        )

        # CONTAINER COMPONENTS
        self.ai_title_badge = ft.Container(
            content=ft.Row(
                controls=[self.ai_title_icon, self.ai_title_text],
                tight=True,
                spacing=6
            ),
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 6, 12, 6),
            border_radius=20,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER)
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=28,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(controls=[self.ai_title_badge]),
                    self.title_text,
                    self.description_text
                ]
            )
        )


class GoogleRequiredCard(ft.Container):
    def __init__(self, lang: dict[str, str]) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.MEDIUM(self.lang["spending.ai_google_required_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.account_icon = ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=Color.PRIMARY_ACTION, size=24)

        # Dynamic texts
        self.message_text = Text.P(self.lang["spending.ai_google_required"], color=Color.SECONDARY_TEXT)

        # CONTAINER COMPONENTS
        self.main_row = ft.Row(
            spacing=12,
            controls=[
                self.account_icon,
                ft.Column(
                    expand=True,
                    spacing=4,
                    controls=[
                        self.title_text,
                        self.message_text
                    ]
                )
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=self.main_row
        )

    def set_access(self, signed_in: bool, message: str | None = None) -> None:
        self.visible = not signed_in
        self.message_text.value = message or self.lang["spending.ai_google_required"]


class ScannerUsageCard(ft.Container):
    def __init__(self, lang: dict[str, str]) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.usage_label = Text.MEDIUM(self.lang["purchase_scanner.usage_loading"], color=Color.PRIMARY_TEXT)

        # CONTAINER COMPONENTS
        self.usage_progress = ft.ProgressBar(
            value=1,
            color=Color.PROGRESS_ACTIVE,
            bgcolor=Color.DARK_BUTTON,
            border_radius=8,
            height=8
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Column(
                spacing=10,
                controls=[
                    self.usage_label,
                    self.usage_progress
                ]
            )
        )


class SelectableOptionGroup(ft.Container):
    """Custom option selector matching the React toggle buttons style."""

    def __init__(self, options: list[tuple[str, str]], initial_value: str, is_dark_selected: bool = False) -> None:
        self.options = options
        self.value = initial_value
        self.is_dark_selected = is_dark_selected
        self.button_controls: dict[str, ft.Container] = {}

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        for val_id, label in self.options:
            button = ft.Container(
                content=Text.BADGE(label, text_align=ft.TextAlign.CENTER),
                padding=ft.Padding(12, 10, 12, 10),
                border_radius=16,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                on_click=lambda e, vid=val_id: self._select(vid),
                expand=True
            )
            self.button_controls[val_id] = button

        chunk_size = 2 if len(options) > 3 else 3
        rows = []
        for i in range(0, len(options), chunk_size):
            chunk_keys = [opt[0] for opt in options[i : i + chunk_size]]
            row_controls = [self.button_controls[k] for k in chunk_keys]
            rows.append(ft.Row(controls=row_controls, spacing=8))

        self.option_rows = rows
        super().__init__(content=ft.Column(controls=rows, spacing=8))
        self.update_styles()

    def resize(self, width: int) -> None:
        self.width = width
        for row in self.option_rows:
            row.width = width

    def _select(self, val_id: str) -> None:
        self.value = val_id
        self.update_styles()
        self.update()

    def update_styles(self) -> None:
        for val_id, button in self.button_controls.items():
            is_selected = val_id == self.value
            text_ctrl: ft.Control | None = button.content

            if is_selected:
                if self.is_dark_selected:
                    button.bgcolor = Color.PRIMARY
                    button.border = ft.Border.all(1.5, Color.PRIMARY)
                    text_ctrl.color = Color.WHITE
                else:
                    button.bgcolor = Color.LIGHT_ACCENT
                    button.border = ft.Border.all(1.5, Color.PRIMARY)
                    text_ctrl.color = Color.PRIMARY
            else:
                button.bgcolor = Color.CARD_BACKGROUND
                button.border = ft.Border.all(1, Color.INPUT_BORDER)
                text_ctrl.color = Color.DEFAULT_TEXT

    def set_enabled(self, enabled: bool) -> None:
        for val_id, button in self.button_controls.items():
            button.on_click = (
                (lambda e, option=val_id: self._select(option)) if enabled else None
            )


class ThinkingTimeUnitContainer(ft.Container):
    """Input field for thinking time value combined with a time unit dropdown."""

    def __init__(self, lang: dict[str, str], default_val: str  , default_unit: str | None) -> None:
        self.lang = lang

        # CONTAINER COMPONENTS
        self.value_field = ft.TextField(
            hint_text="0",
            value=default_val,
            input_filter=ft.InputFilter(
                allow=True, regex_string=FLOAT_REGEX
            ),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            text_size=13,
            height=48,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=ft.Padding(16, 12, 16, 12),
            expand=True
        )

        self.unit_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("minute", self.lang["generic.minute"]),
                ft.dropdown.Option("hour", self.lang["generic.hour"]),
                ft.dropdown.Option("day", self.lang["generic.day"]),
                ft.dropdown.Option("week", self.lang["generic.week"])
            ],
            value=default_unit,
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            text_size=13,
            height=48,
            content_padding=ft.Padding(16, 12, 16, 12)
        )
        row = ft.Row(spacing=10, controls=[self.value_field, self.unit_dropdown])
        super().__init__(content=row)

    @property
    def value(self) -> str:
        val = self.value_field.value.strip() if self.value_field.value else "1"
        unit = self.unit_dropdown.value or "hour"
        return f"{val} {unit}"

    def resize(self, value_width: int, unit_width: int) -> None:
        self.value_field.width = value_width
        self.unit_dropdown.width = unit_width


class ScannerForm(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], currency: str, on_scan_click: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.currency = currency
        self.on_scan_click = on_scan_click

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.form_title_text = Text.H4(self.lang["purchase_scanner.title"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
        self.product_name_label = Text.H6(self.lang["purchase_scanner.product_name"].upper(), color=Color.DEFAULT_TEXT)
        self.price_label = Text.H6(self.lang["purchase_scanner.price"].upper(), color=Color.DEFAULT_TEXT)
        self.trigger_question_label = Text.H6(self.lang["purchase_scanner.trigger_question"].upper(), color=Color.DEFAULT_TEXT)
        self.thinking_time_label = Text.H6(self.lang["purchase_scanner.thinking_time_question"].upper(), color=Color.DEFAULT_TEXT)
        self.reason_label = Text.H6(self.lang["purchase_scanner.reason_label"].upper(), color=Color.DEFAULT_TEXT)
        self.submit_label = Text.BUTTON(self.lang["purchase_scanner.scan_assess"], color=Color.WHITE)

        # Static icons
        self.form_icon = ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, color=Color.PRIMARY, size=20)
        self.submit_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18)

        # CONTAINER COMPONENTS
        self.item_name = ft.TextField(
            hint_text=self.lang["purchase_scanner.product_hint"],
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=13,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        self.item_price = ft.TextField(
            hint_text=self.lang["purchase_scanner.item_price_hint"].format(
                currency=self.currency
            ),
            input_filter=ft.InputFilter(
                allow=True, regex_string=FLOAT_REGEX
            ),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=13,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        self.item_name_error = Text.SMALL("", color=Color.NEGATIVE_ACTION)
        self.item_name_error.visible = False
        self.item_price_error = Text.SMALL("", color=Color.NEGATIVE_ACTION)
        self.item_price_error.visible = False

        self.item_reason = ft.TextField(
            hint_text=self.lang["purchase_scanner.reason_hint"],
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=12,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        # Triggers selection grid
        trigger_options = [
            ("need", self.lang["purchase_scanner.trigger_actual_need"]),
            ("sale", self.lang["purchase_scanner.trigger_flash_sale"]),
            ("tiktok", self.lang["purchase_scanner.trigger_social_media"]),
            ("social", self.lang["purchase_scanner.trigger_friends"]),
            ("emotion", self.lang["purchase_scanner.trigger_emotion"])
        ]

        self.trigger = SelectableOptionGroup(
            trigger_options, initial_value="", is_dark_selected=False
        )

        self.thinking_time = ThinkingTimeUnitContainer(
            lang=self.lang, default_val="0", default_unit="hour"
        )

        self.submit_button = ft.Container(
            content=ft.Row(
                controls=[
                    self.submit_icon,
                    self.submit_label
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            bgcolor=Color.PRIMARY,
            border_radius=16,
            padding=ft.Padding(0, 14, 0, 14),
            on_click=None
        )
        self._scan_enabled = False
        self._scan_busy = False
        self._update_submit_button()

        self.main_container = ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self.form_icon,
                        self.form_title_text
                    ]
                ),
                ft.Divider(height=1, color=Color.CARD_DIVIDER),
                # Name
                ft.Column(
                    [
                        self.product_name_label,
                        self.item_name,
                        self.item_name_error,
                    ],
                    spacing=6
                ),
                # Price
                ft.Column(
                    [
                        self.price_label,
                        self.item_price,
                        self.item_price_error,
                    ],
                    spacing=6
                ),
                # Trigger
                ft.Column(
                    [
                        self.trigger_question_label,
                        self.trigger
                    ],
                    spacing=6
                ),
                # Thinking time
                ft.Column(
                    [
                        self.thinking_time_label,
                        self.thinking_time
                    ],
                    spacing=6
                ),
                # Reason
                ft.Column(
                    [
                        self.reason_label,
                        self.item_reason
                    ],
                    spacing=6
                ),
                self.submit_button
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=24,
            padding=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def _handle_scan_click(self) -> None:
        if not self._scan_enabled:
            return
        item_name = (self.item_name.value or "").strip()
        item_price = (self.item_price.value or "").strip()
        field_required_error = self.lang["purchase_scanner.field_required"]
        self.item_name_error.value = field_required_error
        self.item_name_error.visible = not item_name
        self.item_price_error.value = field_required_error
        self.item_price_error.visible = not item_price
        if not item_name or not item_price:
            self._page.update()
            return

        self.on_scan_click(
            item_name,
            item_price,
            self.item_reason.value,
            self.trigger.value,
            self.thinking_time.value
        )
        self.reset()

    def reset(self) -> None:
        self.item_name.value = ""
        self.item_price.value = ""
        self.item_name_error.value = ""
        self.item_name_error.visible = False
        self.item_price_error.value = ""
        self.item_price_error.visible = False
        self.item_reason.value = ""
        self.trigger.value = ""
        self.trigger.update_styles()
        self.thinking_time.value_field.value = "0"
        self.thinking_time.unit_dropdown.value = "hour"
        self._page.update()

    def set_enabled(self, enabled: bool) -> None:
        self._scan_enabled = enabled
        self.item_name.disabled = not enabled
        self.item_price.disabled = not enabled
        self.item_reason.disabled = not enabled
        self.thinking_time.value_field.disabled = not enabled
        self.thinking_time.unit_dropdown.disabled = not enabled
        self.trigger.set_enabled(enabled)
        self._update_submit_button()
        self.update()

    def set_scanning(self, scanning: bool) -> None:
        self._scan_busy = scanning
        self._update_submit_button()
        self.update()

    def _update_submit_button(self) -> None:
        enabled = self._scan_enabled and not self._scan_busy
        self.submit_button.on_click = self._handle_scan_click if enabled else None
        self.submit_button.bgcolor = Color.PRIMARY if enabled else Color.DARK_BUTTON
        self.submit_icon.color = Color.LIGHT_ACCENT if enabled else Color.SECONDARY_TEXT
        self.submit_label.color = Color.WHITE if enabled else Color.SECONDARY_TEXT

    def resize(self, width: int, content_width: int, thinking_value_width: int, thinking_unit_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        self.item_name.width = content_width
        self.item_price.width = content_width
        self.item_reason.width = content_width
        self.trigger.resize(content_width)
        self.thinking_time.width = content_width
        self.thinking_time.resize(thinking_value_width, thinking_unit_width)
        self.submit_button.width = content_width


class InterventionItem(ft.Container):
    def __init__(self, page: Page, title: str, description: str) -> None:
        self._page = page

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.title_text = Text.MEDIUM(title, weight=ft.FontWeight.BOLD, color=Color.DEFAULT_TEXT)
        self.description_text = Text.P(description, color=Color.SECONDARY_TEXT)

        # Dynamic icons
        self.status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=Color.PRIMARY, size=16)

        # CONTAINER COMPONENTS
        self.main_container = ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    [self.status_icon, self.title_text],
                    spacing=6
                ),
                ft.Container(
                    content=self.description_text,
                    padding=ft.Padding(22, 0, 0, 0)
                )
            ]
        )
        super().__init__(
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=14,
            bgcolor=Color.CARD_BACKGROUND,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class ScannerHistoryCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], currency: str, on_delete_entry: Callable[[int], None] | None = None, on_clear_all: Callable[[], None] | None = None) -> None:
        self._page = page
        self.lang = lang
        self.currency = currency
        self.on_delete_entry = on_delete_entry or (lambda *_: None)
        self.on_clear_all = on_clear_all or (lambda: None)
        self._content_width: int | None = None

        self.history_collapsed = False
        self.history_items: list[ft.Container] = []

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.history_title = Text.LABEL(self.lang["purchase_scanner.history"].upper(), color=Color.SECONDARY_TEXT)
        self.clear_all_label = Text.BUTTON(self.lang["purchase_scanner.clear_history"], color=Color.NEGATIVE_ACTION)

        # Static icons
        self.clear_all_icon = ft.Icon(ft.Icons.DELETE_SWEEP_OUTLINED, color=Color.NEGATIVE_ACTION, size=18)

        # CONTAINER COMPONENTS
        self.history_expander = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_UP,
            on_click=lambda e: self.toggle_history_panel(),
            style=ft.ButtonStyle(shape=ft.CircleBorder())
        )

        self.clear_all_button = ft.TextButton(
            content=ft.Row(
                controls=[self.clear_all_icon, self.clear_all_label], spacing=6
            ),
            on_click=lambda e: self._handle_clear_all(),
            style=ft.ButtonStyle(color=Color.NEGATIVE_ACTION)
        )

        self.history_list = ft.Column(spacing=8)

        self.history_content = ft.Column(
            spacing=10,
            controls=[self.history_list],
            visible=True,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        super().__init__(
            visible=True,
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.history_title,
                            ft.Row(
                                controls=[self.clear_all_button, self.history_expander],
                                spacing=0
                            )
                        ]
                    ),
                    self.history_content
                ]
            )
        )

    def _handle_delete(self, scan_id: int) -> None:
        if scan_id is not None:
            self.on_delete_entry(scan_id)

    def _handle_clear_all(self) -> None:
        self.on_clear_all()

    def set_history(self, history_entries: list[dict[str, Any]]) -> None:
        self.history_list.controls.clear()
        self.history_items.clear()
        self.history_content.visible = not self.history_collapsed
        self.clear_all_button.visible = bool(history_entries)

        if not history_entries:
            no_history_text = Text.SMALL(
                self.lang["purchase_scanner.no_history"],
                color=Color.SECONDARY_TEXT
            )
            self.history_list.controls.append(
                no_history_text
            )
            if self.parent:
                self.update()
            return

        for entry in history_entries:
            item_name = entry.get("item_name") or "Item"
            risk_score_raw = entry.get("risk_score")
            risk_score = int(risk_score_raw or 0)
            created_at = entry.get("created_at", "")
            trigger_display = (
                entry.get("trigger_display") or entry.get("trigger") or "-"
            )
            advice = entry.get("ai_advice") or "-"
            price = entry.get("price", 0)
            scan_id = entry.get("id")

            price_and_trigger_text = Text.SMALL(
                f"{format_number(price)} {self.currency} • {trigger_display}",
                color=Color.SECONDARY_TEXT
            )
            created_at_text = Text.SMALL(created_at, color=Color.SECONDARY_TEXT)
            advice_text = Text.SMALL(advice, color=Color.DEFAULT_TEXT)
            details = ft.Column(
                spacing=4,
                visible=False,
                controls=[price_and_trigger_text, created_at_text, advice_text]
            )
            expander = ft.IconButton(
                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                tooltip=self.lang["purchase_scanner.history"]
            )
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip=self.lang["purchase_scanner.delete_item"],
                icon_color=Color.NEGATIVE_ACTION,
                disabled=not isinstance(scan_id, int)
            )
            if isinstance(scan_id, int):
                delete_button.on_click = self._create_delete_handler(scan_id)
            item_name_text = Text.MEDIUM(
                item_name,
                weight=ft.FontWeight.BOLD,
                color=Color.DEFAULT_TEXT
            )
            risk_score_text = Text.SMALL(
                f"{risk_score}",
                color=Color.WHITE,
                weight=ft.FontWeight.BOLD
            )
            item_card = ft.Container(
                bgcolor=Color.CARD_BACKGROUND,
                border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                border_radius=14,
                padding=12,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                item_name_text,
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=risk_score_text,
                                            bgcolor=Color.PRIMARY
                                            if risk_score < 60
                                            else (
                                                Color.NEGATIVE_ACTION
                                                if risk_score > 75
                                                else Color.WARNING_COLOR
                                            ),
                                            border_radius=12,
                                            padding=ft.Padding(8, 4, 8, 4)
                                        ),
                                        expander,
                                        delete_button
                                    ],
                                    spacing=0
                                )
                            ]
                        ),
                        details
                    ]
                )
            )

            expander.on_click = self._create_history_toggle_handler(
                details,
                expander,
                item_card
            )
            if self._content_width is not None:
                item_card.width = self._content_width
            self.history_list.controls.append(item_card)
            self.history_items.append(item_card)

        self.history_content.visible = not self.history_collapsed
        if self.parent:
            self.update()

    def _create_delete_handler(self, scan_id: int) -> Callable[[ft.Event[ft.IconButton]], None]:
        def delete_entry(_event: ft.Event[ft.IconButton]) -> None:
            self._handle_delete(scan_id)

        return delete_entry

    @staticmethod
    def _create_history_toggle_handler(details: ft.Column, expander: ft.IconButton, item_card: ft.Container) -> Callable[[ft.Event[ft.IconButton]], None]:
        def toggle_entry(_event: ft.Event[ft.IconButton]) -> None:
            details.visible = not details.visible
            expander.icon = (
                ft.Icons.KEYBOARD_ARROW_UP
                if details.visible
                else ft.Icons.KEYBOARD_ARROW_DOWN
            )
            item_card.update()

        return toggle_entry

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self._content_width = content_width
        self.history_list.width = content_width
        for item in self.history_items:
            item.width = content_width

    def toggle_history_panel(self) -> None:
        self.history_collapsed = not self.history_collapsed
        self.history_content.visible = not self.history_collapsed
        self.history_expander.icon = (
            ft.Icons.KEYBOARD_ARROW_DOWN
            if self.history_collapsed
            else ft.Icons.KEYBOARD_ARROW_UP
        )
        self.update()


class ScannerResult(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], currency: str) -> None:
        self._page = page
        self.lang = lang
        self.currency = currency
        self._request_generation = 0
        self._the_rock_audio: fta.Audio | None = None
        self._the_rock_audio_loaded: asyncio.Event | None = None
        self._the_rock_audio_finished: asyncio.Event | None = None
        self._content_width: int | None = None
        self._intervention_width: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.empty_message = Text.SMALL(self.lang["purchase_scanner.fill_info"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
        self.no_results_text = Text.H4(self.lang["purchase_scanner.no_results"], color=Color.DEFAULT_TEXT)
        self.waiting_text = Text.H5(self.lang["purchase_scanner.waiting"], color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER)
        self.loading_hint_text = Text.SMALL(self.lang["purchase_scanner.fill_info"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
        self.risk_index_label = Text.LABEL(self.lang["purchase_scanner.risk_index"].upper(), color=Color.BLAND_TEXT)
        self.expert_perspective_label = Text.SMALL(self.lang["purchase_scanner.expert_perspective"], color=Color.PRIMARY)
        self.intervention_rules_label = Text.LABEL(self.lang["purchase_scanner.intervention_rules"].upper(), color=Color.SECONDARY_TEXT)
        self.risk_status_text = Text.SMALL(self.lang["purchase_scanner.risk_assessment"], color=Color.BLAND_TEXT)

        # Static icons
        self.empty_state_icon = ft.Icon(ft.Icons.SHIELD_OUTLINED, color=Color.PRIMARY, size=52)
        self.expert_perspective_icon = ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=Color.PRIMARY, size=18)

        # Dynamic texts
        self.error_text = Text.SMALL("", color=Color.NEGATIVE_ACTION, text_align=ft.TextAlign.CENTER)
        self.risk_badge_text = Text.H6("", color=Color.LIGHT_ACCENT)
        self.risk_score_text = Text.H1("", color=Color.PROGRESS_ACTIVE)
        self.advice_text = Text.P("", color=Color.DEFAULT_TEXT)

        # CONTAINER COMPONENTS
        self.empty_state = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                self.empty_state_icon,
                self.no_results_text,
                self.empty_message
            ]
        )

        self.error_state = ft.Container(
            visible=False,
            alignment=ft.Alignment.CENTER,
            content=self.error_text
        )

        self.loading_container = ft.Container(
            visible=False,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.ProgressRing(
                        width=48, height=48, stroke_width=5, color=Color.PRIMARY
                    ),
                    self.waiting_text,
                    self.loading_hint_text
                ]
            )
        )

        self.the_rock_animation = ft.Image(
            src="gif/the_rock.gif",
            fit=ft.BoxFit.CONTAIN,
            visible=False
        )

        self.progress_bar = ft.ProgressBar(
            value=0.0, color=Color.PROGRESS_ACTIVE, bgcolor=Color.DARK_BUTTON, height=8
        )

        self.gauge_card = ft.Container(
            bgcolor=Color.DARK_SURFACE,
            border_radius=20,
            padding=18,
            border=ft.Border.all(1, Color.DARK_BUTTON),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.risk_index_label,
                            ft.Container(
                                content=self.risk_badge_text,
                                bgcolor=Color.DARK_BUTTON,
                                padding=ft.Padding(10, 4, 10, 4),
                                border_radius=12
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[self.risk_score_text, self.risk_status_text],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        spacing=10
                    ),
                    self.progress_bar
                ]
            )
        )

        self.advice_box = ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
            border_radius=16,
            padding=14,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        [self.expert_perspective_icon, self.expert_perspective_label],
                        spacing=6
                    ),
                    self.advice_text
                ]
            )
        )

        self.interventions_col = ft.Column(spacing=10)

        self.result_container = ft.Column(
            spacing=16,
            visible=False,
            controls=[
                self.gauge_card,
                self.advice_box,
                ft.Column(
                    [
                        self.intervention_rules_label,
                        self.interventions_col
                    ],
                    spacing=8
                )
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.empty_state,
                    self.error_state,
                    self.loading_container,
                    self.the_rock_animation,
                    self.result_container
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.Alignment.CENTER,
            expand=True
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=24,
            padding=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def set_loading_state(self) -> int:
        self._request_generation += 1
        if self._the_rock_audio is not None:
            self._page.run_task(self._stop_the_rock_audio, self._the_rock_audio)
        self.empty_state.visible = False
        self.error_state.visible = False
        self.loading_container.visible = True
        self.the_rock_animation.visible = False
        self.result_container.visible = False
        self.advice_box.visible = True
        self.empty_message.value = self.lang["purchase_scanner.fill_info"]
        self.advice_text.value = ""
        self.interventions_col.controls.clear()
        self.update()
        return self._request_generation

    async def show_the_rock_result(self, request_generation: int, risk: int | None, trigger_display: str, price: Decimal, ai_advice: str) -> None:
        if request_generation != self._request_generation:
            return
        self.empty_state.visible = False
        self.error_state.visible = False
        self.loading_container.visible = True
        self.result_container.visible = False
        self.the_rock_animation.visible = False
        audio_loaded = asyncio.Event()
        audio_finished = asyncio.Event()
        self._the_rock_audio_loaded = audio_loaded
        self._the_rock_audio_finished = audio_finished
        audio = fta.Audio(
            src="/audio/the_rock.mp3",
            autoplay=False,
            on_state_change=self._on_the_rock_audio_state_change,
            on_loaded=self._on_the_rock_audio_loaded
        )
        self._the_rock_audio = audio
        self._page.services.append(audio)
        self._page.update()
        try:
            await asyncio.wait_for(audio_loaded.wait(), timeout=3.0)
        except TimeoutError:
            Logger.warning("Purchase scanner audio did not load within 3 seconds")
        if request_generation != self._request_generation:
            await self._stop_the_rock_audio(audio)
            return
        self.loading_container.visible = False
        self.the_rock_animation.visible = True
        self._page.update()
        self._page.run_task(self._play_the_rock_audio, audio)
        try:
            await asyncio.wait_for(audio_finished.wait(), timeout=3.0)
        except TimeoutError:
            Logger.warning("Purchase scanner audio did not finish within 3 seconds")
        finally:
            await self._stop_the_rock_audio(audio)
        if request_generation != self._request_generation:
            return
        self.the_rock_animation.visible = False
        self.update_result(risk, trigger_display, price, ai_advice)

    def _on_the_rock_audio_loaded(self, _event: ft.Event[fta.Audio]) -> None:
        if self._the_rock_audio_loaded is not None:
            self._the_rock_audio_loaded.set()

    @staticmethod
    async def _play_the_rock_audio(audio: fta.Audio) -> None:
        try:
            await audio.play()
        except RuntimeError as ex:
            Logger.warning(f"Could not play purchase scanner audio: {ex}")

    def _on_the_rock_audio_state_change(self, e: fta.AudioStateChangeEvent) -> None:
        if (
            e.state == fta.AudioState.COMPLETED
            and self._the_rock_audio_finished is not None
        ):
            self._the_rock_audio_finished.set()

    async def _stop_the_rock_audio(self, audio: fta.Audio) -> None:
        try:
            await audio.pause()
        except RuntimeError as ex:
            Logger.debug(f"Could not pause audio: {ex}")
        if audio in self._page.services:
            self._page.services.remove(audio)
            self._page.update()
        if self._the_rock_audio is audio:
            self._the_rock_audio = None

    def show_error(self, message: str) -> None:
        self._request_generation += 1
        if self._the_rock_audio is not None:
            self._page.run_task(self._stop_the_rock_audio, self._the_rock_audio)
        self.loading_container.visible = False
        self.the_rock_animation.visible = False
        self.result_container.visible = False
        self.empty_state.visible = False
        self.error_text.value = message
        self.error_state.visible = True
        self.update()

    def update_result(self, risk: int | None, trigger_display: str, price: Decimal, ai_advice: str = "") -> None:
        self.empty_state.visible = False
        self.error_state.visible = False
        self.loading_container.visible = False
        self.the_rock_animation.visible = False
        self.result_container.visible = True
        self.gauge_card.visible = risk is not None
        self.advice_box.visible = bool(ai_advice)

        if risk is None:
            self.risk_score_text.value = "—"
            self.risk_score_text.color = Color.BLAND_TEXT
            self.risk_status_text.value = "—"
            self.risk_badge_text.value = "—"
            self.progress_bar.value = 0.0
            self.progress_bar.color = Color.BLAND_TEXT
            self.advice_text.value = ai_advice
            self.interventions_col.controls.clear()
            self.update()
            return

        risk_val = max(0, min(100, int(risk)))

        if risk_val > 65:
            risk_color = Color.NEGATIVE_ACTION
            status_desc = self.lang["purchase_scanner.risk_very_high"]
            pause_time = f"24 {self.lang['generic.hour']}"
        elif risk_val > 35:
            risk_color = Color.WARNING_COLOR
            status_desc = self.lang["purchase_scanner.risk_moderate"]
            pause_time = f"60 {self.lang['generic.second']}"
        else:
            risk_color = Color.PROGRESS_ACTIVE
            status_desc = self.lang["purchase_scanner.risk_rational"]
            pause_time = f"60 {self.lang['generic.second']}"

        self.risk_score_text.value = f"{risk_val}%"
        self.risk_score_text.color = risk_color
        self.risk_status_text.value = status_desc
        self.risk_badge_text.value = pause_time
        self.progress_bar.value = risk_val / 100.0
        self.progress_bar.color = risk_color
        self.advice_text.value = ai_advice

        formatted_price = (
            f"{format_number(price)} {self.currency}"
            if price > 0
            else self.lang["purchase_scanner.price_not_entered"]
        )
        interventions = [
            InterventionItem(
                self._page,
                self.lang["purchase_scanner.pause_rule"],
                self.lang["purchase_scanner.pause_rule_description"].format(
                    pause_time=pause_time
                )
            ),
            InterventionItem(
                self._page,
                self.lang["purchase_scanner.budget_check"],
                self.lang["purchase_scanner.budget_check_description"].format(
                    price=formatted_price
                )
            ),
            InterventionItem(
                self._page,
                self.lang["purchase_scanner.reflection"],
                self.lang["purchase_scanner.reflection_description"].format(
                    trigger=trigger_display
                )
            )
        ]

        self.interventions_col.controls.clear()
        if self._intervention_width is not None:
            for item in interventions:
                item.resize(self._intervention_width)
        self.interventions_col.controls.extend(interventions)
        self.update()

    def resize(self, width: int, content_width: int, intervention_width: int, illustration_size: int) -> None:
        self.width = width
        self._content_width = content_width
        self._intervention_width = intervention_width
        self.main_container.width = content_width
        self.result_container.width = content_width
        self.interventions_col.width = content_width
        self.the_rock_animation.width = illustration_size
        self.the_rock_animation.height = illustration_size
        for item in self.interventions_col.controls:
            if isinstance(item, InterventionItem):
                item.resize(intervention_width)


class ScannerPageContent(ft.Container):
    def __init__(self, lang: dict[str, str], form_card: ScannerForm, result_card: ScannerResult, history_card: ScannerHistoryCard, signed_in: bool) -> None:
        self.lang = lang
        self.form_card = form_card
        self.result_card = result_card
        self.history_card = history_card

        # CONTAINER COMPONENTS
        self.header_banner = ScannerHeaderBanner(self.lang)
        self.google_required_card = GoogleRequiredCard(self.lang)
        self.usage_card = ScannerUsageCard(self.lang)
        self.scanner_locked_overlay = ft.Container(
            left=0,
            top=0,
            right=0,
            bottom=0,
            blur=ft.Blur(6, 6),
            bgcolor=ft.Colors.with_opacity(0.45, Color.DARK_SURFACE),
            alignment=ft.Alignment.CENTER
        )

        self.scan_cards_row = ft.Column(
            spacing=20,
            controls=[
                form_card,
                result_card
            ]
        )

        self.scan_cards_stack = ft.Stack(
            expand=True,
            controls=[
                self.scan_cards_row,
                self.scanner_locked_overlay
            ]
        )

        self.content_container = ft.Container(
            padding=20,
            content=ft.Column(
                spacing=20,
                expand=True,
                controls=[
                    self.header_banner,
                    self.google_required_card,
                    self.usage_card,
                    self.scan_cards_stack,
                    ft.Container(history_card, margin=ft.Margin.only(top=4))
                ]
            )
        )

        super().__init__(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )
        self.set_google_access(signed_in)

    def set_google_access(self, signed_in: bool) -> None:
        self.google_required_card.visible = not signed_in
        self.usage_card.visible = signed_in
        self.scanner_locked_overlay.visible = not signed_in

    def resize(self, page_width: int, page_height: int) -> None:
        content_width = scale_width(page_width, 392)
        component_content_width = scale_width(page_width, 344)
        self.width = page_width
        self.height = page_height
        self.content_container.width = page_width
        self.header_banner.width = content_width
        self.google_required_card.width = content_width
        self.usage_card.width = content_width
        self.scan_cards_stack.width = content_width
        self.scan_cards_row.width = content_width
        self.scanner_locked_overlay.width = content_width
        self.scanner_locked_overlay.height = page_height
        self.form_card.resize(
            width=content_width,
            content_width=component_content_width,
            thinking_value_width=scale_width(page_width, 184),
            thinking_unit_width=scale_width(page_width, 150)
        )
        self.result_card.resize(
            width=content_width,
            content_width=component_content_width,
            intervention_width=scale_width(page_width, 316),
            illustration_size=scale_width(page_width, 240)
        )
        self.history_card.resize(
            width=content_width,
            content_width=scale_width(page_width, 368)
        )
