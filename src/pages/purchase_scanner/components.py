# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import UISettings, Color, Text


class ScannerForm(ft.Container):
    def __init__(self, on_scan_click):
        self.item_name = ft.TextField(
            label="Món muốn mua",
            hint_text="Ví dụ: giày sneaker đang sale",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT
        )
        self.item_price = ft.TextField(
            label="Giá tiền",
            hint_text="Ví dụ: 850000",
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT
        )
        self.item_reason = ft.TextField(
            label="Lý do muốn mua",
            hint_text="Ví dụ: thấy TikTok review, bạn bè cũng mua, sợ hết sale...",
            multiline=True,
            min_lines=3,
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT
        )
        self.trigger = ft.Dropdown(
            label="Nguồn kích thích mua",
            options=[
                ft.dropdown.Option("need", "Nhu cầu thật sự"),
                ft.dropdown.Option("social", "Bạn bè/peer pressure"),
                ft.dropdown.Option("tiktok", "TikTok/social media"),
                ft.dropdown.Option("sale", "Flash sale/giảm giá"),
                ft.dropdown.Option("emotion", "Buồn/chán/stress nên muốn mua"),
            ],
            value="need",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT
        )
        self.thinking_time = ft.Dropdown(
            label="Thời gian suy nghĩ trước khi mua",
            options=[
                ft.dropdown.Option("long", "Trên 24 giờ"),
                ft.dropdown.Option("medium", "1–24 giờ"),
                ft.dropdown.Option("short", "Dưới 1 giờ"),
            ],
            value="long",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Column(
                spacing=15,
                controls=[
                    Text.LABEL("Purchase Decision Scanner", weight=ft.FontWeight.BOLD),
                    Text.P("Nhập một món bạn đang muốn mua. App sẽ phân tích mức rủi ro hành vi.", color=Color.SECONDARY_TEXT),
                    self.item_name,
                    self.item_price,
                    self.item_reason,
                    self.trigger,
                    self.thinking_time,
                    ft.Button(
                        content="Phân tích quyết định mua",
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
                    Text.LABEL(title, weight=ft.FontWeight.BOLD, scale=0.05, min_size=12),
                    Text.P(description, color=Color.SECONDARY_TEXT)
                ]
            )
        )

class ScannerResult(ft.Container):
    def __init__(self):
        self.result_text = Text.P("Chưa có dữ liệu. Hãy thử quét một quyết định mua.", color=Color.PRIMARY_TEXT)
        self.result_box = ft.Container(
            content=self.result_text,
            padding=15,
            border_radius=10,
            bgcolor=Color.AGGREGATE_BACKGROUND
        )
        self.progress_bar = ft.ProgressBar(value=0.0, color=Color.PROGRESS_ACTIVE, bgcolor=Color.PROGRESS_BACKGROUND, height=12)
        self.interventions_col = ft.Column(spacing=10)

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
            content=ft.Column(
                spacing=20,
                controls=[
                    Text.H3("Kết quả phân tích", weight=ft.FontWeight.BOLD),
                    self.result_box,
                    self.progress_bar,
                    self.interventions_col
                ]
            )
        )

    def set_loading_state(self):
        self.result_text.value = "Trí tuệ nhân tạo đang phân tích quyết định của bạn..."
        self.result_text.color = Color.PRIMARY_TEXT
        self.update()

    def update_result(self, risk: int, trigger_display: str, price: float, item_name: str, ai_advice: str = ""):
        if risk >= 70:
            self.result_box.bgcolor = Color.NEGATIVE_ACTION + "22"
            self.result_text.color = Color.NEGATIVE_ACTION
            message = f"Rủi ro cao: {risk}/100.\n{item_name} có dấu hiệu mua bốc đồng. Nên trì hoãn 24 giờ trước khi mua."
            pause_time = "24 giờ"
        elif risk >= 40:
            self.result_box.bgcolor = Color.ERROR_TEXT + "33"
            self.result_text.color = Color.PRIMARY_TEXT
            message = f"Rủi ro trung bình: {risk}/100.\n{item_name} cần được kiểm tra lại bằng bộ lọc Need vs Want."
            pause_time = "60 giây"
        else:
            self.result_box.bgcolor = Color.AGGREGATE_BACKGROUND
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
            InterventionItem("Pause Rule", f"Đợi ít nhất {pause_time} trước khi thanh toán."),
            InterventionItem("Budget Check", f"Món này có giá {formatted_price}. Hãy so với mục tiêu tiết kiệm."),
            InterventionItem("Reflection", f"Bạn mua vì cần thật, hay vì {trigger_display}?")
        ])

        self.interventions_col.controls = interventions
        self.update()   