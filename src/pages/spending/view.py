# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import sqlite3
from datetime import UTC, datetime
from typing import Any

import flet as ft

from src.logger import Logger
from src.pages.common import FinancialChart, Menu
from src.pages.spending.components import DeleteSpendingReportDialog, DeleteTransactionDialog, MetricCards, SpendingGoogleRequiredCard, SpendingMonthDialog, SpendingPageContent, SpendingReportDialog, SpendingReportHistoryCard, SpendingUsageCard, TransactionHistoryCard, TransactionToolbar
from src.pages.spending.logic import MIN_SPENDING_ANALYSIS_TRANSACTIONS, LogicController, SpendingAnalysisApiError
from src.utils import Color, Page, get_menu_resize_values, get_safe_page_size, scale_width

Logger.info("Initializing Spending page...")


class SpendingView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        self.filter_type = "all"
        self.search_query = ""
        self.sort_by = "newest"

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])
        self.spending_report_history = self.controller.get_spending_report_history()

        # FETCH INITIAL DATA
        balance_data, self.raw_transactions = self.controller.get_transaction_data()

        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.sort_by, self.search_query
        )
        self.category_icons = self.controller.get_category_icon_map()

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            username=user_info["username"],
            chart_type="daily",
            show_mode_buttons=True,
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
            sort_by=self.sort_by,
        )

        self.spending_report_dialog = SpendingReportDialog(
            page=self._page,
            lang=self.lang,
            on_delete=self._confirm_delete_spending_report,
        )

        self.delete_spending_report_dialog = DeleteSpendingReportDialog(
            page=self._page,
            lang=self.lang,
            on_confirm=self._delete_spending_report,
        )

        self.spending_month_dialog = SpendingMonthDialog(
            page=self._page,
            lang=self.lang,
            on_confirm=self._run_spending_scan,
        )

        self.spending_report_history_card = SpendingReportHistoryCard(
            lang=self.lang,
            on_open=self._open_saved_report,
        )

        self.spending_report_history_card.set_history(self.spending_report_history)

        self.usage_card = SpendingUsageCard(
            lang=self.lang
        )

        self.google_required_card = SpendingGoogleRequiredCard(
            lang=self.lang,
            on_login=self._open_google_settings,
            visible=not self.controller.has_google_account_session(),
        )

        self.usage_card.visible = self.controller.has_google_account_session()

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

        self.page_content = SpendingPageContent(
            metric_cards=self.metric_cards,
            financial_chart=self.financial_chart,
            google_required_card=self.google_required_card,
            usage_card=self.usage_card,
            toolbar=self.toolbar,
            history_card=self.history_card,
            report_history_card=self.spending_report_history_card,
        )

        super().__init__(
            route="/spending",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Stack(
                        expand=True, controls=[self.page_content, self.menu]
                    ),
                ),
            ],
        )

        self._page.on_resize = self._resize_page
        self._resize_page()
        self._update_google_access()
        if self.controller.has_google_account_session():
            self._page.run_thread(self._load_monthly_usage)

    def _refresh_view(self) -> int:
        self._resize_page()
        self._update_google_access()
        if self.controller.has_google_account_session():
            self._page.run_thread(self._load_monthly_usage)
        balance_data, self.raw_transactions = self.controller.get_transaction_data()
        self.category_icons = self.controller.get_category_icon_map()

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
            sort_by=self.sort_by,
        )

        self.history_card.update_data(filtered_txs, self.category_icons)
        self.spending_report_history = self.controller.get_spending_report_history()
        self.spending_report_history_card.set_history(self.spending_report_history)

        self.financial_chart.update_data()
        self._page.update()
        return 0

    def _delete_transaction(self, transaction_id: int) -> None:
        if self.controller.delete_transaction(transaction_id):
            self._refresh_view()
        else:
            Logger.warn(f"Failed to delete transaction {transaction_id}")

    def _open_google_settings(self, e: ft.ControlEvent | None = None) -> None:
        self._page.navigate_to("/user_management")(e)

    def _update_google_access(self) -> None:
        signed_in = self.controller.has_google_account_session()
        self.google_required_card.set_access(signed_in)
        self.usage_card.visible = signed_in
        if not signed_in:
            self._page.consume_spending_month_dialog_request()
        has_unlimited_access = signed_in and self.controller.is_cached_developer()
        if has_unlimited_access:
            self.usage_card.set_unlimited()
            self.toolbar.set_scan_enabled(True)
        else:
            self.toolbar.set_scan_enabled(False)
        self._page.update()

    def _open_pending_month_dialog(self) -> None:
        if not self._page.consume_spending_month_dialog_request():
            return
        if (
            self.toolbar.scan_button.disabled
            or not self.controller.has_google_account_session()
        ):
            return
        self.spending_month_dialog.trigger()

    def _load_monthly_usage(self) -> None:
        if self.controller.is_cached_developer():
            self.usage_card.set_unlimited()
            self.toolbar.set_scan_enabled(
                self.controller.has_google_account_session()
            )
            self._page.update()
            self._open_pending_month_dialog()
            return
        refresh_token = self.controller.get_google_refresh_token()
        try:
            usage = self.controller.get_monthly_analysis_usage(refresh_token or "")
            remaining, limit = self.controller.get_monthly_usage_counts(usage)
            if limit is not None:
                reset_at = datetime.fromisoformat(usage["reset_at"])
                if reset_at.tzinfo is None:
                    reset_at = reset_at.replace(tzinfo=UTC)
                reset_label = reset_at.astimezone().strftime("%Y-%m-%d %H:%M")
            else:
                reset_label = None
            self.usage_card.set_usage(remaining, limit, reset_label)
            self.toolbar.set_scan_enabled(
                limit is None or (remaining is not None and remaining > 0)
            )
            self._open_pending_month_dialog()
        except SpendingAnalysisApiError as ex:
            Logger.warning(f"Could not load spending analysis usage: {ex}")
            self.usage_card.set_unavailable()
            if ex.status_code in (401, 403):
                self.google_required_card.set_access(
                    False,
                    self.lang["purchase_scanner.google_session_expired"],
                )
                self.usage_card.visible = False
            self.toolbar.set_scan_enabled(False)
            self._page.consume_spending_month_dialog_request()
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid spending analysis usage response: {ex}")
            self.usage_card.set_unavailable()
            self.toolbar.set_scan_enabled(False)
            self._page.consume_spending_month_dialog_request()
        self._page.update()

    def handle_spending_scan(self, e: ft.ControlEvent | None = None) -> None:
        if (
            self.toolbar.scan_button.disabled
            or not self.controller.has_google_account_session()
        ):
            return
        self.spending_month_dialog.trigger(e)

        return

    def _run_spending_scan(self, month: str) -> None:
        if (
            self.toolbar.scan_button.disabled
            or not self.controller.has_google_account_session()
        ):
            return
        transaction_count = self.controller.get_month_transaction_count(month)
        if transaction_count < MIN_SPENDING_ANALYSIS_TRANSACTIONS:
            self.spending_report_dialog.show_error(
                self.lang["spending.ai_min_transactions"].format(
                    required=MIN_SPENDING_ANALYSIS_TRANSACTIONS,
                    count=transaction_count,
                )
            )
            return
        self.toolbar.set_scan_enabled(False)
        self._page.update()
        self.spending_report_dialog.show_loading()

        def worker() -> None:
            try:
                report, history = self.controller.analyze_and_save_spending(
                    self.controller.get_google_refresh_token() or "", month
                )
                self.spending_report_history = history
                self.spending_report_history_card.set_history(
                    self.spending_report_history
                )
                saved_report = self.spending_report_history[0]
                self.spending_report_dialog.show_report(
                    report,
                    saved_report["created_at"],
                    saved_report["id"],
                )
            except SpendingAnalysisApiError as ex:
                Logger.warning(f"Spending analysis request rejected: {ex}")
                if ex.status_code == 429:
                    message = self.lang["spending.ai_monthly_limit"]
                    self.toolbar.set_scan_enabled(False)
                    self._page.update()
                elif ex.status_code == 422:
                    message = self.lang["spending.ai_min_transactions"].format(
                        required=MIN_SPENDING_ANALYSIS_TRANSACTIONS,
                        count=self.controller.get_month_transaction_count(month),
                    )
                elif ex.status_code in (401, 403):
                    message = self.lang["purchase_scanner.sign_in_required"]
                    self.google_required_card.set_access(
                        False,
                        self.lang["purchase_scanner.google_session_expired"],
                    )
                    self.usage_card.visible = False
                    self.toolbar.set_scan_enabled(False)
                    self._page.update()
                elif ex.status_code == 0:
                    message = self.lang["purchase_scanner.connection_error"]
                else:
                    message = self.lang["spending.ai_service_error"]
                self.spending_report_dialog.show_error(message)
            except (KeyError, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
                Logger.error(f"Error during spending analysis: {ex}")
                self.spending_report_dialog.show_error(
                    self.lang["spending.ai_service_error"]
                )
            finally:
                if self.controller.get_google_refresh_token():
                    self._load_monthly_usage()

        self._page.run_thread(worker)

    def _open_saved_report(self, entry: dict[str, Any]) -> None:
        self.spending_report_dialog.show_report(
            entry["report"],
            entry["created_at"],
            entry["id"],
        )

    def _confirm_delete_spending_report(self, report_id: int) -> None:
        self.delete_spending_report_dialog.trigger(report_id)

    def _delete_spending_report(self, report_id: int) -> None:
        if not self.controller.delete_spending_report(report_id):
            Logger.warning(f"Failed to delete spending report {report_id}")
            return
        self.spending_report_dialog.dismiss()
        self.spending_report_history = self.controller.get_spending_report_history()
        self.spending_report_history_card.set_history(self.spending_report_history)
        self._page.update()

    def on_filter_change(self, f_type: str) -> None:
        self.filter_type = f_type

        self.toolbar.update_data(
            filter_type=self.filter_type,
            search_query=self.search_query,
            sort_by=self.sort_by,
        )

        self.update_history_list()

    def on_search_change(self, query: str) -> None:
        self.search_query = query
        self.update_history_list()

    def on_sort_change(self, sort_by: str) -> None:
        self.sort_by = sort_by
        self.update_history_list()

    def update_history_list(self) -> None:
        filtered_txs = self.controller.filter_transactions(
            self.raw_transactions, self.filter_type, self.sort_by, self.search_query
        )
        self.history_card.update_data(filtered_txs)

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_resize_values = self.get_menu_resize_values(page_width, self.menu)

            content_width = scale_width(page_width, 392)
            card_content_width = scale_width(page_width, 352)
            usage_content_width = scale_width(page_width, 356)
            transaction_item_content_width = scale_width(page_width, 324)
            transaction_dialog_width = page_width * 6 // 7
            transaction_dialog_content = scale_width(page_width, 322)
            transaction_title_width = scale_width(page_width, 274)
            report_dialog_width = scale_width(page_width, 408)
            report_card_width = scale_width(page_width, 368)
            secondary_dialog_width = page_width * 6 // 7
            secondary_dialog_content = scale_width(page_width, 330)

            # Resizing main container
            self.page_content.resize(
                page_width=page_width,
                page_height=page_height,
                content_width=content_width,
                card_content_width=card_content_width,
                usage_content_width=usage_content_width,
                transaction_item_content_width=transaction_item_content_width,
            )
            self.menu.resize(
                width=page_width,
                **menu_resize_values,
            )
            self.page_content.set_bottom_margin(self.menu.reserved_height)

            self.delete_dialog.resize(
                outer_width=transaction_dialog_width,
                content_width=transaction_dialog_content,
                title_width=transaction_title_width,
            )
            self.spending_report_dialog.resize(
                dialog_width=report_dialog_width,
                report_card_width=report_card_width,
            )
            self.spending_month_dialog.resize(
                width=secondary_dialog_width,
                content_width=secondary_dialog_content,
            )
            self.delete_spending_report_dialog.resize(
                width=secondary_dialog_width,
                content_width=secondary_dialog_content,
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_spending_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Spending page...")
    return SpendingView(page, lang, user_info)
