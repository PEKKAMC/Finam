# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import sqlite3

import flet as ft

from src.logger import Logger
from src.database import db
from src.pages.common import DeleteSpendingReportDialog, FinancialChart, Menu, SpendingMonthDialog, SpendingReportDialog
from src.pages.home.components import BalanceCard, ExpensePieChart, FeaturedLessonCard, SavingsProgressCard
from src.pages.home.logic import DashboardData, LogicController
from src.pages.spending.logic import MIN_SPENDING_ANALYSIS_TRANSACTIONS, LogicController as SpendingLogicController, SpendingAnalysisApiError
from src.utils import Color, MenuResizeValues, Page, UISettings, get_menu_resize_values, get_safe_page_size, scale_width

Logger.info("Initializing Home page...")


class HomeView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info["username"])
        self.spending_controller = SpendingLogicController(user_info["username"])

        self.spending_report_dialog = SpendingReportDialog(
            page=self._page,
            lang=self.lang,
            on_delete=self._confirm_delete_spending_report
        )
        self.delete_spending_report_dialog = DeleteSpendingReportDialog(
            page=self._page,
            lang=self.lang,
            on_confirm=self._delete_spending_report
        )
        self.spending_month_dialog = SpendingMonthDialog(
            page=self._page,
            lang=self.lang,
            on_confirm=self._run_spending_scan
        )

        # FETCH DASHBOARD DATA
        self._load_dashboard_data()

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.balance_card = BalanceCard(
            lang=self.lang,
            currency=self.currency,
            net_balance=self.dashboard_metrics["net_balance"],
            income=self.dashboard_metrics["total_income"],
            expense=self.dashboard_metrics["total_expense"],
            savings=self.dashboard_metrics["total_savings"],
            advice=self.advice,
            on_add_click=self._page.navigate_to("/category_selection"),
            on_scan_click=self._open_spending_report
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            username=self.user_info["username"],
            chart_type="daily",
            show_mode_buttons=False
        )

        self.savings_progress_card = SavingsProgressCard(
            lang=self.lang,
            objective_items=self.controller.get_saving_progress_items(
                self.objectives,
                self.lang,
                self.currency
            ),
            on_view_all_click=self._page.navigate_to("/savings")
        )

        self.expense_pie_chart = ExpensePieChart(
            lang=self.lang,
            currency=self.currency,
            category_data=self.dashboard_metrics["category_expenses"],
            on_details_click=self._page.navigate_to("/spending")
        )

        self.featured_lesson_card = FeaturedLessonCard(
            lang=self.lang,
            on_learn_click=self._page.navigate_to("/lessons")
        )

        # INITIALIZE MAIN CONTAINER
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
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

        self._page.on_resize = self._resize_page
        self._resize_page()
        self._update_spending_scan_access()
        if db.app_settings.has_google_account_session():
            self._page.run_thread(self._load_spending_usage)

    def _open_spending_report(self, e: ft.ControlEvent | None = None) -> None:
        if (
            self.balance_card.purchase_scanner_button.disabled
            or not db.app_settings.has_google_account_session()
        ):
            return
        self.spending_month_dialog.trigger(e)

    def _update_spending_scan_access(self) -> None:
        if (
            db.app_settings.is_cached_developer()
            and db.app_settings.has_google_account_session()
        ):
            self.balance_card.purchase_scanner_button.disabled = False
        else:
            self.balance_card.purchase_scanner_button.disabled = True

    def _load_dashboard_data(self) -> None:
        self.currency = self.controller.get_currency()
        self.objectives = self.controller.get_user_objectives()
        self.dashboard_metrics: DashboardData = (self.controller.get_dashboard_data())
        self.advice = self.controller.get_advice()

    def _update_dashboard_components(self) -> None:
        self.balance_card.update_data(
            net_balance=self.dashboard_metrics["net_balance"],
            income=self.dashboard_metrics["total_income"],
            expense=self.dashboard_metrics["total_expense"],
            savings=self.dashboard_metrics["total_savings"],
            ai_advice=self.advice,
            currency=self.currency
        )

        self.financial_chart.update_data()

        goal_items, objective_count = (
            self.controller.get_saving_progress_items(
                objectives=self.objectives,
                lang=self.lang,
                currency=self.currency
            )
        )

        self.savings_progress_card.update_data(
            objective_items=goal_items,
            objective_count=objective_count
        )

        self.expense_pie_chart.update_data(
            category_data=self.dashboard_metrics["category_expenses"],
            currency=self.currency
        )

    def _load_spending_usage(self) -> None:
        if not db.app_settings.has_google_account_session():
            self.balance_card.purchase_scanner_button.disabled = True
            return

        if db.app_settings.is_cached_developer():
            self.balance_card.purchase_scanner_button.disabled = False
            self._page.update()
            return

        refresh_token = db.app_settings.get_google_refresh_token()

        try:
            usage = self.spending_controller.get_monthly_analysis_usage(
                refresh_token or ""
            )
            remaining, limit = self.spending_controller.get_monthly_usage_counts(
                usage
            )
            self.balance_card.purchase_scanner_button.disabled = (
                limit is not None and (remaining is None or remaining <= 0)
            )

        except SpendingAnalysisApiError as ex:
            Logger.warning(f"Could not load home spending AI usage: {ex}")
            self.balance_card.purchase_scanner_button.disabled = True

        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid home spending AI usage response: {ex}")
            self.balance_card.purchase_scanner_button.disabled = True

        self._page.update()

    def _run_spending_scan(self, month: str) -> None:
        if (
            self.balance_card.purchase_scanner_button.disabled
            or not self.spending_controller.has_google_account_session()
        ):
            return

        transaction_count = self.spending_controller.get_month_transaction_count(
            month
        )
        if transaction_count < MIN_SPENDING_ANALYSIS_TRANSACTIONS:
            self.spending_report_dialog.show_error(
                self.lang["spending.ai_min_transactions"].format(
                    required=MIN_SPENDING_ANALYSIS_TRANSACTIONS,
                    count=transaction_count
                )
            )
            return

        self.balance_card.purchase_scanner_button.disabled = True
        self._page.update()
        self.spending_report_dialog.show_loading()

        def worker() -> None:
            try:
                report, history = self.spending_controller.analyze_and_save_spending(
                    self.spending_controller.get_google_refresh_token() or "",
                    month
                )
                saved_report = history[0]
                self.spending_report_dialog.show_report(
                    report,
                    saved_report["created_at"],
                    saved_report["id"]
                )
            except SpendingAnalysisApiError as ex:
                Logger.warning(f"Home spending analysis request rejected: {ex}")
                if ex.status_code == 429:
                    message = self.lang["spending.ai_monthly_limit"]
                    self.balance_card.purchase_scanner_button.disabled = True
                elif ex.status_code == 422:
                    message = self.lang["spending.ai_min_transactions"].format(
                        required=MIN_SPENDING_ANALYSIS_TRANSACTIONS,
                        count=self.spending_controller.get_month_transaction_count(
                            month
                        )
                    )
                elif ex.status_code in (401, 403):
                    message = self.lang["purchase_scanner.sign_in_required"]
                    self.balance_card.purchase_scanner_button.disabled = True
                elif ex.status_code == 0:
                    message = self.lang["purchase_scanner.connection_error"]
                else:
                    message = self.lang["spending.ai_service_error"]
                self.spending_report_dialog.show_error(message)
            except (KeyError, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
                Logger.error(f"Error during home spending analysis: {ex}")
                self.spending_report_dialog.show_error(
                    self.lang["spending.ai_service_error"]
                )
            finally:
                self._load_spending_usage()

        self._page.run_thread(worker)

    def _confirm_delete_spending_report(self, report_id: int) -> None:
        self.delete_spending_report_dialog.trigger(report_id)

    def _delete_spending_report(self, report_id: int) -> None:
        if not self.spending_controller.delete_spending_report(report_id):
            Logger.warning(f"Failed to delete spending report {report_id}")
            return
        self.spending_report_dialog.dismiss()
        self._page.update()

    def _refresh_view(self) -> int:
        try:
            self._resize_page()
            self._update_spending_scan_access()
            if db.app_settings.has_google_account_session():
                self._page.run_thread(self._load_spending_usage)
            self._load_dashboard_data()
            self._update_dashboard_components()

            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_resize_values: MenuResizeValues = self.get_menu_resize_values(
                page_width, self.menu
            )

            content_width = scale_width(page_width, 392)
            inner_width = scale_width(page_width, 352)
            savings_inner_width = inner_width
            goal_item_content_width = scale_width(page_width, 328)
            chart_radius = int(page_height * 0.06)
            center_radius = int(page_height * 0.045)
            legend_height = int(page_height * 0.15)
            report_dialog_width = scale_width(page_width, 408)
            report_card_width = scale_width(page_width, 368)
            secondary_dialog_width = page_width * 6 // 7
            secondary_dialog_content = scale_width(page_width, 330)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            self.content_container.width = page_width
            self.main_container.margin.bottom = self.menu.reserved_height

            # Resizing other components
            self.menu.resize(
                width=page_width,
                **menu_resize_values
            )

            self.balance_card.resize(
                width=inner_width
            )

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
                goal_item_content_width=goal_item_content_width
            )

            self.expense_pie_chart.resize(
                width=content_width,
                inner_width=inner_width,
                chart_radius=chart_radius,
                center_radius=center_radius,
                legend_height=legend_height
            )

            self.spending_report_dialog.resize(
                dialog_width=report_dialog_width,
                report_card_width=report_card_width
            )
            self.spending_month_dialog.resize(
                width=secondary_dialog_width,
                content_width=secondary_dialog_content
            )
            self.delete_spending_report_dialog.resize(
                width=secondary_dialog_width,
                content_width=secondary_dialog_content
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")


def get_home_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Home page...")
    return HomeView(page, lang, user_info)