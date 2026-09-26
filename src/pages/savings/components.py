# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from datetime import datetime

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings


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
            lambda e: self.on_click_callback(
                e.page,
                self.objective_id,
                self.objective_title,
                self.subtitle,
                self.current_value,
                self.target_value,
                self.progress,
                self.completed
            ) if self.on_click_callback else None
        )

        # TEXT AND ICON COMPONENTS
        self.title_text = Text.H4(self.objective_title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.completed_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.PROGRESS_ACTIVE, size=18) if self.completed else ft.Container()
        self.subtitle_text = Text.MEDIUM(self.subtitle, color=Color.SECONDARY_TEXT)
        self.badge_text = Text.BADGE(self.percentage, color=badge_text_color, weight=ft.FontWeight.BOLD)

        self.accumulated_label = Text.MEDIUM(self.lang["ui.saving.accumulated"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.current_value_text = Text.H4(self.current_value, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.target_text = Text.SMALL(self.lang["ui.saving.target"].format(target_value=self.target_value), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)
        self.remaining_text = Text.SMALL(self.remaining_value, color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)

        self.deposit_label = Text.MEDIUM(self.lang["ui.saving.deposit"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.withdraw_label = Text.MEDIUM(self.lang["ui.saving.withdraw"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        self.progress_bar = ft.ProgressBar(
            value=self.progress,
            color=Color.PRIMARY,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            height=10
        )

        # CONTAINER COMPONENTS
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

        self.deposit_box = ft.Container(
            content=self.deposit_label,
            bgcolor=Color.PRIMARY,
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=12,
        )

        self.withdraw_box = ft.Container(
            content=self.withdraw_label,
            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=12,
        )

        self.action_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self.deposit_box,
                        self.withdraw_box
                    ]
                )
            ]
        )

        self.divider = ft.Divider(color=Color.CARD_DIVIDER, height=1)

        self.main_container = ft.Column(
            spacing=16,
            controls=[
                self.title_row,
                self.progress_row,
                self.divider,
                self.action_row
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
    def __init__(self, page: Page, lang: dict, total_savings: float, total_target: float, percentage: str, progress_value: float, on_create_click: Callable):
        self._page = page
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        self.title_text = Text.MEDIUM(self.lang["ui.saving.fund_management"].upper(), color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.savings_text = Text.H3(f"{int(total_savings):,}".replace(",", "."), color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.target_text = Text.H5(f" / {int(total_target):,}".replace(",", ".") + " đ", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.progress_label = Text.MEDIUM(self.lang["ui.saving.progress"], color=Color.WHITE)
        self.percentage_text = Text.MEDIUM(f"{percentage}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.add_icon = ft.Icon(ft.Icons.ADD, color=Color.PRIMARY, size=16)

        self.progress_bar = ft.ProgressBar(value=progress_value, color=Color.LIGHT_ACCENT, bgcolor=Color.DARK_SURFACE, height=8, border_radius=4)

        # CONTAINER COMPONENTS
        self.pill_container = ft.Container(
            content=self.title_text,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 6, 12, 6),
            border_radius=20,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER)
        )

        self.add_button_container = ft.Container(
            content=ft.Row(
                spacing=8,
                controls=[self.add_icon]
            ),
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

    def update_data(self, total_savings: float, total_target: float, percentage: str, progress_value: float):
        self.savings_text.value = f"{int(total_savings):,}".replace(",", ".")
        self.target_text.value = f" / {int(total_target):,}".replace(",", ".") + " đ"
        self.percentage_text.value = percentage
        self.progress_bar.value = progress_value

    def resize(self, width: int) -> None:
        self.width = max(width, 0)
        self.main_container.width = max(width, 0)


class CreateObjectiveDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success

        # INPUT AND TEXT COMPONENTS
        self.close_icon_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(e.page),
            icon_color=Color.PRIMARY_TEXT,
        )
        self.title_text = Text.H3(self.lang["saving.create_objectives"], color=Color.DEFAULT_TEXT)

        self.goal_title_input = ft.TextField(
            label=self.lang["saving.goal_title"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9À-ỹ\s]{0,50}$", replacement_string=""),
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.goal_amount_input = ft.TextField(
            label=self.lang["saving.target_amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,12}$", replacement_string=""),
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.reason_input = ft.TextField(
            label=self.lang["saving.reason"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[a-zA-Z0-9À-ỹ\s]{0,50}$", replacement_string=""),
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.submit_button = ft.Button(
            self.lang["saving.save_objective"],
            icon=ft.Icons.ADD_CIRCLE,
            on_click=self._process_add,
            bgcolor=Color.PRIMARY_ACTION,
            color=Color.WHITE,
            width=400,
            height=55,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        )

        # CONTAINER COMPONENTS
        self.header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.close_icon_button,
                self.title_text,
                ft.Container(width=40),
            ],
        )

        self.inputs_column = ft.Column(
            spacing=15,
            controls=[
                self.goal_title_input,
                self.goal_amount_input,
                self.reason_input,
            ],
        )

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH * 0.9,
            height=UISettings.MAX_APP_HEIGHT * 0.9,
            padding=25,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=20,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.header_row,
                    ft.Container(height=10),
                    self.inputs_column,
                    ft.Container(height=25),
                    self.submit_button,
                    ft.Container(height=10),
                ],
            ),
        )

        super().__init__(dialog_content=self.main_container, color=Color.TRANSPARENT)
        self.content_padding = 0

    def _process_add(self, e):
        title = self.goal_title_input.value if self.goal_title_input.value else self.lang["saving.untitled_goal"]
        subtitle = self.reason_input.value if self.reason_input.value else self.lang["saving.no_reason"]
        try:
            target = int(self.goal_amount_input.value)
        except ValueError:
            target = 0

        if self.controller.add_new_objective(title, subtitle, target):
            Dialog.close_most_recent_dialog(e.page)
            self.on_success()


class QuickActionDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_action_objective = {"id": 0, "action": ""}

        # TEXT AND INPUT COMPONENTS
        self.quick_amount_input = ft.TextField(
            label=self.lang["generic.amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,12}$", replacement_string=""),
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
        )

        self.title_text = Text.H3(self.lang["saving.update_savings"], color=Color.PRIMARY_TEXT)

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.save_button = ft.Button(self.lang["generic.save"], on_click=self._process, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.main_container = ft.Container(
            content=ft.Column(tight=True, controls=[self.quick_amount_input])
        )

        super().__init__(dialog_content=self.main_container, color=Color.DIALOG_BACKGROUND)

        self.title = self.title_text
        self.actions = [self.cancel_button, self.save_button]

    def trigger(self, page: Page, objective_id: int, action: str):
        self.current_action_objective = {"id": objective_id, "action": action}
        self.quick_amount_input.value = ""
        self.title_text.value = self.lang["saving.add_money"] if action == "add" else self.lang["saving.remove_money"]
        self.title = self.title_text
        self.show(page)

    def _process(self, e):
        try:
            amount = int(self.quick_amount_input.value)
            objective_id = int(self.current_action_objective["id"])
            action = str(self.current_action_objective["action"])

            success, error_key, extra_val = self.controller.process_quick_action(
                objective_id, action, amount, datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            if not success:
                if error_key == "saving.error.not_enough_balance":
                    msg = (
                        f"Not enough balance. Current: {extra_val:,} VND"
                        if "format" not in self.lang[error_key]
                        else self.lang[error_key].format(remaining=f"{extra_val:,}")
                    )
                    e.page.snack_bar = ft.SnackBar(Text.MEDIUM(msg))
                elif error_key == "saving.error.exceeding_amount":
                    msg = (
                        f"Amount exceeds target! Remaining: {extra_val:,} VND"
                        if "format" not in self.lang[error_key]
                        else self.lang[error_key].format(remaining=f"{extra_val:,}")
                    )
                    e.page.snack_bar = ft.SnackBar(Text.MEDIUM(msg))
                e.page.snack_bar.open = True
                e.page.update()
                return

            Dialog.close_most_recent_dialog(e.page)
            self.on_success()
        except ValueError:
            pass


class CompleteConfirmDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0

        # TEXT AND BUTTON COMPONENTS
        self.desc_text = Text.P(self.lang["saving.complete_objective_desc"], color=Color.DEFAULT_TEXT)
        self.title_text = Text.H3(self.lang["saving.complete_objective_title"], color=Color.PRIMARY_TEXT)

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.complete_button = ft.Button(self.lang["generic.complete"], on_click=self._process, bgcolor=Color.COMPLETED_ACTION, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.main_container = ft.Container(content=self.desc_text)

        super().__init__(dialog_content=self.main_container, color=Color.DIALOG_BACKGROUND)

        self.title = self.title_text
        self.actions = [self.cancel_button, self.complete_button]

    def trigger(self, page: Page, objective_id: int):
        self.current_id = objective_id
        self.show(page)

    def _process(self, e):
        self.controller.complete_objective(self.current_id)
        Dialog.close_most_recent_dialog(e.page)
        self.on_success()


class DeleteConfirmDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_success: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0

        # TEXT AND BUTTON COMPONENTS
        self.desc_text = Text.P(self.lang["saving.delete_objective_desc"], color=Color.DEFAULT_TEXT)
        self.title_text = Text.H3(self.lang["saving.delete_objective_title"], color=Color.PRIMARY_TEXT)

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.delete_button = ft.Button(self.lang["generic.delete"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)

        # CONTAINER COMPONENTS
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

        # TEXT AND BUTTON COMPONENTS
        self.desc_text = Text.P(self.lang["saving.clear_history_desc"])
        self.title_text = Text.H3(self.lang["saving.clear_history_title"])

        self.cancel_button = ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: Dialog.close_most_recent_dialog(e.page))
        self.export_button = ft.Button(self.lang["saving.export_ledger"], on_click=trigger_export, bgcolor=Color.PROGRESS_ACTIVE, color=Color.WHITE)
        self.clear_button = ft.Button(self.lang["saving.clear_history"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)

        super().__init__(dialog_content=self.desc_text, color=Color.DIALOG_BACKGROUND)

        self.title = self.title_text
        self.actions = [self.cancel_button, self.export_button, self.clear_button]

    def _process(self, e):
        self.controller.clear_activity_history()
        Dialog.close_most_recent_dialog(e.page)
        self.on_success()


class GoalDetailsDialog(Dialog):
    def __init__(self, page: Page, lang: dict, controller, on_complete: Callable, on_quick_action: Callable, on_delete: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_complete = on_complete
        self.on_quick_action = on_quick_action
        self.on_delete = on_delete

        super().__init__(dialog_content=ft.Container(), color=Color.TRANSPARENT)
        self.content_padding = 0

    def trigger(self, page: Page, objective_id: int, goal_title: str, subtitle: str, current_value: str, target_value: str, progress: float, completed: bool):
        # PROGRESS AND RING COMPONENTS
        bg_ring = ft.ProgressRing(value=1.0, stroke_width=18, color=Color.PROGRESS_BACKGROUND, width=250, height=250)
        fg_ring = ft.ProgressRing(value=progress, stroke_width=18, color=Color.PROGRESS_COMPLETED if completed else Color.PROGRESS_ACTIVE, width=250, height=250)

        saved_label = Text.SMALL(self.lang["saving.saved"], color=Color.SECONDARY_TEXT)
        current_val_text = Text.MEDIUM(current_value, color=Color.BLACK)
        target_val_text = Text.P(f"/ {target_value}", color=Color.SUBTITLE_TEXT)

        progress_ui = ft.Container(
            content=ft.Stack(
                controls=[
                    bg_ring,
                    fg_ring,
                    ft.Column(
                        [
                            saved_label,
                            current_val_text,
                            target_val_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            padding=ft.Padding(0, 20, 0, 30),
            alignment=ft.Alignment.CENTER,
        )

        # ACTION BUTTONS
        buttons_column = ft.Column(spacing=15)
        if not completed:
            if progress >= 1.0:
                buttons_column.controls.append(
                    ft.Button(
                        self.lang["saving.complete_objective_tooltip"],
                        icon=ft.Icons.CHECK_CIRCLE,
                        on_click=lambda e: self._handle_complete(page, objective_id),
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
                        self.lang["saving.add_money"],
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                        on_click=lambda e: self._handle_quick(page, objective_id, "add"),
                        bgcolor=Color.DARK_BUTTON,
                        color=Color.WHITE,
                        width=400,
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    )
                )
                buttons_column.controls.append(
                    ft.OutlinedButton(
                        self.lang["saving.remove_money"],
                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        on_click=lambda e: self._handle_quick(page, objective_id, "remove"),
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

        # ACTIVITY HISTORY LIST
        history_data = self.controller.get_objective_history(objective_id)
        history_controls = []
        if not history_data:
            history_controls.append(
                Text.SMALL(self.lang["saving.no_recent_activity"], italic=True, color=Color.SUBTITLE_TEXT)
            )
        else:
            for item in history_data:
                amount = f"+{item['amount']:,}" if item["amount"] > 0 else f"{item['amount']:,}"
                color_theme = Color.PRIMARY_ACTION if item["amount"] > 0 else Color.NEGATIVE_ACTION
                history_controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MONEY, color=color_theme),
                        title=Text.MEDIUM(f"{amount} VND", color=color_theme),
                        subtitle=Text.P(f"{item['date']}"),
                    )
                )

        # HEADER AND MAIN LAYOUT
        close_btn = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: Dialog.close_most_recent_dialog(page),
            icon_color=Color.PRIMARY_TEXT,
        )
        title_text = Text.H3(self.lang["saving.objective_details"], color=Color.BLACK)
        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                close_btn,
                title_text,
                ft.Container(width=40),
            ],
        )

        goal_title_text = Text.MEDIUM(goal_title, color=Color.BLACK)
        subtitle_text = Text.P(subtitle, color=Color.SUBTITLE_TEXT)
        recent_activity_title = Text.H3(self.lang["saving.recent_activity"], color=Color.PRIMARY_TEXT)

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

    def _handle_complete(self, page, oid):
        Dialog.close_most_recent_dialog(page)
        self.on_complete(page, oid)

    def _handle_quick(self, page, oid, action):
        Dialog.close_most_recent_dialog(page)
        self.on_quick_action(page, oid, action)

    def _handle_delete(self, page, oid):
        Dialog.close_most_recent_dialog(page)
        self.on_delete(page, oid)