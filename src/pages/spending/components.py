# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Color, Text


class BalanceCard(ft.Container):
    def __init__(self, balance, growth, on_add_income_click, on_add_expense_click):
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND, border_radius=UISettings.CARD_BORDER_RADIUS, padding=UISettings.CARD_PADDING,
            border=ft.Border.only(left=ft.border.BorderSide(4, Color.PRIMARY_ACTION)), shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text.LABEL("CURRENT BALANCE", color=Color.SECONDARY_TEXT),
                            ft.Container(width=100),
                            ft.Button("Income", color=Color.WHITE, bgcolor=Color.PRIMARY_ACTION, height=30, on_click=on_add_income_click),
                            ft.Button("Expense", color=Color.WHITE, bgcolor=Color.DELETE_ACTION, height=30, on_click=on_add_expense_click)
                        ]
                    ),
                    Text.LABEL(balance, color=Color.PRIMARY_TEXT),
                    ft.Row(spacing=5, controls=[ft.Icon(ft.Icons.TRENDING_UP, size=16, color=Color.CHART_INCOME), Text.LABEL(f"{growth} this month", color=Color.CHART_INCOME)])
                ]
            )
        )

class SummaryCards(ft.Row):
    def __init__(self, incomes, expenses):
        super().__init__(
            spacing=15,
            controls=[
                ft.Container(
                    expand=1, bgcolor=Color.CARD_BACKGROUND, border_radius=UISettings.CARD_BORDER_RADIUS, padding=UISettings.CARD_PADDING, shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
                    content=ft.Column(spacing=8, controls=[Text.LABEL("INCOMES", color=Color.SECONDARY_TEXT), Text.LABEL(incomes, color=Color.CHART_INCOME)])
                ),
                ft.Container(
                    expand=1, bgcolor=Color.CARD_BACKGROUND, border_radius=UISettings.CARD_BORDER_RADIUS, padding=UISettings.CARD_PADDING, shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
                    content=ft.Column(spacing=8, controls=[Text.LABEL("EXPENSES", color=Color.SECONDARY_TEXT), Text.LABEL(expenses, color=Color.CHART_EXPENSE)])
                )
            ]
        )

class SearchBar(ft.Row):
    def __init__(self):
        super().__init__(
            spacing=10,
            controls=[
                ft.TextField(hint_text="Search transactions...", prefix_icon=ft.Icons.SEARCH, expand=1, bgcolor=Color.CARD_BACKGROUND, border_color=Color.INPUT_BORDER, border_radius=10, content_padding=10, text_size=14),
                ft.Container(content=ft.Icon(ft.Icons.FILTER_LIST, color=Color.PRIMARY_TEXT), bgcolor=Color.CARD_BACKGROUND, border_radius=10, padding=10, border=ft.Border.all(1, Color.INPUT_BORDER))
            ]
        )

class TransactionItem(ft.Container):
    def __init__(self, data):
        amount_color = Color.CHART_INCOME if data["positive"] else Color.CHART_EXPENSE
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND, border_radius=10, padding=ft.Padding.symmetric(horizontal=15, vertical=12), shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=Color.SHADOW),
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.Container(content=ft.Icon(data["icon"], color=Color.DEFAULT_TEXT, size=20), bgcolor=Color.ACTIVITY_BACKGROUND, padding=10, border_radius=8),
                    ft.Column(expand=1, spacing=2, controls=[Text.LABEL(data["title"], color=Color.PRIMARY_TEXT), Text.SMALL(data["subtitle"], color=Color.SECONDARY_TEXT)]),
                    Text.LABEL(data["amount"], color=amount_color)
                ]
            )
        )

class ChartSelector(ft.Container):
    def __init__(self, current_type: str, on_change_callback):
        self.on_change = on_change_callback
        self.current_type = current_type

        buttons = []
        for t in ["daily", "weekly", "monthly"]:
            is_active = (self.current_type == t)
            buttons.append(ft.Container(
                content=Text.LABEL(t.capitalize(), color=Color.WHITE if is_active else Color.PRIMARY_TEXT),
                bgcolor=Color.PRIMARY_ACTION if is_active else Color.TRANSPARENT, padding=ft.Padding(15, 5, 15, 5), border_radius=20, on_click=self._create_handler(t), ink=True
            ))

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND, border_radius=25, padding=3,
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=buttons, spacing=0)
        )

    def _create_handler(self, new_type: str):
        def handler(e):
            self.on_change(new_type)
            return e
        return handler


class TransactionHistoryList(ft.Column):
    def __init__(self):
        super().__init__(spacing=10)

    def update_data(self, transactions_dict: dict):
        transaction_lists = []
        for date_header, items in transactions_dict.items():
            transaction_lists.append(ft.Container(margin=ft.Margin.only(top=10, bottom=5), content=Text.LABEL(date_header, color=Color.SECONDARY_TEXT)))
            for item in items:
                transaction_lists.append(TransactionItem(item))
        self.controls = transaction_lists