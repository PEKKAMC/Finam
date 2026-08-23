# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft
import flet_charts as fc

from src.utils import Color, Text
from src.logger import Logger


class FinancialChart(ft.Container):
    def __init__(self, chart_date: dict, chart_data: list, chart_type: str, lang: dict):
        self.chart_date = chart_date
        self.chart_data = chart_data
        self.chart_type = chart_type
        self.lang = lang

        max_chart_value = max(max(int(data["income"]), int(data["expense"])) for data in chart_data)
        self.max_value = max_chart_value if max_chart_value > 0 else 1

        from src.utils import UISettings
        super().__init__(
            expand=True,
            height=275,
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=24,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=ft.Column(
                spacing=16,
                controls=[
                    self.build_legend(),
                    ft.Container(
                        content=self.build_bar_chart(),
                        expand=True,
                        padding=ft.Padding.only(top=10)
                    )
                ]
            )
        )

    def build_legend(self):
        Logger.info("Building chart legend...")

        match self.chart_type:
            case "daily":
                date_text = f"{self.lang['generic.week']} {self.chart_date['week']}, {self.chart_date['month']}/{self.chart_date['year']}"
            case "weekly":
                date_text = f"{self.chart_date['month']}/{self.chart_date['year']}"
            case "monthly":
                date_text = f"{self.chart_date['year']}"
            case _:
                date_text = ""
                Logger.error("Unknown chart type")

        legend = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.BAR_CHART, color="#1A4734", size=16),
                            width=32,
                            height=32,
                            bgcolor="#DAF1DE",
                            border_radius=12,
                            alignment=ft.Alignment.CENTER
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                Text.H5(self.lang["financial_chart.chart_title"], color="#1e293b"),
                                Text.LABEL(date_text, color="#64748b")
                            ]
                        )
                    ]
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Container(width=10, height=10, bgcolor="#1A4734", border_radius=5),
                                Text.BUTTON(self.lang["generic.income"], color="#1A4734"),
                            ]
                        ),
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Container(width=10, height=10, bgcolor="#E90C00", border_radius=5),
                                Text.BUTTON(self.lang["generic.expense"], color="#E90C00"),
                            ]
                        )
                    ]
                )
            ]
        )

        return legend

    def _generate_y_axis_labels(self):
        step = self.max_value / 4
        labels = []
        for i in range(5):
            value = int(i * step)
            label_str = f"{value // 1000}K"
            labels.append(
                fc.ChartAxisLabel(
                    value=value,
                    label=Text.LABEL(label_str, color="#64748b")
                )
            )
        return labels

    def build_bar_chart(self):
        Logger.info("Building bar chart...")

        chart_label = []
        groups = []
        bar_size = 18

        for index, data in enumerate(self.chart_data):
            match self.chart_type:
                case "daily":
                    label_text = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"][index]
                case "weekly":
                    label_text = f"{self.lang['generic.week']} {data['week']}"
                case "monthly":
                    label_text = f"{self.lang['generic.month']} {data['month']}"
                case _:
                    label_text = ""
                    Logger.error("Unknown chart type")

            chart_label.append(
                fc.ChartAxisLabel(
                    value=index,
                    label=ft.Container(
                        Text.LABEL(label_text, color="#64748b"),
                        padding=ft.Padding.only(top=10)
                    )
                )
            )

            income_value = int(data["income"])
            expense_value = int(data["expense"])

            groups.append(
                fc.BarChartGroup(
                    x=index,
                    rods=[
                        fc.BarChartRod(
                            from_y=0,
                            to_y=income_value,
                            width=bar_size,
                            color="#1A4734",
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang.get('generic.income', 'Thu nhập')}: {income_value:,} đ"
                            ),
                        ),
                        fc.BarChartRod(
                            from_y=0,
                            to_y=expense_value,
                            width=bar_size,
                            color="#E90C00",
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang.get('generic.expense', 'Chi tiêu')}: {expense_value:,} đ"
                            ),
                        )
                    ]
                )
            )

        return ft.Container(
            content=fc.BarChart(
                groups=groups,
                bottom_axis=fc.ChartAxis(
                    labels=chart_label,
                    label_size=40,
                ),
                left_axis=fc.ChartAxis(
                    labels=self._generate_y_axis_labels(),
                    label_size=35,
                ),
                horizontal_grid_lines=fc.ChartGridLines(color=Color.TRANSPARENT),
                max_y=self.max_value,
                interactive=True,
                tooltip=fc.BarChartTooltip(
                    bgcolor=Color.WHITE,
                    border_radius=8,
                    padding=ft.Padding.all(8),
                    border_side=ft.BorderSide(color="#E2E8F0", width=1),
                ),
            ),
            expand=True,
            padding=ft.Padding.only(top=10)
        )