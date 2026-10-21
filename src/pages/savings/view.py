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

        self._add_dialogs_to_overlay()

    def _add_dialogs_to_overlay(self) -> None:
        dialogs = [
            self.create_objective_dialog,
            self.quick_action_dialog,
            self.complete_dialog,
            self.delete_dialog,
            self.clear_history_dialog,
            self.goal_details_dialog,
        ]
        for dialog in dialogs:
            dialog.add_to_overlay(self._page)


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
            refresh_callback=self._refresh_view,
            trigger_export_callback=self.trigger_export
        )

        # FETCH DASHBOARD DATA
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
                "current_value": f"{objective_savings:,.2f}".translate(str.maketrans(".,", ",.")) + " đ",
                "target_value": f"{target_amount:,.2f}".translate(str.maketrans(".,", ",.")) + " đ",
                "remaining_value": self.lang["savings.remaining"].format(amount=f"{remaining_amt:,.2f}".translate(str.maketrans(".,", ",.")) + " đ"),
                "percentage": card_percentage,
                "progress": card_progress,
                "completed": bool(completed_at)
            })

        self._objective_data = objectives_data

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

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

        self._open_pending_objective_dialog()

        # INITIALIZE MAIN CONTAINER
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

        super().__init__(
            route="/saving",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.menu
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def _refresh_view(self) -> None:
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
                "current_value": f"{objective_savings:,.2f}".translate(str.maketrans(".,", ",.")) + " đ",
                "target_value": f"{target_amount:,.2f}".translate(str.maketrans(".,", ",.")) + " đ",
                "remaining_value": self.lang["savings.remaining"].format(amount=f"{remaining_amt:,.2f}".translate(str.maketrans(".,", ",.")) + " đ"),
                "percentage": card_percentage,
                "progress": card_progress,
                "completed": bool(completed_at)
            })

        self._objective_data = objectives_data
        self.summary_banner.update_data(total_savings, total_target, percentage, progress_value)
        self.objective_grid.update_grid(objectives_data)

        if hasattr(self._page, "delete_cached_view"):
            self._page.delete_cached_view("/home")

        self._page.update()

    def _open_pending_objective_dialog(self) -> None:
        pending_objective_id: int | None = getattr(self._page, "pending_objective_id", None)
        if pending_objective_id is None:
            return

        objective_id = int(pending_objective_id)

        objective = next((item for item in self._objective_data if int(item["objective_id"]) == objective_id), None)
        if objective is None:
            self._page.pending_objective_id = None
            return

        self.dialogs.goal_details_dialog.trigger(
            self._page,
            objective["objective_id"],
            objective["title"],
            objective["reason"],
            objective["current_value"],
            objective["target_value"],
            objective["progress"],
            objective["completed"],
        )
        self._page.pending_objective_id = None

    async def trigger_export(self, e=None) -> None:
        file_path = await ft.FilePicker().save_file(allowed_extensions=["xlsx", "xls"], file_name="savings.xlsx")
        if file_path:
            success, error_message = self.controller.export_ledger_to_excel(file_path, self.lang)
            snack_bar = ft.SnackBar(Text.MEDIUM(self.lang["savings.export_succeeded"] if success else self.lang["savings.error.export_failed"].format(error=error_message)))
            self._page.overlay.append(snack_bar)
            snack_bar.open = True
            self._page.update()

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
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

            return 0

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")
            return 1

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")
            return 2

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")
            return -1


def get_savings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Savings page...")
    return SavingsView(page, lang, user_info)
