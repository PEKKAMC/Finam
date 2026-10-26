# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.savings.components import ActivityHistory, AggregateCard, ClearHistoryDialog, CreateGoalModal, DepositWithdrawModal, CongratulationsModal, DeleteConfirmDialog, GoalGrid
from src.pages.savings.logic import LogicController
from src.utils import Color, Page, Text, UISettings, get_safe_page_size

Logger.info("Initializing Savings page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Savings View matching TSX components."""
    def __init__(self, page: Page, lang: dict, controller: LogicController, currency: str, refresh_callback: Callable, trigger_export_callback: Callable, get_objectives_callback: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.currency = currency
        self._refresh_view = refresh_callback
        self._trigger_export = trigger_export_callback
        self._get_objectives = get_objectives_callback

        self.create_goal_modal = CreateGoalModal(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            currency=self.currency,
            on_success=self._refresh_view
        )

        self.congratulations_modal = CongratulationsModal(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            currency=self.currency,
            on_success=self._refresh_view,
            on_create_with_surplus=lambda surplus: self.create_goal_modal.trigger(surplus)
        )

        self.deposit_withdraw_modal = DepositWithdrawModal(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self._refresh_view,
            on_surplus=lambda goal, surplus: self.congratulations_modal.trigger(goal, surplus, self._get_objectives())
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

    def update_currency(self, currency: str) -> None:
        self.currency = currency
        self.create_goal_modal.currency = currency
        self.congratulations_modal.currency = currency


class SavingsView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])

        # FETCH DASHBOARD DATA
        total_savings, total_target, progress_value, percentage = self.controller.get_dashboard_totals()
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
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.goal_grid = GoalGrid(
            page=self._page,
            lang=self.lang,
            objectives_data=self._objective_data,
            on_deposit=self.dialogs.deposit_withdraw_modal.trigger,
            on_withdraw=self.dialogs.deposit_withdraw_modal.trigger,
            on_delete=self.dialogs.delete_dialog.trigger,
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
            filled=True,
        )
        self.search_bar = ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.search_field,
        )

        self.summary_banner = AggregateCard(
            page=self._page,
            lang=self.lang,
            total_savings=total_savings,
            total_target=total_target,
            percentage=percentage,
            progress_value=progress_value,
            currency=currency,
            on_create_click=lambda e: self.dialogs.create_goal_modal.trigger()
        )

        self.activity_history = ActivityHistory(
            page=self._page,
            lang=self.lang,
            activities=self.controller.get_recent_activity(self.lang),
            currency=currency,
            on_export=self.trigger_export,
            on_clear=lambda e: self.dialogs.clear_history_dialog.trigger(),
        )

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
                                self.search_bar,
                                self.goal_grid,
                                self.activity_history,
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
            route="/savings",
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
        currency = self.controller.get_currency()

        self._page.delete_cached_view("/home")
        self._objective_data = self._build_objective_data(existing_objectives, currency)
        self.dialogs.update_currency(currency)
        self.summary_banner.update_data(total_savings, total_target, percentage, progress_value, currency)
        self.goal_grid.update_grid(self._filter_objectives())
        self.activity_history.update_history(self.controller.get_recent_activity(self.lang), currency)

        self._page.update()

    def on_search_change(self, e: ft.Event[ft.TextField]) -> None:
        self.search_query = e.control.value or ""
        self.goal_grid.update_grid(self._filter_objectives())
        self._page.update()

    def _filter_objectives(self) -> list:
        query = self.search_query.strip().casefold()
        if not query:
            return self._objective_data
        return [
            objective for objective in self._objective_data
            if query in objective["title"].casefold() or query in objective["reason"].casefold()
        ]

    def _build_objective_data(self, objectives: list, currency: str) -> list:
        objectives_data = []
        for objective_id, title, reason, target_amount, _completed_at in objectives:
            objective_savings, card_progress, card_percentage = self.controller.get_objective_progress_data(objective_id, target_amount)
            remaining_amt = max(0, target_amount - objective_savings)

            def format_amount(amount: float) -> str:
                return f"{amount:,.2f}".translate(str.maketrans(".,", ",."))

            objectives_data.append({
                "objective_id": objective_id,
                "title": title,
                "reason": reason,
                "current_value": f"{format_amount(objective_savings)} {currency}",
                "target_value": f"{format_amount(target_amount)} {currency}",
                "remaining_value": self.lang["savings.remaining"].format(amount=f"{format_amount(remaining_amt)} {currency}"),
                "percentage": card_percentage,
                "progress": card_progress,
                "completed": 0 < target_amount <= objective_savings,
            })
        return objectives_data

    async def trigger_export(self, e=None) -> None:
        try:
            file_path = await ft.FilePicker().save_file(allowed_extensions=["xlsx", "xls"], file_name="savings.xlsx")
            if file_path:
                success, error_message = self.controller.export_ledger_to_excel(file_path, self.lang)
                snack_bar = ft.SnackBar(Text.MEDIUM(self.lang["savings.export_succeeded"] if success else self.lang["savings.error.export_failed"].format(error=error_message)))
                self._page.overlay.append(snack_bar)
                snack_bar.open = True
                self._page.update()

        except Exception as ex:
            Logger.error(f"Error during export: {ex}, Event: {e}")
            snack_bar = ft.SnackBar(Text.MEDIUM(self.lang["savings.error.export_failed"].format(error=str(ex))))
            self._page.overlay.append(snack_bar)
            snack_bar.open = True
            self._page.update()

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        try:
            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

            # Resizing other components
            self.menu.resize(
                width=page_width
            )

            self.summary_banner.resize(
                width=page_width
            )

            self.search_bar.width = page_width

            self.goal_grid.resize(
                width=page_width
            )

            self.activity_history.resize(
                width=page_width
            )

            self.dialogs.create_goal_modal.resize(
                width=page_width // 7 * 6
            )

            self.dialogs.congratulations_modal.resize(
                width=page_width // 7 * 6
            )

            self.dialogs.deposit_withdraw_modal.resize(
                width=page_width // 7 * 6
            )

            self.dialogs.delete_dialog.resize(
                width=page_width // 7 * 6
            )

            self.dialogs.clear_history_dialog.resize(
                width=page_width // 7 * 6
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
