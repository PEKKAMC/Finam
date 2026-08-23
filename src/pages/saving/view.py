# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Color, Text
from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar, CreateObjectiveDialog, QuickActionDialog, CompleteConfirmDialog, DeleteConfirmDialog, ClearHistoryDialog, GoalDetailsDialog
from src.pages.saving.logic import LogicController
from src.pages.saving.components import AggregateCard, ObjectiveGrid, ActivityHistoryBoard


class SavingView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController(user_info["username"])

        self.create_objective_dialog = CreateObjectiveDialog(self.lang, self.controller, self.refresh_view)
        self.quick_action_dialog = QuickActionDialog(self.lang, self.controller, self.refresh_view)
        self.complete_dialog = CompleteConfirmDialog(self.lang, self.controller, self.refresh_view)
        self.delete_dialog = DeleteConfirmDialog(self.lang, self.controller, self.refresh_view)
        self.clear_history_dialog = ClearHistoryDialog(self.lang, self.controller, self.refresh_view, self.trigger_export)
        self.goal_details_dialog = GoalDetailsDialog(self.lang, self.controller, self.complete_dialog.trigger, self.quick_action_dialog.trigger, self.delete_dialog.trigger)

        self.menu = None
        self.top_navigation_bar = None
        self.main_container = None
        self.objective_grid = None

        super().__init__(
            route="/saving",
            padding=0,
            bgcolor=Color.CARD_BACKGROUND,
            controls=self.create_ui_components()
        )
        self._page.on_resize = self.on_page_resize
        self.on_page_resize(None)

    def create_ui_components(self):
        Logger.info("Rendering UI for saving page...")
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(current_user=self.user_info["username"])

        total_savings, total_target, progress_value, percentage = self.controller.get_dashboard_totals()
        existing_objectives = self.controller.get_user_objectives()

        objectives_data = []
        for objective_id, title, reason, target_amount, completed_at in existing_objectives:
            objective_savings, card_progress, card_percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
            objectives_data.append({
                "objective_id": objective_id, "title": title, "reason": reason,
                "current_value": f"{int(objective_savings):,} VND", "target_value": f"{int(target_amount):,} VND",
                "percentage": card_percentage, "progress": card_progress, "completed": bool(completed_at)
            })

        self.objective_grid = ObjectiveGrid(objectives_data, self.goal_details_dialog.trigger)
        activity_board = ActivityHistoryBoard(self.lang, self.controller.get_recent_activity(self.lang), lambda e: self.clear_history_dialog.show(self._page), self.trigger_export)

        header_section = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Column(spacing=5, controls=[Text.LABEL(self.lang["saving.title"], color=Color.PRIMARY_TEXT), Text.LABEL(self.lang["saving.description"], color=Color.BODY_TEXT)]),
                ft.Row(spacing=10, controls=[ft.Button(self.lang["saving.create_objectives"], color=Color.WHITE, bgcolor=Color.PRIMARY_ACTION, height=45, on_click=lambda e: self.create_objective_dialog.show(self._page))])
            ]
        )

        dashboard_row = ft.Row(spacing=20, controls=[AggregateCard(self.lang, total_savings, total_target, percentage, progress_value), ft.Container(expand=1, bgcolor=Color.ON_TRACK_BACKGROUND, height=200, border_radius=12)])
        active_objectives_section = ft.Column(spacing=15, controls=[Text.H2(self.lang["saving.active_objectives"], color=Color.PRIMARY_TEXT), self.objective_grid])

        self.main_container = ft.Container(
            padding=20,
            width=UISettings.MAX_APP_WIDTH,
            content=ft.Column(
                spacing=35,
                controls=[
                    self.top_navigation_bar,
                    header_section,
                    dashboard_row,
                    active_objectives_section,
                    activity_board
                ]
            )
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[self.main_container]
                                )
                            ]
                        ),
                        expand=True,
                        padding=0
                    ),
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
            self._page.show_dialog(ft.SnackBar(Text.LABEL(self.lang["saving.export_succeeded"] if success else self.lang["saving.error.export_failed"].format(error=error_message))))
            self._page.update()
        return e

    def on_page_resize(self, e=None):
        safe_width = int(min(self._page.width or UISettings.MAX_APP_WIDTH, UISettings.MAX_APP_WIDTH))
        self.main_container.width = safe_width
        self.top_navigation_bar.width = safe_width * 0.9
        for card in self.objective_grid.controls:
            card.width = max(250, safe_width * 0.22)
        try: self.update()
        except RuntimeError: pass

        return e

def get_savings_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SavingView(page, lang, user_info)