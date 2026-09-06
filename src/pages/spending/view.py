# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, UISettings, Text
from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar
from src.pages.spending.logic import LogicController
from src.pages.spending.components import MetricCards, TransactionToolbar, TransactionItemCard

Logger.info("Initializing Spending page...")


class DialogManager:
    """Handles dialog state and callbacks for the Spending View."""

    def __init__(self, page: ft.Page, lang: dict, controller: LogicController, refresh_callback):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.refresh_view = refresh_callback
        self.current_category_type = None

        self.income_dialog = self.controller.income_dialog
        self.expense_dialog = self.controller.expense_dialog
        self.category_dialog = self.controller.category_dialog

    def close_all(self, e=None):
        dialogs = [
            self.income_dialog,
            self.expense_dialog,
            self.category_dialog
        ]
        for dialog in dialogs:
            if dialog:
                dialog.open = False
        self._page.update()
        return e

    def _open_dialog(self, dialog):
        self.close_all()
        if dialog not in self._page.overlay:
            self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def open_income_dialog(self, e=None):
        self._open_dialog(self.income_dialog)
        return e

    def open_expense_dialog(self, e=None):
        self._open_dialog(self.expense_dialog)
        return e

    def open_category_selector(self, category_type: str):
        self.current_category_type = category_type
        if self.category_dialog not in self._page.overlay:
            self._page.overlay.append(self.category_dialog)
        self.category_dialog.load_categories(category_type)
        self.category_dialog.open = True
        self._page.update()

    def handle_category_selected(self, category_name: str):
        if self.current_category_type == "expense":
            self.expense_dialog.set_category(category_name)
        elif self.current_category_type == "income":
            self.income_dialog.set_category(category_name)
        self.category_dialog.open = False
        self._page.update()

    def handle_save_income(self, e=None):
        return self.controller.handle_save_income()

    def handle_save_expense(self, e=None):
        return self.controller.handle_save_expense()


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
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            refresh_callback=self.refresh_view,
        )

        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info["username"],
        )

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

        self.content_column = ft.Column(
            spacing=20,
            expand=True,
            controls=[
                self.metric_cards,
                self.toolbar,
                self.history_container,
            ]
        )
        self.content_wrapper = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            content=self.content_column,
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_wrapper]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(top=UISettings.TOP_NAVIGATION_HEIGHT, bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/spending",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(expand=True, controls=[self.main_container, self.top_navigation_bar, self.menu]),
        )

        self._page.on_resize = self.on_page_resize
        self.refresh_content()
        self.on_page_resize()

    def refresh_view(self) -> None:
        for control in self._page.overlay:
            if hasattr(control, "open"):
                control.open = False
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
        except Exception:
            try:
                self._page.update()
            except RuntimeError:
                pass

    def _build_history_controls(self, filtered_txs):
        history_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.H4(f"Lịch Sử Giao Dịch ({len(filtered_txs)})", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                Text.SMALL("Cập nhật tự động theo thời gian", color=Color.SECONDARY_TEXT),
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

        self.content_column.controls = [
            self.metric_cards,
            self.toolbar,
            self.history_container,
        ]
        try:
            self._page.update()
        except RuntimeError:
            pass

    def get_safe_page_size(self) -> tuple[int, int]:
        current_width: float = self._page.width or UISettings.MAX_APP_WIDTH
        current_height: float = self._page.height or UISettings.MAX_APP_HEIGHT

        safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
        safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)
        return safe_width, safe_height

    def on_page_resize(self, e=None):
        safe_width, _ = self.get_safe_page_size()
        self.top_navigation_bar.resize(safe_width)
        self.main_container.width = safe_width
        self.menu.resize(safe_width)
        return e


def get_spending_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SpendingView(page, lang, user_info)