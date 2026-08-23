# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Callable

import flet as ft

from src.utils import Color, Text


class ObjectiveCard(ft.Container):
    def __init__(self, objective_id: int, objective_title: str, subtitle: str, current_value: str, target_value: str, remaining_value: str, percentage: str, progress: float, completed: bool, on_click_callback: Callable):
        badge_bg = Color.PROGRESS_ACTIVE if completed else Color.LIGHT_ACCENT
        badge_text = Color.WHITE if completed else Color.PRIMARY

        on_action = lambda e: on_click_callback(e.page, objective_id, objective_title, subtitle, current_value, target_value, progress, completed)

        super().__init__(
            bgcolor=Color.GOAL_ITEM_BACKGROUND if completed else Color.CARD_BACKGROUND,
            border_radius=24,
            padding=24,
            border=ft.Border.all(2, Color.PROGRESS_BACKGROUND) if completed else None,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW) if not completed else None,
            on_click=on_action,
            ink=True
        )

        title_row = ft.Row(
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
                                Text.H4(objective_title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=Color.PROGRESS_ACTIVE, size=18) if completed else ft.Container()
                            ]
                        ),
                        Text.LABEL(subtitle, color=Color.SECONDARY_TEXT),
                    ]
                ),
                ft.Container(
                    content=Text.BADGE(percentage, color=badge_text, weight=ft.FontWeight.BOLD),
                    bgcolor=badge_bg,
                    padding=ft.Padding(12, 6, 12, 6),
                    border_radius=16,
                )
            ]
        )

        progress_row = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text.LABEL("Đã tích lũy", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        Text.H4(current_value, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.ProgressBar(value=progress, color=Color.PRIMARY, bgcolor=Color.PROGRESS_TRACK_BACKGROUND, height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text.SMALL(f"Mục tiêu: {target_value}", color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500),
                        Text.SMALL(remaining_value, color=Color.SECONDARY_TEXT, weight=ft.FontWeight.W_500)
                    ]
                )
            ]
        )

        action_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=Text.LABEL("+ Nạp Tiền", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=Color.PRIMARY,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12,
                        ),
                        ft.Container(
                            content=Text.LABEL("- Rút Tiền", color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                            bgcolor=Color.DEFAULT_CONTAINER_BACKGROUND,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12,
                        )
                    ]
                )
            ]
        )

        self.content = ft.Column(
            spacing=16,
            controls=[
                title_row,
                progress_row,
                ft.Divider(color=Color.CARD_DIVIDER, height=1),
                action_row
            ]
        )


class ObjectiveGrid(ft.Column):
    def __init__(self, objectives_data: list, on_card_click: Callable):
        cards = []
        for data in objectives_data:
            cards.append(ObjectiveCard(
                objective_id=data["objective_id"], objective_title=data["title"], subtitle=data["reason"],
                current_value=data["current_value"], target_value=data["target_value"], remaining_value=data["remaining_value"],
                percentage=data["percentage"], progress=data["progress"], completed=data["completed"],
                on_click_callback=on_card_click
            ))
        super().__init__(spacing=20, controls=cards)


class AggregateCard(ft.Container):
    def __init__(self, lang: dict, total_savings: float, total_target: float, percentage: str, progress_value: float, on_create_click: Callable):
        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=30,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
        )

        self.content = ft.Column(
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
                                    content=Text.LABEL("QUẢN LÝ QUỸ TIẾT KIỆM", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
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
                                        Text.LABEL("Tổng tiến độ tích lũy các mục tiêu đạt", color=Color.WHITE),
                                        Text.LABEL(f"{percentage}", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
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