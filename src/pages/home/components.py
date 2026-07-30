# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft
import flet_charts as fc

from src.utils import Color, Text, UISettings


class ActionSelectionDialog(ft.AlertDialog):
    def __init__(self, on_income, on_expense, on_saving, on_cancel, lang: dict):
        super().__init__(
            content_padding=0, bgcolor=Color.TRANSPARENT,
            content=ft.Container(
                width=350, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
                content=ft.Column(
                    tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.PRIMARY_TEXT)]),
                        ft.Container(height=10),
                        ft.Button(Text.BUTTON(lang["spending.add_income"]), icon=ft.Icons.TRENDING_UP, on_click=on_income, bgcolor=Color.CHART_INCOME, color=Color.WHITE, width=300, height=50),
                        ft.Container(height=5),
                        ft.Button(Text.BUTTON(lang["spending.add_expense"]), icon=ft.Icons.TRENDING_DOWN, on_click=on_expense, bgcolor=Color.CHART_EXPENSE, color=Color.WHITE, width=300, height=50),
                        ft.Container(height=5),
                        ft.Button(Text.BUTTON(lang["saving.objective_details"]), icon=ft.Icons.SAVINGS, on_click=on_saving, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE, width=300, height=50),
                    ]
                )
            )
        )


class BalanceCard(ft.Container):
    def __init__(self, expense, income, saving, on_add_click, lang: dict):
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND, border_radius=UISettings.CARD_BORDER_RADIUS, padding=UISettings.CARD_PADDING, shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(spacing=5, controls=[Text.LABEL(lang["generic.expense"], color=Color.BLAND_TEXT), Text.P(f"{expense:,} VND", color=Color.DEFAULT_TEXT)]),
                    ft.Column(spacing=5, controls=[Text.LABEL(lang["generic.income"], color=Color.BLAND_TEXT), Text.P(f"{income:,} VND", color=Color.DEFAULT_TEXT)]),
                    ft.Column(spacing=5, controls=[Text.LABEL(lang["generic.saving"], color=Color.BLAND_TEXT), Text.P(f"{saving:,} VND", color=Color.DEFAULT_TEXT)]),
                    ft.Column(spacing=5, controls=[ft.Button("+", on_click=on_add_click, bgcolor=Color.CONFIRM_BUTTON, color=Color.WHITE)])
                ]
            )
        )

class SavingGauge(ft.Container):
    def __init__(self, page: ft.Page, total_savings: float, total_target: float, lang: dict):
        percent_value = float(min(total_savings / total_target, 1.0)) * 100 if total_target > 0 else 100.0
        self.goal_percentage = Text.H3(f"{round(percent_value)}%", color=Color.DEFAULT_TEXT)
        self.goal_label = Text.SMALL(lang["home.saving_goal"], color=Color.BLAND_TEXT)

        self.gauge_chart = (
            fc.PieChart(
                sections=[
                    fc.PieChartSection(value=100, color=ft.Colors.TRANSPARENT, radius=15),
                    fc.PieChartSection(value=percent_value, color=Color.CHART_INCOME, radius=30),
                    fc.PieChartSection(value=100 - percent_value, color=Color.CHART_INACTIVE, radius=30),
                ], sections_space=0, expand=True
            ))

        super().__init__(
            bgcolor=Color.WHITE, padding=UISettings.CARD_PADDING, shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            expand=1, aspect_ratio=1.0, on_click=lambda e: page.go("/saving"), ink=True,
            content=ft.Stack(
                controls=[
                    self.gauge_chart,
                    ft.Container(content=ft.Column([self.goal_label, self.goal_percentage], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0), alignment=ft.Alignment.CENTER)
                ], expand=True
            )
        )

    def resize(self, safe_width):
        self.gauge_chart.center_space_radius = max(30, int((safe_width / 4) - 70))