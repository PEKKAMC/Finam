# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Color, Text


class ScannerForm(ft.Container):
    def __init__(self, on_scan_click, lang: dict):
        self.lang = lang
        self.item_name = ft.TextField(
            label=self.lang["purchase_scanner.item_name"],
            hint_text=self.lang["purchase_scanner.item_name_hint"],
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.CARD_BACKGROUND,
            height=55
        )
        self.item_price = ft.TextField(
            label=self.lang["purchase_scanner.item_price"],
            hint_text=self.lang["purchase_scanner.item_price_hint"],
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.CARD_BACKGROUND,
            height=55
        )
        self.item_reason = ft.TextField(
            label=self.lang["purchase_scanner.item_reason"],
            hint_text=self.lang["purchase_scanner.item_reason_hint"],
            multiline=True,
            min_lines=3,
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.CARD_BACKGROUND
        )
        self.trigger = ft.Dropdown(
            label=self.lang["purchase_scanner.source"],
            options=[
                ft.dropdown.Option("need", "Nhu cầu thật sự"),
                ft.dropdown.Option("social", "Bạn bè/peer pressure"),
                ft.dropdown.Option("tiktok", "TikTok/social media"),
                ft.dropdown.Option("sale", "Flash sale/giảm giá"),
                ft.dropdown.Option("emotion", "Buồn/chán/stress nên muốn mua"),
            ],
            value="need",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.CARD_BACKGROUND
        )
        self.thinking_time = ft.Dropdown(
            label=self.lang["purchase_scanner.thinking_time"],
            options=[
                ft.dropdown.Option("long", "Trên 24 giờ"),
                ft.dropdown.Option("medium", "1–24 giờ"),
                ft.dropdown.Option("short", "Dưới 1 giờ"),
            ],
            value="long",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.CARD_BACKGROUND
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=22,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(width=32, height=32, border_radius=10, bgcolor=Color.LIGHT_ACCENT, alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.SHOPPING_BAG, color=Color.PRIMARY, size=18)),
                            Text.H4(self.lang["purchase_scanner.title"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
                        ]
                    ),
                    Text.P(self.lang["purchase_scanner.subtitle"], color=Color.SECONDARY_TEXT),
                    self.item_name,
                    self.item_price,
                    self.item_reason,
                    self.trigger,
                    self.thinking_time,
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.WHITE, size=16), Text.LABEL(self.lang["purchase_scanner.analyze"], weight=ft.FontWeight.BOLD)], tight=True),
                        on_click=lambda e: on_scan_click(
                            self.item_name.value,
                            self.item_price.value,
                            self.item_reason.value,
                            self.trigger.value,
                            self.thinking_time.value
                        ),
                        bgcolor=Color.PRIMARY_ACTION,
                        color=Color.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14), padding=20)
                    )
                ]
            )
        )

class InterventionItem(ft.Container):
    def __init__(self, title, description):
        super().__init__(
            border=ft.Border.all(1, Color.DEFAULT_BORDER),
            border_radius=10,
            padding=15,
            bgcolor=Color.WHITE,
            content=ft.Column(
                spacing=5,
                controls=[
                    Text.LABEL(title, weight=ft.FontWeight.BOLD),
                    Text.P(description, color=Color.SECONDARY_TEXT)
                ]
            )
        )

class ScannerResult(ft.Container):
    def __init__(self, lang: dict):
        self.lang = lang
        self.result_text = Text.P(self.lang["purchase_scanner.no_data"], color=Color.PRIMARY_TEXT)
        self.result_box = ft.Container(
            content=self.result_text,
            padding=18,
            border_radius=18,
            bgcolor=Color.AGGREGATE_BACKGROUND,
            border=ft.Border.all(1, Color.INPUT_BORDER)
        )
        self.progress_bar = ft.ProgressBar(value=0.0, color=Color.PROGRESS_ACTIVE, bgcolor=Color.PROGRESS_BACKGROUND, height=12)
        self.interventions_col = ft.Column(spacing=10)

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=22,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(width=32, height=32, border_radius=10, bgcolor=Color.LIGHT_ACCENT, alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PRIMARY, size=18)),
                            Text.H4(self.lang["purchase_scanner.analysis_result"], weight=ft.FontWeight.BOLD, color=Color.DEFAULT_TEXT)
                        ]
                    ),
                    self.result_box,
                    self.progress_bar,
                    self.interventions_col
                ]
            )
        )

    def set_loading_state(self):
        self.result_text.value = self.lang["purchase_scanner.waiting"]
        self.result_text.color = Color.PRIMARY_TEXT
        self.update()

    def update_result(self, risk: int, trigger_display: str, price: float, item_name: str, ai_advice: str = ""):
        if risk >= 70:
            self.result_box.bgcolor = Color.NEGATIVE_ACTION + "22"
            self.result_box.border = ft.Border.all(1, Color.NEGATIVE_ACTION)
            self.result_text.color = Color.NEGATIVE_ACTION
            message = f"Rủi ro cao: {risk}/100.\n{item_name} có dấu hiệu mua bốc đồng. Nên trì hoãn 24 giờ trước khi mua."
            pause_time = "24 giờ"
        elif risk >= 40:
            self.result_box.bgcolor = Color.EXPENSE_ACTION_BACKGROUND + "22"
            self.result_box.border = ft.Border.all(1, Color.EXPENSE_ACTION_BACKGROUND)
            self.result_text.color = Color.PRIMARY_TEXT
            message = f"Rủi ro trung bình: {risk}/100.\n{item_name} cần được kiểm tra lại bằng bộ lọc Need vs Want."
            pause_time = "60 giây"
        else:
            self.result_box.bgcolor = Color.AGGREGATE_BACKGROUND
            self.result_box.border = ft.Border.all(1, Color.PRIMARY_ACTION)
            self.result_text.color = Color.AGGREGATE_TEXT
            message = f"Rủi ro thấp: {risk}/100.\nQuyết định mua có vẻ hợp lý hơn, nhưng vẫn nên kiểm tra ngân sách."
            pause_time = "60 giây"

        self.result_text.value = message
        self.progress_bar.value = risk / 100.0

        formatted_price = f"{int(price):,}đ" if price > 0 else "chưa nhập"

        interventions = []
        if ai_advice:
            interventions.append(InterventionItem("Lời khuyên từ AI", ai_advice))

        interventions.extend([
            InterventionItem(self.lang["purchase_scanner.pause_rule"], f"Đợi ít nhất {pause_time} trước khi thanh toán."),
            InterventionItem(self.lang["purchase_scanner.budget_check"], f"Món này có giá {formatted_price}. Hãy so với mục tiêu tiết kiệm."),
            InterventionItem(self.lang["purchase_scanner.reflection"], f"Bạn mua vì cần thật, hay vì {trigger_display}?")
        ])

        self.interventions_col.controls = interventions
        self.update()  