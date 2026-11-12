# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import sqlite3
from collections.abc import Callable
from typing import Any, Protocol

import flet as ft

from src.logger import Logger
from src.pages.common.spending_analysis_dialogs import DeleteSpendingReportDialog, SpendingMonthDialog, SpendingReportDialog
from src.utils import Page


class SpendingAnalysisController(Protocol):
    def has_google_account_session(self) -> bool: ...

    def get_month_transaction_count(self, month: str) -> int: ...

    def get_google_refresh_token(self) -> str | None: ...

    def analyze_and_save_spending(
        self, refresh_token: str, month: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]: ...

    def delete_spending_report(self, report_id: int) -> bool: ...


class SpendingAnalysisDialogManager:
    def __init__(
        self,
        page: Page,
        lang: dict[str, str],
        controller: SpendingAnalysisController,
        min_transactions: int,
        api_error_type: type[RuntimeError],
        can_scan: Callable[[], bool],
        set_scan_enabled: Callable[[bool], None],
        refresh_usage: Callable[[], None],
        on_auth_expired: Callable[[], None] | None = None,
        on_report_history_changed: Callable[[list[dict[str, Any]]], None]
        | None = None,
        on_report_deleted: Callable[[], None] | None = None,
    ) -> None:
        self._page = page
        self._lang = lang
        self._controller = controller
        self._min_transactions = min_transactions
        self._api_error_type = api_error_type
        self._can_scan = can_scan
        self._set_scan_enabled = set_scan_enabled
        self._refresh_usage = refresh_usage
        self._on_auth_expired = on_auth_expired
        self._on_report_history_changed = on_report_history_changed
        self._on_report_deleted = on_report_deleted

        self.report_dialog = SpendingReportDialog(
            page=page,
            lang=lang,
            on_delete=self.confirm_delete_report,
        )
        self.delete_report_dialog = DeleteSpendingReportDialog(
            page=page,
            lang=lang,
            on_confirm=self.delete_report,
        )
        self.month_dialog = SpendingMonthDialog(
            page=page,
            lang=lang,
            on_confirm=self.run_scan,
        )

    def open_scan(self, event: ft.ControlEvent | None = None) -> None:
        if not self._can_scan() or not self._controller.has_google_account_session():
            return
        self.month_dialog.trigger(event)

    def run_scan(self, month: str) -> None:
        if not self._can_scan() or not self._controller.has_google_account_session():
            return

        transaction_count = self._controller.get_month_transaction_count(month)
        if transaction_count < self._min_transactions:
            self.report_dialog.show_error(
                self._lang["spending.ai_min_transactions"].format(
                    required=self._min_transactions,
                    count=transaction_count,
                )
            )
            return

        self._set_scan_enabled(False)
        self._page.update()
        self.report_dialog.show_loading()

        def worker() -> None:
            try:
                report, history = self._controller.analyze_and_save_spending(
                    self._controller.get_google_refresh_token() or "",
                    month,
                )
                if self._on_report_history_changed is not None:
                    self._on_report_history_changed(history)
                saved_report = history[0]
                self.report_dialog.show_report(
                    report,
                    saved_report["created_at"],
                    saved_report["id"],
                )
            except self._api_error_type as ex:
                self._handle_api_error(ex, month)
            except (
                IndexError,
                KeyError,
                RuntimeError,
                sqlite3.Error,
                TypeError,
                ValueError,
            ) as ex:
                self._handle_unexpected_error(ex)
            finally:
                self._refresh_usage()

        self._page.run_thread(worker)

    def show_saved_report(self, entry: dict[str, Any]) -> None:
        self.report_dialog.show_report(
            entry["report"],
            entry["created_at"],
            entry["id"],
        )

    def confirm_delete_report(self, report_id: int) -> None:
        self.delete_report_dialog.trigger(report_id)

    def delete_report(self, report_id: int) -> None:
        if not self._controller.delete_spending_report(report_id):
            Logger.warning(f"Failed to delete spending report {report_id}")
            return
        self.report_dialog.dismiss()
        if self._on_report_deleted is not None:
            self._on_report_deleted()

    def resize_report(self, dialog_width: int, report_card_width: int) -> None:
        self.report_dialog.resize(dialog_width, report_card_width)

    def resize_secondary_dialogs(self, width: int, content_width: int) -> None:
        self.month_dialog.resize(width, content_width)
        self.delete_report_dialog.resize(width, content_width)

    def _handle_api_error(self, error: RuntimeError, month: str) -> None:
        status_code = getattr(error, "status_code", None)
        Logger.warning(f"Spending analysis request rejected: {error}")
        if status_code == 429:
            message = self._lang["spending.ai_monthly_limit"]
            self._set_scan_enabled(False)
        elif status_code == 422:
            message = self._lang["spending.ai_min_transactions"].format(
                required=self._min_transactions,
                count=self._controller.get_month_transaction_count(month),
            )
        elif status_code in (401, 403):
            message = self._lang["purchase_scanner.sign_in_required"]
            self._set_scan_enabled(False)
            if self._on_auth_expired is not None:
                self._on_auth_expired()
        elif status_code == 0:
            message = self._lang["purchase_scanner.connection_error"]
        else:
            message = self._lang["spending.ai_service_error"]
        self._page.update()
        self.report_dialog.show_error(message)

    def _handle_unexpected_error(self, error: Exception) -> None:
        Logger.error(f"Error during spending analysis: {error}")
        self.report_dialog.show_error(
            self._lang["spending.ai_service_error"]
        )
