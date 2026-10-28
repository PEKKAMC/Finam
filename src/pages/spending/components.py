# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings, format_number


class MetricCards(ft.ResponsiveRow):
    """Top summary metric cards matching the TSX TransactionsView layout."""
    def __init__(self, page: Page, lang: dict, total_income: str, total_expense: str, net_balance: str):
        self._page = page
        self.lang = lang
        self.total_income = total_income
        self.total_expense = total_expense
        self.net_balance = net_balance

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.income_title_text = Text.SMALL(self.lang["spending.total_income"].upper(), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.expense_title_text = Text.SMALL(self.lang["spending.total_expense"].upper(), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.balance_title_text = Text.SMALL(self.lang["spending.net_balance"].upper(), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.expense_icon = ft.Icon(ft.Icons.SOUTH_EAST, color=Color.EXPENSE_COLOR, size=20)
        self.income_icon = ft.Icon(ft.Icons.NORTH_EAST, color=Color.INCOME_COLOR, size=20)
        self.balance_icon = ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=Color.LIGHT_ACCENT, size=20)

        # Dynamic texts
        self.income_value_text = Text.H3(f"+{self.total_income}", color=Color.INCOME_COLOR, weight=ft.FontWeight.BOLD)
        self.expense_value_text = Text.H3(f"-{self.total_expense}", color=Color.EXPENSE_COLOR, weight=ft.FontWeight.BOLD)
        self.balance_value_text = Text.H3(self.net_balance, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.income_card = ft.Container(
            col={"xs": 12, "sm": 4},
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.only(left=ft.BorderSide(4, Color.INCOME_COLOR)),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[self.income_title_text, self.income_value_text]
                    ),
                    ft.Container(
                        content=self.income_icon,
                        bgcolor=Color.INCOME_BACKGROUND,
                        width=40,
                        height=40,
                        border_radius=16,
                        alignment=ft.Alignment.CENTER
                    )
                ]
            )
        )

        self.expense_card = ft.Container(
            col={"xs": 12, "sm": 4},
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.only(left=ft.BorderSide(4, Color.EXPENSE_COLOR)),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[self.expense_title_text, self.expense_value_text]
                    ),
                    ft.Container(
                        content=self.expense_icon,
                        bgcolor=Color.EXPENSE_BACKGROUND,
                        width=40,
                        height=40,
                        border_radius=16,
                        alignment=ft.Alignment.CENTER
                    )
                ]
            )
        )

        self.balance_card = ft.Container(
            col={"xs": 12, "sm": 4},
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.only(left=ft.BorderSide(4, Color.PRIMARY_ACTION)),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[self.balance_title_text, self.balance_value_text]
                    ),
                    ft.Container(
                        content=self.balance_icon,
                        bgcolor=Color.DARK_SURFACE,
                        width=40,
                        height=40,
                        border_radius=16,
                        alignment=ft.Alignment.CENTER
                    )
                ]
            )
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=16,
                controls=[
                    self.income_card,
                    self.expense_card,
                    self.balance_card
                ]
            )
        )

        super().__init__(
            spacing=16,
            controls=[self.main_container]
        )

    def update_data(self, total_income: str, total_expense: str, net_balance: str):
        self.total_income = total_income
        self.total_expense = total_expense
        self.net_balance = net_balance

        self.income_value_text.value = f"+{self.total_income}"
        self.expense_value_text.value = f"-{self.total_expense}"
        self.balance_value_text.value = self.net_balance

        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width


class TransactionToolbar(ft.Container):
    """Filter, Search, and Action Toolbar"""
    def __init__(self, page: Page, lang: dict, filter_type: str, on_filter_change: Callable, on_search_change: Callable, on_sort_change: Callable, on_add_click: Callable, search_query: str = "", sort_by: str = "newest"):
        self._page = page
        self.lang = lang
        self.on_filter = on_filter_change
        self.on_search = on_search_change
        self.on_sort = on_sort_change
        self.filter_type = filter_type
        self.search_query = search_query
        self.sort_by = sort_by

        def create_filter_button(label: str, f_type: str, active_bg: str):
            is_active = (self.filter_type == f_type)
            return ft.Button(
                content=Text.SMALL(label, color=Color.WHITE if is_active else Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                bgcolor=active_bg if is_active else ft.Colors.TRANSPARENT,
                on_click=lambda e: self.on_filter(f_type) if self.on_filter else None,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=14),
                    padding=ft.Padding(16, 10, 16, 10),
                    bgcolor=active_bg if is_active else Color.CARD_BACKGROUND
                )
            )

        # TEXT AND ICON COMPONENTS
        self.all_filter_button = create_filter_button(self.lang["generic.all"], "all", Color.PRIMARY)
        self.expense_filter_button = create_filter_button(self.lang["spending.expense_label"], "expense", Color.PRIMARY)
        self.income_filter_button = create_filter_button(self.lang["spending.income_label"], "income", Color.PRIMARY)

        self.add_button = ft.Button(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.ADD, color=Color.WHITE, size=18),
                    Text.MEDIUM(self.lang["spending.add_transaction"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
                ],
                tight=True
            ),
            bgcolor=Color.PRIMARY_ACTION,
            on_click=on_add_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=12
            )
        )

        sort_options = [
            ft.dropdown.Option("newest", lang["spending.sort_newest"]),
            ft.dropdown.Option("oldest", lang["spending.sort_oldest"]),
        ]
        valid_sort_keys = [opt.key for opt in sort_options]
        dropdown_value = self.sort_by if self.sort_by in valid_sort_keys else "newest"

        self.search_field = ft.TextField(
            value=self.search_query,
            hint_text=self.lang["spending.search"],
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.on_search(e.control.value) if self.on_search else None,
            bgcolor=Color.CARD_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True
        )

        self.sort_dropdown = ft.Dropdown(
            leading_icon=ft.Icons.ACCESS_TIME,
            options=sort_options,
            value=dropdown_value,
            on_select=lambda e: self.on_sort(e.control.value) if self.on_sort else None,
            bgcolor=Color.CARD_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True
        )

        # LAYOUT CONTAINERS
        self.filter_buttons_row = ft.Row(
            spacing=6,
            controls=[
                self.all_filter_button,
                self.expense_filter_button,
                self.income_filter_button
            ]
        )

        self.action_buttons_row = ft.Row(
            spacing=6,
            controls=[
                self.add_button
            ]
        )

        self.top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
            controls=[
                self.filter_buttons_row,
                self.action_buttons_row
            ]
        )

        self.search_box_container = ft.Container(
            col={"xs": 12, "sm": 6},
            content=self.search_field
        )

        self.sort_box_container = ft.Container(
            col={"xs": 12, "sm": 6},
            content=self.sort_dropdown
        )

        self.inputs_row = ft.ResponsiveRow(
            spacing=12,
            run_spacing=12,
            controls=[
                self.search_box_container,
                self.sort_box_container
            ]
        )

        self.main_container = ft.Column(
            spacing=16,
            controls=[
                self.top_row,
                self.inputs_row
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def update_data(self, filter_type: str, search_query: str, sort_by: str):
        self.filter_type = filter_type
        self.search_query = search_query
        self.sort_by = sort_by

        buttons_info = [
            (self.all_filter_button, "all", Color.PRIMARY),
            (self.expense_filter_button, "expense", Color.PRIMARY),
            (self.income_filter_button, "income", Color.PRIMARY)
        ]

        for button, f_type, active_bg in buttons_info:
            is_active = (self.filter_type == f_type)
            button.content.color = Color.WHITE if is_active else Color.SECONDARY_TEXT
            button.bgcolor = active_bg if is_active else Color.TRANSPARENT
            button.style.bgcolor = active_bg if is_active else Color.CARD_BACKGROUND

        self.search_field.value = self.search_query
        self.sort_dropdown.value = self.sort_by if self.sort_by in ["newest", "oldest"] else "newest"

        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width


class TransactionHistoryCard(ft.Container):
    """Transaction History Container matching HomeView component style."""
    def __init__(self, page: Page, lang: dict, transactions: list, on_delete: Callable):
        self._page = page
        self.lang = lang
        self.transactions = transactions
        self.on_delete = on_delete
        self.is_expanded = True

        self.history_column = ft.Column(spacing=12, controls=[])
        self._render_controls()

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.history_column,
        )

    def _render_controls(self):
        self.history_title = Text.H4(
            self.lang["spending.transaction_history"].format(len=len(self.transactions)),
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD,
        )
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE,
            tooltip=self.lang["generic.collapse"] if self.is_expanded else self.lang["generic.expand"],
            on_click=self._toggle_expanded,
        )
        history_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.history_title,
                self.toggle_button,
            ],
        )

        tx_list_controls: list[ft.Control] = []
        if self.transactions:
            for tx in self.transactions:
                tx_list_controls.append(
                    TransactionItemCard(
                        page=self._page,
                        lang=self.lang,
                        tx=tx,
                        on_delete=self.on_delete,
                    )
                )
        else:
            tx_list_controls = [
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            Text.MEDIUM(self.lang["spending.no_transactions"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                            Text.SMALL(self.lang["spending.try_filter"], color=Color.SECONDARY_TEXT),
                        ],
                    ),
                )
            ]

        self.history_content = ft.Column(
            spacing=12,
            controls=tx_list_controls,
            visible=self.is_expanded,
        )
        self.history_column.controls = [history_header, self.history_content]

    def _toggle_expanded(self, e):
        self.is_expanded = not self.is_expanded
        self.history_content.visible = self.is_expanded
        self.toggle_button.icon = ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        self.toggle_button.tooltip = self.lang["generic.collapse"] if self.is_expanded else self.lang["generic.expand"]
        if self._page is not None:
            self._page.update()

    def update_data(self, transactions: list):
        self.transactions = transactions
        self._render_controls()
        if self.page:
            self.update()

    def resize(self, width: int):
        self.width = max(width, 0)
        self.history_column.width = max(width, 0)


class TransactionItemCard(ft.Container):
    def __init__(self, page: Page, lang: dict, tx: dict, on_delete: Callable | None = None):
        self._page = page
        self.lang = lang
        self.tx = tx
        self.on_delete = on_delete

        is_income = self.tx.get("positive", False)
        amount_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR
        icon_bg = Color.INCOME_BACKGROUND if is_income else Color.EXPENSE_BACKGROUND
        icon_color = amount_color
        icon = ft.Icons.NORTH_EAST if is_income else ft.Icons.SOUTH_EAST

        # TEXT AND ICON COMPONENTS
        self.type_badge_text = Text.SMALL(self.lang["spending.income"] if is_income else self.lang["spending.expense"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
        self.title_text = Text.MEDIUM(self.tx["title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.subtitle_text = Text.SMALL(self.tx.get("subtitle", ""), color=Color.SECONDARY_TEXT)
        self.date_text = Text.SMALL(self.tx.get("date", ""), color=Color.SECONDARY_TEXT)
        self.amount_text = Text.MEDIUM(format_number(self.tx["amount"]), color=amount_color, weight=ft.FontWeight.BOLD)

        self.item_icon = ft.Icon(icon, color=icon_color, size=18)
        self.calendar_icon = ft.Icon(ft.Icons.CALENDAR_MONTH, color=Color.SECONDARY_TEXT, size=12)

        # CONTAINER COMPONENTS
        self.icon_box = ft.Container(
            content=self.item_icon,
            bgcolor=icon_bg,
            width=42,
            height=42,
            border_radius=16,
            alignment=ft.Alignment.CENTER
        )

        self.badge_box = ft.Container(
            content=self.type_badge_text,
            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
            padding=ft.Padding(8, 2, 8, 2),
            border_radius=10
        )

        self.title_row = ft.Row(
            spacing=8,
            controls=[
                self.title_text,
                self.badge_box
            ]
        )

        self.date_row = ft.Row(
            spacing=4,
            controls=[
                self.calendar_icon,
                self.date_text
            ],
            tight=True
        )

        self.info_column = ft.Column(
            spacing=2,
            controls=[
                self.title_row,
                self.subtitle_text,
                self.date_row
            ]
        )

        self.left_group = ft.Row(
            expand=True,
            spacing=14,
            controls=[
                self.icon_box,
                self.info_column
            ]
        )

        if self.on_delete:
            self.delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                icon_size=18,
                on_click=lambda e: self.on_delete(self.tx.get("id")) if self.on_delete else None,
                tooltip=self.lang["spending.delete"]
            )
            right_controls = [self.amount_text, self.delete_button]
        else:
            right_controls = [self.amount_text]

        self.right_group = ft.Row(
            spacing=12,
            controls=right_controls
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.left_group,
                self.right_group
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=14,
            ink=True,
            content=self.main_row
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_row.width = width


class DeleteTransactionDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_confirm: Callable[[int], None]):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        self.transaction_id: int | None = None

        self.title_text = Text.H3(
            self.lang["spending.confirm_delete_title"],
            color=Color.PRIMARY_TEXT,
        )
        self.desc_text = Text.P(
            self.lang["spending.confirm_delete_content"],
            color=Color.SECONDARY_TEXT,
        )
        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"],
        )
        self.delete_button = ft.Button(
            self.lang["generic.delete"],
            on_click=self._confirm,
            bgcolor=Color.DELETE_ACTION,
            color=Color.WHITE,
        )

        self.main_container = ft.Container(
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[self.title_text, self.close_button],
                    ),
                    self.desc_text,
                ],
            ),
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.delete_button],
            padding=0,
        )
        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)

    def trigger(self, transaction_id: int | None) -> None:
        if transaction_id is None:
            return
        self.transaction_id = transaction_id
        self.show()

    def _confirm(self, e=None) -> None:
        if self.transaction_id is None:
            return
        self.dismiss()
        self.on_confirm(self.transaction_id)

    def resize(self, width: int) -> None:
        outer_width = max(width, 0)
        content_width = max(outer_width - 48, 0)
        self.main_container.width = outer_width
        self.main_container.content.width = content_width
        self.title_text.width = max(content_width - 48, 0)
        self.desc_text.width = content_width