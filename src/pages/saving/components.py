# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Callable

import flet as ft

from src.utils import Color, Text


class ObjectiveCard(ft.Container):
    def __init__(self, objective_id: int, objective_title: str, subtitle: str, current_value: str, target_value: str, percentage: str, progress: float, completed: bool, on_click_callback: Callable):
        super().__init__(
            width=280, bgcolor=Color.COMPLETED_BACKGROUND if completed else Color.CARD_BACKGROUND, border_radius=12, padding=20, border=ft.Border.all(1, Color.COMPLETED_BORDER if completed else Color.DEFAULT_BORDER), ink=True,
            on_click=lambda e: on_click_callback(e.page, objective_id, objective_title, subtitle, current_value, target_value, progress, completed),
        )
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[Text.H3(f"{objective_title}" if completed else objective_title, color=Color.COMPLETED_TEXT if completed else Color.PRIMARY_TEXT, expand=True)]),
                Text.P(subtitle, color=Color.BODY_TEXT), ft.Container(height=10),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[Text.LABEL(f"{current_value} / {target_value}", color=Color.PRIMARY_TEXT), Text.LABEL(percentage, color=Color.PRIMARY_TEXT)]),
                ft.ProgressBar(value=progress, color=Color.PROGRESS_COMPLETED if completed else Color.PROGRESS_ACTIVE, bgcolor=Color.PROGRESS_BACKGROUND, height=6), ft.Container(height=5),
            ]
        )


class ObjectiveGrid(ft.Row):
    def __init__(self, objectives_data: list, on_card_click: Callable):
        cards = []
        for data in objectives_data:
            cards.append(ObjectiveCard(
                objective_id=data["objective_id"], objective_title=data["title"], subtitle=data["reason"],
                current_value=data["current_value"], target_value=data["target_value"],
                percentage=data["percentage"], progress=data["progress"], completed=data["completed"],
                on_click_callback=on_card_click
            ))
        super().__init__(spacing=20, scroll=ft.ScrollMode.AUTO, controls=cards)


class AggregateCard(ft.Container):
    def __init__(self, lang: dict, total_savings: float, total_target: float, percentage: str, progress_value: float):
        super().__init__(expand=2, bgcolor=Color.AGGREGATE_BACKGROUND, height=200, border_radius=12, padding=25)
        self.content = ft.Column(
            spacing=8, alignment=ft.MainAxisAlignment.START,
            controls=[
                Text.LABEL(lang["saving.aggregate_portfolio_value"], color=Color.AGGREGATE_TEXT),
                Text.LABEL(f"{int(total_savings):,} VND", color=Color.BLACK),
                Text.H4(f"/{int(total_target):,} VND", color=Color.SUBTITLE_TEXT),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[Text.LABEL(lang["saving.progression"], color=Color.PRIMARY_TEXT), Text.LABEL(percentage, color=Color.PRIMARY_ACTION)]),
                ft.ProgressBar(value=progress_value, color=Color.PROGRESS_ACTIVE, bgcolor=Color.PROGRESS_BACKGROUND, height=8)
            ]
        )


class ActivityListTile(ft.ListTile):
    def __init__(self, item: dict):
        icon_used = ft.Icons.FLAG
        icon_color = Color.NEGATIVE_ACTION
        match item["type"]:
            case "saving":
                icon_used = ft.Icons.ATTACH_MONEY
                icon_color = Color.PRIMARY_ACTION
            case "completed":
                icon_used = ft.Icons.STARS
                icon_color = Color.COMPLETED_ACTION
            case "deleted":
                icon_used = ft.Icons.DELETE_FOREVER
                icon_color = Color.NEGATIVE_ACTION

        super().__init__(
            leading=ft.Icon(icon_used, color=icon_color),
            title=Text.LABEL(item["desc"], color=Color.BODY_TEXT),
            subtitle=Text.SMALL(item["date"], color=Color.SECONDARY_TEXT)
        )

class ActivityHistoryBoard(ft.Container):
    def __init__(self, lang: dict, activity_data: list, on_clear_history, on_export_ledger):
        activity_controls = []
        if not activity_data:
            activity_controls.append(Text.SMALL(lang["saving.no_recent_activity"], color=Color.BODY_TEXT, italic=True))
        else:
            for item in activity_data:
                activity_controls.append(ActivityListTile(item))

        super().__init__(
            bgcolor=Color.ACTIVITY_BACKGROUND, border_radius=12, padding=ft.Padding.only(top=20, bottom=0),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=20),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                Text.H3(lang["saving.recent_activity"], color=Color.PRIMARY_TEXT),
                                ft.Row(spacing=15, controls=[
                                    ft.GestureDetector(on_tap=on_clear_history, content=ft.Row([Text.LABEL(lang["saving.clear_history"], color=Color.NEGATIVE_ACTION), ft.Icon(ft.Icons.DELETE, size=14, color=Color.NEGATIVE_ACTION)])),
                                    ft.GestureDetector(on_tap=on_export_ledger, content=ft.Row([Text.LABEL(lang["saving.export_ledger"], color=Color.PROGRESS_ACTIVE), ft.Icon(ft.Icons.DOWNLOAD, size=14, color=Color.PROGRESS_ACTIVE)]))
                                ])
                            ]
                        )
                    ),
                    ft.Container(height=15),
                    ft.Container(padding=10, content=ft.Column(controls=activity_controls, height=200, scroll=ft.ScrollMode.AUTO))
                ]
            )
        )