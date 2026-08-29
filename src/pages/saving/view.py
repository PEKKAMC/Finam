# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Color, Text
from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar, CreateObjectiveDialog, QuickActionDialog, CompleteConfirmDialog, DeleteConfirmDialog, ClearHistoryDialog, GoalDetailsDialog
from src.pages.saving.logic import LogicController
from src.pages.saving.components import AggregateCard, ObjectiveGrid


class SavingView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self.summary_banner = None
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController(user_info["username"])

        self.create_objective_dialog = CreateObjectiveDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.quick_action_dialog = QuickActionDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.complete_dialog = CompleteConfirmDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.delete_dialog = DeleteConfirmDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.clear_history_dialog = ClearHistoryDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view, trigger_export=self.trigger_export)
        self.goal_details_dialog = GoalDetailsDialog(page=self._page, lang=self.lang, controller=self.controller, on_complete=self.complete_dialog.trigger, on_quick_action=self.quick_action_dialog.trigger, on_delete=self.delete_dialog.trigger)

        self.menu = None
        self.top_navigation_bar = None
        self.main_container = None
        self.objective_grid = None

        super().__init__(
            route="/saving",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            controls=self.create_ui_components()
        )
        self._page.on_resize = self.on_page_resize
        self.on_page_resize(None)

    def create_ui_components(self):
        Logger.info("Rendering UI for saving page...")
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(page=self._page, lang=self.lang, current_user=self.user_info["username"])

        total_savings, total_target, progress_value, percentage = self.controller.get_dashboard_totals()
        existing_objectives = self.controller.get_user_objectives()

        objectives_data = []
        for objective_id, title, reason, target_amount, completed_at in existing_objectives:
            objective_savings, card_progress, card_percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
            remaining_amt = max(0, target_amount - objective_savings)

            objectives_data.append({
                "objective_id": objective_id, "title": title, "reason": reason,
                "current_value": f"{int(objective_savings):,}".replace(",", ".") + " đ",
                "target_value": f"{int(target_amount):,}".replace(",", ".") + " đ",
                "remaining_value": f"Còn lại: {int(remaining_amt):,}".replace(",", ".") + " đ",
                "percentage": card_percentage, "progress": card_progress, "completed": bool(completed_at)
            })

        self.objective_grid = ObjectiveGrid(page=self._page, lang=self.lang, objectives_data=objectives_data, on_card_click=self.goal_details_dialog.trigger)
        self.summary_banner = AggregateCard(page=self._page, lang=self.lang, total_savings=total_savings, total_target=total_target, percentage=percentage, progress_value=progress_value, on_create_click=lambda e: self.create_objective_dialog.show(self._page))

        self.main_container = ft.Container(
            padding=20,
            width=UISettings.MAX_APP_WIDTH,
            margin=ft.Margin(left=16, top=84, right=16, bottom=88),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=25,
                controls=[
                    self.summary_banner,
                    self.objective_grid,
                ]
            )
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        ]

    def refresh_view(self):
        for control in self._page.overlay:
            control.open = False
        if len(self._page.views) > 0:
            self._page.views[-1].controls.clear()
            self._page.views[-1].controls.extend(get_savings_view(self._page, self.lang, self.user_info).controls)
        self._page.update()

    async def trigger_export(self, e=None):
        file_path = await ft.FilePicker().save_file(allowed_extensions=["xlsx", "xls"], file_name="savings.xlsx")
        if file_path:
            success, error_message = self.controller.export_ledger_to_excel(file_path, self.lang)
            self._page.show_dialog(ft.SnackBar(Text.MEDIUM(self.lang["saving.export_succeeded"] if success else self.lang["saving.error.export_failed"].format(error=error_message))))
            self._page.update()
        return e

    def on_page_resize(self, e=None):
        safe_width = int(min(self._page.width or UISettings.MAX_APP_WIDTH, UISettings.MAX_APP_WIDTH))
        self.main_container.width = max(safe_width - 32, 320)
        self.main_container.margin = ft.Margin(left=16, top=84, right=16, bottom=88)
        self.top_navigation_bar.resize(safe_width)
        self.menu.resize(safe_width)

        return e


def get_savings_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SavingView(page, lang, user_info)