# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import CategorySelectionDialog, ExpenseInputDialog, IncomeInputDialog, FinancialChart, Menu
from src.pages.spending.logic import LogicController
from src.pages.spending.components import MetricCards, TransactionToolbar, TransactionItemCard
from src.utils import Color, get_safe_page_size, UISettings, Text

Logger.info("Initializing Spending page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Home View."""
    def __init__(self, page: ft.Page, lang: dict, controller: LogicController, refresh_callback: Callable):
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

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

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

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

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
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        self.filter_type = "all"
        self.search_query = ""
        self.selected_category = "all"
        self.raw_transactions = {}

        self.controller = LogicController(user_info["username"], self._page, self.lang, self.user_info, self.refresh_view)
        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            refresh_callback=self.refresh_view,
        )

        self.financial_chart = FinancialChart(
            lang=self.lang,
            chart_date=self.chart_date,
            chart_data=self.chart_data,
            chart_type=self.chart_type
        )

        self.menu = Menu(self._page, self.lang, self.user_info)

        self.metric_cards = MetricCards(
            page=self._page,
            lang=self.lang,
            total_income="0",
            total_expense="0",
            net_balance="0 VND",
        )
        self.toolbar = TransactionToolbar(
            page=self._page,
            lang=self.lang,
            filter_type=self.filter_type,
            on_filter_change=self.on_filter_change,
            on_search_change=self.on_search_change,
            on_category_change=self.on_category_change,
            categories=[],
            on_add_expense_click=self.dialogs.open_expense_dialog,
            on_add_income_click=self.dialogs.open_income_dialog,
            search_query=self.search_query,
            selected_category=self.selected_category
        )
        self.history_container = ft.Container(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=ft.Column(spacing=12, controls=[]),
        )

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
                                self.history_container
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
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def refresh_view(self) -> None:
        self.refresh_content()
        self._page.update()

    def on_filter_change(self, f_type: str):
        self.filter_type = f_type
        self.refresh_content()

    def on_search_change(self, query: str):
        self.search_query = query
        self.update_history_list()

    def on_category_change(self, cat: str):
        self.selected_category = cat
        self.update_history_list()

    def update_history_list(self):
        filtered_txs = self._filter_transactions(self.raw_transactions)
        self.history_container.content = ft.Column(
            spacing=12,
            controls=self._build_history_controls(filtered_txs),
        )
        try:
            self.history_container.update()
        except Exception as e:
            try:
                self._page.update()
            except RuntimeError:
                pass

    def _build_history_controls(self, filtered_txs):
        history_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.H4(f"Lịch Sử Giao Dịch ({len(filtered_txs)})", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
            ],
        )

        tx_list_controls = [history_header]
        if filtered_txs:
            for tx in filtered_txs:
                tx_list_controls.append(
                    TransactionItemCard(
                        page=self._page,
                        lang=self.lang,
                        tx=tx,
                        on_delete=lambda tid: self.controller.delete_transaction(tid),
                    )
                )
        else:
            tx_list_controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            Text.MEDIUM("Không tìm thấy giao dịch nào phù hợp.", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                            Text.SMALL("Hãy thử thay đổi bộ lọc hoặc thêm giao dịch mới.", color=Color.SECONDARY_TEXT),
                        ],
                    ),
                )
            )
        return tx_list_controls

    def _filter_transactions(self, raw_transactions):
        all_txs = []
        for date_key, items in raw_transactions.items():
            for item in items:
                item["date_group"] = date_key
                all_txs.append(item)

        filtered_txs = []
        for tx in all_txs:
            is_income = tx.get("positive", False)
            t_type = "income" if is_income else "expense"

            if self.filter_type != "all" and t_type != self.filter_type:
                continue
            if self.selected_category != "all" and tx.get("title") != self.selected_category:
                continue
            if self.search_query.strip():
                q = self.search_query.strip().lower()
                title = (tx.get("title") or "").lower()
                subtitle = (tx.get("subtitle") or "").lower()
                amount_str = str(tx.get("amount") or "").lower()

                q_digits = "".join(c for c in q if c.isdigit())
                amt_digits = "".join(c for c in amount_str if c.isdigit())

                match_title = q in title
                match_sub = q in subtitle
                match_amt = q in amount_str
                match_num = q_digits in amt_digits if q_digits else False

                if not (match_title or match_sub or match_amt or match_num):
                    continue
            filtered_txs.append(tx)
        return filtered_txs

    def refresh_content(self):
        balance_data, raw_transactions = self.controller.get_transaction_data()
        self.raw_transactions = raw_transactions

        self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

        all_categories = sorted(list({
            tx["title"] for items in raw_transactions.values() for tx in items if "title" in tx
        }))

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

        filtered_txs = self._filter_transactions(self.raw_transactions)
        self.history_container.content = ft.Column(
            spacing=12,
            controls=self._build_history_controls(filtered_txs),
        )

        self.financial_chart.update_data(
            chart_date=self.chart_date,
            chart_data=self.chart_data,
            chart_type=self.chart_type
        )

        try:
            self._page.update()
        except RuntimeError:
            pass

    def on_page_resize(self, e=None):
        safe_width, safe_height = get_safe_page_size(self._page)
        self.main_container.width = safe_width
        self.menu.resize(safe_width)
        return e


def get_spending_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SpendingView(page, lang, user_info)