# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from datetime import datetime

import flet as ft

from src.utils import Color, Dialog, Page, Text


class ObjectiveCard(ft.Container):
    def __init__(self, page: Page, lang: dict, objective_id: int, objective_title: str, subtitle: str, current_value: str, target_value: str, remaining_value: str, percentage: str, progress: float, completed: bool, on_click_callback: Callable):
        self._page = page
        self.lang = lang
        self.objective_id = objective_id
        self.objective_title = objective_title
        self.subtitle = subtitle
        self.current_value = current_value
        self.target_value = target_value
        self.remaining_value = remaining_value
        self.percentage = percentage
        self.progress = progress
        self.completed = completed
        self.on_click_callback = on_click_callback

        badge_bg = Color.PROGRESS_ACTIVE if self.completed else Color.LIGHT_ACCENT
        badge_text_color = Color.WHITE if self.completed else Color.PRIMARY

        on_action = (
            lambda e: self.on_click_callback(e.page, self.objective_id, self.objective_title, self.subtitle, self.current_value, self.target_value, self.progress, self.completed)
            if self.on_click_callback else None
        )

        self.title_text = Text.H4(self.objective_title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.completed_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.PROGRESS_ACTIVE, size=18) if self.completed else ft.Container()
        self.subtitle_text = Text.MEDIUM(self.subtitle, color=Color.SECONDARY_TEXT)
        self.badge_text = Text.BADGE(self.percentage, color=badge_text_color, weight=ft.FontWeight.BOLD)

        self.accumulated_label = Text.MEDIUM(self.lang["savings.accumulated"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.current_value_text = Text.H4(self.current_value, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.target_text = Text.SMALL(self.lang["savings.target"].format(target_value=self.target_value), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)
        self.remaining_text = Text.SMALL(self.remaining_value, color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)

        self.progress_bar = ft.ProgressBar(
            value=self.progress,
            color=Color.PRIMARY,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            height=10
        )

        self.badge_container = ft.Container(
            content=self.badge_text,
            bgcolor=badge_bg,
            padding=ft.Padding(12, 6, 12, 6),
            border_radius=16,
        )

        self.title_row = ft.Row(
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
                                self.completed_icon
                            ]
                        ),
                        self.subtitle_text,
                    ]
                ),
                self.badge_container
            ]
        )

        self.progress_row = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.accumulated_label,
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
        )

        self.main_container = ft.Column(
            spacing=16,
            controls=[
                self.title_row,
                self.progress_row
            ]
        )

        super().__init__(
            bgcolor=Color.GOAL_ITEM_BACKGROUND if self.completed else Color.CARD_BACKGROUND,
            border_radius=24,
            padding=24,
            border=ft.Border.all(2, Color.PROGRESS_BACKGROUND) if self.completed else None,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW) if not self.completed else None,
            on_click=on_action,
            ink=True,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.width = max(width, 0)
        self.main_container.width = max(width, 0)


class ObjectiveGrid(ft.Column):
    def __init__(self, page: Page, lang: dict, objectives_data: list, on_card_click: Callable):
        self._page = page
        self.lang = lang
        self.on_card_click = on_card_click
        super().__init__(spacing=20)
        self.update_grid(objectives_data)

    def update_grid(self, objectives_data: list):
        cards = []
        for data in objectives_data:
            cards.append(ObjectiveCard(
                page=self._page,
                lang=self.lang,
                objective_id=data["objective_id"],
                objective_title=data["title"],
                subtitle=data["reason"],
                current_value=data["current_value"],
                target_value=data["target_value"],
                remaining_value=data["remaining_value"],
                percentage=data["percentage"],
                progress=data["progress"],
                completed=data["completed"],
                on_click_callback=self.on_card_click
            ))
        self.controls = cards

    def resize(self, width: int) -> None:
        self.width = max(width, 0)


class AggregateCard(ft.Container):
    def __init__(self, page: Page, lang: dict, total_savings: float, total_target: float, percentage: str, progress_value: float, currency: str, on_create_click: Callable):
        self._page = page
        self.lang = lang
        self.currency = currency

        self.title_text = Text.MEDIUM(self.lang["savings.fund_management"].upper(), color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.progress_label = Text.MEDIUM(self.lang["savings.progress"], color=Color.WHITE)
        self.savings_text = Text.H3(f"{total_savings:,.2f}".translate(str.maketrans(".,", ",.")), color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.target_text = Text.H5(f" / {total_target:,.2f}".translate(str.maketrans(".,", ",.")) + f" {self.currency}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.percentage_text = Text.MEDIUM(f"{percentage}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)

        self.add_icon = ft.Icon(ft.Icons.ADD, color=Color.PRIMARY, size=16)
        self.progress_bar = ft.ProgressBar(value=progress_value, color=Color.LIGHT_ACCENT, bgcolor=Color.DARK_SURFACE, height=8, border_radius=4)

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
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=8,
                            controls=[
                                self.pill_container,
                                ft.Row(
                                    vertical_alignment=ft.CrossAxisAlignment.END,
                                    controls=[self.savings_text, self.target_text]
                                ),
                                ft.Row(
                                    controls=[
                                        self.progress_label,
                                        self.percentage_text,
                                    ]
                                )
                            ]
                        ),
                        self.add_button_container
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

    def update_data(self, total_savings: float, total_target: float, percentage: str, progress_value: float, currency: str):
        self.savings_text.value = f"{total_savings:,.2f}".translate(str.maketrans(".,", ",."))
        self.currency = currency
        self.target_text.value = f" / {total_target:,.2f}".translate(str.maketrans(".,", ",.")) + f" {self.currency}"
        self.percentage_text.value = percentage
        self.progress_bar.value = progress_value

    def resize(self, width: int) -> None:
        self.width = max(width, 0)
        self.main_container.width = max(width, 0)


class CreateGoalModal(Dialog):
    """Matches CreateGoalModal.tsx"""
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.initial_surplus = 0.0

        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(e.page),
            icon_color=Color.PRIMARY_TEXT,
        )
        self.title_text = Text.H3(self.lang["savings.create_goal_title"], color=Color.DEFAULT_TEXT)

        self.surplus_banner = ft.Container(visible=False)

        self.goal_title_input = ft.TextField(
            label=self.lang["savings.objective_title"],
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.goal_amount_input = ft.TextField(
            label=self.lang["savings.target_amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.reason_input = ft.TextField(
            label=self.lang["savings.reason"],
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.error_text = Text.SMALL("", color=Color.NEGATIVE_ACTION)
        self.error_container = ft.Container(content=self.error_text, visible=False, padding=10, bgcolor=Color.ERROR_TEXT, border_radius=12)

        self.submit_button = ft.Button(
            self.lang["savings.save_objective"],
            icon=ft.Icons.ADD_CIRCLE,
            on_click=self._process_submit,
            bgcolor=Color.PRIMARY_ACTION,
            color=Color.WHITE,
            width=390,
            height=52,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
        )

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.close_button,
                self.title_text,
                ft.Container(width=40),
            ],
        )

        self.main_container = ft.Container(
            width=390,
            padding=24,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=ft.Column(
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
                    self.submit_button,
                ],
            ),
        )

        super().__init__(dialog_content=self.main_container, color=Color.TRANSPARENT)

    def trigger(self, page: Page, initial_surplus: float = 0.0):
        self.initial_surplus = initial_surplus
        if initial_surplus > 0:
            self.title_text.value = self.lang["savings.create_goal_from_surplus_title"]
            self.goal_title_input.value = self.lang["savings.next_objective"]
            self.goal_amount_input.value = str(int(initial_surplus * 5))
            self.reason_input.value = self.lang["savings.surplus_reason"].format(amount=f"{initial_surplus:,.0f}")
            self.surplus_banner.visible = True
            self.surplus_banner.content = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color=Color.PRIMARY),
                    Text.SMALL(self.lang["savings.surplus_prefill"].format(amount=f"{initial_surplus:,.0f}"), color=Color.PRIMARY)
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
        self.show(page)

    def _process_submit(self, e):
        title = self.goal_title_input.value.strip() if self.goal_title_input.value else ""
        if not title:
            self.error_text.value = self.lang["savings.error.title_required"]
            self.error_container.visible = True
            self.main_container.update()
            return

        try:
            target = float(self.goal_amount_input.value or 0)
        except ValueError:
            target = 0.0

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

        reason = self.reason_input.value.strip() if self.reason_input.value else self.lang["savings.no_reason"]

        if self.initial_surplus > 0:
            success = self.controller.create_goal_with_surplus(title, reason, target, self.initial_surplus)
        else:
            success = self.controller.add_new_objective(title, reason, target)

        if success:
            Dialog.close_most_recent_dialog(e.page)
            self.on_success()


class DepositWithdrawModal(Dialog):
    """Matches DepositWithdrawModal.tsx"""
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable, on_surplus: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.on_surplus = on_surplus
        self.goal = None
        self.mode = "deposit"

        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(e.page),
            icon_color=Color.PRIMARY_TEXT,
        )
        self.title_text = Text.H3(self.lang["savings.deposit_title"], color=Color.DEFAULT_TEXT)

        self.goal_info_text = Text.SMALL("", color=Color.SECONDARY_TEXT)
        self.goal_amount_info = Text.SMALL("", color=Color.PRIMARY)
        self.summary_card = ft.Container(
            padding=14,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column([Text.SMALL(self.lang["savings.objective"], color=Color.SECONDARY_TEXT), self.goal_info_text], spacing=2),
                    ft.Column([Text.SMALL(self.lang["savings.saved_and_needed"], color=Color.SECONDARY_TEXT), self.goal_amount_info], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
                ]
            )
        )

        self.amount_input = ft.TextField(
            label="0",
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.note_input = ft.TextField(
            label=self.lang["savings.optional_note"],
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.error_text = Text.SMALL("", color=Color.NEGATIVE_ACTION)
        self.error_container = ft.Container(content=self.error_text, visible=False, padding=10, bgcolor=Color.ERROR_TEXT, border_radius=12)

        self.submit_button = ft.Button(
            self.lang["savings.confirm_deposit"],
            icon=ft.Icons.ARROW_DOWNWARD,
            on_click=self._process_submit,
            bgcolor=Color.PRIMARY_ACTION,
            color=Color.WHITE,
            width=390,
            height=52,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
        )

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.close_button,
                self.title_text,
                ft.Container(width=40),
            ],
        )

        self.main_container = ft.Container(
            width=390,
            padding=24,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    header_row,
                    self.summary_card,
                    self.error_container,
                    self.amount_input,
                    self.note_input,
                    ft.Container(height=10),
                    self.submit_button,
                ],
            ),
        )

        super().__init__(dialog_content=self.main_container, color=Color.TRANSPARENT)

    def trigger(self, page: Page, goal: dict, mode: str):
        self.goal = goal
        self.mode = mode
        is_deposit = mode == "deposit"

        self.title_text.value = self.lang["savings.deposit_title"] if is_deposit else self.lang["savings.withdraw_title"]
        self.goal_info_text.value = goal["title"]
        self.goal_amount_info.value = f"{goal['current_value']} / {goal['target_value']}"
        self.amount_input.value = ""
        self.note_input.value = ""
        self.error_container.visible = False

        self.submit_button.content = self.lang["savings.confirm_deposit"] if is_deposit else self.lang["savings.confirm_withdraw"]
        self.submit_button.bgcolor = Color.PRIMARY_ACTION if is_deposit else Color.NEGATIVE_ACTION

        self.show(page)

    def _process_submit(self, e):
        try:
            amount = float(self.amount_input.value or 0)
        except ValueError:
            amount = 0.0

        if amount <= 0:
            self.error_text.value = self.lang["savings.error.invalid_amount"]
            self.error_container.visible = True
            self.main_container.update()
            return

        objective_id = int(self.goal["objective_id"])
        current_saved, target_amount = self.controller.get_objective_amounts(objective_id)

        if self.mode == "withdraw" and amount > current_saved:
            self.error_text.value = self.lang["savings.error.withdraw_exceeds_balance"]
            self.error_container.visible = True
            self.main_container.update()
            return

        success, error_key, _, surplus = self.controller.process_quick_action(
            objective_id,
            self.mode,
            amount,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            self.note_input.value.strip() if self.note_input.value else ""
        )

        if not success:
            self.error_text.value = self.lang["savings.error.action_failed"]
            self.error_container.visible = True
            self.main_container.update()
            return

        Dialog.close_most_recent_dialog(e.page)
        self.on_success()

        if surplus > 0:
            self.on_surplus(e.page, self.goal, surplus)


class CongratulationsModal(Dialog):
    """Matches CongratulationsModal.tsx"""
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable, on_create_with_surplus: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.on_create_with_surplus = on_create_with_surplus
        self.completed_goal = None
        self.surplus_amount = 0.0
        self.available_goals = []
        self.selected_target_id = None

        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(e.page),
            icon_color=Color.PRIMARY_TEXT,
        )

        self.goal_title_text = Text.H3(self.lang["savings.congratulations"], color=Color.DEFAULT_TEXT)
        self.desc_text = Text.SMALL(self.lang["savings.goal_completed_desc"], color=Color.SECONDARY_TEXT)

        self.target_amount_text = Text.H4("", color=Color.PRIMARY)
        self.achievement_card = ft.Container(
            padding=16,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            content=ft.Column([
                ft.Row([Text.SMALL(self.lang["savings.achievement_target"], color=Color.SECONDARY_TEXT), self.target_amount_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ProgressBar(value=1.0, color=Color.PRIMARY, height=8),
                ft.Row([Text.SMALL(self.lang["savings.achievement_complete"], color=Color.PRIMARY), Text.SMALL(self.lang["savings.achievement_excellent"], color=Color.SECONDARY_TEXT)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8)
        )

        self.surplus_banner = ft.Container(visible=False)
        self.goals_dropdown_column = ft.Column(spacing=8)
        self.action_button = ft.Button(self.lang["savings.transfer_surplus"], on_click=self._process_transfer, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE, width=380, height=50)
        self.create_new_button = ft.TextButton(self.lang["savings.create_goal_with_surplus_alternative"], icon=ft.Icons.ADD_CIRCLE, on_click=self._process_create_new)

        self.main_container = ft.Container(
            width=420,
            padding=28,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=32,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Row([self.close_button], alignment=ft.MainAxisAlignment.END),
                    ft.Icon(ft.Icons.EMOJI_EVENTS, size=48, color=Color.PRIMARY),
                    self.goal_title_text,
                    self.desc_text,
                    self.achievement_card,
                    self.surplus_banner,
                    self.goals_dropdown_column,
                    self.action_button,
                    self.create_new_button,
                ],
            ),
        )

        super().__init__(dialog_content=self.main_container, color=Color.TRANSPARENT)

    def trigger(self, page: Page, completed_goal: dict, surplus_amount: float, available_goals: list):
        self.completed_goal = completed_goal
        self.surplus_amount = surplus_amount
        self.available_goals = [g for g in available_goals if g["objective_id"] != completed_goal["objective_id"]]

        self.goal_title_text.value = self.lang["savings.goal_completed_title"].format(title=completed_goal["title"])
        self.target_amount_text.value = completed_goal["target_value"]

        if surplus_amount > 0:
            self.surplus_banner.visible = True
            self.surplus_banner.content = ft.Container(
                padding=12,
                bgcolor=Color.ERROR_TEXT,
                border_radius=16,
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, color=Color.NEGATIVE_ACTION),
                    ft.Column([
                        Text.SMALL(self.lang["savings.surplus_exceeded"].format(amount=f"{surplus_amount:,.0f}"), color=Color.NEGATIVE_ACTION),
                        Text.SMALL(self.lang["savings.surplus_transfer_desc"], color=Color.SECONDARY_TEXT)
                    ], spacing=2)
                ])
            )

            if self.available_goals:
                self.selected_target_id = self.available_goals[0]["objective_id"]
                goal_cards = []
                for g in self.available_goals:
                    is_selected = self.selected_target_id == g["objective_id"]
                    goal_cards.append(
                        ft.Container(
                            padding=10,
                            bgcolor=Color.LIGHT_ACCENT if is_selected else Color.CARD_BACKGROUND,
                            border=ft.Border.all(2, Color.PRIMARY if is_selected else Color.INPUT_BORDER),
                            border_radius=12,
                            on_click=lambda e, gid=g["objective_id"]: self._select_target(gid),
                            content=ft.Row([
                                Text.MEDIUM(g["title"], color=Color.PRIMARY_TEXT),
                                Text.SMALL(self.lang["savings.surplus_amount"].format(amount=f"{surplus_amount:,.0f}"), color=Color.PRIMARY)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        )
                    )
                self.goals_dropdown_column.controls = goal_cards
                self.goals_dropdown_column.visible = True
                self.action_button.visible = True
                self.action_button.content = self.lang["savings.transfer_surplus_selected"]
            else:
                self.goals_dropdown_column.visible = False
                self.action_button.visible = True
                self.action_button.content = self.lang["savings.create_goal_with_surplus"]
        else:
            self.surplus_banner.visible = False
            self.goals_dropdown_column.visible = False
            self.action_button.content = self.lang["savings.continue_saving"]
            self.create_new_button.visible = False

        self.show(page)

    def _select_target(self, objective_id: int):
        self.selected_target_id = objective_id
        # Re-render list selection
        self.trigger(self._page, self.completed_goal, self.surplus_amount, self.available_goals)

    def _process_transfer(self, e):
        if self.surplus_amount > 0 and self.available_goals and self.selected_target_id:
            self.controller.transfer_surplus(int(self.completed_goal["objective_id"]), int(self.selected_target_id), self.surplus_amount)
            Dialog.close_most_recent_dialog(e.page)
            self.on_success()
        elif self.surplus_amount > 0 and not self.available_goals:
            Dialog.close_most_recent_dialog(e.page)
            self.on_create_with_surplus(e.page, self.surplus_amount)
        else:
            Dialog.close_most_recent_dialog(e.page)
            self.on_success()

    def _process_create_new(self, e):
        Dialog.close_most_recent_dialog(e.page)
        self.on_create_with_surplus(e.page, self.surplus_amount)


class CompleteConfirmDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable, on_congratulate: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.on_congratulate = on_congratulate
        self.current_goal = None

        self.desc_text = Text.P(self.lang["savings.complete_objective_desc"], color=Color.DEFAULT_TEXT)
        self.title_text = Text.H3(self.lang["savings.complete_objective_title"], color=Color.PRIMARY_TEXT)

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.complete_button = ft.Button(self.lang["generic.complete"], on_click=self._process, bgcolor=Color.COMPLETED_ACTION, color=Color.WHITE)

        self.main_container = ft.Container(content=self.desc_text)
        super().__init__(dialog_content=self.main_container, color=Color.DIALOG_BACKGROUND)
        self.title = self.title_text
        self.actions = [self.cancel_button, self.complete_button]

    def trigger(self, page: Page, goal: dict):
        self.current_goal = goal
        self.show(page)

    def _process(self, e):
        objective_id = int(self.current_goal["objective_id"])
        self.controller.complete_objective(objective_id)
        Dialog.close_most_recent_dialog(e.page)
        self.on_success()
        self.on_congratulate(e.page, self.current_goal, 0.0)


class DeleteConfirmDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0

        self.desc_text = Text.P(self.lang["savings.delete_objective_desc"], color=Color.DEFAULT_TEXT)
        self.title_text = Text.H3(self.lang["savings.delete_objective_title"], color=Color.PRIMARY_TEXT)

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.delete_button = ft.Button(self.lang["generic.delete"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)

        self.main_container = ft.Container(content=self.desc_text)
        super().__init__(dialog_content=self.main_container, color=Color.DIALOG_BACKGROUND)
        self.title = self.title_text
        self.actions = [self.cancel_button, self.delete_button]

    def trigger(self, page: Page, objective_id: int):
        self.current_id = objective_id
        self.show(page)

    def _process(self, e):
        self.controller.delete_objective(self.current_id)
        Dialog.close_most_recent_dialog(e.page)
        self.on_success()


class ClearHistoryDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable, trigger_export: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success

        self.desc_text = Text.P(self.lang["savings.clear_history_desc"])
        self.title_text = Text.H3(self.lang["savings.clear_history_title"])

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.export_button = ft.Button(self.lang["savings.export_ledger"], on_click=trigger_export, bgcolor=Color.PROGRESS_ACTIVE, color=Color.WHITE)
        self.clear_button = ft.Button(self.lang["savings.clear_history"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)

        super().__init__(dialog_content=self.desc_text, color=Color.DIALOG_BACKGROUND)
        self.title = self.title_text
        self.actions = [self.cancel_button, self.export_button, self.clear_button]

    def _process(self, e):
        self.controller.clear_activity_history()
        Dialog.close_most_recent_dialog(e.page)
        self.on_success()


class GoalDetailsDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_complete: Callable, on_deposit_withdraw: Callable, on_delete: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_complete = on_complete
        self.on_deposit_withdraw = on_deposit_withdraw
        self.on_delete = on_delete

        super().__init__(dialog_content=ft.Container(), color=Color.TRANSPARENT)
        self.content_padding = 0

    def trigger(self, page: Page, objective_id: int, goal_title: str, subtitle: str, current_value: str, target_value: str, progress: float, completed: bool):
        goal_data = {
            "objective_id": objective_id,
            "title": goal_title,
            "reason": subtitle,
            "current_value": current_value,
            "target_value": target_value,
            "progress": progress,
            "completed": completed
        }

        bg_ring = ft.ProgressRing(value=1.0, stroke_width=18, color=Color.PROGRESS_BACKGROUND, width=250, height=250)
        fg_ring = ft.ProgressRing(value=progress, stroke_width=18, color=Color.PROGRESS_COMPLETED if completed else Color.PROGRESS_ACTIVE, width=250, height=250)

        saved_label = Text.SMALL(self.lang["savings.saved"], color=Color.SECONDARY_TEXT)
        current_val_text = Text.MEDIUM(current_value, color=Color.BLACK)
        target_val_text = Text.P(f"/ {target_value}", color=Color.SUBTITLE_TEXT)

        progress_ui = ft.Container(
            content=ft.Stack(
                controls=[
                    bg_ring,
                    fg_ring,
                    ft.Column(
                        [saved_label, current_val_text, target_val_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            padding=ft.Padding(0, 20, 0, 30),
            alignment=ft.Alignment.CENTER,
        )

        buttons_column = ft.Column(spacing=15)
        if not completed:
            if progress >= 1.0:
                buttons_column.controls.append(
                    ft.Button(
                        self.lang["savings.complete_objective_tooltip"],
                        icon=ft.Icons.CHECK_CIRCLE,
                        on_click=lambda e: self._handle_complete(page, goal_data),
                        bgcolor=Color.COMPLETED_ACTION,
                        color=Color.WHITE,
                        width=400,
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    )
                )
            else:
                buttons_column.controls.append(
                    ft.Button(
                        self.lang["savings.add_money"],
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                        on_click=lambda e: self._handle_dw(page, goal_data, "deposit"),
                        bgcolor=Color.DARK_BUTTON,
                        color=Color.WHITE,
                        width=400,
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    )
                )
                buttons_column.controls.append(
                    ft.OutlinedButton(
                        self.lang["savings.remove_money"],
                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        on_click=lambda e: self._handle_dw(page, goal_data, "withdraw"),
                        width=400,
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), color=Color.PRIMARY_TEXT),
                    )
                )

        buttons_column.controls.append(
            ft.TextButton(
                self.lang["generic.delete"],
                icon=ft.Icons.DELETE,
                icon_color=Color.DELETE_ACTION,
                on_click=lambda e: self._handle_delete(page, objective_id),
                width=400,
                height=50,
            )
        )

        history_data = self.controller.get_objective_history(objective_id)
        history_controls = []
        if not history_data:
            history_controls.append(
                Text.SMALL(self.lang["savings.no_recent_activity"], italic=True, color=Color.SUBTITLE_TEXT)
            )
        else:
            for item in history_data:
                amount = f"{item['amount']:+,.2f}"
                color_theme = Color.PRIMARY_ACTION if item["amount"] > 0 else Color.NEGATIVE_ACTION
                history_controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MONEY, color=color_theme),
                        title=Text.MEDIUM(f"{amount} {self.controller.get_currency()}", color=color_theme),
                        subtitle=Text.P(f"{item['date']}"),
                    )
                )

        close_btn = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(page),
            icon_color=Color.PRIMARY_TEXT,
        )
        title_text = Text.H3(self.lang["savings.objective"], color=Color.BLACK)
        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[close_btn, title_text, ft.Container(width=40)],
        )

        goal_title_text = Text.MEDIUM(goal_title, color=Color.BLACK)
        subtitle_text = Text.P(subtitle, color=Color.SUBTITLE_TEXT)
        recent_activity_title = Text.H3(self.lang["savings.recent_activity"], color=Color.PRIMARY_TEXT)

        history_scroll_box = ft.Container(
            content=ft.Column(history_controls, scroll=ft.ScrollMode.AUTO),
            expand=True,
        )

        self.content = ft.Container(
            width=525,
            height=900,
            padding=25,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    header_row,
                    goal_title_text,
                    subtitle_text,
                    progress_ui,
                    buttons_column,
                    ft.Divider(height=30, color=Color.DEFAULT_BORDER),
                    recent_activity_title,
                    history_scroll_box,
                ],
            ),
        )
        self.show(page)

    def _handle_complete(self, page, goal):
        Dialog.close_most_recent_dialog(page)
        self.on_complete(page, goal)

    def _handle_dw(self, page, goal, mode):
        Dialog.close_most_recent_dialog(page)
        self.on_deposit_withdraw(page, goal, mode)

    def _handle_delete(self, page, oid):
        Dialog.close_most_recent_dialog(page)
        self.on_delete(page, oid)