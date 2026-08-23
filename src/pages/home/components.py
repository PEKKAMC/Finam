# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft
import flet_charts as fc

from src.database import db
from src.utils import Color, Text, UISettings


class ActionSelectionDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, lang: dict, on_income: Callable, on_expense: Callable, on_saving: Callable, on_cancel: Callable):
        self._page = page
        self.lang = lang

        self.dialog_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.H4(self.lang["home.quick_actions"], color=Color.LIGHT_ACCENT),
                ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.LIGHT_ACCENT),
            ]
        )

        self.add_income_button = ft.Button(
            Text.BUTTON(self.lang["home.add_income"]),
            icon=ft.Icons.ARROW_UPWARD_ROUNDED,
            on_click=on_income,
            bgcolor=Color.PRIMARY,
            color=Color.WHITE
        )

        self.add_expense_button = ft.Button(
            Text.BUTTON(self.lang["home.add_expense"]),
            icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
            on_click=on_expense,
            bgcolor=Color.EXPENSE_ACTION_BACKGROUND,
            color=Color.WHITE
        )

        self.object_details_button = ft.Button(
            Text.BUTTON(self.lang["home.objective_details"]),
            icon=ft.Icons.SAVINGS,
            on_click=on_saving,
            bgcolor=Color.LIGHT_ACCENT,
            color=Color.DARK_SURFACE
        )

        self.main_container = ft.Container(
            padding=25,
            bgcolor=Color.DARK_SURFACE,
            border_radius=24,
            border=ft.Border.all(1, Color.PRIMARY),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.dialog_header,
                    self.add_income_button,
                    self.add_expense_button,
                    self.object_details_button
                ]
            )
        )

        super().__init__(
            content_padding=0,
            bgcolor=Color.TRANSPARENT,
            content=self.main_container
        )

    def resize(self, dialog_width: int, button_width: int, button_height: int):
        self.main_container.width = dialog_width
        self.add_income_button.width, self.add_expense_button.width, self.object_details_button.width = button_width, button_width, button_width
        self.add_income_button.height, self.add_expense_button.height, self.object_details_button.height = button_height, button_height, button_height


class BalanceCard(ft.Container):
    def __init__(self, net_balance: float, income: float, expense: float, saving: float, ai_advice: str, on_add_click: Callable, on_scan_click: Callable, lang: dict):
        self.lang = lang

        balance_header = ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=Text.SMALL(self.lang["home.available_balance"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                    bgcolor=Color.DARK_SURFACE,
                    padding=ft.Padding(12, 4, 12, 4),
                    border_radius=20,
                    border=ft.Border.all(1, Color.PRIMARY)
                ),
                ft.Row(
                    controls=[
                        Text.H1(f"{int(net_balance):,}", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                        Text.P(self.lang["generic.currency"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END
                )
            ]
        )

        action_buttons = ft.Row(
            spacing=8,
            controls=[
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ADD_ROUNDED, color=Color.PRIMARY, size=18),
                            Text.LABEL(self.lang["home.add_transaction"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
                        ],
                        tight=True
                    ),
                    bgcolor=Color.LIGHT_ACCENT,
                    on_click=on_add_click,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16))
                ),
                ft.OutlinedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18),
                            Text.LABEL(self.lang["home.ai_scan"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
                        ],
                        tight=True
                    ),
                    on_click=on_scan_click,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=16),
                        side=ft.BorderSide(1, Color.SCAN_BUTTON_BORDER)
                    )
                )
            ]
        )

        top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[balance_header, action_buttons]
        )

        metrics_row = ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=Color.METRIC_PILL_BACKGROUND,
                    border_radius=16,
                    padding=8,
                    border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.SMALL(self.lang["home.total_income"], color=Color.LIGHT_ACCENT),
                                    Text.LABEL(f"{int(income):,} {self.lang['generic.currency']}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
                                ]
                            ),
                            ft.Icon(ft.Icons.NORTH_EAST, color=Color.LIGHT_ACCENT, size=20)
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    bgcolor=Color.METRIC_PILL_BACKGROUND,
                    border_radius=16,
                    padding=8,
                    border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.SMALL(self.lang["home.total_expense"], color=Color.EXPENSE_LABEL_TEXT),
                                    Text.LABEL(f"-{int(expense):,} {self.lang['generic.currency']}", color=Color.EXPENSE_VALUE_TEXT, weight=ft.FontWeight.BOLD)
                                ]
                            ),
                            ft.Icon(ft.Icons.SOUTH_EAST, color=Color.EXPENSE_VALUE_TEXT, size=20)
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    bgcolor=Color.METRIC_PILL_BACKGROUND,
                    border_radius=16,
                    padding=8,
                    border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.SMALL(self.lang["home.total_savings"], color=Color.SAVINGS_LABEL_TEXT),
                                    Text.LABEL(f"{int(saving):,} {self.lang['generic.currency']}", color=Color.SAVINGS_VALUE_TEXT, weight=ft.FontWeight.BOLD)
                                ]
                            ),
                            ft.Icon(ft.Icons.TRACK_CHANGES, color=Color.SAVINGS_VALUE_TEXT, size=20)
                        ]
                    )
                )
            ]
        )

        ai_banner = ft.Container(
            bgcolor=Color.AI_ADVICE_BACKGROUND,
            border_radius=16,
            padding=12,
            border=ft.Border.all(1, Color.AI_ADVICE_BORDER),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=30,
                        height=30,
                        border_radius=10,
                        bgcolor=Color.LIGHT_ACCENT,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PRIMARY, size=16)
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            Text.SMALL(self.lang["home.ai_advisor"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                            Text.SMALL(ai_advice, color=Color.WHITE)
                        ]
                    )
                ]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=24,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Column(
                spacing=20,
                controls=[top_row, metrics_row, ai_banner]
            )
        )


class SavingsProgressCard(ft.Container):
    def __init__(self, page: ft.Page, objectives: list, lang: dict):
        self._page = page
        self.lang = lang

        items = []
        if not objectives:
            items.append(
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                    content=Text.SMALL(self.lang["home.no_savings_goal"], color=Color.BLAND_TEXT)
                )
            )
        else:
            for obj in objectives[:3]:
                objective_id, title, reason, target_amount, completed_at = obj

                cur = float(db.saving.get_objective_progress(objective_id))
                tgt = float(target_amount) if target_amount > 0 else 1.0

                pct = min(1.0, cur / tgt)
                pct_str = f"{int(pct * 100)}%"
                display_title = title if title else self.lang["home.default_goal_title"]

                items.append(
                    ft.Container(
                        bgcolor=Color.GOAL_ITEM_BACKGROUND,
                        border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                        border_radius=16,
                        padding=12,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        Text.LABEL(display_title, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=Text.SMALL(pct_str, color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                            bgcolor=Color.PRIMARY,
                                            padding=ft.Padding(8, 2, 8, 2),
                                            border_radius=12
                                        )
                                    ]
                                ),
                                ft.ProgressBar(value=pct, color=Color.PRIMARY, bgcolor=Color.PROGRESS_TRACK_BACKGROUND, height=8),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        Text.SMALL(f"{self.lang['home.contributed']}: {int(cur):,} {self.lang['generic.currency']}", color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                                        Text.SMALL(f"{self.lang['home.target']}: {int(tgt):,} {self.lang['generic.currency']}", color=Color.BLAND_TEXT)
                                    ]
                                )
                            ]
                        )
                    )
                )

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=32,
                            height=32,
                            border_radius=10,
                            bgcolor=Color.GOAL_HEADER_ICON_BACKGROUND,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.TRACK_CHANGES, color=Color.GOAL_HEADER_ICON_COLOR, size=18)
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                Text.H4(self.lang["home.saving_goal"], color=Color.DEFAULT_TEXT),
                                Text.SMALL(self.lang["home.saving_goal_subtitle"], color=Color.BLAND_TEXT)
                            ]
                        )
                    ]
                ),
                ft.TextButton(
                    content=ft.Row([
                        Text.SMALL(f"{self.lang['generic.all']} ({len(objectives)})", color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Icon(ft.Icons.ARROW_FORWARD, color=Color.PRIMARY, size=14)
                    ], tight=True),
                    on_click=lambda e: self._page.go("/saving")
                )
            ]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=ft.Column(
                spacing=12,
                controls=[header] + items
            )
        )

class ExpensePieChartCard(ft.Container):
    def __init__(self, page: ft.Page, category_data: dict, lang: dict):
        self._page = page
        self.category_data = category_data
        self.lang = lang

        pie_colors = [
            Color.EXPENSE_ACTION_BACKGROUND,
            Color.PRIMARY,
            Color.GOAL_HEADER_ICON_COLOR,
            Color.LESSON_ICON_COLOR,
            Color.SAVINGS_VALUE_TEXT,
            Color.PROGRESS_ACTIVE,
            Color.PRIMARY_ACTION,
            Color.CHART_INCOME,
        ]

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=32,
                            height=32,
                            border_radius=10,
                            bgcolor=Color.DANGER_SOFT if hasattr(Color, 'DANGER_SOFT') else Color.DIALOG_BACKGROUND,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.PIE_CHART, color=Color.EXPENSE_ACTION_BACKGROUND, size=18)
                        ),
                        Text.H4(self.lang["home.expense_breakdown"], color=Color.DEFAULT_TEXT)
                    ]
                ),
                ft.TextButton(
                    content=ft.Row([
                        Text.SMALL(self.lang["home.view_details"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Icon(ft.Icons.ARROW_FORWARD, color=Color.PRIMARY, size=14)
                    ], tight=True),
                    on_click=lambda e: self._page.go("/spending")
                )
            ]
        )

        if not category_data:
            content_area = ft.Container(
                padding=40,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=Color.DEFAULT_BORDER, size=32),
                        Text.SMALL(self.lang["home.no_expense_data"], color=Color.BLAND_TEXT)
                    ]
                )
            )
        else:
            sections = []
            legend_items = []

            for i, (category, value) in enumerate(category_data.items()):
                color = pie_colors[i % len(pie_colors)]

                sections.append(
                    fc.PieChartSection(
                        value,
                        color=color,
                        radius=45
                    )
                )

                legend_items.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(width=10, height=10, border_radius=5, bgcolor=color),
                                    Text.SMALL(category, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.W_500)
                                ]
                            ),
                            Text.SMALL(f"{int(value):,} đ", color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
                        ]
                    )
                )

            pie_chart = ft.Container(
                alignment=ft.Alignment.CENTER,
                content=fc.PieChart(
                    sections=sections,
                    sections_space=2,
                    center_space_radius=40,
                    expand=True
                )
            )

            legend_list = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                height=120,
                spacing=8,
                controls=legend_items
            )

            content_area = ft.Column(
                spacing=16,
                controls=[pie_chart, legend_list]
            )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=ft.Column(
                spacing=16,
                controls=[header, content_area]
            )
        )

class FeaturedLessonCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict):
        self._page = page
        self.lang = lang

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=32,
                            height=32,
                            border_radius=10,
                            bgcolor=Color.LESSON_ICON_BACKGROUND,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.BOOK_ROUNDED, color=Color.LESSON_ICON_COLOR, size=18)
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                Text.H4(self.lang["home.financial_learning"], color=Color.DEFAULT_TEXT),
                                Text.SMALL(self.lang["home.financial_learning_subtitle"], color=Color.BLAND_TEXT)
                            ]
                        )
                    ]
                ),
                ft.TextButton(
                    content=Text.SMALL(self.lang["home.view_list"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                    on_click=lambda e: self._page.go("/lessons")
                )
            ]
        )

        lesson_banner = ft.Container(
            bgcolor=Color.LESSON_BANNER_BACKGROUND,
            border_radius=16,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Container(
                                content=Text.SMALL(self.lang["home.featured_content"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                bgcolor=Color.DARK_SURFACE,
                                padding=ft.Padding(6, 2, 6, 2),
                                border_radius=6
                            ),
                            Text.P(self.lang["home.featured_lesson_title"], color=Color.WHITE, weight=ft.FontWeight.BOLD),
                            Text.SMALL(self.lang["home.featured_lesson_desc"], color=Color.BLAND_TEXT)
                        ]
                    ),
                    ft.Button(
                        content=Text.SMALL(self.lang["home.learn_now"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD),
                        bgcolor=Color.LIGHT_ACCENT,
                        on_click=lambda e: self._page.go("/lessons"),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                    )
                ]
            )
        )

        footer = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Text.SMALL(self.lang["home.completion_status"], color=Color.BLAND_TEXT),
                Text.SMALL(self.lang["home.financial_motto"], color=Color.PRIMARY, weight=ft.FontWeight.BOLD)
            ]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=True,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=12,
                controls=[header, lesson_banner, ft.Divider(height=1, color=Color.CARD_DIVIDER), footer]
            )
        )