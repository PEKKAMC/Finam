# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import random
from collections.abc import Awaitable, Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

import flet as ft
import flet.canvas as flet_canvas

from src.logger import Logger
from src.pages.common.keyboard_container.components import KeyboardContainer
from src.pages.savings.logic import LogicController
from src.utils import Color, Data, Dialog, Page, Text, format_compact_number, format_display_number, format_number, to_decimal

FLOAT_REGEX = Data().get_regex_string("float")

class GoalCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], goal: dict[str, Any], on_deposit: Callable[[dict[str, Any], str], None], on_achievement: Callable[[dict[str, Any]], None], on_withdraw: Callable[[dict[str, Any], str], None], on_delete: Callable[[int], None]) -> None:
        self._page = page
        self.lang = lang
        self.goal = goal
        self.objective_id = goal["objective_id"]
        self.completed = goal["completed"]

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.withdraw_button_label = Text.BUTTON(self.lang["savings.withdraw_money"], color=Color.WHITE)
        self.accumulated_label_text = Text.MEDIUM(self.lang["savings.accumulated"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.action_message_icon = ft.Icon(ft.Icons.ERROR_OUTLINE, color=Color.ERROR_TEXT, size=14)

        # Dynamic texts
        self.title_text = Text.H4(goal["title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.subtitle_text = Text.SMALL(goal["reason"], color=Color.SECONDARY_TEXT)
        self.percentage_text = Text.BADGE(goal["percentage"], color=Color.WHITE if self.completed else Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.current_value_text = Text.H4(goal["current_value"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.target_text = Text.SMALL(self.lang["savings.target"].format(target_value=goal["target_value"]), color=Color.SECONDARY_TEXT)
        self.remaining_text = Text.SMALL(goal["remaining_value"], color=Color.SECONDARY_TEXT)
        self.action_message_text = Text.SMALL("", color=Color.ERROR_TEXT)
        self.deposit_button_label = Text.BUTTON(self.lang["savings.achievement"] if self.completed else self.lang["savings.deposit_money"], color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.progress_bar = ft.ProgressBar(
            value=goal["progress"],
            color=Color.PRIMARY,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            height=10
        )

        self.deposit_button = ft.Button(
            content=self.deposit_button_label,
            on_click=lambda: (
                on_achievement(goal) if self.completed else on_deposit(goal, "deposit")
            ),
            bgcolor=Color.COMPLETED_ACTION if self.completed else Color.PRIMARY_ACTION
        )

        self.withdraw_button = ft.Button(
            content=self.withdraw_button_label,
            on_click=lambda: on_withdraw(goal, "withdraw"),
            bgcolor=Color.NEGATIVE_ACTION
        )

        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=Color.DELETE_ACTION,
            tooltip=self.lang["generic.delete"],
            on_click=lambda: on_delete(self.objective_id)
        )

        self.action_message_row = ft.Container(
            content=ft.Row(
                spacing=6,
                controls=[
                    self.action_message_icon,
                    self.action_message_text
                ]
            ),
            visible=False
        )
        self._action_message_generation = 0

        self.main_container = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=4,
                            expand=True,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        self.title_text,
                                        ft.Icon(
                                            ft.Icons.CHECK_CIRCLE,
                                            color=Color.PROGRESS_ACTIVE,
                                            size=18
                                        )
                                        if self.completed
                                        else ft.Container()
                                    ]
                                ),
                                self.subtitle_text
                            ]
                        ),
                        ft.Row(
                            spacing=4,
                            wrap=True,
                            controls=[
                                ft.Container(
                                    content=self.percentage_text,
                                    bgcolor=Color.PROGRESS_ACTIVE
                                    if self.completed
                                    else Color.LIGHT_ACCENT,
                                    padding=ft.Padding(10, 5, 10, 5),
                                    border_radius=16
                                ),
                                self.delete_button
                            ]
                        )
                    ]
                ),
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                self.accumulated_label_text,
                                self.current_value_text
                            ]
                        ),
                        self.progress_bar,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                self.target_text,
                                self.remaining_text
                            ]
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10,
                    wrap=True,
                    controls=[
                        self.deposit_button,
                        self.withdraw_button
                    ]
                ),
                self.action_message_row
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=24,
            padding=20,
            border=None,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=self.main_container
        )

    async def show_action_message(self, message: str, is_success: bool = False) -> None:
        self._action_message_generation += 1
        generation = self._action_message_generation
        color = Color.INCOME_COLOR if is_success else Color.ERROR_TEXT
        self.action_message_text.value = message
        self.action_message_text.color = color
        self.action_message_icon.icon = (ft.Icons.CHECK_CIRCLE if is_success else ft.Icons.ERROR_OUTLINE)
        self.action_message_icon.color = color
        self.action_message_row.visible = True
        self.update()
        await asyncio.sleep(3)
        if generation == self._action_message_generation:
            self.action_message_row.visible = False
            self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width


class GoalGrid(ft.Column):
    def __init__(self, page: Page, lang: dict[str, str], objectives_data: list[dict[str, Any]], on_deposit: Callable[[dict[str, Any], str], None], on_achievement: Callable[[dict[str, Any]], None], on_withdraw: Callable[[dict[str, Any], str], None], on_delete: Callable[[int], None]) -> None:
        self._page = page
        self.lang = lang
        self.on_deposit = on_deposit
        self.on_achievement = on_achievement
        self.on_withdraw = on_withdraw
        self.on_delete = on_delete
        self.is_expanded = True
        self._card_width: int | None = None
        self._card_content_width: int | None = None

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.title_text = Text.H3("", color=Color.PRIMARY_TEXT)

        # CONTAINER COMPONENTS
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS,
            tooltip=self.lang["generic.collapse"],
            on_click=self._toggle_expanded
        )

        self.objectives_column = ft.Column(spacing=20)

        super().__init__(
            spacing=20
        )

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.title_text,
                    self.toggle_button
                ]
            ),
            self.objectives_column
        ]

        self.update_grid(objectives_data)

    def update_grid(self, objectives_data: list[dict[str, Any]]) -> None:
        cards = []
        for data in objectives_data:
            cards.append(
                GoalCard(
                    page=self._page,
                    lang=self.lang,
                    goal=data,
                    on_deposit=self.on_deposit,
                    on_achievement=self.on_achievement,
                    on_withdraw=self.on_withdraw,
                    on_delete=self.on_delete
                )
            )
        self.title_text.value = self.lang["savings.objectives"].format(len=len(objectives_data))
        if self._card_width is not None and self._card_content_width is not None:
            for card in cards:
                card.resize(self._card_width, self._card_content_width)
        self.objectives_column.controls = cards
        self.objectives_column.visible = self.is_expanded

    async def show_action_message(self, objective_id: int, message: str, is_success: bool = False) -> None:
        await asyncio.sleep(0.1)
        for card in self.objectives_column.controls:
            if isinstance(card, GoalCard) and card.objective_id == objective_id:
                await card.show_action_message(message, is_success)
                return
        Logger.error(f"Cannot display savings action message: goal {objective_id} is not rendered")

    def _toggle_expanded(self, _event: ft.Event[ft.IconButton]) -> None:
        self.is_expanded = not self.is_expanded
        self.objectives_column.visible = self.is_expanded
        self.toggle_button.icon = (
            ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        )
        self.toggle_button.tooltip = (
            self.lang["generic.collapse"]
            if self.is_expanded
            else self.lang["generic.expand"]
        )
        if self._page is not None:
            self._page.update()

    def resize(self, width: int, card_content_width: int) -> None:
        self.width = width
        self._card_width = width
        self._card_content_width = card_content_width
        self.objectives_column.width = width
        for card in self.objectives_column.controls:
            if isinstance(card, GoalCard):
                card.resize(width, card_content_width)


class AggregateCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], total_savings: Decimal, total_target: Decimal, percentage: str, progress_value: float, currency: str, on_create_click: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.currency = currency

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.MEDIUM(self.lang["savings.fund_management"].upper(), color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.progress_label = Text.MEDIUM(self.lang["savings.progress"], color=Color.WHITE)

        # Dynamic texts
        self.savings_text = Text.H2(format_display_number(total_savings, self.lang), color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.target_text = Text.H6(f" / {format_display_number(total_target, self.lang)} {self.currency}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.percentage_text = Text.MEDIUM(f"{percentage}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.add_icon = ft.Icon(ft.Icons.ADD, color=Color.PRIMARY, size=16)
        self.progress_bar = ft.ProgressBar(
            value=progress_value,
            color=Color.LIGHT_ACCENT,
            bgcolor=Color.DARK_SURFACE,
            height=8,
            border_radius=4
        )

        self.pill_container = ft.Container(
            content=self.title_text,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 6, 12, 6),
            border_radius=20,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER)
        )

        self.add_button_container = ft.Container(
            content=self.add_icon,
            bgcolor=Color.LIGHT_ACCENT,
            padding=ft.Padding(16, 12, 16, 12),
            border_radius=16,
            ink=True,
            on_click=on_create_click
        )

        self.main_container = ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            spacing=8,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        self.pill_container,
                                        self.add_button_container
                                    ]
                                ),
                                self.savings_text,
                                self.target_text,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        self.progress_label,
                                        self.percentage_text
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                self.progress_bar
            ]
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=30,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=self.main_container
        )

    def update_data(self, total_savings: Decimal, total_target: Decimal, percentage: str, progress_value: float, currency: str) -> None:
        self.savings_text.value = format_display_number(total_savings, self.lang)
        self.currency = currency
        self.target_text.value = (
            f" / {format_display_number(total_target, self.lang)} {self.currency}"
        )
        self.percentage_text.value = percentage
        self.progress_bar.value = progress_value

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width


class ActivityHistory(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], activities: list[dict[str, Any]], currency: str, on_export: Callable[..., None] | ft.CoroutineType[Any, Any, None], on_clear: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.currency = currency
        self.on_export = on_export
        self.on_clear = on_clear
        self.is_expanded = True
        self.activity_list = ft.Column(spacing=0)

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.export_button_label = Text.BUTTON(self.lang["savings.export_ledger"], color=Color.PRIMARY_ACTION)
        self.clear_history_button_label = Text.BUTTON(self.lang["savings.clear_history"], color=Color.DELETE_ACTION)

        # Static icons
        self.export_button_icon = ft.Icon(ft.Icons.DOWNLOAD, color=Color.PRIMARY_ACTION)
        self.clear_history_button_icon = ft.Icon(ft.Icons.DELETE_OUTLINE, color=Color.DELETE_ACTION)

        # Dynamic texts
        self.history_title = Text.H3(self.lang["savings.recent_activity"].format(len=len(activities)), color=Color.PRIMARY_TEXT)

        # CONTAINER COMPONENTS
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS,
            tooltip=self.lang["generic.collapse"],
            on_click=self._toggle_expanded
        )

        self.activity_content = ft.Container(
            content=self.activity_list,
            visible=self.is_expanded
        )

        self.main_container = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True,
                    controls=[
                        self.history_title,
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.TextButton(
                                    content=ft.Row(
                                        controls=[
                                            self.export_button_icon,
                                            self.export_button_label
                                        ],
                                        tight=True
                                    ),
                                    on_click=self.on_export
                                ),
                                ft.TextButton(
                                    content=ft.Row(
                                        controls=[
                                            self.clear_history_button_icon,
                                            self.clear_history_button_label
                                        ],
                                        tight=True
                                    ),
                                    on_click=self.on_clear
                                ),
                                self.toggle_button
                            ]
                        )
                    ]
                ),
                self.activity_content
            ]
        )
        self.update_history(activities, currency)

        super().__init__(
            content=self.main_container,
            padding=20,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=24
        )

    def update_history(self, activities: list[dict[str, Any]], currency: str) -> None:
        self.currency = currency
        self.history_title.value = self.lang["savings.recent_activity"].format(len=len(activities))
        self.activity_list.controls.clear()
        if not activities:
            no_activity_text = Text.SMALL(
                self.lang["savings.no_recent_activity"],
                italic=True,
                color=Color.SUBTITLE_TEXT
            )
            self.activity_list.controls.append(
                no_activity_text
            )
            return

        for item in activities:
            activity_type = item["type"]
            icon = (
                ft.Icons.MONEY
                if activity_type == "saving"
                else ft.Icons.CHECK_CIRCLE
                if activity_type == "completed"
                else ft.Icons.HISTORY
            )
            amount = item.get("amount")
            description_text = Text.MEDIUM(
                item["desc"],
                color=Color.PRIMARY_TEXT
            )
            date_text = Text.SMALL(
                item["date"],
                color=Color.SECONDARY_TEXT
            )
            activity_controls: list[ft.Control] = [
                ft.Icon(icon, color=Color.PRIMARY_ACTION),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[description_text, date_text]
                )
            ]
            if isinstance(amount, (int, Decimal)) and not isinstance(amount, bool):
                amount_text = Text.MEDIUM(
                    f"{format_compact_number(amount, decimals=1, signed=True, translations=self.lang)} {self.currency}",
                    color=Color.PRIMARY_ACTION
                    if amount > 0
                    else Color.NEGATIVE_ACTION,
                    text_align=ft.TextAlign.RIGHT
                )
                activity_controls.append(
                    amount_text
                )
            self.activity_list.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=8),
                    content=ft.Row(
                        spacing=18,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=activity_controls
                    )
                )
            )

    def _toggle_expanded(self, _event: ft.Event[ft.IconButton]) -> None:
        self.is_expanded = not self.is_expanded
        self.activity_content.visible = self.is_expanded
        self.toggle_button.icon = (
            ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        )
        self.toggle_button.tooltip = (
            self.lang["generic.collapse"]
            if self.is_expanded
            else self.lang["generic.expand"]
        )
        if self._page is not None:
            self._page.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width


class CreateGoalDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, currency: str, on_success: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.currency = currency
        self.on_success = on_success
        self.initial_surplus = Decimal(0)

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["savings.create_goal_title"], color=Color.PRIMARY_TEXT, expand=True)
        self.submit_button_label = Text.BUTTON(self.lang["savings.save_objective"], color=Color.WHITE)

        # Static icons
        self.submit_button_icon = ft.Icon(ft.Icons.ADD_CIRCLE, color=Color.WHITE)

        # Dynamic texts
        self.error_text = Text.SMALL("", color=Color.NEGATIVE_ACTION)

        # CONTAINER COMPONENTS
        self.close_button = ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.dismiss(), icon_color=Color.PRIMARY_TEXT)

        self.surplus_banner = ft.Container(visible=False)

        self.goal_title_input = ft.TextField(
            label=self.lang["savings.objective_title"],
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION
        )

        self.goal_amount_input = ft.TextField(
            label=self.lang["savings.target_amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=FLOAT_REGEX
            ),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION
        )

        self.reason_input = ft.TextField(
            label=self.lang["savings.reason"],
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION
        )

        self.error_container = ft.Container(
            content=self.error_text,
            visible=False,
            padding=10,
            bgcolor=Color.ERROR_TEXT,
            border_radius=12
        )

        self.submit_button = ft.Button(
            content=ft.Row(
                controls=[self.submit_button_icon, self.submit_button_label],
                spacing=6
            ),
            on_click=self._process_submit,
            bgcolor=Color.PRIMARY_ACTION,
            height=52,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16))
        )

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.title_text,
                self.close_button
            ]
        )

        self.content_column = ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                header_row,
                self.surplus_banner,
                self.error_container,
                self.goal_title_input,
                self.goal_amount_input,
                self.reason_input,
                ft.Container(height=10),
                self.submit_button
            ]
        )

        self.main_container = ft.Container(
            padding=24,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=self.content_column
        )

        super().__init__(
            dialog_content=self.main_container, color=Color.TRANSPARENT, padding=0
        )

        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)

    def trigger(self, initial_surplus: Decimal = Decimal(0)) -> None:
        self.initial_surplus = initial_surplus
        if initial_surplus > 0:
            self.title_text.value = self.lang["savings.create_goal_from_surplus_title"]
            self.goal_title_input.value = self.lang["savings.next_objective"]
            self.goal_amount_input.value = format(initial_surplus * 5, "f")
            self.reason_input.value = self.lang["savings.surplus_reason"].format(
                amount=format_number(initial_surplus, decimals=0),
                currency=self.currency
            )
            self.surplus_banner.visible = True
            surplus_prefill_text = Text.SMALL(
                self.lang["savings.surplus_prefill"].format(
                    amount=format_number(initial_surplus, decimals=0),
                    currency=self.currency
                ),
                color=Color.PRIMARY
            )
            self.surplus_banner.content = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color=Color.PRIMARY),
                    surplus_prefill_text
                ]
            )
            self.surplus_banner.bgcolor = Color.LIGHT_ACCENT
            self.surplus_banner.padding = 12
            self.surplus_banner.border_radius = 16
        else:
            self.title_text.value = self.lang["savings.create_goal_title"]
            self.goal_title_input.value = ""
            self.goal_amount_input.value = ""
            self.reason_input.value = ""
            self.surplus_banner.visible = False

        self.error_container.visible = False
        self.show()

    def _process_submit(self, _event: ft.Event[ft.Button]) -> None:
        title = (
            self.goal_title_input.value.strip() if self.goal_title_input.value else ""
        )
        if not title:
            self.error_text.value = self.lang["savings.error.title_required"]
            self.error_container.visible = True
            self.main_container.update()
            return

        try:
            target = to_decimal(self.goal_amount_input.value or 0)
        except ValueError:
            target = Decimal(0)

        if target <= 0:
            self.error_text.value = self.lang["savings.error.target_must_be_positive"]
            self.error_container.visible = True
            self.main_container.update()
            return

        if self.initial_surplus > 0 and target < self.initial_surplus:
            self.error_text.value = self.lang["savings.error.target_below_surplus"]
            self.error_container.visible = True
            self.main_container.update()
            return

        reason = (
            self.reason_input.value.strip()
            if self.reason_input.value
            else self.lang["savings.no_reason"]
        )

        if self.initial_surplus > 0:
            success = self.controller.create_goal_with_surplus(
                title, reason, target, self.initial_surplus
            )
        else:
            success = self.controller.add_new_objective(title, reason, target)

        if success:
            self.dismiss()
            self.on_success()

    def resize(self, outer_width: int, content_width: int) -> None:
        self.main_container.width = outer_width
        self.content_column.width = content_width
        self.goal_title_input.width = content_width
        self.goal_amount_input.width = content_width
        self.reason_input.width = content_width
        self.surplus_banner.width = content_width
        self.submit_button.width = content_width


class DepositWithdrawDialog(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, on_success: Callable[..., None], on_surplus: Callable[..., None], on_action_message: Callable[[int, str, bool], Awaitable[None]] | None = None) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.on_surplus = on_surplus
        self.on_action_message = on_action_message
        self.goal = None
        self.mode = "deposit"

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["savings.deposit_title"], color=Color.PRIMARY_TEXT, expand=True)
        self.overview_title = Text.SMALL(self.lang["savings.goal_overview"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.progress_label = Text.SMALL(self.lang["savings.progress_toward_goal"], color=Color.SECONDARY_TEXT)
        self.current_goal_label = Text.MEDIUM(self.lang["savings.current_goal"], color=Color.SECONDARY_TEXT)
        self.saved_label = Text.MEDIUM(self.lang["savings.saved"], color=Color.SECONDARY_TEXT)
        self.remaining_label = Text.MEDIUM(self.lang["savings.remaining_label"], color=Color.SECONDARY_TEXT)

        # Dynamic texts
        self.goal_title = Text.MEDIUM("", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.target_amount = Text.MEDIUM("", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.progress_text = Text.SMALL("", color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.saved_text = Text.MEDIUM("", color=Color.PRIMARY_ACTION, weight=ft.FontWeight.BOLD)
        self.remaining_text = Text.MEDIUM("", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self._close,
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"]
        )

        self.progress_bar = ft.ProgressBar(
            value=0,
            color=Color.PRIMARY_ACTION,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            bar_height=12,
            border_radius=8
        )

        self.summary_card = ft.Container(
            padding=14,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.current_goal_label,
                            self.target_amount
                        ]
                    ),
                    self.goal_title,
                    self.progress_label,
                    ft.Stack(
                        height=16,
                        controls=[
                            self.progress_bar,
                            ft.Container(
                                alignment=ft.Alignment.CENTER_RIGHT,
                                padding=ft.Padding.only(right=8),
                                content=self.progress_text
                            )
                        ]
                    )
                ]
            )
        )

        self.balance_card = ft.Container(
            padding=14,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.saved_label,
                            self.saved_text
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.remaining_label,
                            self.remaining_text
                        ]
                    )
                ]
            )
        )

        self.keyboard_container = KeyboardContainer(
            page=self._page,
            lang=self.lang,
            on_save=self._process_keyboard_save
        )

        self.keyboard_container.bottom = 0

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.title_text,
                self.close_button
            ]
        )

        self.content_column = ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header_row,
                self.overview_title,
                self.summary_card,
                self.balance_card
            ]
        )

        self.main_container = ft.Container(
            padding=24,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=self.content_column
        )

        self.backdrop = ft.Container(
            expand=True,
            bgcolor="#80000000",
            on_click=self._ignore_backdrop_click
        )

        self.dialog_panel = ft.Container(
            left=0,
            right=0,
            top=16,
            alignment=ft.Alignment.CENTER,
            content=self.main_container
        )

        self.overlay_stack = ft.SafeArea(
            expand=True,
            content=ft.Stack(
                expand=True,
                controls=[
                    self.backdrop,
                    self.dialog_panel,
                    self.keyboard_container
                ]
            )
        )

        super().__init__(
            expand=True,
            visible=False,
            content=self.overlay_stack
        )

        if self._page.overlay is not None and self not in self._page.overlay:
            self._page.overlay.append(self)

    def trigger(self, goal: dict[str, Any], mode: str) -> None:
        self.goal = goal
        self.mode = mode
        is_deposit = mode == "deposit"

        self.title_text.value = (
            self.lang["savings.deposit_title"]
            if is_deposit
            else self.lang["savings.withdraw_title"]
        )
        current_saved, target_amount = self.controller.get_objective_amounts(
            int(goal["objective_id"])
        )
        remaining_amount = max(Decimal(0), target_amount - current_saved)
        progress = min(current_saved / target_amount, Decimal(1)) if target_amount > 0 else Decimal(0)
        currency = self.controller.get_currency()

        self.goal_title.value = goal["title"]
        self.target_amount.value = f"{format_number(target_amount)} {currency}"
        self.progress_text.value = f"{int(progress * 100)}%"
        self.progress_bar.value = float(progress)
        self.saved_text.value = f"{format_number(current_saved)} {currency}"
        self.remaining_text.value = f"{format_number(remaining_amount)} {currency}"

        self.keyboard_container.visible = True
        self.visible = True
        self._page.update()
        self.keyboard_container.reset_inputs()

    def _close(self) -> None:
        self.keyboard_container.visible = False
        self.visible = False
        self._page.update()

    @staticmethod
    def _ignore_backdrop_click(_event: ft.Event[ft.Container]) -> None:
        pass

    def _process_keyboard_save(self, values: dict[str, Any]) -> None:
        try:
            amount = to_decimal(values.get("amount") or 0)
        except TypeError, ValueError:
            amount = Decimal(0)

        if amount <= 0:
            self._show_error(self.lang["savings.error.invalid_amount"])
            return

        if self.goal is None:
            Logger.error("Cannot save savings action without a selected goal")
            return

        objective_id = int(self.goal["objective_id"])
        success, error_key, current_saved, surplus, reached_target = (
            self.controller.process_quick_action(
                objective_id,
                self.mode,
                amount,
                values.get("date") or datetime.now().strftime("%Y-%m-%d %H:%M"),
                (values.get("note") or "").strip()
            )
        )

        if not success:
            message = self.lang.get(error_key, self.lang["savings.error.action_failed"])
            if "{remaining}" in message:
                message = message.format(
                    remaining=format_number(current_saved),
                    currency=self.controller.get_currency()
                )
            self._show_error(message)
            return

        self.keyboard_container.reset_inputs()
        self.keyboard_container.visible = False
        self.visible = False
        self.on_success()
        success_message_key = (
            "savings.success.deposit"
            if self.mode == "deposit"
            else "savings.success.withdraw"
        )
        self._schedule_action_message(
            self.lang[success_message_key],
            is_success=True
        )

        if surplus > 0 or reached_target:
            self.on_surplus(self.goal, surplus)

    def _show_error(self, message: str) -> None:
        if self.goal is None:
            Logger.error(
                f"Cannot display savings action error without a goal: {message}"
            )
            return
        if self.on_action_message is None:
            Logger.error(f"No savings action error handler is configured: {message}")
            return
        self._close()
        self._schedule_action_message(message, is_success=False)

    def _schedule_action_message(self, message: str, is_success: bool) -> None:
        if self.goal is None:
            Logger.error("Cannot schedule a savings action message without a goal")
            return
        if self.on_action_message is None:
            Logger.error("No savings action message handler is configured")
            return
        self._page.run_task(
            self.on_action_message,
            int(self.goal["objective_id"]),
            message,
            is_success
        )

    def resize(self, page_width: int, outer_width: int, content_width: int) -> None:
        self.main_container.width = outer_width
        self.dialog_panel.width = page_width
        self.content_column.width = content_width
        self.summary_card.width = content_width
        self.balance_card.width = content_width
        self.keyboard_container.width = page_width
        self.keyboard_container.resize(page_width)


class CongratulationsDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, currency: str, on_success: Callable[..., None], on_create_with_surplus: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.currency = currency
        self.on_success = on_success
        self.on_create_with_surplus = on_create_with_surplus
        self.completed_goal = None
        self.surplus_amount = Decimal(0)
        self.available_goals: list[dict[str, Any]] = []
        self.selected_target_id = None
        self.goal_option_cards: dict[int, ft.Container] = {}
        self.pending_followup: (tuple[dict[str, Any], Decimal, list[dict[str, Any]]] | None) = None
        self._confetti_canvas = flet_canvas.Canvas(
            visible=False,
            disabled=True,
            expand=True
        )
        self._confetti_generation = 0

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["savings.congratulations"], color=Color.PRIMARY_TEXT, expand=True)
        self.desc_text = Text.SMALL(self.lang["savings.goal_completed_desc"], color=Color.SECONDARY_TEXT)
        self.achievement_target_label = Text.SMALL(self.lang["savings.achievement_target"], color=Color.SECONDARY_TEXT)
        self.achievement_complete_label = Text.SMALL(self.lang["savings.achievement_complete"], color=Color.PRIMARY)
        self.achievement_excellent_label = Text.SMALL(self.lang["savings.achievement_excellent"], color=Color.SECONDARY_TEXT)

        # Dynamic texts
        self.target_amount_text = Text.H4("", color=Color.PRIMARY)

        # CONTAINER COMPONENTS
        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT
        )

        self.achievement_card = ft.Container(
            padding=16,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            content=ft.Column(
                [
                    ft.Row(
                        [self.achievement_target_label, self.target_amount_text],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.ProgressBar(value=1.0, color=Color.PRIMARY, height=8),
                    ft.Row(
                        [
                            self.achievement_complete_label,
                            self.achievement_excellent_label
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=8
            )
        )

        self.surplus_banner = ft.Container(visible=False)
        self.goals_dropdown_column = ft.Column(spacing=8)
        self.action_button_label = Text.BUTTON(
            self.lang["savings.transfer_surplus"], color=Color.WHITE
        )
        self.action_button = ft.Button(
            content=self.action_button_label,
            on_click=self._process_transfer,
            bgcolor=Color.PRIMARY_ACTION,
            color=Color.WHITE,
            height=50
        )

        self.content_column = ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Row(
                    [self.title_text, self.close_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Icon(ft.Icons.EMOJI_EVENTS, size=48, color=Color.ERROR_TEXT),
                self.desc_text,
                self.achievement_card,
                self.surplus_banner,
                self.goals_dropdown_column,
                self.action_button
            ]
        )
        self.main_container = ft.Container(
            padding=28,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=self.content_column
        )

        super().__init__(
            dialog_content=self.main_container, color=Color.TRANSPARENT, padding=0
        )

        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)
        self.on_dismiss = self._handle_dismiss

    def trigger(self, completed_goal: dict[str, Any], surplus_amount: Decimal, available_goals: list[dict[str, Any]], confetti: bool = False) -> None:
        self._confetti_generation += 1
        generation = self._confetti_generation
        if not confetti:
            self._confetti_canvas.visible = False
            self._confetti_canvas.shapes = []
            if self._confetti_canvas in self._page.overlay:
                self._page.overlay.remove(self._confetti_canvas)

        self.completed_goal = completed_goal
        self.surplus_amount = surplus_amount
        self.available_goals = [
            g
            for g in available_goals
            if g["objective_id"] != completed_goal["objective_id"]
        ]
        self.selected_target_id = None
        self.goal_option_cards.clear()
        self.goals_dropdown_column.controls = []

        self.title_text.value = self.lang["savings.goal_completed_title"].format(title=completed_goal["title"])
        self.target_amount_text.value = completed_goal["target_value"]

        if surplus_amount > 0:
            self.surplus_banner.visible = True
            surplus_exceeded_text = Text.SMALL(
                self.lang["savings.surplus_exceeded"].format(
                    amount=format_number(surplus_amount, decimals=0),
                    currency=self.currency
                ),
                color=Color.NEGATIVE_ACTION
            )
            surplus_description_text = Text.SMALL(
                self.lang["savings.surplus_transfer_desc"],
                color=Color.SECONDARY_TEXT,
                expand=True
            )
            self.surplus_banner.content = ft.Container(
                padding=12,
                bgcolor=Color.ERROR_TEXT,
                border_radius=16,
                content=ft.Row(
                    expand=True,
                    controls=[
                        ft.Icon(ft.Icons.ADD, color=Color.NEGATIVE_ACTION),
                        ft.Column(
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            spacing=2,
                            controls=[
                                surplus_exceeded_text,
                                surplus_description_text
                            ]
                        )
                    ]
                )
            )

            if self.available_goals:
                self.selected_target_id = self.available_goals[0]["objective_id"]
                goal_cards = []
                for g in self.available_goals:
                    is_selected = self.selected_target_id == g["objective_id"]
                    goal_title_text = Text.MEDIUM(
                        g["title"], color=Color.PRIMARY_TEXT
                    )
                    goal_surplus_text = Text.SMALL(
                        self.lang["savings.surplus_amount"].format(
                            amount=format_number(surplus_amount, decimals=0),
                            currency=self.currency
                        ),
                        color=Color.PRIMARY
                    )
                    option_card = ft.Container(
                        padding=10,
                        bgcolor=Color.LIGHT_ACCENT
                        if is_selected
                        else Color.CARD_BACKGROUND,
                        border=ft.Border.all(
                            2, Color.PRIMARY if is_selected else Color.INPUT_BORDER
                        ),
                        border_radius=12,
                        on_click=lambda e, gid=g["objective_id"]: self._select_target(
                            gid
                        ),
                        content=ft.Row(
                            [goal_title_text, goal_surplus_text],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    )
                    goal_cards.append(option_card)
                    self.goal_option_cards[g["objective_id"]] = option_card
                self.goals_dropdown_column.controls = goal_cards
                self.goals_dropdown_column.visible = True
                self.action_button.visible = True
                self.action_button.content = self.lang["savings.transfer_surplus"]
            else:
                self.goals_dropdown_column.visible = False
                self.action_button.visible = True
                self.action_button.content = self.lang[
                    "savings.create_goal_with_surplus"
                ]
        else:
            self.surplus_banner.visible = False
            self.goals_dropdown_column.visible = False
            self.action_button.visible = True
            self.action_button.content = self.lang["savings.continue_saving"]

        self.show()
        if confetti:
            self._page.run_task(self._animate_confetti, generation)

    async def _animate_confetti(self, generation: int) -> None:
        width = max(float(self._page.width or 800), 1)
        height = max(float(self._page.height or 600), 1)
        colors = ["#F44336", "#FFC107", "#4CAF50", "#2196F3", "#9C27B0", "#FF9800"]
        paints = {color: ft.Paint(color=color) for color in colors}
        particles = []
        for _ in range(120):
            x = random.uniform(0, width)
            y = random.uniform(-height * 0.25, height * 0.65)
            size = random.uniform(5, 10)
            color = random.choice(colors)
            shape = flet_canvas.Rect(
                x,
                y,
                size,
                size * 1.6,
                paint=paints[color]
            )
            particles.append(
                (x, y, random.uniform(-1.5, 1.5), random.uniform(3, 6), size, shape)
            )

        self._confetti_canvas.width = width
        self._confetti_canvas.height = height
        self._confetti_canvas.left = 0
        self._confetti_canvas.top = 0
        self._confetti_canvas.shapes = [particle[5] for particle in particles]
        self._confetti_canvas.visible = True
        if self._confetti_canvas in self._page.overlay:
            self._page.overlay.remove(self._confetti_canvas)
        self._page.overlay.append(self._confetti_canvas)
        self._page.update()

        loop = asyncio.get_running_loop()
        animation_start = loop.time()
        for frame in range(300):
            if generation != self._confetti_generation:
                return

            updated_particles = []
            for x, y, x_speed, y_speed, size, shape in particles:
                x += x_speed
                y += y_speed
                if y < height:
                    shape.x = x
                    shape.y = y
                    updated_particles.append(
                        (x, y, x_speed, y_speed + 0.01, size, shape)
                    )
            particles = updated_particles
            self._confetti_canvas.shapes = [particle[5] for particle in particles]
            self._confetti_canvas.update()
            next_frame = animation_start + (frame + 1) / 60
            await asyncio.sleep(max(0, next_frame - loop.time()))

        self._confetti_canvas.visible = False
        self._confetti_canvas.shapes = []
        if self._confetti_canvas in self._page.overlay:
            self._page.overlay.remove(self._confetti_canvas)
        self._page.update()

    def _select_target(self, objective_id: int) -> None:
        if objective_id not in self.goal_option_cards:
            return

        self.selected_target_id = objective_id
        for goal in self.available_goals:
            is_selected = goal["objective_id"] == objective_id
            option_card = self.goal_option_cards[goal["objective_id"]]
            option_card.bgcolor = (
                Color.LIGHT_ACCENT if is_selected else Color.CARD_BACKGROUND
            )
            option_card.border = ft.Border.all(
                2, Color.PRIMARY if is_selected else Color.INPUT_BORDER
            )
        self._page.update()

    def _handle_dismiss(self, _event: ft.Event[ft.DialogControl]) -> None:
        if self.pending_followup is None:
            return

        completed_goal, surplus_amount, available_goals = self.pending_followup
        self.pending_followup = None
        self.trigger(completed_goal, surplus_amount, available_goals)

    def _process_transfer(self, _event: ft.Event[ft.Button]) -> None:
        if self.surplus_amount > 0 and self.available_goals and self.selected_target_id:
            if self.completed_goal is None:
                Logger.error("Cannot transfer surplus without a completed goal")
                return
            target_goal = next(
                (
                    goal
                    for goal in self.available_goals
                    if goal["objective_id"] == self.selected_target_id
                ),
                None
            )
            if target_goal is None:
                Logger.error(
                    f"Selected transfer objective {self.selected_target_id} is unavailable"
                )
                return

            success, remaining_surplus = self.controller.transfer_surplus(
                int(self.completed_goal["objective_id"]),
                int(self.selected_target_id),
                self.surplus_amount
            )
            if not success:
                Logger.error(
                    f"Failed to transfer surplus to objective {self.selected_target_id}"
                )
                return

            if remaining_surplus > 0:
                self.pending_followup = (
                    target_goal,
                    remaining_surplus,
                    self.available_goals
                )
            self.dismiss()
            self.on_success()
        elif self.surplus_amount > 0 and not self.available_goals:
            self.dismiss()
            self.on_create_with_surplus(self.surplus_amount)
        else:
            self.dismiss()
            self.on_success()

    def resize(self, outer_width: int, content_width: int) -> None:
        self.main_container.width = outer_width
        self.content_column.width = content_width
        self.achievement_card.width = content_width
        self.surplus_banner.width = content_width
        self.goals_dropdown_column.width = content_width
        self.action_button.width = content_width


class DeleteConfirmDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, on_success: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["savings.delete_objective_title"], color=Color.PRIMARY_TEXT)
        self.desc_text = Text.P(self.lang["savings.delete_objective_desc"], color=Color.DEFAULT_TEXT)
        self.delete_button_label = Text.BUTTON(self.lang["generic.delete"], color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=self._close_dialog,
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"]
        )

        self.delete_button = ft.Button(
            content=self.delete_button_label,
            on_click=self._delete,
            bgcolor=Color.DELETE_ACTION
        )

        self.content_column = ft.Column(
            tight=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.title_text,
                        self.close_button
                    ]
                ),
                self.desc_text
            ],
            spacing=12
        )
        self.main_container = ft.Container(
            content=self.content_column,
            padding=20
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.delete_button],
            padding=0
        )

        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)

    def trigger(self, objective_id: int) -> None:
        self.current_id = objective_id
        self.show()

    def _close_dialog(self, _event: ft.Event[ft.IconButton]) -> None:
        self.dismiss()

    def _delete(self, _event: ft.Event[ft.Button]) -> None:
        self.controller.delete_objective(self.current_id)
        self.dismiss()
        self.on_success()

    def resize(self, outer_width: int, content_width: int, title_width: int) -> None:
        self.main_container.width = outer_width
        self.content_column.width = content_width
        self.title_text.width = title_width
        self.desc_text.width = content_width


class ClearHistoryDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, on_success: Callable[..., None]) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["savings.clear_history_title"], color=Color.PRIMARY_TEXT)
        self.desc_text = Text.P(self.lang["savings.clear_history_desc"])
        self.clear_button_label = Text.BUTTON(self.lang["savings.clear_history"], color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"]
        )

        self.clear_button = ft.Button(
            content=self.clear_button_label,
            on_click=self._process,
            bgcolor=Color.DELETE_ACTION
        )

        self.content_column = ft.Column(
            tight=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[self.title_text, self.close_button]
                ),
                self.desc_text
            ],
            spacing=12
        )
        self.main_container = ft.Container(
            content=self.content_column,
            padding=20
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.clear_button],
            padding=0
        )

        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)

    def trigger(self) -> None:
        self.show()

    def _process(self, _event: ft.Event[ft.Button]) -> None:
        self.controller.clear_activity_history()
        self.dismiss()
        self.on_success()

    def resize(self, outer_width: int, content_width: int, title_width: int) -> None:
        self.main_container.width = outer_width
        self.content_column.width = content_width
        self.title_text.width = title_width
        self.desc_text.width = content_width
