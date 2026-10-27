# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
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
        chart_data = [{"day": i + 1, "income": 0.0, "expense": 0.0} for i in range(7)]
    elif chart_type == "weekly":
        chart_data = [{"week": i + 1, "income": 0.0, "expense": 0.0} for i in range(4)]
    elif chart_type == "monthly":
        chart_data = [{"month": i + 1, "income": 0.0, "expense": 0.0} for i in range(12)]
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
                amount = float(expense.get("amount", 0))
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
                amount = float(income.get("amount", 0))
                if chart_type == "daily" and start_of_week <= inc_date <= end_of_week:
                    chart_data[inc_date.weekday()]["income"] += amount
                elif chart_type == "weekly" and inc_date.year == target_date.year and inc_date.month == target_date.month:
                    week_of_month = min((inc_date.day - 1) // 7, 3)
                    chart_data[week_of_month]["income"] += amount
                elif chart_type == "monthly" and inc_date.year == target_date.year:
                    chart_data[inc_date.month - 1]["income"] += amount
            except (ValueError, TypeError):
                pass
    except Exception as ex:
        Logger.error(f"Error formatting dashboard chart data: {ex}")

    return chart_date, chart_data


class FinancialChart(ft.Container):
    def __init__(self, lang: dict, username: str, chart_type: str, show_mode_buttons: bool):
        self.lang = lang
        self.username = username
        self.currency = db.users.get_currency(username)
        self.chart_type = chart_type
        self.show_mode_buttons = show_mode_buttons

        now = datetime.datetime.now()
        self.real_current_year = now.year
        self.real_current_month = now.month
        self.real_current_page = 0 if self.real_current_month <= 6 else 1

        # State tracking for date navigation
        self.date_offset = 0
        self.monthly_year = self.real_current_year

        temp_date, _ = get_financial_chart_data(username=self.username, chart_type="monthly", target_year=self.monthly_year)
        month_val = temp_date.get("month", self.real_current_month)
        self.monthly_page = 0 if month_val <= 6 else 1

        self.total_pan_x = 0.0
        self.is_dragging = False
        self.prev_container = None
        self.curr_container = None
        self.next_container = None
        self.chart_width = 380
        self.drag_sensitivity = 4

        self._load_all_periods_data()

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
            bgcolor=Color.CARD_BACKGROUND,
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
        return self.date_offset < 0

    @property
    def can_go_prev(self) -> bool:
        """Allows unlimited past period navigation across all modes."""
        return True

    def _schedule_after_drag(self, callback, *args):
        """Schedule the async drag completion/cleanup on the active event loop."""
        if self.page:
            self.page.run_task(callback, *args)
            return

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(callback(*args))
            return
        except RuntimeError:
            pass

        try:
            asyncio.run(callback(*args))
        except TypeError:
            callback(*args)

    def _prepare_containers_for_animation(self):
        """Makes adjacent charts visible and resets offsets before starting an animation."""
        self.is_dragging = True

        if self.prev_container:
            self.prev_container.visible = self.can_go_prev
            self.prev_container.animate_offset = None
            self.prev_container.offset = ft.Offset(-1.0, 0.0)
            self.prev_container.update()

        if self.curr_container:
            self.curr_container.animate_offset = None
            self.curr_container.offset = ft.Offset(0.0, 0.0)
            self.curr_container.update()

        if self.next_container:
            self.next_container.visible = self.can_go_next
            self.next_container.animate_offset = None
            self.next_container.offset = ft.Offset(1.0, 0.0)
            self.next_container.update()

    def _handle_pan_start(self, e: ft.DragStartEvent) -> ft.DragStartEvent:
        """Resets accumulated drag distance and makes adjacent charts visible for dragging."""
        self.total_pan_x = 0.0
        self._prepare_containers_for_animation()
        return e

    def _handle_pan_update(self, e: ft.DragUpdateEvent):
        """Accumulates horizontal delta and updates container offsets for live preview dragging."""
        delta = getattr(e, "primary_delta", None)
        if delta is None:
            local_delta = getattr(e, "local_delta", None)
            if local_delta is not None:
                delta = getattr(local_delta, "x", 0)
        if delta is None:
            delta = getattr(e, "delta_x", 0)
        if delta is None and getattr(e, "local_delta", None) is not None:
            delta = getattr(e.local_delta, "x", None)

        if delta is not None and self.curr_container is not None:
            try:
                dx = float(delta)
                if dx == dx and dx != float("inf") and dx != float("-inf"):
                    self.total_pan_x += dx * self.drag_sensitivity
                    w = max(100, self.chart_width)
                    fraction = self.total_pan_x / w

                    if not self.can_go_prev and fraction > 0:
                        fraction = 0.0
                    elif not self.can_go_next and fraction < 0:
                        fraction = 0.0

                    fraction = max(-1.0, min(1.0, fraction))

                    if self.prev_container and self.prev_container.visible:
                        self.prev_container.offset = ft.Offset(-1.0 + fraction, 0.0)
                        self.prev_container.update()

                    if self.curr_container:
                        self.curr_container.offset = ft.Offset(0.0 + fraction, 0.0)
                        self.curr_container.update()

                    if self.next_container and self.next_container.visible:
                        self.next_container.offset = ft.Offset(1.0 + fraction, 0.0)
                        self.next_container.update()
            except Exception as ex:
                Logger.error(f"Error occurred while handling pan update: {ex}")

    def _handle_pan_end(self, e: ft.DragEndEvent) -> ft.DragEndEvent:
        """Triggers smooth animated previous/next navigation or snap-back based on drag threshold."""
        threshold = 35
        direction = "none"

        if self.total_pan_x > threshold and self.can_go_prev:
            direction = "prev"
        elif self.total_pan_x < -threshold and self.can_go_next:
            direction = "next"

        self._schedule_after_drag(self._handle_pan_end_async, direction)

        self.total_pan_x = 0.0
        return e

    async def _handle_pan_end_async(self, direction: str):
        anim = ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_OUT)

        for c in [self.prev_container, self.curr_container, self.next_container]:
            if c and c.visible:
                c.animate_offset = anim
                c.update()

        await asyncio.sleep(0.02)

        if direction == "prev":
            if self.prev_container:
                self.prev_container.offset = ft.Offset(0.0, 0.0)
                self.prev_container.update()
            if self.curr_container:
                self.curr_container.offset = ft.Offset(1.0, 0.0)
                self.curr_container.update()
            if self.next_container and self.next_container.visible:
                self.next_container.offset = ft.Offset(2.0, 0.0)
                self.next_container.update()
        elif direction == "next":
            if self.prev_container and self.prev_container.visible:
                self.prev_container.offset = ft.Offset(-2.0, 0.0)
                self.prev_container.update()
            if self.curr_container:
                self.curr_container.offset = ft.Offset(-1.0, 0.0)
                self.curr_container.update()
            if self.next_container:
                self.next_container.offset = ft.Offset(0.0, 0.0)
                self.next_container.update()
        else:
            if self.prev_container and self.prev_container.visible:
                self.prev_container.offset = ft.Offset(-1.0, 0.0)
                self.prev_container.update()
            if self.curr_container:
                self.curr_container.offset = ft.Offset(0.0, 0.0)
                self.curr_container.update()
            if self.next_container and self.next_container.visible:
                self.next_container.offset = ft.Offset(1.0, 0.0)
                self.next_container.update()

        await asyncio.sleep(0.25)

        if direction == "prev":
            self._apply_prev_state()
            self.update_data()
        elif direction == "next":
            self._apply_next_state()
            self.update_data()
        else:
            self.is_dragging = False
            if self.prev_container:
                self.prev_container.visible = False
                self.prev_container.animate_offset = None
                self.prev_container.offset = ft.Offset(-1.0, 0.0)
                self.prev_container.update()
            if self.curr_container:
                self.curr_container.animate_offset = None
                self.curr_container.offset = ft.Offset(0.0, 0.0)
                self.curr_container.update()
            if self.next_container:
                self.next_container.visible = False
                self.next_container.animate_offset = None
                self.next_container.offset = ft.Offset(1.0, 0.0)
                self.next_container.update()

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
                                ft.Container(width=10, height=10, bgcolor=Color.INCOME_BACKGROUND, border_radius=5),
                                Text.LABEL(self.lang["generic.income"], color=Color.INCOME_COLOR),
                            ]
                        ),
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=Color.EXPENSE_BACKGROUND, border_radius=5),
                                Text.LABEL(self.lang["generic.expense"], color=Color.EXPENSE_COLOR),
                            ]
                        )
                    ]
                )
            ]
        )

    def _generate_y_axis_labels(self):
        max_val = max(1, self.max_value)
        step = max_val / 4.0
        labels = []
        for i in range(5):
            value = i * step
            labels.append(
                fc.ChartAxisLabel(
                    value=float(value),
                    label=Text.LABEL(f"{value / 1000:g}K", color=Color.SECONDARY_TEXT)
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

            income_value = float(data.get("income", 0))
            expense_value = float(data.get("expense", 0))

            groups.append(
                fc.BarChartGroup(
                    x=index,
                    rods=[
                        fc.BarChartRod(
                            from_y=0,
                            to_y=income_value,
                            width=bar_size,
                            color=Color.INCOME_BACKGROUND,
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang['generic.income']}: {income_value:,.2f} {self.currency}"
                            ),
                        ),
                        fc.BarChartRod(
                            from_y=0,
                            to_y=expense_value,
                            width=bar_size,
                            color=Color.EXPENSE_BACKGROUND,
                            border_radius=6,
                            tooltip=fc.BarChartRodTooltip(
                                text=f"{self.lang['generic.expense']}: {expense_value:,.2f} {self.currency}"
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
                        bgcolor=Color.CARD_BACKGROUND,
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
        prev_chart = self._build_single_chart(self.prev_data, start_index=self.prev_start_idx)
        curr_chart = self._build_single_chart(self.curr_data, start_index=self.curr_start_idx)
        next_chart = self._build_single_chart(self.next_data, start_index=self.next_start_idx)

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

        self.prev_container = ft.Container(
            content=prev_chart,
            expand=True,
            visible=self.is_dragging and self.can_go_prev,
            offset=ft.Offset(-1.0, 0.0),
        )
        self.curr_container = ft.Container(
            content=curr_chart,
            expand=True,
            visible=True,
            offset=ft.Offset(0.0, 0.0),
        )
        self.next_container = ft.Container(
            content=next_chart,
            expand=True,
            visible=self.is_dragging and self.can_go_next,
            offset=ft.Offset(1.0, 0.0),
        )

        chart_stack = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            controls=[
                self.prev_container,
                self.curr_container,
                self.next_container,
            ]
        )

        chart_viewport = ft.Stack(
            expand=True,
            controls=[
                chart_stack,
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.TRANSPARENT,
                    content=ft.GestureDetector(
                        expand=True,
                        drag_interval=10,
                        mouse_cursor=ft.MouseCursor.MOVE,
                        on_horizontal_drag_start=self._handle_pan_start,
                        on_horizontal_drag_update=self._handle_pan_update,
                        on_horizontal_drag_end=self._handle_pan_end,
                        on_pan_start=self._handle_pan_start,
                        on_pan_update=self._handle_pan_update,
                        on_pan_end=self._handle_pan_end,
                    )
                )
            ]
        )

        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                prev_btn,
                ft.Container(content=chart_viewport, expand=True),
                next_btn,
            ]
        )

    def resize(self, width: int) -> None:
        self.chart_width = width
        self.main_container.width = width

    def _load_all_periods_data(self):
        """Fetches data for previous, current, and next periods to enable live drag previews."""
        curr_offset = 0 if self.chart_type == "monthly" else self.date_offset
        self.chart_date, self.curr_data, self.curr_start_idx = self._get_period_data(
            self.chart_type, curr_offset, self.monthly_year, self.monthly_page
        )

        prev_offset, prev_year, prev_page = self._get_prev_coords()
        _, self.prev_data, self.prev_start_idx = self._get_period_data(
            self.chart_type, prev_offset, prev_year, prev_page
        )

        next_offset, next_year, next_page = self._get_next_coords()
        _, self.next_data, self.next_start_idx = self._get_period_data(
            self.chart_type, next_offset, next_year, next_page
        )

        all_data = self.prev_data + self.curr_data + self.next_data
        max_chart_value = (
            max(max(float(d["income"]), float(d["expense"])) for d in all_data)
            if all_data
            else 1
        )
        self.max_value = max_chart_value if max_chart_value > 0 else 1

    def update_data(self):
        """Fetches fresh chart data for all three periods and refreshes the UI."""
        self.is_dragging = False
        self._load_all_periods_data()
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

    def _apply_prev_state(self):
        if self.chart_type == "monthly":
            if self.monthly_page == 1:
                self.monthly_page = 0
            else:
                self.monthly_page = 1
                self.monthly_year -= 1
        else:
            self.date_offset -= 1

    def _apply_next_state(self):
        if self.chart_type == "monthly":
            if self.monthly_page == 0:
                self.monthly_page = 1
            else:
                self.monthly_page = 0
                self.monthly_year += 1
        else:
            self.date_offset += 1

    def _handle_prev(self):
        """Navigates to the previous period with animation."""
        if not self.can_go_prev:
            return
        self._prepare_containers_for_animation()
        self._schedule_after_drag(self._handle_pan_end_async, "prev")

    def _handle_next(self):
        """Navigates to the next period with animation if within upper limit bounds."""
        if not self.can_go_next:
            return
        self._prepare_containers_for_animation()
        self._schedule_after_drag(self._handle_pan_end_async, "next")


    def _get_prev_coords(self):
        """Returns the coordinates for the previous period used in the chart stack."""
        if self.chart_type == "monthly":
            if self.monthly_page == 0:
                return 0, self.monthly_year - 1, 1
            return 0, self.monthly_year, 0
        return self.date_offset - 1, None, None

    def _get_next_coords(self):
        """Returns the coordinates for the next period used in the chart stack."""
        if self.chart_type == "monthly":
            if self.monthly_page == 0:
                return 0, self.monthly_year, 1
            return 0, self.monthly_year + 1, 0
        return self.date_offset + 1, None, None

    def _get_period_data(self, chart_type: str, date_offset: int, target_year: int | None = None, page: int | None = None):
        """Loads chart data for a designated period and slices the monthly view to the proper half-year."""
        chart_date, chart_data = get_financial_chart_data(
            username=self.username,
            chart_type=chart_type,
            date_offset=date_offset,
            target_year=target_year,
        )

        if chart_type == "monthly":
            if page == 1:
                return chart_date, chart_data[6:12], 6
            return chart_date, chart_data[0:6], 0

        return chart_date, chart_data, 0