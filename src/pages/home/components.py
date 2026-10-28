# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft
import flet_charts as fc

from src.database import db
from src.utils import Color, Text, UISettings, format_number


class BalanceCard(ft.Container):
    def __init__(self, lang: dict, username: dict, net_balance: float, income: float, expense: float, savings: float, advice: str, on_add_click: Callable, on_scan_click: Callable | None):
        self.lang = lang
        self.username = username
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.advice = advice
        self.on_add_click = on_add_click
        self.on_scan_click = on_scan_click
        self.currency = db.users.get_currency(self.username)

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.balance_label_text = Text.LABEL(self.lang["home.available_balance"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.currency_label = Text.P(self.currency, color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.add_transaction_button_label = Text.BUTTON(self.lang["home.add_transaction"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.purchase_scanner_button_label = Text.BUTTON(self.lang["home.ai_scan"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.income_title = Text.H6(self.lang["home.total_income"], color=Color.LIGHT_ACCENT)
        self.expense_title = Text.H6(self.lang["home.total_expense"], color=Color.EXPENSE_LABEL_TEXT)
        self.saving_title = Text.H6(self.lang["home.total_savings"], color=Color.SAVINGS_LABEL_TEXT)
        self.ai_banner_title = Text.SMALL(self.lang["home.ai_advisor"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.add_transaction_button_icon = ft.Icon(ft.Icons.ADD_ROUNDED, color=Color.PRIMARY, size=18)
        self.purchase_scanner_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18)
        self.ai_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PRIMARY, size=16)

        # Dynamic texts
        self.balance_amount_text = Text.H1(format_number(self.net_balance), color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.income_text = Text.MEDIUM(f"{format_number(self.income)} {self.currency}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.expense_text = Text.MEDIUM(f"{format_number(self.expense)} {self.currency}", color=Color.EXPENSE_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.savings_text = Text.MEDIUM(f"{format_number(self.savings)} {self.currency}", color=Color.SAVINGS_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.advice_text = Text.SMALL(self.advice, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.balance_label_container = ft.Container(
            content=self.balance_label_text,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 4, 12, 4),
            border_radius=20,
            border=ft.Border.all(1, Color.PRIMARY)
        )

        self.balance_amount_text = ft.Row(
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
                self.balance_amount_text
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
                ],
                tight=True
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
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.purchase_scanner_icon,
                    self.purchase_scanner_button_label
                ],
                tight=True
            ),
            on_click=self.on_scan_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=0,
                alignment=ft.Alignment.CENTER,
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
            border_radius=UISettings.METRIC_PILL_BORDER_RADIUS,
            padding=UISettings.METRIC_PILL_PADDING,
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
            border_radius=UISettings.METRIC_PILL_BORDER_RADIUS,
            padding=UISettings.METRIC_PILL_PADDING,
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
            border_radius=UISettings.METRIC_PILL_BORDER_RADIUS,
            padding=UISettings.METRIC_PILL_PADDING,
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
            content=self.ai_icon,
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
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=self.main_container
        )

    def update_data(self, net_balance: float, income: float, expense: float, savings: float, ai_advice: str):
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.advice = ai_advice
        self.currency = db.users.get_currency(self.username)

        self.balance_amount_text.value = format_number(self.net_balance)
        self.currency_label.value = self.currency
        self.income_text.value = f"{format_number(self.income)} {self.currency}"
        self.expense_text.value = f"{format_number(self.expense)} {self.currency}"
        self.savings_text.value = f"{format_number(self.savings)} {self.currency}"
        self.advice_text.value = self.advice

        self.update()

    def resize(self, width: int):
        self.main_container.width = width

        inner_width = width - (UISettings.CARD_PADDING * 2)
        self.balance_top_row.width = inner_width
        self.metrics_row.width = inner_width
        self.ai_banner_container.width = inner_width


class SavingsGoalItem(ft.Container):
    def __init__(self, item: dict):
        self.item = item
        self.completed = item.get("completed", False)

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.title_text = Text.MEDIUM(item["title"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
        self.progress_text = Text.SMALL(item["progress_text"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.contributed_label = Text.SMALL(item["contributed_label"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.target_label = Text.SMALL(item["target_label"], color=Color.BLAND_TEXT)

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
            bgcolor=Color.GOAL_ITEM_BACKGROUND if self.completed else Color.CARD_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER) if self.completed else ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=12,
            ink=True,
            content=self.main_container
        )

    def update_data(self, item: dict):
        self.item = item
        self.completed = item.get("completed", False)

        self.title_text.value = item["title"]
        self.progress_text.value = item["progress_text"]
        self.progress_bar.value = item["progress_ratio"]
        self.contributed_label.value = item["contributed_label"]
        self.target_label.value = item["target_label"]
        self.bgcolor = Color.GOAL_ITEM_BACKGROUND if self.completed else Color.CARD_BACKGROUND
        self.border = ft.Border.all(1, Color.GOAL_ITEM_BORDER) if self.completed else ft.Border.all(1, Color.INPUT_BORDER)

        self.update()

    def resize(self, width: int):
        self.main_container.width = width

        self.header_row.width = width
        self.progress_bar.width = width
        self.footer_row.width = width


class SavingsProgressCard(ft.Container):
    def __init__(self, lang: dict, objective_items: tuple[list, int], on_view_all_click: Callable | None):
        self.lang = lang
        self.objective_items, self.objective_count = objective_items
        self.on_view_all_click = on_view_all_click

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
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def update_data(self, objective_items: list):
        self.objective_items = objective_items or []
        self.view_all_count.value = f"{self.lang['generic.all']} ({len(self.objective_items)})"

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

            self.goal_items_column.controls = list(self.goal_items)

        self.update()

    def resize(self, width: int):
        self.main_container.width = width

        inner_width = max(0, width - (UISettings.CARD_PADDING * 2))
        self.goal_header_row.width = inner_width
        self.goal_items_column.width = inner_width

        for item in self.goal_items:
            item.resize(inner_width)


class ExpenseCategoryItem(ft.Row):
    def __init__(self, name: str, val: float, currency_lang: str, color: str):


        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.expense_name_text = Text.SMALL(name, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.W_500)
        self.expense_value_text = Text.SMALL(f"{format_number(val)} {currency_lang}", color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.color_box = ft.Container(
            width=10,
            height=10,
            border_radius=5,
            bgcolor=color
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

    def update_data(self, name: str, val: float, currency_lang: str, color: str):
        self.color_box.bgcolor = color
        self.expense_name_text.value = name
        self.expense_value_text.value = f"{format_number(val)} {currency_lang}"

        self.update()

    def resize(self, width: int):
        self.width = width


class ExpensePieChart(ft.Container):
    def __init__(self, lang: dict, username: dict, category_data: dict, on_details_click: Callable | None):
        self.lang = lang
        self.username = username
        self.category_data = category_data or {}
        self.on_details_click = on_details_click
        self.currency = db.users.get_currency(self.username)

        self.pie_colors = [
            Color.PIE_CHART_RED,
            Color.PIE_CHART_BLUE,
            Color.PIE_CHART_GREEN,
            Color.PIE_CHART_YELLOW,
            Color.PIE_CHART_TURQUOISE,
            Color.PIE_CHART_PURPLE
        ]

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.chart_title = Text.H4(self.lang["home.expense_breakdown"], color=Color.DEFAULT_TEXT)
        self.view_details_title = Text.SMALL(self.lang["home.view_details"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.no_data_title = Text.SMALL(self.lang["home.no_expense_data"], color=Color.BLAND_TEXT)

        # Static icons
        self.chart_icon = ft.Icon(ft.Icons.PIE_CHART, color=Color.EXPENSE_ACTION_BACKGROUND, size=18)
        self.view_details_icon = ft.Icon(ft.Icons.ARROW_FORWARD, color=Color.PRIMARY, size=14)
        self.no_data_icon = ft.Icon(ft.Icons.ERROR_OUTLINE, color=Color.DEFAULT_BORDER, size=32)

        self.pie_chart = fc.PieChart(
            sections=[
                fc.PieChartSection(val, color=self.pie_colors[idx % len(self.pie_colors)], radius=45)
                for idx, val in enumerate(self.category_data.values())
            ] if self.category_data else [fc.PieChartSection(1, color=Color.TRANSPARENT, radius=45)],
            sections_space=2,
            center_space_radius=40,
            expand=True
        )

        self.legend_items: list[ExpenseCategoryItem] = [
            ExpenseCategoryItem(name, val, self.currency, self.pie_colors[idx % len(self.pie_colors)])
            for idx, (name, val) in enumerate(self.category_data.items())
        ] if self.category_data else []

        self.legend_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=120,
            spacing=8,
            controls=self.legend_items
        )

        # CONTAINER COMPONENTS
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
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def update_data(self, category_data: dict):
        self.category_data = category_data or {}
        self.currency = db.users.get_currency(self.username)

        if not self.category_data:
            self.legend_items.clear()
            self.chart_content_area.content = self.empty_state_container
            self.pie_chart.sections = [fc.PieChartSection(1, color=Color.TRANSPARENT, radius=45)]
        else:
            self.chart_content_area.content = self.active_chart_layout
            categories = list(self.category_data.items())

            if len(self.pie_chart.sections) == 1 and self.pie_chart.sections[0].color == Color.TRANSPARENT:
                self.pie_chart.sections.clear()

            while len(self.pie_chart.sections) > len(categories):
                self.pie_chart.sections.pop()
            while len(self.legend_items) > len(categories):
                self.legend_items.pop()

            for idx, (name, val) in enumerate(categories):
                color = self.pie_colors[idx % len(self.pie_colors)]

                if idx < len(self.pie_chart.sections):
                    self.pie_chart.sections[idx].value = val
                    self.pie_chart.sections[idx].color = color
                else:
                    self.pie_chart.sections.append(
                        fc.PieChartSection(val, color=color, radius=45)
                    )

                if idx < len(self.legend_items):
                    self.legend_items[idx].update_data(name, val, self.currency, color)
                else:
                    self.legend_items.append(
                        ExpenseCategoryItem(name, val, self.currency, color)
                    )

            self.legend_list.controls = list(self.legend_items)

        self.update()

    def resize(self, width: int, height: int):
        self.main_container.width = width

        inner_width = width - (UISettings.CARD_PADDING * 2)
        self.chart_header_row.width = inner_width
        self.chart_content_area.width = inner_width

        chart_radius = int(height * 0.06)
        center_radius = int(height * 0.045)

        for section in self.pie_chart.sections:
            section.radius = chart_radius

        self.pie_chart.center_space_radius = center_radius
        self.legend_list.height = int(height * 0.15)

        for item in self.legend_items:
            item.resize(inner_width)


class FeaturedLessonCard(ft.Container):
    def __init__(self, lang: dict, on_learn_click: Callable | None):
        self.lang = lang
        self.on_learn_click = on_learn_click

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.card_title = Text.H4(self.lang["home.financial_learning"], color=Color.DEFAULT_TEXT)
        self.card_subtitle = Text.SMALL(self.lang["home.financial_learning_subtitle"], color=Color.BLAND_TEXT)
        self.view_list_title = Text.SMALL(self.lang["home.view_list"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
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

        self.view_list_button = ft.TextButton(
            content=self.view_list_title,
            on_click=self.on_learn_click
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
                ),
                self.view_list_button
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

        self.footer_divider = ft.Divider(height=1, color=Color.CARD_DIVIDER)

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
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def resize(self, width: int):
        self.main_container.width = width

        inner_width = width - (UISettings.CARD_PADDING * 2)
        self.lesson_header_row.width = inner_width
        self.lesson_banner_container.width = inner_width
        self.footer_row.width = inner_width
