# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.database import db
from src.pages.global_components import FinancialChart, Menu
from src.pages.home.components import BalanceCard, SavingsProgressCard, ExpensePieChart, FeaturedLessonCard
from src.pages.home.logic import LogicController
from src.pages.spending.logic import (
    LogicController as SpendingController,
    SpendingAnalysisApiError,
)
from src.utils import Color, Page, get_menu_resize_values, get_safe_page_size, scale_width, UISettings

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
        self.spending_controller = SpendingController(self.user_info["username"])

        # FETCH DASHBOARD DATA & CURRENCY
        self.currency = self.controller.get_currency()
        self.objectives = self.controller.get_user_objectives()
        self.metrics = self.controller.get_dashboard_data()
        self.advice = self.controller.get_advice()

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.balance_card = BalanceCard(
            lang=self.lang,
            currency=self.currency,
            net_balance=self.metrics["net_balance"],
            income=self.metrics["total_income"],
            expense=self.metrics["total_expense"],
            savings=self.metrics["total_savings"],
            advice=self.advice,
            on_add_click=self._page.navigate_to("/category_selection"),
            on_scan_click=self._open_spending_report,
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            username=self.user_info["username"],
            chart_type="daily",
            show_mode_buttons=False
        )

        self.savings_progress_card = SavingsProgressCard(
            lang=self.lang,
            objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang, self.currency),
            on_view_all_click=self._page.navigate_to("/savings")
        )

        self.expense_pie_chart = ExpensePieChart(
            lang=self.lang,
            currency=self.currency,
            category_data=self.metrics["category_expenses"],
            on_details_click=self._page.navigate_to("/spending")
        )

        self.featured_lesson_card = FeaturedLessonCard(
            lang=self.lang,
            on_learn_click=self._page.navigate_to("/lessons")
        )

        # INITIALIZE MAIN CONTAINER
        self.content_container = ft.Container(
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

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
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
        self._update_spending_scan_access()
        if db.app_settings.has_google_account_session():
            self._page.run_thread(self._load_spending_usage)

    def _open_spending_report(self, e=None) -> None:
        if (
            self.balance_card.purchase_scanner_button.disabled
            or not db.app_settings.has_google_account_session()
        ):
            return
        self._page.open_spending_month_dialog = True
        self._page.navigate_to("/spending")(e)

    def _is_cached_developer(self) -> bool:
        account = db.app_settings.get_google_account()
        return bool(
            account
            and db.app_settings.get_google_account_tier(account["uid"])
            == "developer"
        )

    def _update_spending_scan_access(self) -> None:
        if self._is_cached_developer() and db.app_settings.has_google_account_session():
            self.balance_card.purchase_scanner_button.disabled = False
        else:
            self.balance_card.purchase_scanner_button.disabled = True

    def _load_spending_usage(self) -> None:
        if not db.app_settings.has_google_account_session():
            self.balance_card.purchase_scanner_button.disabled = True
            return
        if self._is_cached_developer():
            self.balance_card.purchase_scanner_button.disabled = False
            self._page.update()
            return

        refresh_token = db.app_settings.get_google_refresh_token()
        try:
            usage = self.spending_controller.get_monthly_analysis_usage(
                refresh_token or ""
            )
            limit = usage["limit"]
            remaining = usage["remaining"]
            if limit is None:
                available = remaining is None
            else:
                available = (
                    isinstance(limit, int)
                    and isinstance(remaining, int)
                    and 0 <= remaining <= limit
                    and remaining > 0
                )
                if not available:
                    raise ValueError("Invalid monthly spending usage counts")
            self.balance_card.purchase_scanner_button.disabled = not available
        except SpendingAnalysisApiError as ex:
            Logger.warning(f"Could not load home spending AI usage: {ex}")
            self.balance_card.purchase_scanner_button.disabled = True
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid home spending AI usage response: {ex}")
            self.balance_card.purchase_scanner_button.disabled = True
        self._page.update()

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self._update_spending_scan_access()
            if db.app_settings.has_google_account_session():
                self._page.run_thread(self._load_spending_usage)
            self.currency = self.controller.get_currency()
            self.objectives = self.controller.get_user_objectives()
            self.metrics = self.controller.get_dashboard_data()
            self.advice = self.controller.get_advice()

            self.balance_card.update_data(
                net_balance=self.metrics["net_balance"],
                income=self.metrics["total_income"],
                expense=self.metrics["total_expense"],
                savings=self.metrics["total_savings"],
                ai_advice=self.advice,
                currency=self.currency
            )

            self.financial_chart.update_data()

            self.savings_progress_card.update_data(
                objective_items=self.controller.get_saving_progress_items(
                    objectives=self.objectives,
                    lang=self.lang,
                    currency=self.currency
                )[0]
            )

            self.expense_pie_chart.update_data(
                category_data=self.metrics["category_expenses"],
                currency=self.currency
            )

            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)

            # Get component size values
            content_width = scale_width(page_width, 392)
            inner_width = scale_width(page_width, 352)
            savings_inner_width = inner_width
            goal_item_content_width = scale_width(page_width, 328)
            menu_resize_values = get_menu_resize_values(page_width, self.menu)
            chart_radius = int(page_height * 0.06)
            center_radius = int(page_height * 0.045)
            legend_height = int(page_height * 0.15)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            self.content_container.width = page_width
            self.main_container.margin.bottom = self.menu.reserved_height

            # Resizing other components
            self.menu.resize(
                width=page_width,
                **menu_resize_values,
            )

            self.balance_card.resize(width=inner_width)

            self.featured_lesson_card.resize(
                width=content_width,
                inner_width=inner_width
            )

            self.financial_chart.resize(
                width=inner_width
            )

            self.savings_progress_card.resize(
                width=content_width,
                inner_width=savings_inner_width,
                goal_item_content_width=goal_item_content_width,
            )

            self.expense_pie_chart.resize(
                width=content_width,
                inner_width=inner_width,
                chart_radius=chart_radius,
                center_radius=center_radius,
                legend_height=legend_height
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


def get_home_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Home page...")
    return HomeView(page, lang, user_info)