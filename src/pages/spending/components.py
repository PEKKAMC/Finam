# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from typing import Any

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings, format_compact_number, to_decimal


class MetricCards(ft.ResponsiveRow):
    """Top summary metric cards matching the TSX TransactionsView layout."""

    def __init__(self, page: Page, lang: dict[str, str], total_income: str, total_expense: str, net_balance: str) -> None:
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
        self.income_value_text = Text.H4(f"+{self.total_income}", color=Color.INCOME_COLOR, weight=ft.FontWeight.BOLD)
        self.expense_value_text = Text.H4(f"-{self.total_expense}", color=Color.EXPENSE_COLOR, weight=ft.FontWeight.BOLD)
        self.balance_value_text = Text.H4(self.net_balance, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.income_card = ft.Container(
            col={"xs": 12, "sm": 4},
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            border=ft.Border.only(left=ft.BorderSide(4, Color.INCOME_BACKGROUND)),
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
            border_radius=28,
            padding=20,
            border=ft.Border.only(left=ft.BorderSide(4, Color.EXPENSE_BACKGROUND)),
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
            border_radius=28,
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

    def update_data(self, total_income: str, total_expense: str, net_balance: str) -> None:
        self.total_income = total_income
        self.total_expense = total_expense
        self.net_balance = net_balance

        self.income_value_text.value = f"+{self.total_income}"
        self.expense_value_text.value = f"-{self.total_expense}"
        self.balance_value_text.value = self.net_balance

        self.update()

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width


class TransactionToolbar(ft.Container):
    """Filter, Search, and Action Toolbar"""

    def __init__(self, page: Page, lang: dict[str, str], filter_type: str, on_filter_change: Callable[..., None], on_search_change: Callable[..., None], on_sort_change: Callable[..., None], on_add_click: Callable[..., None], on_scan_click: Callable[..., None] | None = None, search_query: str = '', sort_by: str = 'newest') -> None:
        self._page = page
        self.lang = lang
        self.on_filter = on_filter_change
        self.on_search = on_search_change
        self.on_sort = on_sort_change
        self.filter_type = filter_type
        self.search_query = search_query
        self.sort_by = sort_by

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.add_transaction_text = Text.MEDIUM(
            self.lang["spending.add_transaction"],
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )
        self.scan_label = Text.MEDIUM(
            self.lang["spending.ai_scan"],
            color=Color.SECONDARY_TEXT,
            weight=ft.FontWeight.BOLD
        )

        # Static icons
        self.add_transaction_icon = ft.Icon(ft.Icons.ADD, color=Color.WHITE, size=18)
        self.add_button = ft.Button(
            content=ft.Row(
                spacing=8,
                controls=[self.add_transaction_icon, self.add_transaction_text],
                tight=True
            ),
            bgcolor=Color.PRIMARY_ACTION,
            on_click=on_add_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16), padding=12
            )
        )
        self.scan_icon = ft.Icon(
            ft.Icons.AUTO_AWESOME,
            color=Color.SECONDARY_TEXT,
            size=18
        )
        self.scan_button = ft.Button(
            content=ft.Row(
                spacing=8,
                controls=[
                    self.scan_icon,
                    self.scan_label
                ],
                tight=True
            ),
            bgcolor=Color.DARK_BUTTON,
            disabled=True,
            on_click=on_scan_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=12
            )
        )

        sort_options = [
            ft.dropdown.Option("newest", lang["spending.sort_newest"]),
            ft.dropdown.Option("oldest", lang["spending.sort_oldest"])
        ]
        valid_sort_keys = [opt.key for opt in sort_options]
        dropdown_value = self.sort_by if self.sort_by in valid_sort_keys else "newest"

        self.search_field = ft.TextField(
            value=self.search_query,
            hint_text=self.lang["spending.search"],
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: (
                self.on_search(e.control.value) if self.on_search else None
            ),
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

        # CONTAINER COMPONENTS
        self.all_filter_button = self.create_filter_button(
            label=self.lang["generic.all"],
            f_type="all",
            active_bg=Color.PRIMARY
        )

        self.expense_filter_button = self.create_filter_button(
            label=self.lang["spending.expense_label"],
            f_type="expense",
            active_bg=Color.PRIMARY
        )

        self.income_filter_button = self.create_filter_button(
            label=self.lang["spending.income_label"],
            f_type="income",
            active_bg=Color.PRIMARY
        )

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
                self.add_button,
                self.scan_button
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
            col={"xs": 12, "sm": 6}, content=self.search_field
        )

        self.sort_box_container = ft.Container(
            col={"xs": 12, "sm": 6}, content=self.sort_dropdown
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
            border_radius=28,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def create_filter_button(self, label: str, f_type: str, active_bg: str) -> ft.Button:
        is_active = self.filter_type == f_type
        filter_button_text = Text.SMALL(
            label,
            color=Color.WHITE if is_active else Color.SECONDARY_TEXT,
            weight=ft.FontWeight.BOLD
        )
        return ft.Button(
            content=filter_button_text,
            bgcolor=active_bg if is_active else ft.Colors.TRANSPARENT,
            on_click=lambda _event: (
                self.on_filter(f_type) if self.on_filter else None
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.Padding(16, 10, 16, 10),
                bgcolor=active_bg if is_active else Color.CARD_BACKGROUND
            )
        )

    def set_scan_enabled(self, enabled: bool) -> None:
        self.scan_button.disabled = not enabled
        self.scan_button.bgcolor = Color.PRIMARY if enabled else Color.DARK_BUTTON
        self.scan_icon.color = Color.WHITE if enabled else Color.SECONDARY_TEXT
        self.scan_label.color = Color.WHITE if enabled else Color.SECONDARY_TEXT
        self.scan_button.update()

    def update_data(self, filter_type: str, search_query: str, sort_by: str) -> None:
        self.filter_type = filter_type
        self.search_query = search_query
        self.sort_by = sort_by

        buttons_info = [
            (self.all_filter_button, "all", Color.PRIMARY),
            (self.expense_filter_button, "expense", Color.PRIMARY),
            (self.income_filter_button, "income", Color.PRIMARY)
        ]

        for button, f_type, active_bg in buttons_info:
            is_active = self.filter_type == f_type
            if isinstance(button.content, ft.Text):
                button.content.color = (
                    Color.WHITE if is_active else Color.SECONDARY_TEXT
                )
            button.bgcolor = active_bg if is_active else Color.TRANSPARENT
            if button.style is not None:
                button.style.bgcolor = (
                    active_bg if is_active else Color.CARD_BACKGROUND
                )

        self.search_field.value = self.search_query
        self.sort_dropdown.value = self.sort_by if self.sort_by in ["newest", "oldest"] else "newest"

        self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width


class TransactionHistoryCard(ft.Container):
    """Transaction History Container matching HomeView component style."""

    def __init__(self, page: Page, lang: dict[str, str], transactions: list[dict[str, Any]], on_delete: Callable[[int], None], category_icons: dict[str, str] | None = None) -> None:
        self._page = page
        self.lang = lang
        self.transactions = transactions
        self.on_delete = on_delete
        self.category_icons = category_icons or {}
        self.is_expanded = True
        self._item_width: int | None = None
        self._item_content_width: int | None = None

        self.history_column = ft.Column(spacing=12, controls=[])
        self._render_controls()

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.history_column
        )

    def _render_controls(self) -> None:
        self.history_title = Text.H4(
            self.lang["spending.transaction_history"].format(
                len=len(self.transactions)
            ),
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD
        )
        empty_history_title = Text.MEDIUM(
            self.lang["spending.no_transactions"],
            color=Color.SECONDARY_TEXT,
            weight=ft.FontWeight.BOLD
        )
        empty_history_hint = Text.SMALL(
            self.lang["spending.try_filter"],
            color=Color.SECONDARY_TEXT
        )

        # Dynamic icons
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE,
            tooltip=self.lang["generic.collapse"]
            if self.is_expanded
            else self.lang["generic.expand"],
            on_click=self._toggle_expanded
        )
        history_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.history_title,
                self.toggle_button
            ]
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
                        category_icons=self.category_icons
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
                        controls=[empty_history_title, empty_history_hint]
                    )
                )
            ]

        self.history_content = ft.Column(
            spacing=12,
            controls=tx_list_controls,
            visible=self.is_expanded
        )
        self.history_column.controls = [history_header, self.history_content]
        if self._item_width is not None and self._item_content_width is not None:
            for item in tx_list_controls:
                if isinstance(item, TransactionItemCard):
                    item.resize(self._item_width, self._item_content_width)

    def _toggle_expanded(self, _event: ft.Event[ft.IconButton]) -> None:
        self.is_expanded = not self.is_expanded
        self.history_content.visible = self.is_expanded
        self.toggle_button.icon = (
            ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        )
        self.toggle_button.tooltip = (
            self.lang["generic.collapse"]
            if self.is_expanded
            else self.lang["generic.expand"]
        )
        if self._page is not None:
            self._page.update()

    def update_data(self, transactions: list[dict[str, Any]], category_icons: dict[str, str] | None = None) -> None:
        self.transactions = transactions
        if category_icons is not None:
            self.category_icons = category_icons
        self._render_controls()
        if self.page:
            self.update()

    def resize(self, width: int, content_width: int, item_width: int, item_content_width: int) -> None:
        self.width = width
        self.history_column.width = content_width
        self._item_width = item_width
        self._item_content_width = item_content_width
        for item in self.history_content.controls:
            if isinstance(item, TransactionItemCard):
                item.resize(item_width, item_content_width)
            elif isinstance(item, ft.Container):
                item.width = content_width


class TransactionItemCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], tx: dict[str, Any], on_delete: Callable[[int], None] | None = None, category_icons: dict[str, str] | None = None) -> None:
        self._page = page
        self.lang = lang
        self.tx = tx
        self.on_delete = on_delete

        is_income = self.tx.get("positive", False)
        amount_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR
        icon_bg = Color.INCOME_BACKGROUND if is_income else Color.EXPENSE_BACKGROUND
        icon_color = amount_color
        icon_name = (category_icons or {}).get(self.tx["title"])
        icon = (
            getattr(ft.Icons, icon_name)
            if icon_name and hasattr(ft.Icons, icon_name)
            else ft.Icons.NORTH_EAST
            if is_income
            else ft.Icons.SOUTH_EAST
        )

        # TEXT AND ICON COMPONENTS
        # Static icons
        self.calendar_icon = ft.Icon(ft.Icons.CALENDAR_MONTH, color=Color.SECONDARY_TEXT, size=12)

        # Dynamic texts
        self.title_text = Text.MEDIUM(self.tx["title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.date_text = Text.SMALL(self.tx.get("date", ""), color=Color.SECONDARY_TEXT)
        self.amount_text = Text.MEDIUM(
            format_compact_number(
                to_decimal(self.tx["amount"]) if is_income else -to_decimal(self.tx["amount"]),
                decimals=1,
                signed=True,
                translations=self.lang
            ),
            color=amount_color,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.RIGHT
        )

        # Dynamic icons
        self.item_icon = ft.Icon(icon, color=icon_color, size=18)

        # CONTAINER COMPONENTS
        self.icon_box = ft.Container(
            content=self.item_icon,
            bgcolor=icon_bg,
            width=42,
            height=42,
            border_radius=16,
            alignment=ft.Alignment.CENTER
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
            expand=True,
            spacing=4,
            controls=[
                self.title_text,
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

        transaction_id = self.tx.get("id")
        if self.on_delete and isinstance(transaction_id, int):
            self.delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                icon_size=18,
                on_click=self._delete_transaction,
                tooltip=self.lang["spending.delete"]
            )
            right_controls: list[ft.Control] = [
                self.amount_text,
                self.delete_button
            ]
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

    def _delete_transaction(self, _event: ft.Event[ft.IconButton]) -> None:
        transaction_id = self.tx.get("id")
        if self.on_delete and isinstance(transaction_id, int):
            self.on_delete(transaction_id)

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_row.width = content_width


class DeleteTransactionDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], on_confirm: Callable[[int], None]) -> None:
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        self.transaction_id: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["spending.confirm_delete_title"], color=Color.PRIMARY_TEXT)
        self.desc_text = Text.P(self.lang["spending.confirm_delete_content"], color=Color.SECONDARY_TEXT)
        self.delete_button_label = Text.BUTTON(self.lang["generic.delete"], color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.delete_button = ft.Button(
            content=self.delete_button_label,
            on_click=self._confirm,
            bgcolor=Color.DELETE_ACTION
        )

        self.close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda _event: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"]
        )

        self.main_container = ft.Container(
            padding=20,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[self.title_text, self.close_button]
                    ),
                    self.desc_text
                ]
            )
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.delete_button],
            padding=0
        )
        self.inset_padding = ft.Padding.symmetric(horizontal=16, vertical=24)

    def trigger(self, transaction_id: int | None) -> None:
        if transaction_id is None:
            return
        self.transaction_id = transaction_id
        self.show()

    def _confirm(self, _event: ft.ControlEvent | None = None) -> None:
        if self.transaction_id is None:
            return
        self.dismiss()
        self.on_confirm(self.transaction_id)

    def resize(self, outer_width: int, content_width: int, title_width: int) -> None:
        self.main_container.width = outer_width
        if isinstance(self.main_container.content, ft.Column):
            self.main_container.content.width = content_width
        self.title_text.width = title_width
        self.desc_text.width = content_width


class SpendingUsageCard(ft.Container):
    def __init__(self, lang: dict[str, str]) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.usage_label = Text.MEDIUM(self.lang["spending.ai_usage_loading"], color=Color.PRIMARY_TEXT)

        # CONTAINER COMPONENTS
        self.usage_progress = ft.ProgressBar(
            value=1,
            color=Color.PROGRESS_ACTIVE,
            bgcolor=Color.DARK_BUTTON,
            border_radius=5,
            height=8
        )

        self.main_container = ft.Column(
            spacing=10,
            controls=[
                self.usage_label,
                self.usage_progress
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=self.main_container
        )

    def set_usage(self, remaining: int | None, limit: int | None, reset_at: str | None) -> None:
        if limit is None:
            self.usage_label.value = self.lang["spending.ai_usage_unlimited"]
            self.usage_progress.value = 1
        elif remaining is None:
            self.set_unavailable()
            return
        else:
            self.usage_label.value = self.lang["spending.ai_usage_remaining"].format(
                remaining=remaining,
                limit=limit,
                reset=reset_at
            )
            self.usage_progress.value = remaining / limit if limit else 0
        self.usage_progress.color = (
            Color.PROGRESS_ACTIVE if limit is None or remaining else Color.WARNING_COLOR
        )
        self.update()

    def set_unavailable(self, message: str | None = None) -> None:
        self.usage_label.value = message or self.lang["spending.ai_usage_unavailable"]
        self.update()

    def set_unlimited(self) -> None:
        self.usage_label.value = self.lang["spending.ai_usage_unlimited"]
        self.usage_progress.value = 1
        self.usage_progress.color = Color.PROGRESS_ACTIVE
        self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        self.usage_label.width = content_width
        self.usage_progress.width = content_width


class SpendingGoogleRequiredCard(ft.Container):
    def __init__(self, lang: dict[str, str], visible: bool) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.MEDIUM(self.lang["spending.ai_google_required_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.account_icon = ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=Color.PRIMARY_ACTION, size=24)

        # Dynamic texts
        self.message_text = Text.P(self.lang["spending.ai_google_required"], color=Color.SECONDARY_TEXT)

        # CONTAINER COMPONENTS
        self.main_row = ft.Row(
            spacing=12,
            controls=[
                self.account_icon,
                ft.Column(
                    expand=True,
                    spacing=4,
                    controls=[
                        self.title_text,
                        self.message_text
                    ]
                )
            ]
        )

        super().__init__(
            visible=visible,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=self.main_row
        )

    def set_access(self, signed_in: bool, message: str | None = None) -> None:
        self.visible = not signed_in
        self.message_text.value = message or self.lang["spending.ai_google_required"]


class SpendingPageContent(ft.Container):
    def __init__(self, metric_cards: MetricCards, financial_chart: Any, google_required_card: SpendingGoogleRequiredCard, usage_card: SpendingUsageCard, toolbar: TransactionToolbar, history_card: TransactionHistoryCard, report_history_card: "SpendingReportHistoryCard") -> None:
        self.metric_cards = metric_cards
        self.financial_chart = financial_chart
        self.google_required_card = google_required_card
        self.usage_card = usage_card
        self.toolbar = toolbar
        self.history_card = history_card
        self.report_history_card = report_history_card

        # CONTAINER COMPONENTS
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
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
                    self.report_history_card
                ]
            )
        )
        super().__init__(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO, controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

    def resize(self, page_width: int, page_height: int, content_width: int, card_content_width: int, usage_content_width: int, transaction_item_content_width: int) -> None:
        self.width = page_width
        self.height = page_height
        self.content_container.width = page_width
        self.google_required_card.width = content_width
        self.usage_card.resize(content_width, usage_content_width)
        self.report_history_card.resize(content_width, card_content_width)
        self.metric_cards.resize(content_width)
        self.toolbar.resize(content_width, card_content_width)
        self.history_card.resize(
            width=content_width,
            content_width=card_content_width,
            item_width=card_content_width,
            item_content_width=transaction_item_content_width
        )
        self.financial_chart.resize(card_content_width)

    def set_bottom_margin(self, height: int) -> None:
        self.margin = ft.Margin(bottom=height)


class SpendingReportHistoryCard(ft.Container):
    def __init__(self, lang: dict[str, str], on_open: Callable[[dict[str, Any]], None]) -> None:
        self.lang = lang
        self.on_open = on_open
        self.reports: list[dict[str, Any]] = []
        self.is_expanded = True
        self._content_width: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.history_title = Text.H4(self.lang["spending.ai_history"].format(len=0), color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.empty_history_text = Text.SMALL(self.lang["spending.ai_no_history"], color=Color.SECONDARY_TEXT)

        # CONTAINER COMPONENTS
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS,
            tooltip=self.lang["generic.collapse"],
            on_click=self._toggle_expanded
        )

        self.history_content = ft.Column(spacing=10)

        self.history_column = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.history_title,
                        self.toggle_button
                    ]
                ),
                self.history_content
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.history_column
        )

    def set_history(self, reports: list[dict[str, Any]]) -> None:
        self.reports = reports
        self.history_title.value = self.lang["spending.ai_history"].format(len=len(reports))
        if not reports:
            self.history_content.controls = [self.empty_history_text]
        else:
            self.history_content.controls = [
                self._make_history_item(item) for item in reports
            ]
        if self._content_width is not None:
            for item in self.history_content.controls:
                if isinstance(item, ft.Container):
                    item.width = self._content_width
        self.history_content.visible = self.is_expanded
        if self.parent:
            self.update()

    def _make_history_item(self, item: dict[str, Any]) -> ft.Control:
        report = item.get("report", {})
        overview = report.get("monthly_overview", {})
        summary = overview.get("headline") or overview.get("month", "")
        created_at = str(item.get("created_at", ""))
        history_item_title = Text.MEDIUM(
            self.lang["spending.ai_history_item_title"],
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD
        )
        history_item_created_at = Text.SMALL(created_at, color=Color.SECONDARY_TEXT)
        history_item_summary = Text.SMALL(summary, color=Color.SECONDARY_TEXT)
        return ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
            border_radius=14,
            padding=14,
            ink=True,
            on_click=self._create_open_report_handler(item),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=40,
                        height=40,
                        border_radius=14,
                        bgcolor=Color.DARK_SURFACE,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            ft.Icons.AUTO_AWESOME,
                            color=Color.LIGHT_ACCENT,
                            size=20
                        )
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            history_item_title,
                            history_item_created_at,
                            history_item_summary
                        ]
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color=Color.SECONDARY_TEXT
                    )
                ]
            )
        )

    def _create_open_report_handler(self, report: dict[str, Any]) -> Callable[[ft.Event[ft.Container]], None]:
        def open_report(_event: ft.Event[ft.Container]) -> None:
            self.on_open(report)

        return open_report

    def _toggle_expanded(self, _event: ft.Event[ft.IconButton]) -> None:
        self.is_expanded = not self.is_expanded
        self.history_content.visible = self.is_expanded
        self.toggle_button.icon = (
            ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        )
        self.toggle_button.tooltip = (
            self.lang["generic.collapse"]
            if self.is_expanded
            else self.lang["generic.expand"]
        )
        self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self._content_width = content_width
        self.history_column.width = content_width
        self.history_content.width = content_width
        for item in self.history_content.controls:
            if isinstance(item, ft.Container):
                item.width = width
