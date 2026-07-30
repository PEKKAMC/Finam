# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft


from src.utils import Color, UISettings
from src.logger import Logger
from src.pages.global_components import SideMenu, TopNavigationBar, FinancialChart
from src.pages.spending.logic import LogicController
from src.pages.spending.components import BalanceCard, SummaryCards, SearchBar, ChartSelector, TransactionHistoryList

class SpendingView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state

        self.financial_chart = None
        self.chart_selector = None
        self.top_navigation_bar = None
        self.menu = None
        self.main_container = None

        self.controller = LogicController(user_state["current_user"], self._page, self.user_state, self.refresh_view)
        self.balance_data, self.transactions = self.controller.get_transaction_data()
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()
        self.transaction_history = TransactionHistoryList()

        super().__init__(
            route="/spending",
            padding=0,
            bgcolor=Color.WHITE,
            controls=self.create_ui_components()
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def refresh_view(self):
        for control in self._page.overlay: control.open = False
        if len(self._page.views) > 0:
            self._page.views[-1].controls.clear()
            self._page.views[-1].controls.extend(get_spending_view(self._page, self.lang, self.user_state).controls)
        self._page.update()

    def change_chart_type(self, new_type: str):
        if new_type == self.controller.current_chart_type: return
        self.controller.current_chart_type = new_type
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()
        self.financial_chart = FinancialChart(self.chart_date, self.chart_data, self.chart_type, self.lang)
        self.chart_selector = ChartSelector(self.controller.current_chart_type, self.change_chart_type)
        self.update_main_controls()
        self.update()

    def update_main_controls(self):
        self.transaction_history.update_data(self.transactions)
        self.main_container.content.controls = [
            self.top_navigation_bar,
            BalanceCard(self.balance_data["current"], self.balance_data["growth"], on_add_income_click=lambda e: self.controller.open_income_dialog(), on_add_expense_click=lambda e: self.controller.open_expense_dialog()),
            SummaryCards(self.balance_data["incomes"], self.balance_data["expenses"]),
            ft.Row([self.chart_selector], alignment=ft.MainAxisAlignment.END),
            self.financial_chart, SearchBar(),
            self.transaction_history
        ]

    def create_ui_components(self):
        Logger.info("Rendering UI for Spending page...")
        self.menu = SideMenu(self._page, self.lang, self.user_state)
        self.top_navigation_bar = TopNavigationBar(menu_button=self.menu.menu_button, current_user=self.user_state["current_user"])
        self.financial_chart = FinancialChart(self.chart_date, self.chart_data, self.chart_type, self.lang)
        self.chart_selector = ChartSelector(self.controller.current_chart_type, self.change_chart_type)

        self.main_container = ft.Container(width=UISettings.MAX_APP_WIDTH, padding=UISettings.CARD_PADDING, content=ft.Column(spacing=15))
        self.update_main_controls()

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
                    self.menu.view
                ]
            )
        ]

    def on_page_resize(self, e=None):
        safe_width = int(min(self._page.width or UISettings.MAX_APP_WIDTH, UISettings.MAX_APP_WIDTH))
        safe_height = int(max(300, (self._page.height or 800) * 0.4))
        self.top_navigation_bar.width = safe_width * 0.9
        self.main_container.width = safe_width
        self.financial_chart.width = safe_width * 0.95
        self.financial_chart.height = safe_height
        try: self.update()
        except RuntimeError: pass

def get_spending_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return SpendingView(page, lang, user_state)