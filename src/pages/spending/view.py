# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import CategorySelectionDialog, ExpenseInputDialog, FinancialChart, IncomeInputDialog, Menu
from src.pages.spending.components import MetricCards, TransactionHistoryCard, TransactionToolbar
from src.pages.spending.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, Text, UISettings

Logger.info("Initializing Spending page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Spending View."""
    def __init__(self, page: Page, lang: dict, controller: LogicController, refresh_callback: Callable):
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

        self.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self.snack_bar.open = True

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

        self.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self.snack_bar.open = True

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


class SpendingView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        self.filter_type = "all"
        self.search_query = ""
        self.selected_category = "all"

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"], self._page, self.lang, self.user_info, self.refresh_view)

        # FETCH INITIAL DATA
        balance_data, self.raw_transactions = self.controller.get_transaction_data()
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

        all_categories = sorted(list({
            tx["title"] for items in self.raw_transactions.values() for tx in items if "title" in tx
        }))
        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.selected_category, self.search_query
        )

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            refresh_callback=self.refresh_view,
        )

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(self._page, self.lang, self.user_info)

        self.financial_chart = FinancialChart(
            lang=self.lang,
            chart_date=self.chart_date,
            chart_data=self.chart_data,
            chart_type=self.chart_type
        )

        self.metric_cards = MetricCards(
            page=self._page,
            lang=self.lang,
            total_income=balance_data["incomes"].replace("+", "").replace(" VND", ""),
            total_expense=balance_data["expenses"].replace("-", "").replace(" VND", ""),
            net_balance=balance_data["current"],
        )

        self.toolbar = TransactionToolbar(
            page=self._page,
            lang=self.lang,
            filter_type=self.filter_type,
            on_filter_change=self.on_filter_change,
            on_search_change=self.on_search_change,
            on_category_change=self.on_category_change,
            categories=all_categories,
            on_add_expense_click=self.dialogs.open_expense_dialog,
            on_add_income_click=self.dialogs.open_income_dialog,
            search_query=self.search_query,
            selected_category=self.selected_category
        )

        self.history_card = TransactionHistoryCard(
            page=self._page,
            lang=self.lang,
            transactions=filtered_txs,
            on_delete=lambda tid: self.controller.delete_transaction(tid)
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
                                self.metric_cards,
                                self.financial_chart,
                                self.toolbar,
                                self.history_card
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
            route="/spending",
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

    def refresh_view(self) -> int:
        try:
            balance_data, self.raw_transactions = self.controller.get_transaction_data()
            self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

            all_categories = sorted(list({
                tx["title"] for items in self.raw_transactions.values() for tx in items if "title" in tx
            }))
            filtered_txs = self.controller.filter_transactions(
                self.raw_transactions, self.filter_type, self.selected_category, self.search_query
            )

            self.metric_cards.update_data(
                total_income=balance_data["incomes"].replace("+", "").replace(" VND", ""),
                total_expense=balance_data["expenses"].replace("-", "").replace(" VND", ""),
                net_balance=balance_data["current"],
            )

            self.toolbar.update_data(
                filter_type=self.filter_type,
                search_query=self.search_query,
                selected_category=self.selected_category,
                categories=all_categories
            )

            self.history_card.update_data(filtered_txs)

            self.financial_chart.update_data(
                chart_date=self.chart_date,
                chart_data=self.chart_data,
                chart_type=self.chart_type
            )

            if self._page:
                self._page.update()

            return 0
        except RuntimeError as e:
            Logger.warn(f"Failed to refresh view {e}")
            return -1

    def on_filter_change(self, f_type: str):
        self.filter_type = f_type
        self.update_history_list()

    def on_search_change(self, query: str):
        self.search_query = query
        self.update_history_list()

    def on_category_change(self, cat: str):
        self.selected_category = cat
        self.update_history_list()

    def update_history_list(self):
        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.selected_category, self.search_query
        )
        self.history_card.update_data(filtered_txs)

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

        self.metric_cards.resize(
            width=page_width
        )

        self.toolbar.resize(
            width=page_width
        )

        self.history_card.resize(
            width=page_width
        )

        return e


def get_spending_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Spending page...")
    return SpendingView(page, lang, user_info)