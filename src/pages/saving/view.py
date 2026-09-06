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
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # controller and dialogs
        self.controller = LogicController(user_info["username"])
        self.create_objective_dialog = CreateObjectiveDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.quick_action_dialog = QuickActionDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.complete_dialog = CompleteConfirmDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.delete_dialog = DeleteConfirmDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view)
        self.clear_history_dialog = ClearHistoryDialog(page=self._page, lang=self.lang, controller=self.controller, on_success=self.refresh_view, trigger_export=self.trigger_export)
        self.goal_details_dialog = GoalDetailsDialog(page=self._page, lang=self.lang, controller=self.controller, on_complete=self.complete_dialog.trigger, on_quick_action=self.quick_action_dialog.trigger, on_delete=self.delete_dialog.trigger)

        # components
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(page=self._page, lang=self.lang, current_user=self.user_info["username"])

        # load data and build UI
        self._load_and_build()

        super().__init__(
            route="/saving",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(expand=True, controls=[self.main_container, self.top_navigation_bar, self.menu])
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
                "objective_id": objective_id, "title": title, "reason": reason,
                "current_value": f"{int(objective_savings):,}".replace(",", ".") + " đ",
                "target_value": f"{int(target_amount):,}".replace(",", ".") + " đ",
                "remaining_value": f"Còn lại: {int(remaining_amt):,}".replace(",", ".") + " đ",
                "percentage": card_percentage, "progress": card_progress, "completed": bool(completed_at)
            })

        self.objective_grid = ObjectiveGrid(page=self._page, lang=self.lang, objectives_data=objectives_data, on_card_click=self.goal_details_dialog.trigger)
        self.summary_banner = AggregateCard(page=self._page, lang=self.lang, total_savings=total_savings, total_target=total_target, percentage=percentage, progress_value=progress_value, on_create_click=lambda e: self.create_objective_dialog.show(self._page))

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
            margin=ft.Margin(top=UISettings.TOP_NAVIGATION_HEIGHT, bottom=UISettings.MENU_HEIGHT)
        )

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

    def get_safe_page_size(self) -> tuple[int, int]:
        current_width: float = self._page.width or UISettings.MAX_APP_WIDTH
        current_height: float = self._page.height or UISettings.MAX_APP_HEIGHT

        safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
        safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)
        return safe_width, safe_height

    def on_page_resize(self, e=None):
        page_width, page_height = self.get_safe_page_size()

        self.main_container.width = page_width
        self.top_navigation_bar.resize(page_width)
        self.menu.resize(page_width)

        return e


def get_savings_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SavingView(page, lang, user_info)
