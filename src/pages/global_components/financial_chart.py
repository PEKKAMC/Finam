# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import datetime

import flet as ft
import flet_charts as fc

from src.database import db
from src.logger import Logger
from src.utils import Color, Text, UISettings

Logger.info("Building financial chart...")


def get_financial_chart_data(username: str, chart_type: str = "daily", date_offset: int = 0, target_year: int | None = None) -> tuple[dict, list]:
    """Fetches expenses and incomes directly from the database and structures data for the requested period and mode."""
    now = datetime.datetime.now()

    if chart_type == "daily":
        target_date = now + datetime.timedelta(weeks=date_offset)
    elif chart_type == "weekly":
        total_months = (now.year * 12 + (now.month - 1)) + date_offset
        year = total_months // 12
        month = (total_months % 12) + 1
        target_date = now.replace(year=year, month=month, day=1)
    elif chart_type == "monthly":
        tgt_year = target_year if target_year is not None else now.year
        tgt_month = now.month if tgt_year == now.year else 1
        target_date = now.replace(year=tgt_year, month=tgt_month, day=1)
    else:
        target_date = now

    iso_year, iso_week, _ = target_date.isocalendar()
    chart_date = {"month": target_date.month, "year": target_date.year, "week": iso_week}

    if chart_type == "daily":
        chart_data = [{"day": i + 1, "income": 0, "expense": 0} for i in range(7)]
    elif chart_type == "weekly":
        chart_data = [{"week": i + 1, "income": 0, "expense": 0} for i in range(4)]
    elif chart_type == "monthly":
        chart_data = [{"month": i + 1, "income": 0, "expense": 0} for i in range(12)]
    else:
        chart_data = []

    start_of_week = target_date - datetime.timedelta(days=target_date.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

    expenses = db.spending.get_user_expenses(username) or []
    incomes = db.spending.get_user_incomes(username) or []

    try:
        for expense in expenses:
            try:
                exp_date = datetime.datetime.strptime(str(expense["date"])[:16], "%Y-%m-%d %H:%M")
                amount = int(expense.get("amount", 0))
                if chart_type == "daily" and start_of_week <= exp_date <= end_of_week:
                    chart_data[exp_date.weekday()]["expense"] += amount
                elif chart_type == "weekly" and exp_date.year == target_date.year and exp_date.month == target_date.month:
                    week_of_month = min((exp_date.day - 1) // 7, 3)
                    chart_data[week_of_month]["expense"] += amount
                elif chart_type == "monthly" and exp_date.year == target_date.year:
                    chart_data[exp_date.month - 1]["expense"] += amount
            except (ValueError, TypeError):
                pass

        for income in incomes:
            try:
                inc_date = datetime.datetime.strptime(str(income["date"])[:16], "%Y-%m-%d %H:%M")
                amount = int(income.get("amount", 0))
                if chart_type == "daily" and start_of_week <= inc_date <= end_of_week:
                    chart_data[inc_date.weekday()]["income"] += amount
                elif chart_type == "weekly" and inc_date.year == target_date.year and inc_date.month == target_date.month:
                    week_of_month = min((inc_date.day - 1) // 7, 3)
                    chart_data[week_of_month]["income"] += amount
                elif chart_type == "monthly" and inc_date.year == target_date.year:
                    chart_data[inc_date.month - 1]["income"] += amount
            except (ValueError, TypeError):
                pass
    except Exception as e:
        Logger.error(f"Error formatting dashboard chart data: {e}")

    return chart_date, chart_data


class FinancialChart(ft.Container):
    def __init__(self, lang: dict, username: str, chart_type: str, show_mode_buttons: bool):
        self.lang = lang
        self.username = username
        self.chart_type = chart_type
        self.show_mode_buttons = show_mode_buttons

        now = datetime.datetime.now()
        self.real_current_year = now.year
        self.real_current_month = now.month
        self.real_current_page = 0 if self.real_current_month <= 6 else 1

        # State tracking for date navigation
        self.date_offset = 0
        self.monthly_year = self.real_current_year

        self.chart_date, self.chart_data = get_financial_chart_data(
            username=self.username,
            chart_type=self.chart_type,
            date_offset=self.date_offset,
            target_year=self.monthly_year
        )

        month_val = self.chart_date.get("month", self.real_current_month)
        self.monthly_page = 0 if month_val <= 6 else 1

        max_chart_value = (
            max(max(int(data["income"]), int(data["expense"])) for data in self.chart_data)
            if self.chart_data
            else 1
        )
        self.max_value = max_chart_value if max_chart_value > 0 else 1

        controls = []
        if self.show_mode_buttons:
            controls.append(self.build_mode_buttons())

        controls.extend([
            self.build_legend(),
            self.build_bar_chart()
        ])

        self.main_container = ft.Column(
            spacing=12,
            controls=controls
        )

        container_height = 310 if self.show_mode_buttons else 275

        super().__init__(
            expand=True,
            height=container_height,
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.main_container
        )

    @property
    def can_go_next(self) -> bool:
        """Determines if navigating forward is allowed (upper bound = present period)."""
        if self.chart_type == "monthly":
            if self.monthly_year < self.real_current_year:
                return True
            if self.monthly_year == self.real_current_year and self.monthly_page < self.real_current_page:
                return True
            return False
        else:
            return self.date_offset < 0

    @property
    def can_go_prev(self) -> bool:
        """Allows unlimited past period navigation across all modes."""
        return True

    def update_data(self):
        """Fetches fresh chart data directly and refreshes the UI."""
        self.chart_date, self.chart_data = get_financial_chart_data(
            username=self.username,
            chart_type=self.chart_type,
            date_offset=self.date_offset,
            target_year=self.monthly_year if self.chart_type == "monthly" else None
        )
        max_chart_value = (
            max(max(int(data["income"]), int(data["expense"])) for data in self.chart_data)
            if self.chart_data
            else 1
        )
        self.max_value = max_chart_value if max_chart_value > 0 else 1
        self._refresh_ui()

    def _handle_mode_change(self, mode: str):
        """Handles internal mode switching (daily, weekly, monthly)."""
        if self.chart_type == mode:
            return
        self.chart_type = mode
        self.date_offset = 0
        self.monthly_year = self.real_current_year
        self.monthly_page = 0 if self.real_current_month <= 6 else 1

        self.update_data()

    def _handle_prev(self):
        """Navigates to the previous period."""
        if self.chart_type == "monthly":
            if self.monthly_page == 1:
                self.monthly_page = 0
            else:
                self.monthly_page = 1
                self.monthly_year -= 1
        else:
            self.date_offset -= 1

        self.update_data()

    def _handle_next(self):
        """Navigates to the next period if within upper limit bounds."""
        if not self.can_go_next:
            return

        if self.chart_type == "monthly":
            if self.monthly_page == 0:
                self.monthly_page = 1
            else:
                self.monthly_page = 0
                self.monthly_year += 1
        else:
            self.date_offset += 1

        self.update_data()

    def _refresh_ui(self):
        controls = []
        if self.show_mode_buttons:
            controls.append(self.build_mode_buttons())
        controls.extend([
            self.build_legend(),
            self.build_bar_chart()
        ])
        self.main_container.controls = controls
        self.update()

    def build_mode_buttons(self):
        modes = [
            ("daily", self.lang["financial_chart.daily"]),
            ("weekly", self.lang["financial_chart.weekly"]),
            ("monthly", self.lang["financial_chart.monthly"])
        ]

        buttons = []
        for mode_key, mode_label in modes:
            is_active = self.chart_type == mode_key
            buttons.append(
                ft.Container(
                    content=Text.LABEL(
                        mode_label,
                        color=Color.WHITE if is_active else Color.PRIMARY,
                    ),
                    bgcolor=Color.PRIMARY if is_active else Color.LIGHT_ACCENT,
                    border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    on_click=lambda _, m=mode_key: self._handle_mode_change(m),
                    ink=True
                )
            )

        return ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
            controls=buttons
        )

    def build_legend(self):
        match self.chart_type:
            case "daily":
                date_text = f"{self.lang['generic.week']} {self.chart_date.get('week', '')}, {self.chart_date.get('month', '')}/{self.chart_date.get('year', '')}"
            case "weekly":
                date_text = f"{self.chart_date.get('month', '')}/{self.chart_date.get('year', '')}"
            case "monthly":
                period_str = "1 - 6" if self.monthly_page == 0 else "7 - 12"
                month_label = self.lang['generic.month']
                date_text = f"{self.monthly_year} ({month_label} {period_str})"
            case _:
                date_text = ""
                Logger.error("Unknown chart type")

        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.BAR_CHART, color=Color.PRIMARY, size=16),
                            width=32,
                            height=32,
                            bgcolor=Color.LIGHT_ACCENT,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                Text.H6(self.lang["financial_chart.chart_title"], color=Color.DEFAULT_TEXT),
                                Text.SMALL(date_text, color=Color.SECONDARY_TEXT)
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
                                ft.Container(width=10, height=10, bgcolor=Color.PRIMARY, border_radius=5),
                                Text.LABEL(self.lang["generic.income"], color=Color.PRIMARY),
                            ]
                        ),
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=Color.EXPENSE_ACTION_BACKGROUND, border_radius=5),
                                Text.LABEL(self.lang["generic.expense"], color=Color.EXPENSE_ACTION_BACKGROUND),
                            ]
                        )
                    ]
                )
            ]
        )

    def _generate_y_axis_labels(self):
        step = self.max_value / 4
        labels = []
        for i in range(5):
            value = int(i * step)
            labels.append(
                fc.ChartAxisLabel(
                    value=value,
                    label=Text.LABEL(f"{value // 1000}K", color=Color.SECONDARY_TEXT)
                )
            )
        return labels

    def _build_single_chart(self, chart_data_subset, start_index=0):
        chart_label = []
        groups = []
        bar_size = 18

        for index, data in enumerate(chart_data_subset):
            actual_index = start_index + index

            match self.chart_type:
                case "daily":
                    days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
                    label_text = days[actual_index] if actual_index < len(days) else ""
                case "weekly":
                    label_text = f"{self.lang['generic.week']} {data.get('week', index+1)}"
                case "monthly":
                    label_text = f"{self.lang['generic.month']} {data.get('month', actual_index+1)}"
                case _:
                    label_text = ""
                    Logger.error("Unknown chart type")

            chart_label.append(
                fc.ChartAxisLabel(
                    value=index,
                    label=ft.Container(
                        Text.LABEL(label_text, color=Color.SECONDARY_TEXT),
                        padding=ft.Padding.only(top=10)
                    )
                )
            )

            income_value = int(data.get("income", 0))
            expense_value = int(data.get("expense", 0))

            groups.append(
                fc.BarChartGroup(
                    x=index,
                    rods=[
                        fc.BarChartRod(
                            from_y=0,
                            to_y=income_value,
                            width=bar_size,
                            color=Color.PRIMARY,
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang['generic.income']}: {income_value:,} đ"
                            ),
                        ),
                        fc.BarChartRod(
                            from_y=0,
                            to_y=expense_value,
                            width=bar_size,
                            color=Color.EXPENSE_ACTION_BACKGROUND,
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang['generic.expense']}: {expense_value:,} đ"
                            ),
                        )
                    ]
                )
            )

        return ft.Container(
            content=ft.Container(
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
                        border_side=ft.BorderSide(color=Color.DEFAULT_BORDER, width=1),
                    ),
                ),
                expand=True,
                padding=ft.Padding.only(top=10)
            ),
            expand=True,
            padding=ft.Padding.only(top=10)
        )

    def build_bar_chart(self):
        if self.chart_type == "monthly":
            data_subset = self.chart_data[:6] if self.monthly_page == 0 else self.chart_data[6:12]
            start_index = 0 if self.monthly_page == 0 else 6
            chart = self._build_single_chart(data_subset, start_index=start_index)
        else:
            chart = self._build_single_chart(self.chart_data, start_index=0)

        prev_enabled = self.can_go_prev
        next_enabled = self.can_go_next

        prev_btn = ft.IconButton(
            width=28,
            height=28,
            padding=0,
            icon=ft.Icons.CHEVRON_LEFT,
            icon_size=18,
            icon_color=Color.PRIMARY if prev_enabled else Color.SECONDARY_TEXT,
            disabled=not prev_enabled,
            on_click=lambda _: self._handle_prev(),
            tooltip="Previous"
        )
        next_btn = ft.IconButton(
            width=28,
            height=28,
            padding=0,
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_size=18,
            icon_color=Color.PRIMARY if next_enabled else Color.SECONDARY_TEXT,
            disabled=not next_enabled,
            on_click=lambda _: self._handle_next(),
            tooltip="Next"
        )

        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                prev_btn,
                ft.Container(content=chart, expand=True),
                next_btn,
            ]
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width