# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from decimal import Decimal

import flet as ft
import flet_charts as fc

from src.pages.home.logic import SavingsProgressItem
from src.utils import Color, Text, UISettings, format_compact_number, format_display_number

DEFAULT_CHART_RADIUS = 45
DEFAULT_CHART_CENTER_RADIUS = 40
PIE_CHART_SECTION_SPACING = 2
PIE_CHART_COLORS = (
    Color.PIE_CHART_RED,
    Color.PIE_CHART_BLUE,
    Color.PIE_CHART_GREEN,
    Color.PIE_CHART_YELLOW,
    Color.PIE_CHART_TURQUOISE,
    Color.PIE_CHART_PURPLE
)


class BalanceCard(ft.Container):
    def __init__(self, lang: dict[str, str], currency: str, net_balance: Decimal, income: Decimal, expense: Decimal, savings: Decimal, advice: str, on_add_click: Callable[..., None], on_scan_click: Callable[..., None] | None) -> None:
        self.lang = lang
        self.currency = currency
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.advice = advice
        self.on_add_click = on_add_click
        self.on_scan_click = on_scan_click

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.balance_label_text = Text.LABEL(self.lang["home.available_balance"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.currency_label = Text.P(self.currency, color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.add_transaction_button_label = Text.BUTTON(self.lang["home.add_transaction"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.purchase_scanner_button_label = Text.BUTTON(self.lang["home.ai_scan"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.income_title = Text.H6(self.lang["home.total_income"], color=Color.LIGHT_ACCENT)
        self.expense_title = Text.H6(self.lang["home.total_expense"], color=Color.EXPENSE_LABEL_TEXT)
        self.saving_title = Text.H6(self.lang["home.total_savings"], color=Color.SAVINGS_LABEL_TEXT)
        self.ai_banner_title = Text.SMALL(self.lang["home.ai_advisor"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.add_transaction_button_icon = ft.Icon(ft.Icons.ADD_ROUNDED, color=Color.PRIMARY, size=18)
        self.purchase_scanner_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.SECONDARY_TEXT, size=18)
        self.ai_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PRIMARY, size=16)

        # Dynamic texts
        self.balance_amount_text = Text.H2(format_display_number(self.net_balance, self.lang), color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.income_text = Text.SMALL(f"{format_display_number(self.income, self.lang)} {self.currency}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.expense_text = Text.SMALL(f"{format_display_number(self.expense, self.lang)} {self.currency}", color=Color.EXPENSE_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.savings_text = Text.SMALL(f"{format_display_number(self.savings, self.lang)} {self.currency}", color=Color.SAVINGS_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.advice_text = Text.SMALL(self.advice, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.balance_label_container = ft.Container(
            content=self.balance_label_text,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 4, 12, 4),
            border_radius=20,
            border=ft.Border.all(1, Color.PRIMARY)
        )

        self.balance_amount_row = ft.Row(
            controls=[
                self.balance_amount_text,
                self.currency_label
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.END
        )

        self.balance_header = ft.Column(
            spacing=4,
            controls=[
                self.balance_label_container,
                self.balance_amount_row
            ]
        )

        self.add_transaction_button = ft.Button(
            expand=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    self.add_transaction_button_icon,
                    self.add_transaction_button_label
                ]
            ),
            bgcolor=Color.LIGHT_ACCENT,
            on_click=self.on_add_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=0,
                alignment=ft.Alignment.CENTER
            )
        )

        self.purchase_scanner_button = ft.OutlinedButton(
            expand=True,
            disabled=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.purchase_scanner_icon,
                    self.purchase_scanner_button_label
                ]
            ),
            on_click=self.on_scan_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=0,
                alignment=ft.Alignment.CENTER,
                bgcolor=Color.DARK_BUTTON,
                side=ft.BorderSide(1, Color.SCAN_BUTTON_BORDER)
            )
        )

        self.action_buttons_row = ft.Row(
            spacing=8,
            controls=[
                self.add_transaction_button,
                self.purchase_scanner_button
            ]
        )

        self.balance_top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[
                self.balance_header,
                self.action_buttons_row
            ]
        )

        self.income_metric_container = ft.Container(
            expand=True,
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border_radius=16,
            padding=8,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=2,
                controls=[
                    self.income_title,
                    self.income_text
                ]
            )
        )

        self.expense_metric_container = ft.Container(
            expand=True,
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border_radius=16,
            padding=8,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=2,
                controls=[
                    self.expense_title,
                    self.expense_text
                ]
            )
        )

        self.saving_metric_container = ft.Container(
            expand=True,
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border_radius=16,
            padding=8,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=2,
                controls=[
                    self.saving_title,
                    self.savings_text
                ]
            )
        )

        self.metrics_row = ft.Column(
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.income_metric_container,
                self.expense_metric_container,
                self.saving_metric_container
            ]
        )

        self.ai_icon_container = ft.Container(
            width=30,
            height=30,
            border_radius=10,
            bgcolor=Color.LIGHT_ACCENT,
            alignment=ft.Alignment.CENTER,
            content=self.ai_icon
        )

        self.ai_banner_texts = ft.Column(
            expand=True,
            spacing=2,
            controls=[
                self.ai_banner_title,
                self.advice_text
            ]
        )

        self.ai_banner_container = ft.Container(
            bgcolor=Color.AI_ADVICE_BACKGROUND,
            border_radius=16,
            padding=12,
            border=ft.Border.all(1, Color.AI_ADVICE_BORDER),
            content=ft.Row(
                spacing=10,
                controls=[
                    self.ai_icon_container,
                    self.ai_banner_texts
                ]
            )
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=20,
                controls=[
                    self.balance_top_row,
                    self.metrics_row,
                    self.ai_banner_container
                ]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=self.main_container
        )

    def set_scan_enabled(self, enabled: bool) -> None:
        self.purchase_scanner_button.disabled = not enabled
        self.purchase_scanner_button.style.bgcolor = (
            ft.Colors.TRANSPARENT if enabled else Color.DARK_BUTTON
        )
        self.purchase_scanner_icon.color = (
            Color.LIGHT_ACCENT if enabled else Color.SECONDARY_TEXT
        )
        self.purchase_scanner_button_label.color = (
            Color.WHITE if enabled else Color.SECONDARY_TEXT
        )

    def update_data(self, net_balance: Decimal, income: Decimal, expense: Decimal, savings: Decimal, ai_advice: str, currency: str) -> None:
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.advice = ai_advice
        self.currency = currency

        self.balance_amount_text.value = format_display_number(self.net_balance, self.lang)
        self.currency_label.value = self.currency
        self.income_text.value = f"{format_display_number(self.income, self.lang)} {self.currency}"
        self.expense_text.value = f"{format_display_number(self.expense, self.lang)} {self.currency}"
        self.savings_text.value = f"{format_display_number(self.savings, self.lang)} {self.currency}"
        self.advice_text.value = self.advice

        self.update()

    def resize(self, width: int) -> None:
        self.main_container.width = width
        self.balance_top_row.width = width
        self.metrics_row.width = width
        self.ai_banner_container.width = width


class SavingsGoalItem(ft.Container):
    def __init__(self, item: SavingsProgressItem) -> None:
        self.item = item
        self.completed = item.get("completed", False)

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.title_text = Text.MEDIUM(
            item["title"],
            color=Color.DEFAULT_TEXT,
            weight=ft.FontWeight.BOLD,
            expand=True
        )
        self.progress_text = Text.SMALL(item["progress_text"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.contributed_label = Text.SMALL(
            item["contributed_label"],
            color=Color.PRIMARY,
            weight=ft.FontWeight.BOLD,
            expand=True
        )
        self.target_label = Text.SMALL(
            item["target_label"],
            color=Color.BLAND_TEXT,
            expand=True
        )

        # CONTAINER COMPONENTS
        self.progress_bar = ft.ProgressBar(
            value=item["progress_ratio"],
            color=Color.PRIMARY,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            height=8
        )

        self.progress_badge_container = ft.Container(
            content=self.progress_text,
            bgcolor=Color.PRIMARY,
            padding=ft.Padding(8, 2, 8, 2),
            border_radius=12
        )

        self.header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                self.title_text,
                self.progress_badge_container
            ]
        )

        self.footer_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.contributed_label,
                self.target_label
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    self.header_row,
                    self.progress_bar,
                    self.footer_row
                ]
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=12,
            ink=True,
            content=self.main_container
        )

    def update_data(self, item: SavingsProgressItem) -> None:
        self.item = item
        self.completed = item.get("completed", False)

        self.title_text.value = item["title"]
        self.progress_text.value = item["progress_text"]
        self.progress_bar.value = item["progress_ratio"]
        self.contributed_label.value = item["contributed_label"]
        self.target_label.value = item["target_label"]
        self.update()

    def resize(self, width: int, content_width: int) -> None:
        self.main_container.width = width
        self.header_row.width = content_width
        self.progress_bar.width = content_width
        self.footer_row.width = content_width


class SavingsProgressCard(ft.Container):
    def __init__(self, lang: dict[str, str], objective_items: tuple[list[SavingsProgressItem], int], on_view_all_click: Callable[..., None] | None) -> None:
        self.lang = lang
        self.objective_items, self.objective_count = objective_items
        self.on_view_all_click = on_view_all_click
        self._inner_width: int | None = None
        self._goal_item_content_width: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.goal_title = Text.H4(self.lang["home.savings_goal"], color=Color.DEFAULT_TEXT)
        self.goal_subtitle = Text.SMALL(self.lang["home.savings_goal_subtitle"], color=Color.BLAND_TEXT)
        self.empty_state_text = Text.SMALL(self.lang["home.no_savings_goal"], color=Color.BLAND_TEXT)

        # Static icons
        self.goal_header_icon = ft.Icon(ft.Icons.TRACK_CHANGES, color=Color.GOAL_HEADER_ICON_COLOR, size=18)
        self.view_all_arrow_icon = ft.Icon(ft.Icons.ARROW_FORWARD, color=Color.PRIMARY, size=14)

        # Dynamic texts
        self.view_all_count = Text.SMALL(
            f"{self.lang['generic.all']} ({self.objective_count})",
            color=Color.PRIMARY,
            weight=ft.FontWeight.BOLD
        )

        # CONTAINER COMPONENTS
        self.goal_icon_container = ft.Container(
            width=32,
            height=32,
            border_radius=10,
            bgcolor=Color.GOAL_HEADER_ICON_BACKGROUND,
            alignment=ft.Alignment.CENTER,
            content=self.goal_header_icon
        )

        self.goal_title_column = ft.Column(
            spacing=0,
            controls=[
                self.goal_title,
                self.goal_subtitle
            ]
        )

        self.view_all_button = ft.TextButton(
            content=ft.Row(
                spacing=4,
                tight=True,
                controls=[
                    self.view_all_count,
                    self.view_all_arrow_icon
                ]
            ),
            on_click=self.on_view_all_click
        )

        self.goal_header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self.goal_icon_container,
                        self.goal_title_column
                    ]
                ),
                self.view_all_button
            ]
        )

        self.empty_state_container = ft.Container(
            padding=20,
            alignment=ft.Alignment.CENTER,
            content=self.empty_state_text
        )

        self.goal_items: list[SavingsGoalItem] = [SavingsGoalItem(item) for item in self.objective_items]

        self.goal_items_column = ft.Column(
            spacing=6,
            controls=(
                [self.empty_state_container] if not self.objective_items
                else self.goal_items
            )
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=12,
                controls=[
                    self.goal_header_row,
                    self.goal_items_column
                ]
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def update_data(self, objective_items: list[SavingsProgressItem], objective_count: int | None = None) -> None:
        self.objective_items = objective_items or []
        total_objective_count = (
            len(self.objective_items)
            if objective_count is None
            else objective_count
        )
        self.view_all_count.value = (
            f"{self.lang['generic.all']} ({total_objective_count})"
        )

        if not self.objective_items:
            self.goal_items.clear()
            self.goal_items_column.controls = [self.empty_state_container]
        else:
            while len(self.goal_items) > len(self.objective_items):
                self.goal_items.pop()

            for i, item in enumerate(self.objective_items):
                if i < len(self.goal_items):
                    self.goal_items[i].update_data(item)
                else:
                    self.goal_items.append(SavingsGoalItem(item))
                    if self._inner_width is not None:
                        self.goal_items[-1].resize(
                            self._inner_width,
                            self._goal_item_content_width or 0
                        )

            self.goal_items_column.controls = list(self.goal_items)

        self.update()

    def resize(self, width: int, inner_width: int, goal_item_content_width: int) -> None:
        self.width = width
        self._inner_width = inner_width
        self._goal_item_content_width = goal_item_content_width
        self.main_container.width = inner_width
        self.goal_header_row.width = inner_width
        self.goal_items_column.width = inner_width

        for item in self.goal_items:
            item.resize(inner_width, goal_item_content_width)


class ExpenseCategoryItem(ft.Row):
    def __init__(self, lang: dict[str, str], name: str, value: Decimal, currency: str, color: str) -> None:
        self.lang = lang
        self.name = name
        self.value = value
        self.currency = currency
        self.color = color

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.expense_name_text = Text.SMALL(self.name, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.W_500)
        self.expense_value_text = Text.SMALL(f"{format_compact_number(self.value, translations=self.lang)} {self.currency}", color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.color_box = ft.Container(
            width=10,
            height=10,
            border_radius=5,
            bgcolor=self.color
        )

        self.category_label = ft.Row(
            spacing=8,
            controls=[
                self.color_box,
                self.expense_name_text
            ]
        )

        super().__init__(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.category_label,
                self.expense_value_text
            ]
        )

    def update_data(self, name: str, value: Decimal, currency: str, color: str) -> None:
        self.color_box.bgcolor = color
        self.expense_name_text.value = name
        self.expense_value_text.value = f"{format_compact_number(value, translations=self.lang)} {currency}"

        self.update()

    def resize(self, width: int) -> None:
        self.width = width


class ExpensePieChart(ft.Container):
    def __init__(self, lang: dict[str, str], currency: str, category_data: dict[str, Decimal], on_details_click: Callable[..., None] | None) -> None:
        self.lang = lang
        self.currency = currency
        self.category_data = category_data or {}
        self.on_details_click = on_details_click
        self.chart_radius = DEFAULT_CHART_RADIUS
        self.center_radius = DEFAULT_CHART_CENTER_RADIUS
        self._inner_width: int | None = None

        self.pie_colors = PIE_CHART_COLORS

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.chart_title = Text.H4(self.lang["home.expense_breakdown"], color=Color.DEFAULT_TEXT)
        self.view_details_title = Text.SMALL(self.lang["home.view_details"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.no_data_title = Text.SMALL(self.lang["home.no_expense_data"], color=Color.BLAND_TEXT)

        # Static icons
        self.chart_icon = ft.Icon(ft.Icons.PIE_CHART, color=Color.EXPENSE_ACTION_BACKGROUND, size=18)
        self.view_details_icon = ft.Icon(ft.Icons.ARROW_FORWARD, color=Color.PRIMARY, size=14)
        self.no_data_icon = ft.Icon(ft.Icons.ERROR_OUTLINE, color=Color.DEFAULT_BORDER, size=32)

        # CONTAINER COMPONENTS
        self.pie_chart = fc.PieChart(
            sections=[
                fc.PieChartSection(
                    float(val),
                    color=self._get_section_color(idx, len(self.category_data)),
                    radius=self.chart_radius
                )
                for idx, val in enumerate(self.category_data.values())
            ] if self.category_data else [fc.PieChartSection(1, color=Color.TRANSPARENT, radius=self.chart_radius)],
            sections_space=PIE_CHART_SECTION_SPACING,
            center_space_radius=self.center_radius,
            expand=True
        )

        self.legend_items: list[ExpenseCategoryItem] = [
            ExpenseCategoryItem(self.lang, name, val, self.currency, self.pie_colors[idx % len(self.pie_colors)])
            for idx, (name, val) in enumerate(self.category_data.items())
        ] if self.category_data else []

        self.legend_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=self.legend_items
        )

        self.chart_icon_container = ft.Container(
            width=32,
            height=32,
            border_radius=10,
            bgcolor=Color.DIALOG_BACKGROUND,
            alignment=ft.Alignment.CENTER,
            content=self.chart_icon
        )

        self.view_details_button = ft.TextButton(
            content=ft.Row(
                spacing=4,
                tight=True,
                controls=[self.view_details_title, self.view_details_icon]
            ),
            on_click=self.on_details_click
        )

        self.chart_header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self.chart_icon_container,
                        self.chart_title
                    ]
                ),
                self.view_details_button
            ]
        )

        self.empty_state_container = ft.Container(
            padding=40,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.no_data_icon,
                    self.no_data_title
                ]
            )
        )

        self.pie_chart_container = ft.Container(
            alignment=ft.Alignment.CENTER,
            content=self.pie_chart
        )

        self.active_chart_layout = ft.Column(
            spacing=16,
            controls=[
                self.pie_chart_container,
                self.legend_list
            ]
        )

        self.chart_content_area = ft.Container(
            content=self.active_chart_layout if self.category_data else self.empty_state_container
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=16,
                controls=[
                    self.chart_header_row,
                    self.chart_content_area
                ]
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def _get_section_color(self, index: int, section_count: int) -> str:
        if (
            section_count > 1
            and section_count % len(self.pie_colors) == 1
            and index == section_count - 1
        ):
            return self.pie_colors[1]
        return self.pie_colors[index % len(self.pie_colors)]

    def update_data(self, category_data: dict[str, Decimal], currency: str) -> None:
        self.category_data = category_data or {}
        self.currency = currency

        if not self.category_data:
            self.legend_items.clear()
            self.chart_content_area.content = self.empty_state_container
            self.pie_chart.sections = [
                fc.PieChartSection(1, color=Color.TRANSPARENT, radius=self.chart_radius)
            ]
        else:
            self.chart_content_area.content = self.active_chart_layout
            categories = list(self.category_data.items())
            while len(self.legend_items) > len(categories):
                self.legend_items.pop()

            sections = []
            for idx, (name, val) in enumerate(categories):
                color = self._get_section_color(idx, len(categories))
                sections.append(
                    fc.PieChartSection(float(val), color=color, radius=self.chart_radius)
                )

                if idx < len(self.legend_items):
                    self.legend_items[idx].update_data(name, val, self.currency, color)
                else:
                    self.legend_items.append(
                        ExpenseCategoryItem(self.lang, name, val, self.currency, color)
                    )

            self.pie_chart.sections = sections
            self.legend_list.controls = list(self.legend_items)

        if self._inner_width is not None:
            for item in self.legend_items:
                item.resize(self._inner_width)
        self.update()

    def resize(self, width: int, inner_width: int, chart_radius: int, center_radius: int, legend_height: int) -> None:
        self.width = width
        self._inner_width = inner_width
        self.main_container.width = inner_width
        self.chart_header_row.width = inner_width
        self.chart_content_area.width = inner_width

        self.chart_radius = chart_radius
        self.center_radius = center_radius

        for section in self.pie_chart.sections:
            section.radius = chart_radius

        self.pie_chart.center_space_radius = center_radius
        self.legend_list.height = legend_height

        for item in self.legend_items:
            item.resize(inner_width)


class FeaturedLessonCard(ft.Container):
    def __init__(self, lang: dict[str, str], on_learn_click: Callable[..., None] | None) -> None:
        self.lang = lang
        self.on_learn_click = on_learn_click

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.card_title = Text.H4(self.lang["home.financial_learning"], color=Color.DEFAULT_TEXT)
        self.card_subtitle = Text.SMALL(self.lang["home.financial_learning_subtitle"], color=Color.BLAND_TEXT)
        self.featured_badge_title = Text.SMALL(self.lang["home.featured_content"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.featured_lesson_title = Text.P(self.lang["home.featured_lesson_title"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.featured_lesson_desc = Text.SMALL(self.lang["home.featured_lesson_desc"], color=Color.BLAND_TEXT)
        self.learn_now_title = Text.SMALL(self.lang["home.learn_now"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.completion_status_title = Text.SMALL(self.lang["home.completion_status"], color=Color.BLAND_TEXT)
        self.motto_title = Text.SMALL(self.lang["home.financial_motto"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)

        # Static icons
        self.lesson_header_icon = ft.Icon(ft.Icons.BOOK_ROUNDED, color=Color.LESSON_ICON_COLOR, size=18)

        # CONTAINER COMPONENTS
        self.lesson_icon_container = ft.Container(
            width=32,
            height=32,
            border_radius=10,
            bgcolor=Color.LESSON_ICON_BACKGROUND,
            alignment=ft.Alignment.CENTER,
            content=self.lesson_header_icon
        )

        self.lesson_title_column = ft.Column(
            spacing=0,
            controls=[
                self.card_title,
                self.card_subtitle
            ]
        )

        self.lesson_header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self.lesson_icon_container,
                        self.lesson_title_column
                    ]
                )
            ]
        )

        self.featured_badge_container = ft.Container(
            content=self.featured_badge_title,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(6, 2, 6, 2),
            border_radius=6
        )

        self.lesson_banner_texts = ft.Column(
            expand=True,
            spacing=4,
            controls=[
                self.featured_badge_container,
                self.featured_lesson_title,
                self.featured_lesson_desc
            ]
        )

        self.learn_now_button = ft.Button(
            content=self.learn_now_title,
            bgcolor=Color.LIGHT_ACCENT,
            on_click=self.on_learn_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        self.lesson_banner_container = ft.Container(
            bgcolor=Color.LESSON_BANNER_BACKGROUND,
            border_radius=16,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.lesson_banner_texts,
                    self.learn_now_button
                ]
            )
        )

        self.footer_divider = ft.Divider(
            height=1,
            color=Color.CARD_DIVIDER
        )

        self.footer_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.completion_status_title,
                self.motto_title
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=12,
                controls=[
                    self.lesson_header_row,
                    self.lesson_banner_container,
                    self.footer_divider,
                    self.footer_row
                ]
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def resize(self, width: int, inner_width: int) -> None:
        self.width = width
        self.main_container.width = inner_width
        self.lesson_header_row.width = inner_width
        self.lesson_banner_container.width = inner_width
        self.footer_row.width = inner_width