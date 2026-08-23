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


class SpendingView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        self.filter_type = "all"
        self.search_query = ""
        self.selected_category = "all"

        self.top_navigation_bar = None
        self.menu = None
        self.main_container = None

        self.controller = LogicController(user_info["username"], self._page, self.user_info, self.refresh_view)

        super().__init__(
            route="/spending",
            padding=0,
            bgcolor="#FAFAF8",
            controls=self.create_ui_components()
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def refresh_view(self):
        for control in self._page.overlay:
            control.open = False
        if len(self._page.views) > 0:
            self._page.views[-1].controls.clear()
            self._page.views[-1].controls.extend(get_spending_view(self._page, self.lang, self.user_info).controls)
        self._page.update()

    def on_filter_change(self, f_type: str):
        self.filter_type = f_type
        self.update_main_content()

    def on_search_change(self, query: str):
        self.search_query = query.lower()
        self.update_main_content()

    def on_category_change(self, cat: str):
        self.selected_category = cat
        self.update_main_content()

    def update_main_content(self):
        balance_data, raw_transactions = self.controller.get_transaction_data()

        all_txs = []
        for date_key, items in raw_transactions.items():
            for item in items:
                item["date_group"] = date_key
                all_txs.append(item)

        categories = list(set(t["title"] for t in all_txs))

        # Filter transactions based on type, search query, and category
        filtered_txs = []
        for tx in all_txs:
            is_income = tx.get("positive", False)
            t_type = "income" if is_income else "expense"

            if self.filter_type != "all" and t_type != self.filter_type:
                continue
            if self.selected_category != "all" and tx["title"] != self.selected_category:
                continue
            if self.search_query.strip():
                q = self.search_query
                match_cat = q in tx["title"].lower()
                match_note = q in tx.get("subtitle", "").lower()
                match_amt = q in str(tx["amount"]).lower()
                if not (match_cat or match_note or match_amt):
                    continue
            filtered_txs.append(tx)

        # Metric Cards Header
        metric_cards = MetricCards(
            total_income=balance_data["incomes"].replace("+", "").replace(" VND", ""),
            total_expense=balance_data["expenses"].replace("-", "").replace(" VND", ""),
            net_balance=balance_data["current"]
        )

        # Toolbar
        toolbar = TransactionToolbar(
            filter_type=self.filter_type,
            on_filter_change=self.on_filter_change,
            on_search_change=self.on_search_change,
            on_category_change=self.on_category_change,
            categories=categories,
            on_add_click=lambda e: self.controller.open_income_dialog(),
            lang=self.lang
        )

        # Transaction History List Container
        history_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.H4(f"Lịch Sử Giao Dịch ({len(filtered_txs)})", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                Text.SMALL("Cập nhật tự động theo thời gian", color=Color.SECONDARY_TEXT)
            ]
        )

        tx_list_controls = [history_header]
        if filtered_txs:
            for tx in filtered_txs:
                tx_list_controls.append(TransactionItemCard(tx, on_delete=lambda tid: self.controller.delete_transaction(tid)))
        else:
            tx_list_controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            Text.LABEL("Không tìm thấy giao dịch nào phù hợp.", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                            Text.SMALL("Hãy thử thay đổi bộ lọc hoặc thêm giao dịch mới.", color=Color.SECONDARY_TEXT)
                        ]
                    )
                )
            )

        history_container = ft.Container(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=ft.Column(spacing=12, controls=tx_list_controls)
        )

        self.main_container.content.controls = [
            metric_cards,
            toolbar,
            history_container
        ]
        try:
            self._page.update()
        except RuntimeError:
            pass

    def create_ui_components(self):
        Logger.info("Rendering UI for Spending page...")
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(current_user=self.user_info["username"])

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=0,
            margin=ft.Margin(left=16, top=84, right=16, bottom=88),
            content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=20)
        )
        self.update_main_content()

        return [
            ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        ]

    def on_page_resize(self, e=None):
        safe_width = int(min(self._page.width or UISettings.MAX_APP_WIDTH, UISettings.MAX_APP_WIDTH))
        self.top_navigation_bar.resize(safe_width)
        self.main_container.width = max(safe_width - 32, 320)
        self.main_container.margin = ft.Margin(left=16, top=84, right=16, bottom=88)
        self.menu.resize(safe_width)
        try:
            self.update()
        except RuntimeError:
            pass


def get_spending_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return SpendingView(page, lang, user_info)