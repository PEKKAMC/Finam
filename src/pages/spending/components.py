# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft
from src.utils import Color, Text


class MetricCards(ft.ResponsiveRow):
    """Top summary metric cards matching the TSX TransactionsView layout."""
    def __init__(self, total_income: str, total_expense: str, net_balance: str):
        def card(title: str, value: str, text_color: str, border_color: str, icon: ft.Icon, icon_bg: str):
            return ft.Container(
                col={"xs": 12, "sm": 4},
                bgcolor=Color.WHITE,
                border_radius=24,
                padding=20,
                border=ft.Border.only(left=ft.BorderSide(4, border_color)),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=Color.SHADOW),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                Text.SMALL(title, color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                                Text.H3(value, color=text_color, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.Container(
                            content=icon,
                            bgcolor=icon_bg,
                            width=40,
                            height=40,
                            border_radius=16,
                            alignment=ft.Alignment.CENTER
                        )
                    ]
                )
            )

        super().__init__(
            spacing=16,
            controls=[
                card(
                    "TỔNG THU NHẬP",
                    f"+{total_income}",
                    "#1A4734",
                    "#1A4734",
                    ft.Icon(ft.Icons.NORTH_EAST, color="#1A4734", size=20),
                    "#DAF1DE"
                ),
                card(
                    "TỔNG CHI TIÊU",
                    f"-{total_expense}",
                    "#E90C00",
                    "#E90C00",
                    ft.Icon(ft.Icons.SOUTH_EAST, color="#E90C00", size=20),
                    "#FEE2E2",
                ),
                card(
                    "SỐ DƯ RÒNG",
                    net_balance,
                    Color.PRIMARY_TEXT,
                    "#059669",
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#DAF1DE", size=20),
                    "#064E3B"
                ),
            ]
        )


class TransactionToolbar(ft.Container):
    """Filter, Search, and Action Toolbar matching the TSX design."""
    def __init__(self, filter_type: str, on_filter_change, on_search_change, on_category_change, categories: list, on_add_click: Callable, lang: dict):
        self.on_filter = on_filter_change
        self.on_search = on_search_change
        self.on_category = on_category_change

        # Filter type buttons
        def filter_btn(label: str, f_type: str, active_bg: str):
            is_active = (filter_type == f_type)
            return ft.Button(
                content=Text.SMALL(label, color=ft.Colors.WHITE if is_active else Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                bgcolor=active_bg if is_active else ft.Colors.TRANSPARENT,
                on_click=lambda e: self.on_filter(f_type),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=14),
                    padding=ft.Padding(16, 10, 16, 10),
                    bgcolor=active_bg if is_active else ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
                )
            )

        category_options = [ft.dropdown.Option("all", "Tất cả danh mục chi/thu")] + [ft.dropdown.Option(c, c) for c in categories]

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    filter_btn("Tất cả", "all", "#1A4734"),
                                    filter_btn("Khoản chi (-)", "expense", "#E90C00"),
                                    filter_btn("Khoản thu (+)", "income", "#1A4734")
                                ]
                            ),
                            ft.Button(
                                content=ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.ADD, color="#DAF1DE", size=18),
                                        Text.LABEL("Thêm Giao Dịch", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                    ],
                                    tight=True
                                ),
                                bgcolor="#1A4734",
                                on_click=on_add_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=16),
                                    padding=12
                                )
                            )
                        ]
                    ),
                    ft.ResponsiveRow(
                        spacing=12,
                        run_spacing=12,
                        controls=[
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=ft.TextField(
                                    hint_text="Tìm theo từ khóa, ghi chú, số tiền...",
                                    prefix_icon=ft.Icons.SEARCH,
                                    on_change=lambda e: self.on_search(e.control.value),
                                    bgcolor=Color.CARD_BACKGROUND,
                                    border_color=Color.INPUT_BORDER,
                                    border_radius=16,
                                    text_size=13,
                                    content_padding=12,
                                    filled=True
                                )
                            ),
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=ft.Dropdown(
                                    leading_icon=ft.Icons.TAG,
                                    options=category_options,
                                    value="all",
                                    on_select=lambda e: self.on_category(e.control.value),
                                    bgcolor=Color.CARD_BACKGROUND,
                                    border_color=Color.INPUT_BORDER,
                                    border_radius=16,
                                    text_size=13,
                                    content_padding=12,
                                    filled=True
                                )
                            )
                        ]
                    )
                ]
            )
        )


class TransactionItemCard(ft.Container):
    def __init__(self, tx: dict, on_delete=None):
        is_income = tx.get("positive", False)
        amount_color = "#1A4734" if is_income else "#E90C00"
        amount_prefix = "+" if is_income else "-"
        icon_bg = "#DAF1DE" if is_income else "#FEE2E2"
        icon_color = "#1A4734" if is_income else "#E90C00"
        icon = ft.Icons.NORTH_EAST if is_income else ft.Icons.SOUTH_EAST

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=18,
            padding=14,
            ink=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color=icon_color, size=18),
                                bgcolor=icon_bg,
                                width=42,
                                height=42,
                                border_radius=16,
                                alignment=ft.Alignment.CENTER
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            Text.LABEL(tx["title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                            ft.Container(
                                                content=Text.SMALL("Thu nhập" if is_income else "Chi tiêu", color=ft.Colors.SLATE_700 if hasattr(ft.Colors, 'SLATE_700') else "#334155", weight=ft.FontWeight.BOLD),
                                                bgcolor=ft.Colors.SLATE_100 if hasattr(ft.Colors, 'SLATE_100') else "#F1F5F9",
                                                padding=ft.Padding(8, 2, 8, 2),
                                                border_radius=10
                                            )
                                        ]
                                    ),
                                    Text.SMALL(tx.get("subtitle", ""), color=Color.SECONDARY_TEXT),
                                    ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.CALENDAR_MONTH, color=Color.SECONDARY_TEXT, size=12),
                                            Text.SMALL(tx.get("date", ""), color=Color.SECONDARY_TEXT)
                                        ],
                                        tight=True
                                    )
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            Text.LABEL(f"{amount_prefix}{tx['amount']}", color=amount_color, weight=ft.FontWeight.BOLD),
                            *(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400,
                                        icon_size=18,
                                        on_click=lambda e: on_delete(tx.get("id")) if on_delete else None,
                                        tooltip="Xóa giao dịch"
                                    )
                                ] if on_delete else []
                            )
                        ]
                    )
                ]
            )
        )