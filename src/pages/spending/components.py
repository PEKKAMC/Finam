# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from datetime import datetime

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
            border_radius=UISettings.CARD_BORDER_RADIUS,
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
    def __init__(self, page: Page, lang: dict, filter_type: str, on_filter_change: Callable, on_search_change: Callable, on_sort_change: Callable, on_add_click: Callable, on_scan_click: Callable | None = None, search_query: str = "", sort_by: str = "newest"):
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
        self.scan_icon = ft.Icon(
            ft.Icons.AUTO_AWESOME,
            color=Color.SECONDARY_TEXT,
            size=18,
        )
        self.scan_label = Text.MEDIUM(
            self.lang["spending_ai.scan"],
            color=Color.SECONDARY_TEXT,
            weight=ft.FontWeight.BOLD,
        )
        self.scan_button = ft.Button(
            content=ft.Row(
                spacing=8,
                controls=[
                    self.scan_icon,
                    self.scan_label,
                ],
                tight=True,
            ),
            bgcolor=Color.DARK_BUTTON,
            disabled=True,
            on_click=on_scan_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=12,
            ),
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
                self.add_button,
                self.scan_button,
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

    def set_scan_enabled(self, enabled: bool) -> None:
        self.scan_button.disabled = not enabled
        self.scan_button.bgcolor = Color.PRIMARY if enabled else Color.DARK_BUTTON
        self.scan_icon.color = Color.WHITE if enabled else Color.SECONDARY_TEXT
        self.scan_label.color = Color.WHITE if enabled else Color.SECONDARY_TEXT
        self.scan_button.update()

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

    def resize(self, width: int, content_width: int):
        self.width = width
        self.main_container.width = content_width


class TransactionHistoryCard(ft.Container):
    """Transaction History Container matching HomeView component style."""
    def __init__(self, page: Page, lang: dict, transactions: list, on_delete: Callable, category_icons: dict[str, str] | None = None, ):
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
                        category_icons=self.category_icons,
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
        if self._item_width is not None and self._item_content_width is not None:
            for item in tx_list_controls:
                if isinstance(item, TransactionItemCard):
                    item.resize(self._item_width, self._item_content_width)

    def _toggle_expanded(self, e):
        self.is_expanded = not self.is_expanded
        self.history_content.visible = self.is_expanded
        self.toggle_button.icon = ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE
        self.toggle_button.tooltip = self.lang["generic.collapse"] if self.is_expanded else self.lang["generic.expand"]
        if self._page is not None:
            self._page.update()

    def update_data(self, transactions: list, category_icons: dict[str, str] | None = None):
        self.transactions = transactions
        if category_icons is not None:
            self.category_icons = category_icons
        self._render_controls()
        if self.page:
            self.update()

    def resize(self, width: int, content_width: int, item_width: int, item_content_width: int):
        self.width = width
        self.history_column.width = content_width
        self._item_width = item_width
        self._item_content_width = item_content_width
        for item in self.history_content.controls:
            if isinstance(item, TransactionItemCard):
                item.resize(item_width, item_content_width)
            else:
                item.width = content_width


class TransactionItemCard(ft.Container):
    def __init__(self, page: Page, lang: dict, tx: dict, on_delete: Callable | None = None, category_icons: dict[str, str] | None = None):
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
            else ft.Icons.NORTH_EAST if is_income else ft.Icons.SOUTH_EAST
        )

        # TEXT AND ICON COMPONENTS
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
                self.title_text,
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

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_row.width = content_width


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

    def resize(
        self,
        outer_width: int,
        content_width: int,
        title_width: int,
    ) -> None:
        self.main_container.width = outer_width
        self.main_container.content.width = content_width
        self.title_text.width = title_width
        self.desc_text.width = content_width


class SpendingUsageCard(ft.Container):
    def __init__(self, lang: dict):
        self.lang = lang
        self.usage_label = Text.MEDIUM(
            self.lang["spending_ai.usage_loading"],
            color=Color.PRIMARY_TEXT,
        )
        self.usage_progress = ft.ProgressBar(
            value=1,
            color=Color.PROGRESS_ACTIVE,
            bgcolor=Color.DARK_BUTTON,
            height=8,
        )
        self.main_container = ft.Column(
            spacing=10,
            controls=[self.usage_label, self.usage_progress],
        )
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=self.main_container,
        )

    def set_usage(
        self,
        remaining: int | None,
        limit: int | None,
        reset_at: str | None,
    ) -> None:
        if limit is None:
            self.usage_label.value = self.lang[
                "spending_ai.usage_unlimited"
            ]
            self.usage_progress.value = 1
        else:
            self.usage_label.value = self.lang["spending_ai.usage_remaining"].format(
                remaining=remaining,
                limit=limit,
                reset=reset_at,
            )
            self.usage_progress.value = remaining / limit if limit else 0
        self.usage_progress.color = (
            Color.PROGRESS_ACTIVE
            if limit is None or remaining
            else Color.WARNING_COLOR
        )
        self.update()

    def set_unavailable(self, message: str | None = None) -> None:
        self.usage_label.value = message or self.lang["spending_ai.usage_unavailable"]
        self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        self.usage_label.width = content_width
        self.usage_progress.width = content_width


class SpendingMonthDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_confirm: Callable[[str], None]):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.month_dropdown = ft.Column(
            controls=[
                ft.Dropdown(
                    label=self.lang["spending_ai.month_label"],
                    value=str(self.month),
                    options=[],
                    on_select=self._on_month_changed,
                    menu_height=300,
                    expand=True
                )
            ]
        )
        self.year_dropdown = ft.Column(
            controls=[
                ft.Dropdown(
                    label=self.lang["spending_ai.year_label"],
                    value=str(self.year),
                    options=[
                        ft.dropdown.Option(str(year), str(year))
                        for year in range(now.year, now.year - 51, -1)
                    ],
                    on_select=self._on_year_changed,
                    menu_height=300,
                    expand=True
                )
            ]
        )
        self._update_month_options()
        self.main_container = ft.Container(
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    Text.H4(
                        self.lang["spending_ai.select_month_title"],
                        color=Color.PRIMARY_TEXT,
                    ),
                    self.month_dropdown,
                    self.year_dropdown,
                ],
            ),
        )
        self.cancel_button = ft.TextButton(
            self.lang["generic.cancel"],
            on_click=lambda e: self.dismiss(),
        )
        self.confirm_button = ft.Button(
            self.lang["spending_ai.scan_month"],
            on_click=self._confirm,
            bgcolor=Color.PRIMARY,
            color=Color.WHITE,
        )
        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.cancel_button, self.confirm_button],
            padding=0,
        )

    def resize(self, width: int, content_width: int) -> None:
        self.main_container.width = width
        self.month_dropdown.width = content_width
        self.year_dropdown.width = content_width

    def _on_month_changed(self, e=None) -> None:
        self.month = int(self.month_dropdown.value)
        self.month_dropdown.update()

    def _on_year_changed(self, e=None) -> None:
        self.year = int(self.year_dropdown.value)
        self._update_month_options()
        self.month_dropdown.value = str(self.month)
        self.month_dropdown.update()

    def _update_month_options(self) -> None:
        latest_month = datetime.now().month if self.year == datetime.now().year else 12
        self.month_dropdown.options = [
            ft.dropdown.Option(
                str(month),
                self.lang[f"spending_ai.month_{month:02d}"],
            )
            for month in range(1, latest_month + 1)
        ]
        if self.month > latest_month:
            self.month = latest_month

    def trigger(self, e=None) -> None:
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.year_dropdown.value = str(self.year)
        self._update_month_options()
        self.month_dropdown.value = str(self.month)
        self.show()

    def _confirm(self, e=None) -> None:
        month = f"{self.year:04d}-{self.month:02d}"
        self.dismiss()
        self.on_confirm(month)


class DeleteSpendingReportDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_confirm: Callable[[int], None]):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        self.report_id: int | None = None
        self.main_container = ft.Container(
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    Text.H3(
                        self.lang["spending_ai.confirm_delete_title"],
                        color=Color.PRIMARY_TEXT,
                    ),
                    Text.P(
                        self.lang["spending_ai.confirm_delete_content"],
                        color=Color.SECONDARY_TEXT,
                    ),
                ],
            ),
        )
        self.cancel_button = ft.TextButton(
            self.lang["generic.cancel"],
            on_click=lambda e: self.dismiss(),
        )
        self.delete_button = ft.Button(
            self.lang["generic.delete"],
            on_click=self._confirm,
            bgcolor=Color.DELETE_ACTION,
            color=Color.WHITE,
        )
        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.cancel_button, self.delete_button],
            padding=0,
        )

    def resize(self, width: int, content_width: int) -> None:
        self.main_container.width = width
        self.main_container.content.width = content_width

    def trigger(self, report_id: int | None) -> None:
        if report_id is None:
            return
        self.report_id = report_id
        self.show()

    def _confirm(self, e=None) -> None:
        if self.report_id is None:
            return
        report_id = self.report_id
        self.report_id = None
        self.dismiss()
        self.on_confirm(report_id)


class SpendingReportDialog(Dialog):
    SECTION_KEYS = (
        "monthly_overview",
        "spending_trends",
        "top_income_source",
        "largest_expense",
        "savings_advice",
        "spending_actions",
    )

    def __init__(self, page: Page, lang: dict, on_delete: Callable[[int], None]):
        self._page = page
        self.lang = lang
        self.on_delete = on_delete
        self.report_id: int | None = None
        self.title_text = Text.H4(
            self.lang["spending_ai.title"],
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD,
            expand=True,
        )
        self.updated_text = Text.SMALL("", color=Color.SECONDARY_TEXT)
        self.error_text = Text.MEDIUM(
            "",
            color=Color.NEGATIVE_ACTION,
            text_align=ft.TextAlign.CENTER,
        )
        self.loading_content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.ProgressRing(color=Color.PRIMARY, width=42, height=42),
                Text.MEDIUM(
                    self.lang["spending_ai.waiting"],
                    color=Color.SECONDARY_TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )
        self.report_content = ft.Column(
            spacing=12,
        )
        self.report_card_width = 0
        self.body = ft.Container(
            content=self.loading_content,
            alignment=ft.Alignment.CENTER
        )
        self.delete_button = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            visible=False,
            on_click=self._request_delete,
            icon_color=Color.NEGATIVE_ACTION,
            tooltip=self.lang["spending_ai.delete_report"],
        )
        close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda e: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"],
        )
        self.main_container = ft.Container(
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                expand=True,
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.WHITE, size=16),
                                        bgcolor=Color.DARK_SURFACE,
                                        width=30,
                                        height=30,
                                        border_radius=10,
                                        alignment=ft.Alignment.CENTER,
                                    ),
                                    self.title_text
                                ],
                            ),
                            ft.Row(
                                tight=True,
                                spacing=0,
                                controls=[self.delete_button, close_button],
                            ),
                        ],
                    ),
                    self.updated_text,
                    self.body,
                ],
            ),
        )
        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            padding=0,
        )
        self.scrollable = True
        self.inset_padding = ft.Padding.symmetric(horizontal=12, vertical=20)

    def show_loading(self) -> None:
        self.report_id = None
        self.delete_button.visible = False
        self.updated_text.value = ""
        self.body.content = self.loading_content
        self.show()
        self.update()

    def show_error(self, message: str) -> None:
        self.body.content = ft.Container(
            alignment=ft.Alignment.CENTER,
            content=self.error_text,
        )
        self.error_text.value = message
        self.update()

    def show_report(self, report: dict, created_at: str, report_id: int | None = None) -> None:
        self.report_id = report_id
        self.delete_button.visible = report_id is not None
        self.updated_text.value = self.lang["spending_ai.updated"].format(
            date=created_at
        )

        controls = []
        i = 0
        while i < len(self.SECTION_KEYS):
            key = self.SECTION_KEYS[i]
            if key == "top_income_source":
                sec3 = report.get("top_income_source", {})
                sec4 = report.get("largest_expense", {})
                row_control = ft.ResponsiveRow(
                    spacing=12,
                    run_spacing=12,
                    controls=[
                        ft.Container(
                            col={"xs": 12, "sm": 6},
                            content=self._make_section_card(3, "top_income_source", sec3)
                        ),
                        ft.Container(
                            col={"xs": 12, "sm": 6},
                            content=self._make_section_card(4, "largest_expense", sec4)
                        ),
                    ]
                )
                controls.append(row_control)
                i += 2
            else:
                index = i + 1
                section_data = report.get(key, {})
                controls.append(self._make_section_card(index, key, section_data))
                i += 1

        self.report_content.controls = controls
        self.body.content = self.report_content
        self.show()
        self.update()

    def _request_delete(self, e=None) -> None:
        if self.report_id is not None:
            self.on_delete(self.report_id)

    def _make_section_card(self, index: int, key: str, data) -> ft.Container:
        title = self.lang[f"spending_ai.section_{index}"]
        section = data if isinstance(data, dict) else {}

        top_header_row = ft.Row(
            controls=[
                ft.Container(
                    width=28,
                    height=28,
                    alignment=ft.Alignment.CENTER,
                    border_radius=9,
                    bgcolor=Color.DARK_SURFACE,
                    content=Text.SMALL(
                        str(index),
                        color=Color.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                Text.MEDIUM(
                    title,
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
            ]
        )

        card_content_items = [top_header_row]

        if key in ("savings_advice", "spending_actions"):
            items = data if isinstance(data, list) else (data.get("items", []) if isinstance(data, dict) else [])
            for idx, advice in enumerate(items, start=1):
                card_content_items.append(
                    ft.Container(
                        padding=14,
                        border_radius=14,
                        bgcolor=Color.GOAL_ITEM_BACKGROUND if key == "savings_advice" else Color.CARD_BACKGROUND,
                        border=ft.Border.all(1, Color.GOAL_ITEM_BORDER if key == "savings_advice" else Color.WARNING_COLOR),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=24,
                                            height=24,
                                            border_radius=12,
                                            bgcolor=Color.DARK_SURFACE if key == "savings_advice" else Color.WARNING_BACKGROUND,
                                            alignment=ft.Alignment.CENTER,
                                            content=Text.SMALL(
                                                str(idx),
                                                color=Color.WHITE if key == "savings_advice" else Color.WARNING_COLOR,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ),
                                        Text.MEDIUM(
                                            str(advice.get("title", "")),
                                            color=Color.PRIMARY_TEXT,
                                            weight=ft.FontWeight.BOLD,
                                            expand=True,
                                        ),
                                    ],
                                ),
                                Text.SMALL(
                                    str(advice.get("description", "")),
                                    color=Color.SECONDARY_TEXT,
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.BOLT if key == "spending_actions" else ft.Icons.VERIFIED_OUTLINED,
                                            color=Color.WARNING_COLOR if key == "spending_actions" else Color.PRIMARY,
                                            size=16,
                                        ),
                                        Text.MEDIUM(
                                            str(advice.get("outcome", "")),
                                            color=Color.WARNING_COLOR if key == "spending_actions" else Color.PRIMARY,
                                            weight=ft.FontWeight.BOLD,
                                            expand=True,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )
        elif key == "monthly_overview" and "income" in section:
            card_content_items.append(
                Text.SMALL(
                    str(section.get("month", "")),
                    color=Color.SECONDARY_TEXT,
                )
            )
            expenses = float(section.get("expenses", 0))
            income = float(section.get("income", 0))
            expenses_val = format_number(expenses)
            income_val = format_number(income)
            currency = str(section.get("currency", "đ"))

            overview_row = ft.ResponsiveRow(
                spacing=10,
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 6},
                        padding=14,
                        border_radius=14,
                        bgcolor=Color.CARD_BACKGROUND,
                        border=ft.Border.all(1, Color.INPUT_BORDER),
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                Text.SMALL(self.lang["spending_ai.month_total_expenses"].upper(), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                                Text.H3(f"-{expenses_val} {currency}".strip(), color=Color.EXPENSE_COLOR, weight=ft.FontWeight.BOLD),
                            ]
                        )
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6},
                        padding=14,
                        border_radius=14,
                        bgcolor=Color.CARD_BACKGROUND,
                        border=ft.Border.all(1, Color.INPUT_BORDER),
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                Text.SMALL(self.lang["spending_ai.month_total_income"].upper(), color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                                Text.H3(f"+{income_val} {currency}".strip(), color=Color.INCOME_COLOR, weight=ft.FontWeight.BOLD),
                            ]
                        )
                    ),
                ]
            )
            card_content_items.append(overview_row)

            net_bal = format_number(float(section.get("net_balance", 0)))
            card_content_items.append(
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor=Color.GOAL_ITEM_BACKGROUND,
                    border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                color=Color.EXPENSE_COLOR,
                                size=18,
                                visible=expenses > income,
                            ),
                            Text.MEDIUM(
                                self.lang["spending.net_balance"],
                                color=Color.SECONDARY_TEXT,
                                expand=True,
                            ),
                            Text.MEDIUM(
                                f"{net_bal} {currency}".strip(),
                                color=Color.EXPENSE_COLOR,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                        ],
                    ),
                )
            )
        elif key in ("top_income_source", "largest_expense"):
            is_income = (key == "top_income_source")
            amount_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR
            badge_bg = Color.INCOME_BACKGROUND if is_income else Color.EXPENSE_BACKGROUND
            badge_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR

            card_content_items.append(
                Text.MEDIUM(
                    str(section.get("headline", "")),
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD,
                )
            )
            metric_str = str(section.get("metric", ""))
            card_content_items.append(
                Text.H3(
                    metric_str,
                    color=amount_color,
                    weight=ft.FontWeight.BOLD,
                )
            )
            summary_str = str(section.get("summary", ""))
            if summary_str:
                card_content_items.append(
                    ft.Container(
                        content=Text.SMALL(summary_str, color=badge_color, weight=ft.FontWeight.BOLD),
                        bgcolor=badge_bg,
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                    )
                )
            card_content_items.append(
                Text.SMALL(
                    str(section.get("details", "")),
                    color=Color.SECONDARY_TEXT,
                )
            )
        elif key == "spending_trends":
            card_content_items.append(
                Text.MEDIUM(
                    str(section.get("headline", "")),
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD,
                )
            )
            card_content_items.append(
                Text.SMALL(
                    str(section.get("summary", "")),
                    color=Color.SECONDARY_TEXT,
                )
            )
            details_str = str(section.get("details", ""))
            if details_str:
                card_content_items.append(
                    ft.Container(
                        padding=12,
                        border_radius=12,
                        bgcolor=Color.GOAL_ITEM_BACKGROUND,
                        border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                        content=Text.MEDIUM(
                            details_str,
                            color=Color.PRIMARY_TEXT,
                            weight=ft.FontWeight.BOLD,
                        ),
                    )
                )
        else:
            card_content_items.append(
                Text.MEDIUM(
                    str(section.get("headline", "")),
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD,
                )
            )
            card_content_items.append(
                Text.SMALL(
                    str(section.get("summary", "")),
                    color=Color.SECONDARY_TEXT,
                )
            )
            card_content_items.append(
                Text.SMALL(
                    str(section.get("details", "")),
                    color=Color.SECONDARY_TEXT,
                )
            )
            metric = section.get("metric")
            if metric:
                card_content_items.append(
                    ft.Container(
                        padding=ft.Padding(10, 8, 10, 8),
                        border_radius=12,
                        bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
                        content=Text.MEDIUM(
                            str(metric),
                            color=Color.PRIMARY,
                            weight=ft.FontWeight.BOLD,
                        ),
                    )
                )

        return ft.Container(
            width=self.report_card_width if self.report_card_width > 0 else None,
            padding=14,
            border_radius=16,
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=card_content_items,
            ),
        )

    def resize(self, dialog_width: int, report_card_width: int) -> None:
        self.main_container.width = dialog_width
        self.report_card_width = report_card_width
        for card in self.report_content.controls:
            if isinstance(card, ft.Container):
                card.width = report_card_width
            elif isinstance(card, ft.ResponsiveRow):
                card.width = report_card_width


class SpendingReportHistoryCard(ft.Container):
    def __init__(self, lang: dict, on_open: Callable[[dict], None]):
        self.lang = lang
        self.on_open = on_open
        self.reports: list[dict] = []
        self.is_expanded = True
        self._content_width: int | None = None
        self.history_title = Text.H4(
            self.lang["spending_ai.history"].format(len=0),
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD,
        )
        self.toggle_button = ft.IconButton(
            ft.Icons.EXPAND_LESS,
            tooltip=self.lang["generic.collapse"],
            on_click=self._toggle_expanded,
        )
        self.history_content = ft.Column(spacing=10)
        self.history_column = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[self.history_title, self.toggle_button],
                ),
                self.history_content,
            ],
        )
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=20,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.history_column,
        )

    def set_history(self, reports: list[dict]) -> None:
        self.reports = reports
        self.history_title.value = self.lang["spending_ai.history"].format(
            len=len(reports)
        )
        if not reports:
            self.history_content.controls = [
                Text.SMALL(
                    self.lang["spending_ai.no_history"],
                    color=Color.SECONDARY_TEXT,
                )
            ]
        else:
            self.history_content.controls = [
                self._make_history_item(item) for item in reports
            ]
        if self._content_width is not None:
            for item in self.history_content.controls:
                item.width = self._content_width
        self.history_content.visible = self.is_expanded
        if self.parent:
            self.update()

    def _make_history_item(self, item: dict) -> ft.Control:
        report = item.get("report", {})
        overview = report.get("monthly_overview", {})
        summary = overview.get("headline") or overview.get("month", "")
        created_at = str(item.get("created_at", ""))
        return ft.Container(
            bgcolor=Color.GOAL_ITEM_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
            border_radius=14,
            padding=14,
            ink=True,
            on_click=lambda e, saved=item: self.on_open(saved),
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
                            size=20,
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            Text.MEDIUM(
                                self.lang["spending_ai.history_item_title"],
                                color=Color.PRIMARY_TEXT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            Text.SMALL(created_at, color=Color.SECONDARY_TEXT),
                            Text.SMALL(summary, color=Color.SECONDARY_TEXT),
                        ],
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color=Color.SECONDARY_TEXT,
                    ),
                ],
            ),
        )

    def _toggle_expanded(self, e=None) -> None:
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
            item.width = width