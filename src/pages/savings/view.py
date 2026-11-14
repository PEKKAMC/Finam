# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from decimal import Decimal
from typing import Any

import flet as ft

from src.logger import Logger
from src.pages.common import Menu
from src.pages.savings.components import ActivityHistory, AggregateCard, ClearHistoryDialog, CongratulationsDialog, CreateGoalDialog, DeleteConfirmDialog, DepositWithdrawDialog, GoalGrid
from src.pages.savings.logic import LogicController
from src.utils import Color, MenuResizeValues, Page, UISettings, format_number, get_menu_resize_values, get_safe_page_size, scale_width

Logger.info("Initializing Savings page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Savings View matching TSX components."""

    def __init__(self, page: Page, lang: dict[str, str], controller: LogicController, currency: str, refresh_callback: Callable[..., None], trigger_export_callback: Callable[..., None] | ft.CoroutineType[Any, Any, None], get_objectives_callback: Callable[[], list[dict[str, Any]]]) -> None:
        self._page = page
        self.lang = lang
        self.controller = controller
        self.currency = currency
        self._refresh_view = refresh_callback
        self._trigger_export = trigger_export_callback
        self._get_objectives = get_objectives_callback

        self.create_goal_dialog = CreateGoalDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            currency=self.currency,
            on_success=self._refresh_view
        )

        self.congratulations_dialog = CongratulationsDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            currency=self.currency,
            on_success=self._refresh_view,
            on_create_with_surplus=lambda surplus: self.create_goal_dialog.trigger(
                surplus
            )
        )

        self.deposit_withdraw_dialog = DepositWithdrawDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view,
            on_surplus=lambda goal, surplus: self.congratulations_dialog.trigger(
                goal,
                surplus,
                self._get_objectives(),
                confetti=True
            )
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
            on_success=self._refresh_view
        )

    def update_currency(self, currency: str) -> None:
        self.currency = currency
        self.create_goal_dialog.currency = currency
        self.congratulations_dialog.currency = currency


class SavingsView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])

        # FETCH DASHBOARD DATA
        total_savings, total_target, progress_value, percentage = (
            self.controller.get_dashboard_totals()
        )
        existing_objectives = self.controller.get_user_objectives()
        currency = self.controller.get_currency()

        self._objective_data = self._build_objective_data(existing_objectives, currency)
        self.search_query = ""

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            currency=currency,
            refresh_callback=self._refresh_view,
            trigger_export_callback=self.trigger_export,
            get_objectives_callback=lambda: self._objective_data
        )

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(page=self._page, lang=self.lang, user_info=self.user_info)

        self.goal_grid = GoalGrid(
            page=self._page,
            lang=self.lang,
            objectives_data=self._objective_data,
            on_deposit=self.dialogs.deposit_withdraw_dialog.trigger,
            on_achievement=lambda goal: self.dialogs.congratulations_dialog.trigger(
                goal,
                Decimal(0),
                self._objective_data
            ),
            on_withdraw=self.dialogs.deposit_withdraw_dialog.trigger,
            on_delete=self.dialogs.delete_dialog.trigger
        )
        self.dialogs.deposit_withdraw_dialog.on_action_message = (
            self.goal_grid.show_action_message
        )

        self.search_field = ft.TextField(
            value=self.search_query,
            hint_text=self.lang["savings.search"],
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            bgcolor=Color.CARD_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True
        )
        self.search_bar = ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=8,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.search_field
        )

        self.summary_banner = AggregateCard(
            page=self._page,
            lang=self.lang,
            total_savings=total_savings,
            total_target=total_target,
            percentage=percentage,
            progress_value=progress_value,
            currency=currency,
            on_create_click=lambda e: self.dialogs.create_goal_dialog.trigger()
        )

        self.activity_history = ActivityHistory(
            page=self._page,
            lang=self.lang,
            activities=self.controller.get_recent_activity(self.lang),
            currency=currency,
            on_export=self.trigger_export,
            on_clear=lambda e: self.dialogs.clear_history_dialog.trigger()
        )

        # INITIALIZE MAIN CONTAINER
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=25,
                controls=[
                    self.summary_banner,
                    self.search_bar,
                    self.goal_grid,
                    self.activity_history
                ]
            )
        )
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO, controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

        super().__init__(
            route="/savings",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True, controls=[self.main_container, self.menu]
                )
            )
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

    def _refresh_view(self) -> None:
        self._resize_page()
        total_savings, total_target, progress_value, percentage = (
            self.controller.get_dashboard_totals()
        )
        existing_objectives = self.controller.get_user_objectives()
        currency = self.controller.get_currency()

        self._objective_data = self._build_objective_data(existing_objectives, currency)
        self.dialogs.update_currency(currency)
        self.summary_banner.update_data(
            total_savings, total_target, percentage, progress_value, currency
        )
        self.goal_grid.update_grid(self._filter_objectives())
        self.activity_history.update_history(
            self.controller.get_recent_activity(self.lang), currency
        )

        self._page.update()

    def on_search_change(self, e: ft.Event[ft.TextField]) -> None:
        self.search_query = e.control.value or ""
        self.goal_grid.update_grid(self._filter_objectives())
        self._page.update()

    def _filter_objectives(self) -> list[dict[str, Any]]:
        query = self.search_query.strip().casefold()
        if not query:
            return self._objective_data
        return [
            objective
            for objective in self._objective_data
            if query in objective["title"].casefold()
            or query in objective["reason"].casefold()
        ]

    def _build_objective_data(self, objectives: list[tuple[int, str, str | None, Decimal, str | None]], currency: str) -> list[dict[str, Any]]:
        objectives_data = []
        for objective_id, title, reason, target_amount, _completed_at in objectives:
            objective_id = int(objective_id)
            objective_savings, card_progress, card_percentage = (
                self.controller.get_objective_progress_data(objective_id, target_amount)
            )
            remaining_amt = max(Decimal(0), target_amount - objective_savings)

            def format_amount(amount: Decimal) -> str:
                return format_number(amount)

            objectives_data.append(
                {
                    "objective_id": objective_id,
                    "title": title,
                    "reason": reason,
                    "current_value": f"{format_amount(objective_savings)} {currency}",
                    "target_value": f"{format_amount(target_amount)} {currency}",
                    "remaining_value": self.lang["savings.remaining"].format(amount=f"{format_amount(remaining_amt)} {currency}"),
                    "percentage": card_percentage,
                    "progress": card_progress,
                    "completed": 0 < target_amount <= objective_savings,
                }
            )
        return objectives_data

    async def trigger_export(self, e: ft.ControlEvent | None = None) -> None:
        try:
            file_bytes, error_message = self.controller.get_ledger_excel_bytes(
                self.lang
            )
            if file_bytes is None:
                raise RuntimeError(error_message)

            await ft.FilePicker().save_file(
                allowed_extensions=["xlsx"],
                file_name="savings.xlsx",
                src_bytes=file_bytes
            )

        except (OSError, RuntimeError, ValueError) as ex:
            Logger.error(f"Error during export: {ex}, Event: {e}")

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_resize_values: MenuResizeValues = self.get_menu_resize_values(
                page_width, self.menu
            )

            content_width = scale_width(page_width, 392)

            dialog_width = page_width * 6 // 7
            card_content_width = scale_width(page_width, 352)
            summary_content_width = scale_width(page_width, 332)
            activity_content_width = card_content_width
            create_content_width = scale_width(page_width, 322)
            achievement_content_width = scale_width(page_width, 314)
            delete_content_width = scale_width(page_width, 322)
            delete_title_width = scale_width(page_width, 274)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            self.content_container.width = page_width

            # Resizing other components
            self.menu.resize(
                width=page_width,
                **menu_resize_values
            )

            self.main_container.margin.bottom = self.menu.reserved_height

            self.summary_banner.resize(
                width=content_width,
                content_width=summary_content_width
            )

            self.search_bar.width = content_width

            self.goal_grid.resize(
                width=content_width,
                card_content_width=card_content_width
            )

            self.activity_history.resize(
                width=content_width,
                content_width=activity_content_width
            )

            self.dialogs.create_goal_dialog.resize(
                page_width=page_width,
                outer_width=dialog_width,
                content_width=create_content_width
            )

            self.dialogs.congratulations_dialog.resize(
                outer_width=dialog_width,
                content_width=achievement_content_width
            )

            self.dialogs.deposit_withdraw_dialog.resize(
                page_width=page_width,
                outer_width=dialog_width,
                content_width=create_content_width
            )

            self.dialogs.delete_dialog.resize(
                outer_width=dialog_width,
                content_width=delete_content_width,
                title_width=delete_title_width
            )

            self.dialogs.clear_history_dialog.resize(
                outer_width=dialog_width,
                content_width=delete_content_width,
                title_width=delete_title_width
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_savings_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Savings page...")
    return SavingsView(page, lang, user_info)
