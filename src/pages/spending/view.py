# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime, timezone

import flet as ft

from src.logger import Logger
from src.database import db
from src.pages.global_components import FinancialChart, Menu
from src.pages.spending.components import DeleteTransactionDialog, MetricCards, SpendingReportDialog, SpendingReportHistoryCard, SpendingUsageCard, TransactionHistoryCard, TransactionToolbar
from src.pages.spending.logic import LogicController, SpendingAnalysisApiError
from src.utils import Color, Page, Text, get_safe_page_size, UISettings

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
        self.spending_report_history = self.controller.get_spending_report_history()

        # FETCH INITIAL DATA
        balance_data, self.raw_transactions = self.controller.get_transaction_data()
        self.current_chart_type = "daily"
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data(self.current_chart_type)

        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.sort_by, self.search_query
        )
        self.category_icons = self.controller.get_category_icon_map()

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
            on_scan_click=self.handle_spending_scan,
            search_query=self.search_query,
            sort_by=self.sort_by
        )

        self.spending_report_dialog = SpendingReportDialog(
            page=self._page,
            lang=self.lang,
        )
        self.spending_report_history_card = SpendingReportHistoryCard(
            lang=self.lang,
            on_open=self._open_saved_report,
        )
        self.spending_report_history_card.set_history(self.spending_report_history)
        self.usage_card = SpendingUsageCard(self.lang)
        self.google_required_message = ft.Text(
            self.lang["spending_ai.google_required"],
            color=Color.SECONDARY_TEXT,
            size=13,
        )
        self.google_required_card = ft.Container(
            visible=not db.app_settings.has_google_account_session(),
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Icon(
                        ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                        color=Color.PRIMARY_ACTION,
                        size=24,
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            Text.MEDIUM(
                                self.lang["spending_ai.google_required_title"],
                                color=Color.PRIMARY_TEXT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            self.google_required_message,
                        ],
                    ),
                    ft.TextButton(
                        content=self.lang["purchase_scanner.google_login_action"],
                        on_click=self._open_google_settings,
                    ),
                ],
            ),
        )
        self.usage_card.visible = db.app_settings.has_google_account_session()

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
            category_icons=self.category_icons,
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
                                self.google_required_card,
                                self.usage_card,
                                self.toolbar,
                                self.history_card,
                                self.spending_report_history_card,
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
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
        self._update_google_access()
        if db.app_settings.has_google_account_session():
            self._page.run_thread(self._load_monthly_usage)

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self._update_google_access()
            if db.app_settings.has_google_account_session():
                self._page.run_thread(self._load_monthly_usage)
            self.current_chart_type = self.financial_chart.chart_type

            if self.financial_chart.chart_type == self.current_chart_type:
                date_offset = self.financial_chart.date_offset
                target_year = self.financial_chart.monthly_year
            else:
                date_offset = 0
                target_year = None

            balance_data, self.raw_transactions = self.controller.get_transaction_data()
            self.category_icons = self.controller.get_category_icon_map()

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

            self.history_card.update_data(filtered_txs, self.category_icons)
            self.spending_report_history = (
                self.controller.get_spending_report_history()
            )
            self.spending_report_history_card.set_history(
                self.spending_report_history
            )

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

    def _open_google_settings(self, e=None):
        self._page.navigate_to("/user_management")()

    def _update_google_access(self) -> None:
        signed_in = db.app_settings.has_google_account_session()
        self.google_required_card.visible = not signed_in
        self.usage_card.visible = signed_in
        self.toolbar.set_scan_enabled(False)
        self.google_required_message.value = self.lang["spending_ai.google_required"]
        self._page.update()

    def _load_monthly_usage(self) -> None:
        refresh_token = db.app_settings.get_google_refresh_token()
        try:
            usage = self.controller.get_monthly_analysis_usage(refresh_token or "")
            reset_at = datetime.fromisoformat(usage["reset_at"])
            if reset_at.tzinfo is None:
                reset_at = reset_at.replace(tzinfo=timezone.utc)
            reset_label = reset_at.astimezone().strftime("%Y-%m-%d %H:%M")
            remaining = usage["remaining"]
            if not isinstance(remaining, int) or remaining not in (0, 1):
                raise ValueError("Invalid monthly usage remaining count")
            self.usage_card.set_usage(remaining, reset_label)
            self.toolbar.set_scan_enabled(remaining > 0)
        except SpendingAnalysisApiError as ex:
            Logger.warning(f"Could not load spending analysis usage: {ex}")
            self.usage_card.set_unavailable()
            if ex.status_code in (401, 403):
                self.google_required_message.value = self.lang[
                    "purchase_scanner.google_session_expired"
                ]
                self.google_required_card.visible = True
                self.usage_card.visible = False
                self.toolbar.set_scan_enabled(False)
            elif ex.status_code == 404:
                self.toolbar.set_scan_enabled(False)
            else:
                self.toolbar.set_scan_enabled(False)
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid spending analysis usage response: {ex}")
            self.usage_card.set_unavailable()
            self.toolbar.set_scan_enabled(False)
        self._page.update()

    def handle_spending_scan(self, e=None) -> None:
        if (
            self.toolbar.scan_button.disabled
            or not db.app_settings.has_google_account_session()
        ):
            return
        self.toolbar.set_scan_enabled(False)
        self._page.update()
        self.spending_report_dialog.show_loading()

        def worker():
            try:
                report = self.controller.analyze_spending(
                    db.app_settings.get_google_refresh_token() or ""
                )
                if not self.controller.save_spending_report(report):
                    raise RuntimeError("Could not save generated spending report.")
                self.spending_report_history = (
                    self.controller.get_spending_report_history()
                )
                self.spending_report_history_card.set_history(
                    self.spending_report_history
                )
                created_at = self.spending_report_history[0]["created_at"]
                self.spending_report_dialog.show_report(report, created_at)
            except SpendingAnalysisApiError as ex:
                Logger.warning(f"Spending analysis request rejected: {ex}")
                if ex.status_code == 429:
                    message = self.lang["spending_ai.monthly_limit"]
                    self.toolbar.set_scan_enabled(False)
                    self._page.update()
                elif ex.status_code in (401, 403):
                    message = self.lang["purchase_scanner.sign_in_required"]
                    self.google_required_message.value = self.lang[
                        "purchase_scanner.google_session_expired"
                    ]
                    self.google_required_card.visible = True
                    self.usage_card.visible = False
                    self.toolbar.set_scan_enabled(False)
                    self._page.update()
                elif ex.status_code == 0:
                    message = self.lang["purchase_scanner.connection_error"]
                else:
                    message = self.lang["spending_ai.service_error"]
                self.spending_report_dialog.show_error(message)
            except Exception as ex:
                Logger.error(f"Error during spending analysis: {ex}")
                self.spending_report_dialog.show_error(
                    self.lang["spending_ai.service_error"]
                )
            finally:
                if db.app_settings.get_google_refresh_token():
                    self._load_monthly_usage()

        self._page.run_thread(worker)

    def _open_saved_report(self, entry: dict) -> None:
        self.spending_report_dialog.show_report(
            entry["report"],
            entry["created_at"],
        )

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
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_item_size = page_width // self.menu.items_count
            menu_inside_size = menu_item_size // 6 * 5

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

            # Resizing other components
            self.menu.resize(
                width=page_width,
                item_size=menu_item_size,
                inside_size=menu_inside_size,
            )
            self.main_container.margin.bottom = self.menu.reserved_height

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
            self.spending_report_dialog.resize(
                width=page_width,
                height=page_height,
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