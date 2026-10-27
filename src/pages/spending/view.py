# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import FinancialChart, Menu
from src.pages.spending.components import (
    DeleteTransactionDialog,
    MetricCards,
    TransactionHistoryCard,
    TransactionToolbar,
)
from src.pages.spending.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, UISettings

Logger.info("Initializing Spending page...")


class SpendingView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        self.filter_type = "all"
        self.search_query = ""
        self.sort_by = "newest"

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])

        # FETCH INITIAL DATA
        balance_data, self.raw_transactions = self.controller.get_transaction_data()
        self.current_chart_type = "daily"
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data(self.current_chart_type)

        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.sort_by, self.search_query
        )

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(self._page, self.lang, self.user_info)

        self.financial_chart = FinancialChart(
            lang=self.lang,
            username=user_info["username"],
            chart_type=self.chart_type,
            show_mode_buttons=True
        )

        self.metric_cards = MetricCards(
            page=self._page,
            lang=self.lang,
            total_income=balance_data["incomes"].replace("+", ""),
            total_expense=balance_data["expenses"].replace("-", ""),
            net_balance=balance_data["current"],
        )

        self.toolbar = TransactionToolbar(
            page=self._page,
            lang=self.lang,
            filter_type=self.filter_type,
            on_filter_change=self.on_filter_change,
            on_search_change=self.on_search_change,
            on_sort_change=self.on_sort_change,
            on_add_click=self._page.navigate_to("/category_selection"),
            search_query=self.search_query,
            sort_by=self.sort_by
        )

        self.delete_dialog = DeleteTransactionDialog(
            page=self._page,
            lang=self.lang,
            on_confirm=self._delete_transaction,
        )

        self.history_card = TransactionHistoryCard(
            page=self._page,
            lang=self.lang,
            transactions=filtered_txs,
            on_delete=self.delete_dialog.trigger,
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

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self.current_chart_type = self.financial_chart.chart_type

            if self.financial_chart.chart_type == self.current_chart_type:
                date_offset = self.financial_chart.date_offset
                target_year = self.financial_chart.monthly_year
            else:
                date_offset = 0
                target_year = None

            balance_data, self.raw_transactions = self.controller.get_transaction_data()

            self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data(
                self.current_chart_type,
                date_offset=date_offset,
                target_year=target_year
            )

            filtered_txs = self.controller.filter_transactions(
                self.raw_transactions, self.filter_type, self.sort_by, self.search_query
            )

            self.metric_cards.update_data(
                total_income=balance_data["incomes"].replace("+", ""),
                total_expense=balance_data["expenses"].replace("-", ""),
                net_balance=balance_data["current"],
            )

            self.toolbar.update_data(
                filter_type=self.filter_type,
                search_query=self.search_query,
                sort_by=self.sort_by
            )

            self.history_card.update_data(filtered_txs)

            self.financial_chart.update_data()
            self._page.update()

            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _delete_transaction(self, transaction_id: int) -> None:
        if self.controller.delete_transaction(transaction_id):
            self._refresh_view()
        else:
            Logger.warn(f"Failed to delete transaction {transaction_id}")

    def on_filter_change(self, f_type: str):
        self.filter_type = f_type

        self.toolbar.update_data(
            filter_type=self.filter_type,
            search_query=self.search_query,
            sort_by=self.sort_by
        )

        self.update_history_list()

    def on_search_change(self, query: str):
        self.search_query = query
        self.update_history_list()

    def on_sort_change(self, sort_by: str):
        self.sort_by = sort_by
        self.update_history_list()

    def update_history_list(self):
        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.sort_by, self.search_query
        )
        self.history_card.update_data(filtered_txs)

    def _on_page_resize(self, e = None) -> int:
        try:
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

            self.delete_dialog.resize(
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


def get_spending_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Spending page...")
    return SpendingView(page, lang, user_info)