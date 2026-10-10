# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import FinancialChart, Menu
from src.pages.home.components import BalanceCard, SavingsProgressCard, ExpensePieChart, FeaturedLessonCard
from src.pages.home.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, UISettings

Logger.info("Initializing Home page...")


class HomeView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info["username"])

        # FETCH DASHBOARD DATA
        self.objectives = self.controller.get_user_objectives()
        self.metrics = self.controller.get_dashboard_data()

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
            on_add_click=self._page.navigate_to("/category_selection"),
            on_scan_click=self._page.navigate_to("/purchase_scanner")
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            username=self.user_info["username"],
            chart_type="daily",
            show_mode_buttons=False
        )

        self.savings_progress_card = SavingsProgressCard(
            lang=self.lang,
            objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang, self.user_info.get("username", "Admin")),
            on_view_all_click=self._page.navigate_to("/saving")
        )

        self.expense_pie_chart = ExpensePieChart(
            lang=self.lang,
            category_data=self.metrics["category_expenses"],
            on_details_click=self._page.navigate_to("/spending")
        )

        self.featured_lesson_card = FeaturedLessonCard(
            lang=self.lang,
            on_learn_click=self._page.navigate_to("/lessons")
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
            self.objectives = self.controller.get_user_objectives()
            self.metrics = self.controller.get_dashboard_data()

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

            self.financial_chart.update_data()

            self.savings_progress_card.update_data(
                objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang)
            )

            self.expense_pie_chart.update_data(
                category_data=self.metrics["category_expenses"]
            )

            return 0

        except Exception as e:
            Logger.warn(f"Failed to refresh view {e}")
            return -1

    def _on_page_resize(self, e = None) -> None:
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

        self.balance_card.resize(
            width=page_width
        )

        self.featured_lesson_card.resize(
            width=page_width
        )

        self.balance_card.resize(
            width=page_width
        )

        self.savings_progress_card.resize(
            width=page_width
        )

        self.expense_pie_chart.resize(
            width=page_width,
            height=page_height
        )
        self.featured_lesson_card.resize(
            width=page_width
        )


def get_home_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Home page...")
    return HomeView(page, lang, user_info)