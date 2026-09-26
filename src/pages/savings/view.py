# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.savings.components import AggregateCard, ClearHistoryDialog, CompleteConfirmDialog, CreateObjectiveDialog, DeleteConfirmDialog, GoalDetailsDialog, ObjectiveGrid, QuickActionDialog
from src.pages.savings.logic import LogicController
from src.utils import Color, Page, Text, UISettings, get_safe_page_size

Logger.info("Initializing Savings page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Savings View."""
    def __init__(self, page: Page, lang: dict, controller: LogicController, refresh_callback: Callable, trigger_export_callback: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self._refresh_view = refresh_callback
        self._trigger_export = trigger_export_callback

        self.create_objective_dialog = CreateObjectiveDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view
        )

        self.quick_action_dialog = QuickActionDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view
        )

        self.complete_dialog = CompleteConfirmDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view
        )

        self.delete_dialog = DeleteConfirmDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view
        )

        self.clear_history_dialog = ClearHistoryDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view,
            trigger_export=self._trigger_export
        )

        self.goal_details_dialog = GoalDetailsDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_complete=self.complete_dialog.trigger,
            on_quick_action=self.quick_action_dialog.trigger,
            on_delete=self.delete_dialog.trigger
        )


class SavingsView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            refresh_callback=self.refresh_view,
            trigger_export_callback=self.trigger_export
        )

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(self._page, self.lang, self.user_info)

        # BUILD UI
        self._load_and_build()

        super().__init__(
            route="/saving",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def _load_and_build(self):
        Logger.info("Rendering UI for saving page...")
        total_savings, total_target, progress_value, percentage = self.controller.get_dashboard_totals()
        existing_objectives = self.controller.get_user_objectives()

        objectives_data = []
        for objective_id, title, reason, target_amount, completed_at in existing_objectives:
            objective_savings, card_progress, card_percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
            remaining_amt = max(0, target_amount - objective_savings)

            objectives_data.append({
                "objective_id": objective_id,
                "title": title,
                "reason": reason,
                "current_value": f"{int(objective_savings):,}".replace(",", ".") + " đ",
                "target_value": f"{int(target_amount):,}".replace(",", ".") + " đ",
                "remaining_value": self.lang["ui.saving.remaining"].format(amount=f"{int(remaining_amt):,}".replace(",", ".") + " đ"),
                "percentage": card_percentage,
                "progress": card_progress,
                "completed": bool(completed_at)
            })

        self.objective_grid = ObjectiveGrid(
            page=self._page,
            lang=self.lang,
            objectives_data=objectives_data,
            on_card_click=self.dialogs.goal_details_dialog.trigger
        )

        self.summary_banner = AggregateCard(
            page=self._page,
            lang=self.lang,
            total_savings=total_savings,
            total_target=total_target,
            percentage=percentage,
            progress_value=progress_value,
            on_create_click=lambda e: self.dialogs.create_objective_dialog.show(self._page)
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=25,
                            controls=[
                                self.summary_banner,
                                self.objective_grid,
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=UISettings.MENU_HEIGHT)
        )

    def refresh_view(self) -> None:
        total_savings, total_target, progress_value, percentage = self.controller.get_dashboard_totals()
        existing_objectives = self.controller.get_user_objectives()

        objectives_data = []
        for objective_id, title, reason, target_amount, completed_at in existing_objectives:
            objective_savings, card_progress, card_percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
            remaining_amt = max(0, target_amount - objective_savings)

            objectives_data.append({
                "objective_id": objective_id,
                "title": title,
                "reason": reason,
                "current_value": f"{int(objective_savings):,}".replace(",", ".") + " đ",
                "target_value": f"{int(target_amount):,}".replace(",", ".") + " đ",
                "remaining_value": self.lang["ui.saving.remaining"].format(amount=f"{int(remaining_amt):,}".replace(",", ".") + " đ"),
                "percentage": card_percentage,
                "progress": card_progress,
                "completed": bool(completed_at)
            })

        self.summary_banner.update_data(total_savings, total_target, percentage, progress_value)
        self.objective_grid.update_grid(objectives_data)

        self._page.update()

    async def trigger_export(self, e=None):
        file_path = await ft.FilePicker().save_file(allowed_extensions=["xlsx", "xls"], file_name="savings.xlsx")
        if file_path:
            success, error_message = self.controller.export_ledger_to_excel(file_path, self.lang)
            self._page.show_dialog(ft.SnackBar(Text.MEDIUM(self.lang["saving.export_succeeded"] if success else self.lang["saving.error.export_failed"].format(error=error_message))))
            self._page.update()
        return e

    def on_page_resize(self, e=None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(page=self._page)

        self.main_container.width = page_width
        self.main_container.height = page_height

        self.menu.resize(
            width=page_width
        )

        self.summary_banner.resize(
            width=page_width
        )

        self.objective_grid.resize(
            width=page_width
        )

        return e


def get_savings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Savings page...")
    return SavingsView(page, lang, user_info)