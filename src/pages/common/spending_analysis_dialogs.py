# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from datetime import datetime
from typing import Any

import flet as ft

from src.utils import Color, Dialog, Page, Text, format_number, to_decimal


class SpendingMonthDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], on_confirm: Callable[[str], None]) -> None:
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        now = datetime.now()
        self.year = now.year
        self.month = now.month

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.month_selection_title = Text.H4(self.lang["spending.ai_select_month_title"], color=Color.PRIMARY_TEXT)
        self.cancel_button_label = Text.BUTTON(self.lang["generic.cancel"])
        self.confirm_button_label = Text.BUTTON(self.lang["spending.ai_scan_month"], color=Color.WHITE)

        self.month_dropdown = ft.Dropdown(
            label=self.lang["spending.ai_month_label"],
            value=str(self.month),
            options=[],
            on_select=self._on_month_changed,
            menu_height=300
        )

        self.year_dropdown = ft.Dropdown(
            label=self.lang["spending.ai_year_label"],
            value=str(self.year),
            options=[
                ft.dropdown.Option(str(year), str(year))
                for year in range(now.year, now.year - 51, -1)
            ],
            on_select=self._on_year_changed,
            menu_height=300
        )

        self._update_month_options()

        self.main_container = ft.Container(
            padding=20,
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    self.month_selection_title,
                    self.month_dropdown,
                    self.year_dropdown
                ]
            )
        )

        self.cancel_button = ft.TextButton(
            content=self.cancel_button_label,
            on_click=lambda _event: self.dismiss()
        )

        self.confirm_button = ft.Button(
            content=self.confirm_button_label,
            on_click=self._confirm,
            bgcolor=Color.PRIMARY
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[
                self.cancel_button,
                self.confirm_button
            ],
            padding=0
        )

    def resize(self, width: int, content_width: int) -> None:
        self.main_container.width = width
        self.month_dropdown.width = content_width
        self.year_dropdown.width = content_width

    def _on_month_changed(self, _event: ft.ControlEvent | None = None) -> None:
        if self.month_dropdown.value is None:
            return
        self.month = int(self.month_dropdown.value)
        self.month_dropdown.update()

    def _on_year_changed(self, _event: ft.ControlEvent | None = None) -> None:
        if self.year_dropdown.value is None:
            return
        self.year = int(self.year_dropdown.value)
        self._update_month_options()
        self.month_dropdown.value = str(self.month)
        self.month_dropdown.update()

    def _update_month_options(self) -> None:
        latest_month = datetime.now().month if self.year == datetime.now().year else 12
        self.month_dropdown.options = [
            ft.dropdown.Option(
                str(month),
                self.lang[f"spending.ai_month_{month:02d}"]
            )
            for month in range(1, latest_month + 1)
        ]
        self.month = min(self.month, latest_month)

    def trigger(self, _event: ft.ControlEvent | None = None) -> None:
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.year_dropdown.value = str(self.year)
        self._update_month_options()
        self.month_dropdown.value = str(self.month)
        self.show()

    def _confirm(self, _event: ft.ControlEvent | None = None) -> None:
        month = f"{self.year:04d}-{self.month:02d}"
        self.dismiss()
        self.on_confirm(month)


class DeleteSpendingReportDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], on_confirm: Callable[[int], None]) -> None:
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm
        self.report_id: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.confirm_delete_title = Text.H3(self.lang["spending.ai_confirm_delete_title"], color=Color.PRIMARY_TEXT)
        self.confirm_delete_description = Text.P(self.lang["spending.ai_confirm_delete_content"], color=Color.SECONDARY_TEXT)
        self.cancel_button_label = Text.BUTTON(self.lang["generic.cancel"])
        self.delete_button_label = Text.BUTTON(self.lang["generic.delete"], color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.main_container = ft.Container(
            padding=20,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    self.confirm_delete_title,
                    self.confirm_delete_description
                ]
            )
        )

        self.cancel_button = ft.TextButton(
            content=self.cancel_button_label,
            on_click=lambda _event: self.dismiss()
        )

        self.delete_button = ft.Button(
            content=self.delete_button_label,
            on_click=self._confirm,
            bgcolor=Color.DELETE_ACTION
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            options=[
                self.cancel_button,
                self.delete_button
            ],
            padding=0
        )

    def resize(self, width: int, content_width: int) -> None:
        self.main_container.width = width
        if isinstance(self.main_container.content, ft.Column):
            self.main_container.content.width = content_width

    def trigger(self, report_id: int | None) -> None:
        if report_id is None:
            return
        self.report_id = report_id
        self.show()

    def _confirm(self, _event: ft.ControlEvent | None = None) -> None:
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
        "spending_actions"
    )

    def __init__(self, page: Page, lang: dict[str, str], on_delete: Callable[[int], None]) -> None:
        self._page = page
        self.lang = lang
        self.on_delete = on_delete
        self.report_id: int | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H4(self.lang["spending.ai_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD, expand=True)

        # Dynamic texts
        self.updated_text = Text.SMALL("", color=Color.SECONDARY_TEXT)
        self.error_text = Text.MEDIUM("", color=Color.NEGATIVE_ACTION, text_align=ft.TextAlign.CENTER)
        self.loading_text = Text.MEDIUM(self.lang["spending.ai_waiting"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)

        # CONTAINER COMPONENTS
        self.loading_content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.ProgressRing(color=Color.PRIMARY, width=42, height=42),
                self.loading_text
            ]
        )

        self.report_content = ft.Column(spacing=12)

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
            tooltip=self.lang["spending.ai_delete_report"]
        )

        close_button = ft.IconButton(
            ft.Icons.CLOSE,
            on_click=lambda _event: self.dismiss(),
            icon_color=Color.PRIMARY_TEXT,
            tooltip=self.lang["generic.close"]
        )

        self.main_container = ft.Container(
            padding=20,
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
                                        content=ft.Icon(
                                            ft.Icons.AUTO_AWESOME,
                                            color=Color.WHITE,
                                            size=16
                                        ),
                                        bgcolor=Color.DARK_SURFACE,
                                        width=30,
                                        height=30,
                                        border_radius=10,
                                        alignment=ft.Alignment.CENTER
                                    ),
                                    self.title_text
                                ]
                            ),
                            ft.Row(
                                tight=True,
                                spacing=0,
                                controls=[self.delete_button, close_button]
                            )
                        ]
                    ),
                    self.updated_text,
                    self.body
                ]
            )
        )
        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND,
            padding=0
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
            content=self.error_text
        )
        self.error_text.value = message
        self.show()
        self.update()

    def show_report(self, report: dict[str, Any], created_at: str, report_id: int | None = None) -> None:
        self.report_id = report_id
        self.delete_button.visible = report_id is not None
        self.updated_text.value = self.lang["spending.ai_updated"].format(
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
                            content=self._make_section_card(
                                3, "top_income_source", sec3
                            )
                        ),
                        ft.Container(
                            col={"xs": 12, "sm": 6},
                            content=self._make_section_card(4, "largest_expense", sec4)
                        )
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

    def _request_delete(self, _event: ft.ControlEvent | None = None) -> None:
        if self.report_id is not None:
            self.on_delete(self.report_id)

    def _make_section_card(self, index: int, key: str, data: Any) -> ft.Container:
        title = self.lang[f"spending.ai_section_{index}"]
        section = data if isinstance(data, dict) else {}
        section_number_text = Text.SMALL(
            str(index),
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )
        section_title_text = Text.MEDIUM(
            title,
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD,
            expand=True
        )

        top_header_row = ft.Row(
            controls=[
                ft.Container(
                    width=28,
                    height=28,
                    alignment=ft.Alignment.CENTER,
                    border_radius=9,
                    bgcolor=Color.DARK_SURFACE,
                    content=section_number_text
                ),
                section_title_text
            ]
        )

        card_content_items: list[ft.Control] = [top_header_row]

        if key in ("savings_advice", "spending_actions"):
            raw_items = (
                data
                if isinstance(data, list)
                else (data.get("items", []) if isinstance(data, dict) else [])
            )
            items = (
                [advice for advice in raw_items if isinstance(advice, dict)]
                if isinstance(raw_items, list)
                else []
            )
            for idx, advice in enumerate(items, start=1):
                advice_index_text = Text.SMALL(
                    str(idx),
                    color=Color.WHITE
                    if key == "savings_advice"
                    else Color.WARNING_COLOR,
                    weight=ft.FontWeight.BOLD
                )
                advice_title_text = Text.MEDIUM(
                    str(advice.get("title", "")),
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD,
                    expand=True
                )
                advice_description_text = Text.SMALL(
                    str(advice.get("description", "")),
                    color=Color.SECONDARY_TEXT
                )
                advice_outcome_text = Text.MEDIUM(
                    str(advice.get("outcome", "")),
                    color=Color.WARNING_COLOR
                    if key == "spending_actions"
                    else Color.LIGHT_ACCENT,
                    weight=ft.FontWeight.BOLD,
                    expand=True
                )
                card_content_items.append(
                    ft.Container(
                        padding=14,
                        border_radius=14,
                        bgcolor=Color.CARD_BACKGROUND,
                        border=ft.Border.all(
                            1,
                            Color.GOAL_ITEM_BORDER
                        ),
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
                                            bgcolor=Color.DARK_SURFACE
                                            if key == "savings_advice"
                                            else Color.WARNING_BACKGROUND,
                                            alignment=ft.Alignment.CENTER,
                                            content=advice_index_text
                                        ),
                                        advice_title_text
                                    ]
                                ),
                                advice_description_text,
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.BOLT
                                            if key == "spending_actions"
                                            else ft.Icons.VERIFIED_OUTLINED,
                                            color=Color.WARNING_COLOR
                                            if key == "spending_actions"
                                            else Color.PRIMARY,
                                            size=16
                                        ),
                                        advice_outcome_text
                                    ]
                                )
                            ]
                        )
                    )
                )
        elif key == "monthly_overview" and "income" in section:
            month_name_text = Text.SMALL(
                str(section.get("month", "")),
                color=Color.SECONDARY_TEXT
            )
            card_content_items.append(
                month_name_text
            )
            expenses = to_decimal(section.get("expenses", 0))
            income = to_decimal(section.get("income", 0))
            expenses_val = format_number(expenses)
            income_val = format_number(income)
            currency = str(section.get("currency", "đ"))
            total_expenses_label = Text.SMALL(
                self.lang["spending.ai_month_total_expenses"].upper(),
                color=Color.SECONDARY_TEXT,
                weight=ft.FontWeight.BOLD
            )
            total_expenses_value = Text.H3(
                f"-{expenses_val} {currency}".strip(),
                color=Color.EXPENSE_COLOR,
                weight=ft.FontWeight.BOLD
            )
            total_income_label = Text.SMALL(
                self.lang["spending.ai_month_total_income"].upper(),
                color=Color.SECONDARY_TEXT,
                weight=ft.FontWeight.BOLD
            )
            total_income_value = Text.H3(
                f"+{income_val} {currency}".strip(),
                color=Color.INCOME_COLOR,
                weight=ft.FontWeight.BOLD
            )

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
                            controls=[total_expenses_label, total_expenses_value]
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
                            controls=[total_income_label, total_income_value]
                        )
                    )
                ]
            )
            card_content_items.append(overview_row)

            net_bal = format_number(to_decimal(section.get("net_balance", 0)))
            net_balance_label = Text.MEDIUM(
                self.lang["spending.net_balance"],
                color=Color.SECONDARY_TEXT,
                expand=True
            )
            net_balance_value = Text.MEDIUM(
                f"{net_bal} {currency}".strip(),
                color=Color.EXPENSE_COLOR,
                weight=ft.FontWeight.BOLD,
                expand=True
            )
            card_content_items.append(
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor=Color.CARD_BACKGROUND,
                    border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.WARNING_AMBER_ROUNDED,
                                color=Color.EXPENSE_COLOR,
                                size=18,
                                visible=expenses > income
                            ),
                            net_balance_label,
                            net_balance_value
                        ]
                    )
                )
            )
        elif key in ("top_income_source", "largest_expense"):
            is_income = key == "top_income_source"
            amount_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR
            badge_bg = (
                Color.INCOME_BACKGROUND if is_income else Color.EXPENSE_BACKGROUND
            )
            badge_color = Color.INCOME_COLOR if is_income else Color.EXPENSE_COLOR

            headline_text = Text.MEDIUM(
                str(section.get("headline", "")),
                color=Color.PRIMARY_TEXT,
                weight=ft.FontWeight.BOLD
            )
            card_content_items.append(headline_text)
            metric_str = str(section.get("metric", ""))
            metric_text = Text.H3(
                metric_str,
                color=amount_color,
                weight=ft.FontWeight.BOLD
            )
            card_content_items.append(metric_text)
            summary_str = str(section.get("summary", ""))
            if summary_str:
                summary_text = Text.SMALL(
                    summary_str,
                    color=badge_color,
                    weight=ft.FontWeight.BOLD
                )
                card_content_items.append(
                    ft.Container(
                        content=summary_text,
                        bgcolor=badge_bg,
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=8,
                        alignment=ft.Alignment.CENTER
                    )
                )
            details_text = Text.SMALL(
                str(section.get("details", "")),
                color=Color.SECONDARY_TEXT
            )
            card_content_items.append(details_text)
        elif key == "spending_trends":
            trend_headline_text = Text.MEDIUM(
                str(section.get("headline", "")),
                color=Color.PRIMARY_TEXT,
                weight=ft.FontWeight.BOLD
            )
            card_content_items.append(trend_headline_text)
            trend_summary_text = Text.SMALL(
                str(section.get("summary", "")),
                color=Color.SECONDARY_TEXT
            )
            card_content_items.append(trend_summary_text)
            data_clarification = str(section.get("data_clarification") or "").strip()
            if data_clarification:
                clarification_title = Text.SMALL(
                    self.lang["spending.ai_data_clarification"],
                    color=Color.WARNING_COLOR,
                    weight=ft.FontWeight.BOLD
                )
                clarification_text = Text.SMALL(
                    data_clarification,
                    color=Color.PRIMARY_TEXT
                )
                card_content_items.append(
                    ft.Container(
                        padding=12,
                        border_radius=12,
                        bgcolor=Color.WARNING_BACKGROUND,
                        border=ft.Border.all(1, Color.WARNING_COLOR),
                        content=ft.Column(
                            spacing=6,
                            controls=[clarification_title, clarification_text]
                        )
                    )
                )
            details_str = str(section.get("details", ""))
            if details_str:
                trend_details_text = Text.MEDIUM(
                    details_str,
                    color=Color.PRIMARY_TEXT,
                    weight=ft.FontWeight.BOLD
                )
                card_content_items.append(
                    ft.Container(
                        padding=12,
                        border_radius=12,
                        bgcolor=Color.CARD_BACKGROUND,
                        border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                        content=trend_details_text
                    )
                )
        else:
            section_headline_text = Text.MEDIUM(
                str(section.get("headline", "")),
                color=Color.PRIMARY_TEXT,
                weight=ft.FontWeight.BOLD
            )
            card_content_items.append(section_headline_text)
            section_summary_text = Text.SMALL(
                str(section.get("summary", "")),
                color=Color.SECONDARY_TEXT
            )
            card_content_items.append(section_summary_text)
            section_details_text = Text.SMALL(
                str(section.get("details", "")),
                color=Color.SECONDARY_TEXT
            )
            card_content_items.append(section_details_text)
            metric = section.get("metric")
            if metric:
                metric_text = Text.MEDIUM(
                    str(metric),
                    color=Color.PRIMARY,
                    weight=ft.FontWeight.BOLD
                )
                card_content_items.append(
                    ft.Container(
                        padding=ft.Padding(10, 8, 10, 8),
                        border_radius=12,
                        bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
                        content=metric_text
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
                controls=card_content_items
            )
        )

    def resize(self, dialog_width: int, report_card_width: int) -> None:
        self.main_container.width = dialog_width
        self.report_card_width = report_card_width
        for card in self.report_content.controls:
            if isinstance(card, ft.Container):
                card.width = report_card_width
            elif isinstance(card, ft.ResponsiveRow):
                card.width = report_card_width
