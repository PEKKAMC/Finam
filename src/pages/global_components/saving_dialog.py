# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime

import flet as ft

from src.database import db
from src.utils import Color, Text, UISettings

class BaseDialog(ft.AlertDialog):
    def show(self, page: ft.Page):
        if self not in page.overlay:
            page.overlay.append(self)
        self.open = True
        page.update()

    def close(self, page: ft.Page):
        self.open = False
        page.update()

class CreateObjectiveDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_success):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success

        self.goal_title_input = ft.TextField(label=lang["saving.goal_title"], color=Color.DEFAULT_TEXT, border_radius=10, border_color=Color.INPUT_BORDER, focused_border_color=Color.PRIMARY_ACTION)
        self.goal_amount_input = ft.TextField(label=lang["saving.target_amount"], color=Color.DEFAULT_TEXT, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), border_radius=10, border_color=Color.INPUT_BORDER, focused_border_color=Color.PRIMARY_ACTION)
        self.reason_input = ft.TextField(label=lang["saving.reason"], color=Color.DEFAULT_TEXT, border_radius=10, border_color=Color.INPUT_BORDER, focused_border_color=Color.PRIMARY_ACTION)

        submit_button = ft.Button(
            lang["saving.save_objective"], icon=ft.Icons.ADD_CIRCLE, on_click=self._process_add, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE, width=400, height=55, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )
        super().__init__(
            content_padding=0, bgcolor=Color.TRANSPARENT,
            content=ft.Container(
                width=UISettings.MAX_APP_WIDTH * 0.9, height=UISettings.MAX_APP_HEIGHT * 0.9, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
                content=ft.Column(tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.close(e.page), icon_color=Color.PRIMARY_TEXT), Text.H3(lang["saving.create_objectives"], color=Color.DEFAULT_TEXT), ft.Container(width=40)]),
                    ft.Container(height=10), ft.Column(spacing=15, controls=[self.goal_title_input, self.goal_amount_input, self.reason_input]), ft.Container(height=25), submit_button, ft.Container(height=10),
                ])
            )
        )

    def _process_add(self, e):
        title = self.goal_title_input.value if self.goal_title_input.value else self.lang["saving.untitled_goal"]
        subtitle = self.reason_input.value if self.reason_input.value else self.lang["saving.no_reason"]
        try: target = int(self.goal_amount_input.value)
        except ValueError: target = 0

        if self.controller.add_new_objective(title, subtitle, target):
            self.close(e.page)
            self.on_success()

class QuickActionDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_success):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_success = on_success
        self.current_action_objective = {"id": 0, "action": ""}

        self.quick_amount_input = ft.TextField(label=lang["generic.amount"], color=Color.DEFAULT_TEXT, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), border_radius=10, border_color=Color.INPUT_BORDER, focused_border_color=Color.PRIMARY_ACTION)

        super().__init__(
            title=Text.H3(self.lang["saving.update_savings"], color=Color.PRIMARY_TEXT),
            bgcolor=Color.DIALOG_BACKGROUND,
            content=ft.Container(content=ft.Column(tight=True, controls=[self.quick_amount_input])),
            actions=[
                ft.TextButton(self.lang["generic.cancel"], on_click=lambda e: self.close(e.page)),
                ft.Button(self.lang["generic.save"], on_click=self._process, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE)
            ]
        )

    def trigger(self, page: ft.Page, objective_id: int, action: str):
        self.current_action_objective = {"id": objective_id, "action": action}
        self.quick_amount_input.value = ""
        self.title = Text.H3(self.lang["saving.add_money"] if action == "add" else self.lang["saving.remove_money"])
        self.show(page)

    def _process(self, e):
        try:
            amount = int(self.quick_amount_input.value)
            objective_id = int(self.current_action_objective["id"])
            action = str(self.current_action_objective["action"])

            success, error_key = self.controller.process_quick_action(objective_id, action, amount, datetime.now().strftime("%Y-%m-%d %H:%M"))
            if not success:
                if error_key == "saving.error.not_enough_balance":
                    current = db.saving.get_objective_progress(objective_id)
                    e.page.snack_bar = ft.SnackBar(Text.MEDIUM(f"Not enough balance. Current: {current:,} VND" if "format" not in self.lang[error_key] else self.lang[error_key].format(remaining=f"{current:,}")))
                elif error_key == "saving.error.exceeding_amount":
                    remaining = db.saving.get_objective_target(objective_id) - db.saving.get_objective_progress(objective_id)
                    e.page.snack_bar = ft.SnackBar(Text.MEDIUM(f"Amount exceeds target! Remaining: {remaining:,} VND" if "format" not in self.lang[error_key] else self.lang[error_key].format(remaining=f"{remaining:,}")))
                e.page.snack_bar.open = True
                e.page.update()
                return

            self.close(e.page)
            self.on_success()
        except ValueError: pass

class CompleteConfirmDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_success):
        self._page = page
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0
        super().__init__(
            title=Text.H3(lang["saving.complete_objective_title"], color=Color.PRIMARY_TEXT),
            bgcolor=Color.DIALOG_BACKGROUND,
            content=ft.Container(content=Text.P(lang["saving.complete_objective_desc"], color=Color.DEFAULT_TEXT)),
            actions=[
                ft.TextButton(lang["generic.cancel"], on_click=lambda e: self.close(e.page)),
                ft.Button(lang["generic.complete"], on_click=self._process, bgcolor=Color.COMPLETED_ACTION, color=Color.WHITE)
            ]
        )

    def trigger(self, page: ft.Page, objective_id: int):
        self.current_id = objective_id
        self.show(page)

    def _process(self, e):
        self.controller.complete_objective(self.current_id)
        self.close(e.page)
        self.on_success()

class DeleteConfirmDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_success):
        self._page = page
        self.controller = controller
        self.on_success = on_success
        self.current_id = 0
        super().__init__(
            title=Text.H3(lang["saving.delete_objective_title"], color=Color.PRIMARY_TEXT),
            bgcolor=Color.DIALOG_BACKGROUND,
            content=ft.Container(content=Text.P(lang["saving.delete_objective_desc"], color=Color.DEFAULT_TEXT)),
            actions=[
                ft.TextButton(lang["generic.cancel"], on_click=lambda e: self.close(e.page)),
                ft.Button(lang["generic.delete"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)
            ]
        )

    def trigger(self, page: ft.Page, objective_id: int):
        self.current_id = objective_id
        self.show(page)

    def _process(self, e):
        self.controller.delete_objective(self.current_id)
        self.close(e.page)
        self.on_success()

class ClearHistoryDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_success, trigger_export):
        self._page = page
        self.controller = controller
        self.on_success = on_success
        super().__init__(
            title=Text.H3(lang["saving.clear_history_title"]),
            content=Text.P(lang["saving.clear_history_desc"]),
            actions=[
                ft.TextButton(lang["generic.cancel"], on_click=lambda e: self.close(e.page)),
                ft.Button(lang["saving.export_ledger"], on_click=trigger_export, bgcolor=Color.PROGRESS_ACTIVE, color=Color.WHITE),
                ft.Button(lang["saving.clear_history"], on_click=self._process, bgcolor=Color.NEGATIVE_ACTION, color=Color.WHITE)
            ]
        )

    def _process(self, e):
        self.controller.clear_activity_history()
        self.close(e.page)
        self.on_success()

class GoalDetailsDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_complete, on_quick_action, on_delete):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_complete = on_complete
        self.on_quick_action = on_quick_action
        self.on_delete = on_delete
        super().__init__(content_padding=0, bgcolor=Color.TRANSPARENT)

    def trigger(self, page: ft.Page, objective_id: int, goal_title: str, subtitle: str, current_value: str, target_value: str, progress: float, completed: bool):
        progress_ui = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.ProgressRing(value=1.0, stroke_width=18, color=Color.PROGRESS_BACKGROUND, width=250, height=250),
                    ft.ProgressRing(value=progress, stroke_width=18, color=Color.PROGRESS_COMPLETED if completed else Color.PROGRESS_ACTIVE, width=250, height=250),
                    ft.Column([Text.SMALL(self.lang["saving.saved"], color=Color.SECONDARY_TEXT), Text.MEDIUM(current_value, color=Color.BLACK), Text.P(f"/ {target_value}", color=Color.SUBTITLE_TEXT)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.Alignment.CENTER
            ), padding=ft.Padding(0, 20, 0, 30), alignment=ft.Alignment.CENTER
        )

        buttons_column = ft.Column(spacing=15)
        if not completed:
            if progress >= 1.0:
                buttons_column.controls.append(ft.Button(self.lang["saving.complete_objective_tooltip"], icon=ft.Icons.CHECK_CIRCLE, on_click=lambda e: self._handle_complete(page, objective_id), bgcolor=Color.COMPLETED_ACTION, color=Color.WHITE, width=400, height=55, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))))
            else:
                buttons_column.controls.append(ft.Button(self.lang["saving.add_money"], icon=ft.Icons.ADD_CIRCLE_OUTLINE, on_click=lambda e: self._handle_quick(page, objective_id, "add"), bgcolor=Color.DARK_BUTTON, color=Color.WHITE, width=400, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))))
                buttons_column.controls.append(ft.OutlinedButton(self.lang["saving.remove_money"], icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, on_click=lambda e: self._handle_quick(page, objective_id, "remove"), width=400, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), color=Color.PRIMARY_TEXT)))

        buttons_column.controls.append(ft.TextButton(self.lang["generic.delete"], icon=ft.Icons.DELETE, icon_color=Color.DELETE_ACTION, on_click=lambda e: self._handle_delete(page, objective_id), width=400, height=50))

        history_data = self.controller.get_objective_history(objective_id)
        history_controls = []
        if not history_data:
            history_controls.append(Text.SMALL(self.lang["saving.no_recent_activity"], italic=True, color=Color.SUBTITLE_TEXT))
        else:
            for item in history_data:
                amount = f"+{item['amount']:,}" if item["amount"] > 0 else f"{item['amount']:,}"
                color_theme = Color.PRIMARY_ACTION if item["amount"] > 0 else Color.NEGATIVE_ACTION
                history_controls.append(ft.ListTile(leading=ft.Icon(ft.Icons.MONEY, color=color_theme), title=Text.MEDIUM(f"{amount} VND", color=color_theme), subtitle=Text.P(f"{item['date']}")))

        self.content = ft.Container(
            width=525, height=900, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.close(page), icon_color=Color.PRIMARY_TEXT), Text.H3(self.lang["saving.objective_details"], color=Color.BLACK), ft.Container(width=40)]),
                    Text.MEDIUM(goal_title, color=Color.BLACK), Text.P(subtitle, color=Color.SUBTITLE_TEXT), progress_ui, buttons_column,
                    ft.Divider(height=30, color=Color.DEFAULT_BORDER), Text.H3(self.lang["saving.recent_activity"], color=Color.PRIMARY_TEXT),
                    ft.Container(content=ft.Column(history_controls, scroll=ft.ScrollMode.AUTO), expand=True)
                ]
            )
        )
        self.show(page)

    def _handle_complete(self, page, oid):
        self.close(page)
        self.on_complete(page, oid)

    def _handle_quick(self, page, oid, action):
        self.close(page)
        self.on_quick_action(page, oid, action)

    def _handle_delete(self, page, oid):
        self.close(page)
        self.on_delete(page, oid)

class ObjectiveSelectionDialog(BaseDialog):
    def __init__(self, page: ft.Page, lang: dict, controller, on_select):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.on_select = on_select
        self.selection_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        super().__init__(
            content_padding=0, bgcolor=Color.TRANSPARENT,
            content=ft.Container(
                width=UISettings.MAX_APP_WIDTH * 0.9, height=UISettings.MAX_APP_HEIGHT * 0.8, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
                content=ft.Column(tight=True, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.close(e.page), icon_color=Color.PRIMARY_TEXT), Text.H3("Select Objective", color=Color.DEFAULT_TEXT), ft.Container(width=40)]),
                    ft.Container(height=10), self.selection_list
                ])
            )
        )

    def load_objectives(self, page: ft.Page):
        self.selection_list.controls.clear()
        objectives = self.controller.get_user_objectives()
        if not objectives:
            self.selection_list.controls.append(Text.P("No active objectives found.", color=Color.SECONDARY_TEXT))
        else:
            for obj in objectives:
                objective_id, title, reason, target_amount, completed_at = obj
                obj_savings, progress, percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
                card = ft.Container(
                    bgcolor=Color.CARD_BACKGROUND, border_radius=10, padding=15, border=ft.Border.all(1, Color.DEFAULT_BORDER), ink=True,
                    on_click=self._create_selection_handler(page, objective_id, title, reason, f"{int(obj_savings):,} VND", f"{int(target_amount):,} VND", progress, bool(completed_at)),
                    content=ft.Column([
                        ft.Row([Text.H3(title, color=Color.PRIMARY_TEXT), Text.MEDIUM(percentage, color=Color.PRIMARY_ACTION)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        Text.P(reason, color=Color.SECONDARY_TEXT), ft.ProgressBar(value=progress, color=Color.PROGRESS_COMPLETED if completed_at else Color.PROGRESS_ACTIVE, bgcolor=Color.PROGRESS_BACKGROUND)
                    ])
                )
                self.selection_list.controls.append(card)
        self.show(page)

    def _create_selection_handler(self, page, oid, title, reason, cur, tgt, prog, comp):
        def handler(e):
            self.close(page)
            self.on_select(page, oid, title, reason, cur, tgt, prog, comp)
            return e
        return handler