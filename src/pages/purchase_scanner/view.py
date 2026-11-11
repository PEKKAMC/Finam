# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import sqlite3
from datetime import UTC, datetime

import flet as ft

from src.logger import Logger
from src.pages.common import Menu
from src.pages.purchase_scanner.components import (
    ScannerForm,
    ScannerHistoryCard,
    ScannerPageContent,
    ScannerResult,
)
from src.pages.purchase_scanner.logic import LogicController, ScannerApiError
from src.utils import Color, MenuResizeValues, Page, get_menu_resize_values, get_safe_page_size

Logger.info("Initializing Purchase Scanner page...")


class PurchaseScannerView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(user_info["username"])
        self.scan_history = self.controller.get_scan_history()
        self.currency = self.controller.get_currency()

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(page=self._page, lang=self.lang, user_info=self.user_info)

        self.form_card = ScannerForm(
            page=self._page,
            lang=self.lang,
            currency=self.currency,
            on_scan_click=self.handle_scan_click,
        )

        self.result_card = ScannerResult(
            page=self._page, lang=self.lang, currency=self.currency
        )

        self.history_card = ScannerHistoryCard(
            page=self._page,
            lang=self.lang,
            on_delete_entry=self.handle_delete_history_entry,
            on_clear_all=self.handle_clear_history,
            currency=self.currency,
        )

        self.history_card.set_history(self.scan_history)
        self.scanner_content = ScannerPageContent(
            lang=self.lang,
            form_card=self.form_card,
            result_card=self.result_card,
            history_card=self.history_card,
            signed_in=self.controller.has_google_account_session(),
        )

        super().__init__(
            route="/purchase_scanner",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.scanner_content,
                        self.menu
                    ]
                ),
            ),
        )

        self._page.on_resize = self._resize_page
        self._resize_page()
        self._update_google_access()

    def _update_google_access(self) -> None:
        signed_in = self.controller.has_google_account_session()
        self.scanner_content.set_google_access(signed_in)
        if not signed_in or not self.controller.is_cached_developer():
            self.form_card.set_enabled(False)
            return
        self._show_unlimited_usage()
        self.form_card.set_enabled(True)

    def _show_unlimited_usage(self) -> None:
        usage_card = self.scanner_content.usage_card
        usage_card.usage_label.value = self.lang["purchase_scanner.usage_unlimited"]
        usage_card.usage_progress.value = 1
        usage_card.usage_progress.color = Color.PROGRESS_ACTIVE

    def _load_monthly_usage(self) -> None:
        if self.controller.is_cached_developer():
            self._show_unlimited_usage()
            self.form_card.set_enabled(
                self.controller.has_google_account_session()
            )
            self._page.update()
            return
        try:
            usage = self.controller.get_monthly_usage_for_current_session()
            remaining = usage["remaining"]
            limit = usage["limit"]
            if limit is None:
                self.scanner_content.usage_card.usage_label.value = self.lang["purchase_scanner.usage_unlimited"]
                progress = 1.0
            else:
                reset_at_value = usage["reset_at"]
                if remaining is None or reset_at_value is None:
                    raise ValueError("Monthly usage is missing reset or remaining data")
                reset_at = datetime.fromisoformat(reset_at_value)
                if reset_at.tzinfo is None:
                    reset_at = reset_at.replace(tzinfo=UTC)
                reset_label = reset_at.astimezone().strftime("%Y-%m-%d %H:%M")
                remaining_label = self.lang["purchase_scanner.usage_remaining"].format(
                    remaining=remaining, limit=limit, reset=reset_label
                )
                progress = remaining / limit if limit > 0 else 0.0
                self.scanner_content.usage_card.usage_label.value = remaining_label
            self.scanner_content.usage_card.usage_progress.value = progress
            self.form_card.set_enabled(
                (limit is None or (remaining is not None and remaining > 0))
                and self.controller.has_google_account_session()
            )
            self.scanner_content.usage_card.usage_progress.color = (
                Color.PROGRESS_ACTIVE
                if limit is None or remaining
                else Color.WARNING_COLOR
            )
        except ScannerApiError as ex:
            Logger.warning(f"Could not load purchase scanner monthly usage: {ex}")
            self.scanner_content.usage_card.usage_label.value = self.lang["purchase_scanner.usage_unavailable"]
            self.form_card.set_enabled(False)
            if ex.status_code in (401, 403):
                self.scanner_content.google_required_card.message_text.value = self.lang["purchase_scanner.google_session_expired"]
                self.scanner_content.set_google_access(False)
                self.form_card.set_enabled(False)
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid purchase scanner usage response: {ex}")
            self.scanner_content.usage_card.usage_label.value = self.lang["purchase_scanner.usage_unavailable"]
            self.form_card.set_enabled(False)
        try:
            self.scanner_content.usage_card.update()
            self.scanner_content.google_required_card.update()
            self.form_card.update()
        except RuntimeError:
            pass

    def handle_scan_click(self, name: str, price: str, reason: str, trigger: str, time: str) -> None:
        if not self.controller.has_google_account_session():
            return
        self.form_card.set_scanning(True)
        self._page.update()
        request_generation = self.result_card.set_loading_state()
        item_name = name if name else self.lang["purchase_scanner.item"]

        def worker() -> None:
            try:
                risk, trigger_display, price_val, ai_advice = (self.controller.analyze_and_save_purchase(self.lang, item_name, price, reason, trigger, time))

                if risk is not None:
                    self.history_card.set_history(self.controller.get_scan_history())

                if risk is None:
                    self._page.run_task(self.result_card.show_the_rock_result, request_generation, risk, trigger_display, price_val, ai_advice)
                else:
                    self.result_card.update_result(
                        risk, trigger_display, price_val, ai_advice
                    )

            except ScannerApiError as ex:
                Logger.warning(f"Purchase scanner request rejected: {ex}")
                if ex.status_code == 429:
                    error_message = self.lang["purchase_scanner.monthly_limit"]
                    self.form_card.set_enabled(False)
                elif ex.status_code in (401, 403):
                    error_message = self.lang["purchase_scanner.sign_in_required"]
                    self.scanner_content.set_google_access(False)
                    self.form_card.set_enabled(False)
                elif ex.status_code == 0:
                    error_message = self.lang["purchase_scanner.connection_error"]
                else:
                    error_message = self.lang["purchase_scanner.service_error"]
                self.result_card.show_error(error_message)
            except (KeyError, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
                Logger.error(f"Error during background analysis: {ex}")
                self.result_card.show_error(self.lang["purchase_scanner.service_error"])
            finally:
                if self.controller.has_google_refresh_token():
                    self._load_monthly_usage()
                self.form_card.set_scanning(False)
                self._page.update()

        self._page.run_thread(worker)

    def handle_delete_history_entry(self, entry: int) -> None:
        self.controller.delete_scan_result(entry)
        self.history_card.set_history(self.controller.get_scan_history())

    def handle_clear_history(self) -> None:
        self.controller.clear_scan_history()
        self.history_card.set_history(self.controller.get_scan_history())

    def _refresh_view(self) -> int:
        self._update_google_access()
        self._resize_page()
        self.scan_history = self.controller.get_scan_history()
        self.history_card.set_history(self.scan_history)
        if self.controller.has_google_account_session():
            self._page.run_thread(self._load_monthly_usage)
        return 0

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_resize_values: MenuResizeValues = self.get_menu_resize_values(
                page_width, self.menu
            )

            self.scanner_content.resize(page_width, page_height)
            self.menu.resize(
                width=page_width,
                **menu_resize_values,
            )
            self.scanner_content.margin.bottom = self.menu.reserved_height


        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_scanner_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Purchase Scanner page...")
    return PurchaseScannerView(page, lang, user_info)
