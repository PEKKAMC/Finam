# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import CategorySelectionDialog, ExpenseInputDialog, FinancialChart, IncomeInputDialog, Menu
from src.pages.home.components import BalanceCard, SavingsProgressCard, ExpensePieChartCard, FeaturedLessonCard
from src.pages.home.logic import LogicController
from src.utils import Color, get_safe_page_size, navigate_to, Text, UISettings

Logger.info("Initializing Home page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Home View."""
    def __init__(self, page: ft.Page, lang: dict, controller: LogicController, refresh_callback: Callable):
        self._page = page
        self.lang = lang
        self.controller = controller
        self._refresh_view = refresh_callback
        self.current_category_type = "expense"

        # INITIALIZE DIALOG COMPONENTS
        self.category_dialog = CategorySelectionDialog(
            page=self._page,
            lang=self.lang,
            on_select=self._handle_category_selected,
            on_cancel=self._cancel_category_selector_dialog
        )
        self.category_dialog.load_categories("expense")

        self.expense_dialog = ExpenseInputDialog(
            page=self._page,
            lang=self.lang,
            on_save=self._handle_save_expense,
            on_cancel=self._cancel_expense_dialog,
            on_category_click=lambda e=None: self._load_category_selector_data()
        )

        self.income_dialog = IncomeInputDialog(
            page=self._page,
            lang=self.lang,
            on_save=self._handle_save_income,
            on_cancel=self._cancel_income_dialog,
            on_category_click=lambda e=None: self._load_category_selector_data()
        )

        self._add_dialogs_to_overlay()

    # CATEGORY SELECTOR DIALOG
    def _load_category_selector_data(self) -> int:
        try:
            if self.expense_dialog.open:
                self.expense_dialog.close_most_recent_dialog(self._page)
            if self.income_dialog.open:
                self.income_dialog.close_most_recent_dialog(self._page)

            self.category_dialog.load_categories(self.current_category_type)
            self.category_dialog.show(self._page)
            return 0

        except Exception as e:
            Logger.error(f"Error loading category selector data: {e}")
            return -1

    def open_category_selector_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self._load_category_selector_data()
        return e

    def _cancel_category_selector_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self.category_dialog.close_most_recent_dialog(self._page)
        return e

    def _handle_category_selected(self, category_name: str, category_type: str, e = None) -> None:
        self.category_dialog.close_most_recent_dialog(self._page)

        if category_type == "expense":
            self.expense_dialog.set_category(category_name)
            self.expense_dialog.show(self._page)
        elif category_type == "income":
            self.income_dialog.set_category(category_name)
            self.income_dialog.show(self._page)

        self.current_category_type = category_type

        return e

    # EXPENSE DIALOG
    def open_expense_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self.expense_dialog.show(self._page)
        return e

    def _cancel_expense_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self.expense_dialog.close_most_recent_dialog(self._page)
        return e

    def _handle_save_expense(self, e: ft.ControlEvent) -> ft.ControlEvent:
        success, message = self.controller.add_expense_entry(self.expense_dialog.get_values())

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

        if success:
            self.expense_dialog.clear()
            self._refresh_view()
            self.expense_dialog.close_most_recent_dialog(self._page)
        else:
            self._page.update()

        return e

    # INCOME DIALOG
    def open_income_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self.income_dialog.show(self._page)
        return e

    def _cancel_income_dialog(self, e: ft.ControlEvent) -> ft.ControlEvent:
        self.income_dialog.close_most_recent_dialog(self._page)
        return e

    def _handle_save_income(self, e: ft.ControlEvent) -> ft.ControlEvent:
        success, message = self.controller.add_income_entry(self.income_dialog.get_values())

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

        if success:
            self.income_dialog.clear()
            self._refresh_view()
            self.income_dialog.close_most_recent_dialog(self._page)
        else:
            self._page.update()

        return e

    # OVERLAY MANAGEMENT
    def _add_dialogs_to_overlay(self) -> None:
        dialogs = [
            self.category_dialog,
            self.expense_dialog,
            self.income_dialog
        ]
        for d in dialogs:
            d.add_to_overlay(self._page)

    def _remove_dialogs_from_overlay(self) -> None:
        dialogs = [
            self.category_dialog,
            self.expense_dialog,
            self.income_dialog
        ]
        for d in dialogs:
            d.remove_from_overlay(self._page)

class HomeView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.navigate_to = navigate_to
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info["username"])

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            refresh_callback=self.refresh_view
        )

        # FETCH DASHBOARD DATA
        self.objectives = self.controller.get_user_objectives()
        self.metrics, self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

        self.ai_advice = self.controller.get_ai_advice(
            net_balance=self.metrics["net_balance"],
            total_income=self.metrics["total_income"],
            total_expense=self.metrics["total_expense"]
        )

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.balance_card = BalanceCard(
            lang=self.lang,
            net_balance=self.metrics["net_balance"],
            income=self.metrics["total_income"],
            expense=self.metrics["total_expense"],
            savings=self.metrics["total_savings"],
            ai_advice=self.ai_advice,
            on_add_click=self.dialogs.open_category_selector_dialog,
            on_scan_click=self.navigate_to(self._page, "/purchase_scanner")
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            chart_date=self.chart_date,
            chart_data=self.chart_data,
            chart_type=self.chart_type
        )

        self.savings_progress_card = SavingsProgressCard(
            lang=self.lang,
            objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang),
            on_view_all_click=self.navigate_to(self._page, "/saving")
        )

        self.expense_pie_chart = ExpensePieChartCard(
            lang=self.lang,
            category_data=self.metrics["category_expenses"],
            on_details_click=self.navigate_to(self._page, "/spending")
        )

        self.featured_lesson_card = FeaturedLessonCard(
            lang=self.lang,
            on_learn_click=self.navigate_to(self._page, "/lessons")
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
                            spacing=20,
                            expand=True,
                            controls=[
                                self.balance_card,
                                self.financial_chart,
                                self.expense_pie_chart,
                                self.savings_progress_card,
                                self.featured_lesson_card
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
            route="/home",
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

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def refresh_view(self) -> int:
        try:
            self.objectives = self.controller.get_user_objectives()
            self.metrics, self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

            self.ai_advice = self.controller.get_ai_advice(
                self.metrics["net_balance"],
                self.metrics["total_income"],
                self.metrics["total_expense"]
            )

            self.balance_card.update_data(
                net_balance=self.metrics["net_balance"],
                income=self.metrics["total_income"],
                expense=self.metrics["total_expense"],
                savings=self.metrics["total_savings"],
                ai_advice=self.ai_advice
            )

            self.financial_chart.update_data(
                chart_date=self.chart_date,
                chart_data=self.chart_data,
                chart_type=self.chart_type
            )

            self.savings_progress_card.update_data(
                objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang)
            )

            self.expense_pie_chart.update_data(
                category_data=self.metrics["category_expenses"]
            )

            return 0

        except Exception as e:
            Logger.error(f"Error refreshing Home view: {e}")
            return -1

    def _on_page_resize(self, e = None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        # Resizing main container
        self.main_container.width = page_width
        self.main_container.height = page_height

        # Resizing other components
        self.menu.resize(
            width=page_width
        )

        self.dialogs.category_dialog.resize(
            dialog_width=int(page_width * 0.9),
            dialog_height=int(page_height * 0.9)
        )

        return e

def get_home_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return HomeView(page, lang, user_info)