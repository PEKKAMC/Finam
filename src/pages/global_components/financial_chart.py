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
            height=UISettings.CHART_HEIGHT,
            bgcolor=Color.WHITE,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Column(
                spacing=10,
                controls=[
                    self.build_legend(),
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                self.build_bar_chart(),
                                self.build_line_chart()
                            ],
                            expand=True
                        ),
                        expand=True,
                        padding=ft.Padding.only(top=30)
                    )
                ]
            )
        )

    def build_legend(self):
        Logger.info("Building chart legend...")

        match self.chart_type:
            case "daily":
                date_text = f"{self.lang["generic.week"]} {self.chart_date["week"]}, {self.chart_date["month"]}/{self.chart_date["year"]}"
            case "weekly":
                date_text = f"{self.chart_date["month"]}/{self.chart_date["year"]}"
            case "monthly":
                date_text = f"{self.chart_date["year"]}"
            case _:
                date_text = ""
                Logger.error("Unknown chart type")

        legend = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=Color.CHART_INCOME, shape=ft.BoxShape.CIRCLE),
                    Text.SMALL(self.lang["generic.income"], color=Color.BLAND_TEXT),
                    ft.Container(width=12, height=12, bgcolor=Color.CHART_EXPENSE, shape=ft.BoxShape.CIRCLE, margin=ft.Margin(left=10, top=0, right=0, bottom=0)),
                    Text.SMALL(self.lang["generic.expense"], color=Color.BLAND_TEXT),
                ]),
                ft.Row([
                    Text.SMALL(
                        date_text,
                        color=Color.DEFAULT_TEXT,
                    )
                ])
            ]
        )

        return legend
    def build_bar_chart(self):
        Logger.info("Building bar chart...")
        match self.chart_type:
            case "daily":
                chart_label = [
                    fc.ChartAxisLabel(
                        value=index,
                        label=ft.Container(
                            Text.SMALL(f"{["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][index]}", color=Color.BLAND_TEXT),
                            padding=ft.Padding.only(top=10)
                        )
                    ) for index, data in enumerate(self.chart_data)
                ]
            case "weekly":
                chart_label = [
                    fc.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            Text.SMALL(f"{self.lang["generic.week"]} {d["week"]}", color=Color.BLAND_TEXT),
                            padding=ft.Padding.only(top=10)
                        )
                    ) for i, d in enumerate(self.chart_data)
                ]
            case "monthly":
                chart_label = [
                    fc.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            Text.SMALL(f"{self.lang["generic.month"]} {d["month"]}", color=Color.BLAND_TEXT),
                            padding=ft.Padding.only(top=10)
                        )
                    ) for i, d in enumerate(self.chart_data)
                ]
            case _:
                chart_label = []
                Logger.error("Unknown chart type")

        return fc.BarChart(
            groups=[
                fc.BarChartGroup(
                    x=index,
                    rods=[
                        fc.BarChartRod(
                            from_y=0,
                            to_y=data["income"],
                            width=4,
                            color=Color.CHART_INCOME,
                            bg_to_y=self.max_value,
                            bgcolor=Color.CHART_INACTIVE,
                            border_radius=8,
                            tooltip=f"{self.lang['generic.income']}: {data['income']}\n{self.lang["generic.expense"]}: {data["expense"]}"
                        )
                    ]
                ) for index, data in enumerate(self.chart_data)
            ],
            bottom_axis=fc.ChartAxis(
                labels=chart_label,
                label_size=40,
            ),
            horizontal_grid_lines=fc.ChartGridLines(color=ft.Colors.TRANSPARENT),
            tooltip=fc.BarChartTooltip(bgcolor=Color.DEFAULT_TEXT),
            max_y=self.max_value,
            interactive=True
        )


    def build_line_chart(self):
        Logger.info("Building line chart...")

        return ft.TransparentPointer(fc.LineChart(
            data_series=[
                fc.LineChartData(
                    color=Color.CHART_EXPENSE,
                    stroke_width=3,
                    curved=False,
                    point=fc.ChartCirclePoint(
                        radius=4,
                        color=Color.CHART_EXPENSE,
                        stroke_width=0
                    ),
                    points=[fc.LineChartDataPoint(index, data["expense"]) for index, data in enumerate(self.chart_data)]
                )
            ],
            max_y=self.max_value,
            min_y=0,
            bottom_axis=fc.ChartAxis(
                labels=[
                    fc.ChartAxisLabel(
                        value=index,
                        label=ft.Container()
                    ) for index in range(len(self.chart_data))
                ],
                label_size=40
            ),
            min_x=len(self.chart_data) / 240 - 1,
            max_x=len(self.chart_data) - len(self.chart_data) / 240,
            interactive=False
        ))

