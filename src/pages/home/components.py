# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

import flet_charts as fc

from src.utils import Color, Text, UISettings


class _GoalItemCard(ft.Container):
    def __init__(self, item: dict):
        self.title_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.MEDIUM(item["title"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=Text.SMALL(item["progress_text"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                    bgcolor=Color.PRIMARY,
                    padding=ft.Padding(8, 2, 8, 2),
                    border_radius=12
                )
            ]
        )

        self.progress_bar = ft.ProgressBar(
            value=item["progress_ratio"],
            color=Color.PRIMARY,
            bgcolor=Color.PROGRESS_TRACK_BACKGROUND,
            height=8
        )

        self.metric_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.SMALL(item["contributed_label"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                Text.SMALL(item["target_label"], color=Color.BLAND_TEXT)
            ]
        )

        super().__init__(
            bgcolor=Color.GOAL_ITEM_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=6,
                controls=[self.title_row, self.progress_bar, self.metric_row]
            )
        )


class _LegendItemRow(ft.Row):
    def __init__(self, category_name: str, category_value: float, color: str, currency: str):
        self.category_badge = ft.Container(width=10, height=10, border_radius=5, bgcolor=color)
        self.category_label = Text.SMALL(category_name, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.W_500)
        self.value_label = Text.SMALL(f"{int(category_value):,} {currency}", color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)

        self.left_group = ft.Row(
            spacing=8,
            controls=[
                self.category_badge,
                self.category_label
            ]
        )

        super().__init__(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.left_group,
                self.value_label
            ]
        )


class BalanceCard(ft.Container):
    def __init__(self, lang: dict, net_balance: int, income: int, expense: int, savings: int, ai_advice: str, on_add_click: Callable, on_scan_click: Callable | None):
        self.lang = lang
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.ai_advice = ai_advice
        self.on_add_click = on_add_click
        self.on_scan_click = on_scan_click

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.balance_label_title = Text.SMALL(self.lang["home.available_balance"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.currency_label = Text.P(self.lang["generic.currency"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.add_transaction_button_label = Text.MEDIUM(self.lang["home.add_transaction"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
        self.purchase_scanner_title = Text.MEDIUM(self.lang["home.ai_scan"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.income_title = Text.H6(self.lang["home.total_income"], color=Color.LIGHT_ACCENT)
        self.expense_title = Text.H6(self.lang["home.total_expense"], color=Color.EXPENSE_LABEL_TEXT)
        self.saving_title = Text.H6(self.lang["home.total_savings"], color=Color.SAVINGS_LABEL_TEXT)
        self.ai_banner_title = Text.SMALL(self.lang["home.ai_advisor"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.add_transaction_button_icon = ft.Icon(ft.Icons.ADD_ROUNDED, color=Color.PRIMARY, size=18)
        self.purchase_scanner_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18)
        self.ai_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PRIMARY, size=16)

        # Dynamic texts
        self.balance_amount_display = Text.H1(f"{int(self.net_balance):,}", color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.income_display = Text.MEDIUM(f"{int(self.income):,} {self.lang['generic.currency']}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
        self.expense_display = Text.MEDIUM(f"-{int(self.expense):,} {self.lang['generic.currency']}", color=Color.EXPENSE_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.saving_display = Text.MEDIUM(f"{int(self.savings):,} {self.lang['generic.currency']}", color=Color.SAVINGS_VALUE_TEXT, weight=ft.FontWeight.BOLD)
        self.ai_advice_display = Text.SMALL(self.ai_advice, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.balance_label_container = ft.Container(
            content=self.balance_label_title,
            bgcolor=Color.DARK_SURFACE,
            padding=ft.Padding(12, 4, 12, 4),
            border_radius=20,
            border=ft.Border.all(1, Color.PRIMARY)
        )

        self.balance_amount_text = ft.Row(
            controls=[
                self.balance_amount_display,
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
            content=ft.Row(
                spacing=5,
                controls=[
                    self.add_transaction_button_label,
                    self.add_transaction_button_icon
                ],
                tight=True
            ),
            bgcolor=Color.LIGHT_ACCENT,
            on_click=self.on_add_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16))
        )

        self.purchase_scanner_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    self.purchase_scanner_icon,
                    self.purchase_scanner_title
                ],
                tight=True
            ),
            on_click=self.on_scan_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
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
            content=ft.Column(
                spacing=2,
                controls=[
                    self.income_title,
                    self.income_display
                ]
            )
        )

        self.expense_metric_container = ft.Container(
            expand=True,
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border_radius=UISettings.METRIC_PILL_BORDER_RADIUS,
            padding=UISettings.METRIC_PILL_PADDING,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            content=ft.Column(
                spacing=2,
                controls=[
                    self.expense_title,
                    self.expense_display
                ]
            )
        )

        self.saving_metric_container = ft.Container(
            expand=True,
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border_radius=UISettings.METRIC_PILL_BORDER_RADIUS,
            padding=UISettings.METRIC_PILL_PADDING,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            content=ft.Column(
                spacing=2,
                controls=[
                    self.saving_title,
                    self.saving_display
                ]
            )
        )

        self.metrics_row = ft.Row(
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
                self.ai_advice_display
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

    def update_data(self, net_balance: int, income: int, expense: int, savings: int, ai_advice: str):
        self.net_balance = net_balance
        self.income = income
        self.expense = expense
        self.savings = savings
        self.ai_advice = ai_advice

        self.balance_amount_display.value = f"{int(self.net_balance):,}"
        self.income_display.value = f"{int(self.income):,} {self.lang['generic.currency']}"
        self.expense_display.value = f"-{int(self.expense):,} {self.lang['generic.currency']}"
        self.saving_display.value = f"{int(self.savings):,} {self.lang['generic.currency']}"
        self.ai_advice_display.value = self.ai_advice

        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class SavingsProgressCard(ft.Container):
    def __init__(self, lang: dict, objective_items: list, on_view_all_click: Callable | None):
        self.lang = lang
        self.objective_items = objective_items or []
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
        self.view_all_count_display = Text.SMALL(
            f"{self.lang['generic.all']} ({len(self.objective_items)})",
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
                    self.view_all_count_display,
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

        self.goal_items_column = ft.Column(
            spacing=6,
            controls=(
                [self.empty_state_container] if not self.objective_items
                else [_GoalItemCard(item) for item in self.objective_items]
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
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def update_data(self, objective_items: list):
        self.objective_items = objective_items or []
        self.view_all_count_display.value = f"{self.lang['generic.all']} ({len(self.objective_items)})"

        self.goal_items_column.controls = (
            [self.empty_state_container] if not self.objective_items
            else [_GoalItemCard(item) for item in self.objective_items]
        )

        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class ExpensePieChartCard(ft.Container):
    def __init__(self, lang: dict, category_data: dict, on_details_click: Callable | None):
        self.lang = lang
        self.category_data = category_data or {}
        self.on_details_click = on_details_click

        self.pie_colors = [
            Color.EXPENSE_ACTION_BACKGROUND,
            Color.PRIMARY,
            Color.GOAL_HEADER_ICON_COLOR,
            Color.LESSON_ICON_COLOR,
            Color.SAVINGS_VALUE_TEXT,
            Color.PROGRESS_ACTIVE,
            Color.PRIMARY_ACTION,
            Color.CHART_INCOME,
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

        # Dynamic controls
        self.pie_chart = fc.PieChart(
            sections=[
                fc.PieChartSection(val, color=self.pie_colors[idx % len(self.pie_colors)], radius=45)
                for idx, val in enumerate(self.category_data.values())
            ] if self.category_data else [],
            sections_space=2,
            center_space_radius=40,
            expand=True
        )

        self.legend_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=120,
            spacing=8,
            controls=[
                _LegendItemRow(name, val, self.pie_colors[idx % len(self.pie_colors)], self.lang["generic.currency"])
                for idx, (name, val) in enumerate(self.category_data.items())
            ] if self.category_data else []
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
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def update_data(self, category_data: dict):
        self.category_data = category_data or {}

        if not self.category_data:
            self.chart_content_area.content = self.empty_state_container
        else:
            self.pie_chart.sections = [
                fc.PieChartSection(val, color=self.pie_colors[idx % len(self.pie_colors)], radius=45)
                for idx, val in enumerate(self.category_data.values())
            ]
            self.legend_list.controls = [
                _LegendItemRow(name, val, self.pie_colors[idx % len(self.pie_colors)], self.lang["generic.currency"])
                for idx, (name, val) in enumerate(self.category_data.items())
            ]
            self.chart_content_area.content = self.active_chart_layout

        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


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
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=self.main_container
        )

    def resize(self, width: int):
        self.main_container.width = width
        self.main_container.content.width = width