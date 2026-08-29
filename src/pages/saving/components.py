# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Callable

import flet as ft

from src.utils import Color, Text


class ObjectiveCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, objective_id: int, objective_title: str, subtitle: str, current_value: str, target_value: str, remaining_value: str, percentage: str, progress: float, completed: bool, on_click_callback: Callable):
        self._page = page
        self.lang = lang
        self.objective_id = objective_id
        self.objective_title = objective_title
        self.subtitle = subtitle
        self.current_value = current_value
        self.target_value = target_value
        self.remaining_value = remaining_value
        self.percentage = percentage
        self.progress = progress
        self.completed = completed
        self.on_click_callback = on_click_callback
        badge_bg = Color.PROGRESS_ACTIVE if self.completed else Color.LIGHT_ACCENT
        badge_text = Color.WHITE if self.completed else Color.PRIMARY

        on_action = lambda e: self.on_click_callback(e.page, self.objective_id, self.objective_title, self.subtitle, self.current_value, self.target_value, self.progress, self.completed) if self.on_click_callback else None

        self.title_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                Text.H4(self.objective_title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.PROGRESS_ACTIVE, size=18) if self.completed else ft.Container()
                            ]
                        ),
                        Text.MEDIUM(self.subtitle, color=Color.SECONDARY_TEXT),
                    ]
                ),
                ft.Container(
                    content=Text.BADGE(self.percentage, color=badge_text, weight=ft.FontWeight.BOLD),
                    bgcolor=badge_bg,
                    padding=ft.Padding(12, 6, 12, 6),
                    border_radius=16,
                )
            ]
        )

        self.progress_row = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text.MEDIUM("Đã tích lũy", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        Text.H4(self.current_value, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.ProgressBar(value=self.progress, color=Color.PRIMARY, bgcolor=Color.PROGRESS_TRACK_BACKGROUND, height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text.SMALL(f"Mục tiêu: {self.target_value}", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500),
                        Text.SMALL(self.remaining_value, color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)
                    ]
                )
            ]
        )

        self.action_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=Text.MEDIUM("+ Nạp Tiền", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=Color.PRIMARY,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12,
                        ),
                        ft.Container(
                            content=Text.MEDIUM("- Rút Tiền", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12,
                        )
                    ]
                )
            ]
        )
        self.main_container = ft.Column(
            spacing=16,
            controls=[
                self.title_row,
                self.progress_row,
                ft.Divider(color=Color.CARD_DIVIDER, height=1),
                self.action_row
            ]
        )

        super().__init__(
            bgcolor=Color.GOAL_ITEM_BACKGROUND if self.completed else Color.CARD_BACKGROUND,
            border_radius=24,
            padding=24,
            border=ft.Border.all(2, Color.PROGRESS_BACKGROUND) if self.completed else None,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW) if not self.completed else None,
            on_click=on_action,
            ink=True,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class ObjectiveGrid(ft.Column):
    def __init__(self, page: ft.Page, lang: dict, objectives_data: list, on_card_click: Callable):
        self._page = page
        self.lang = lang
        cards = []
        for data in objectives_data:
            cards.append(ObjectiveCard(
                page=self._page,
                lang=self.lang,
                objective_id=data["objective_id"], objective_title=data["title"], subtitle=data["reason"],
                current_value=data["current_value"], target_value=data["target_value"], remaining_value=data["remaining_value"],
                percentage=data["percentage"], progress=data["progress"], completed=data["completed"],
                on_click_callback=on_card_click
            ))
        self.main_container = ft.Column(spacing=20, controls=cards)
        super().__init__(spacing=20, controls=cards)

    def resize(self, width: int) -> None:
        self.main_container.width = width


class AggregateCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, total_savings: float, total_target: float, percentage: str, progress_value: float, on_create_click: Callable):
        self._page = page
        self.lang = lang
        self.main_container = ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    content=Text.MEDIUM("QUẢN LÝ QUỸ TIẾT KIỆM", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                    bgcolor=Color.DARK_SURFACE,
                                    padding=ft.Padding(12, 6, 12, 6),
                                    border_radius=20,
                                    border=ft.Border.all(1, Color.METRIC_PILL_BORDER)
                                ),
                                ft.Row(
                                    vertical_alignment=ft.CrossAxisAlignment.END,
                                    controls=[
                                        Text.H3(f"{int(total_savings):,}".replace(",", "."), color=Color.WHITE, weight=ft.FontWeight.BOLD),
                                        Text.H5(f" / {int(total_target):,}".replace(",", ".") + " đ", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        Text.MEDIUM("Tổng tiến độ tích lũy các mục tiêu đạt", color=Color.WHITE),
                                        Text.MEDIUM(f"{percentage}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                                    ]
                                )
                            ]
                        ),
                        ft.Container(
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.ADD, color=Color.PRIMARY, size=16)
                                ]
                            ),
                            bgcolor=Color.LIGHT_ACCENT,
                            padding=ft.Padding(16, 12, 16, 12),
                            border_radius=16,
                            ink=True,
                            on_click=on_create_click
                        )
                    ]
                ),
                ft.ProgressBar(value=progress_value, color=Color.LIGHT_ACCENT, bgcolor=Color.DARK_SURFACE, height=8, border_radius=4)
            ]
        )
        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=30,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width