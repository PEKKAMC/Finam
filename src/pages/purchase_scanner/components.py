# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Page, Text


class SelectableOptionGroup(ft.Container):
    """Custom option selector matching the React toggle buttons style."""
    def __init__(self, options: list[tuple[str, str]], initial_value: str, is_dark_selected: bool = False):
        self.options = options
        self.value = initial_value
        self.is_dark_selected = is_dark_selected
        self.button_controls: dict[str, ft.Container] = {}

        for val_id, label in self.options:
            btn = ft.Container(
                content=Text.BADGE(
                    label,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=ft.Padding(12, 10, 12, 10),
                border_radius=16,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                on_click=lambda e, vid=val_id: self._select(vid),
                expand=True
            )
            self.button_controls[val_id] = btn

        chunk_size = 2 if len(options) > 3 else 3
        rows = []
        for i in range(0, len(options), chunk_size):
            chunk_keys = [opt[0] for opt in options[i:i + chunk_size]]
            row_controls = [self.button_controls[k] for k in chunk_keys]
            rows.append(ft.Row(controls=row_controls, spacing=8))

        super().__init__(content=ft.Column(controls=rows, spacing=8))
        self._update_styles()

    def _select(self, val_id: str):
        self.value = val_id
        self._update_styles()
        self.update()

    def _update_styles(self):
        for val_id, btn in self.button_controls.items():
            is_selected = (val_id == self.value)
            text_ctrl: ft.Text = btn.content

            if is_selected:
                if self.is_dark_selected:
                    btn.bgcolor = Color.PRIMARY
                    btn.border = ft.Border.all(1.5, Color.PRIMARY)
                    text_ctrl.color = Color.WHITE
                else:
                    btn.bgcolor = Color.LIGHT_ACCENT
                    btn.border = ft.Border.all(1.5, Color.PRIMARY)
                    text_ctrl.color = Color.PRIMARY
            else:
                btn.bgcolor = Color.WHITE
                btn.border = ft.Border.all(1, Color.INPUT_BORDER)
                text_ctrl.color = Color.DEFAULT_TEXT


class ScannerForm(ft.Container):
    def __init__(self, page: Page, lang: dict, on_scan_click):
        self._page = page
        self.lang = lang
        self.on_scan_click = on_scan_click

        # Input fields matching React design specifications
        self.item_name = ft.TextField(
            hint_text="Ví dụ: Giày Sneaker, Áo khoác sale, Tai nghe bluetooth...",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=13,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        self.item_price = ft.TextField(
            hint_text="0 đ",
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=14,
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        self.item_reason = ft.TextField(
            hint_text="Tại sao bạn lại cần sản phẩm này ngay lúc này?",
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=12,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        # Triggers selection grid
        trigger_options = [
            ("need", self.lang["ui.scanner.trigger_actual_need"]),
            ("sale", self.lang["ui.scanner.trigger_flash_sale"]),
            ("tiktok", self.lang["ui.scanner.trigger_social_media"]),
            ("social", self.lang["ui.scanner.trigger_friends"]),
            ("emotion", self.lang["ui.scanner.trigger_emotion"])
        ]
        self.trigger = SelectableOptionGroup(trigger_options, initial_value="tiktok", is_dark_selected=False)

        # Thinking time selection grid
        thinking_options = [
            ("short", self.lang["ui.scanner.thinking_under_1h"]),
            ("medium", self.lang["ui.scanner.thinking_within_24h"]),
            ("long", self.lang["ui.scanner.thinking_over_3_days"])
        ]
        self.thinking_time = SelectableOptionGroup(thinking_options, initial_value="short", is_dark_selected=True)

        self.submit_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18),
                    Text.BUTTON(self.lang["ui.scanner.scan_assess"], color=Color.WHITE)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            bgcolor=Color.PRIMARY,
            border_radius=16,
            padding=ft.Padding(0, 14, 0, 14),
            on_click=lambda e: self.on_scan_click(
                self.item_name.value,
                self.item_price.value,
                self.item_reason.value,
                self.trigger.value,
                self.thinking_time.value
            ) if self.on_scan_click else None
        )

        self.main_container = ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, color=Color.PRIMARY, size=20),
                        Text.H4(self.lang["purchase_scanner.title"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.Divider(height=1, color=Color.CARD_DIVIDER),

                # Name
                ft.Column([
                    Text.H6(self.lang["ui.scanner.product_name"].upper(), color=Color.DEFAULT_TEXT),
                    self.item_name
                ], spacing=6),

                # Price
                ft.Column([
                    Text.H6(self.lang["ui.scanner.price"].upper(), color=Color.DEFAULT_TEXT),
                    self.item_price
                ], spacing=6),

                # Trigger
                ft.Column([
                    Text.H6(self.lang["ui.scanner.trigger_question"].upper(), color=Color.DEFAULT_TEXT),
                    self.trigger
                ], spacing=6),

                # Thinking time
                ft.Column([
                    Text.H6(self.lang["ui.scanner.thinking_time_question"].upper(), color=Color.DEFAULT_TEXT),
                    self.thinking_time
                ], spacing=6),

                # Reason
                ft.Column([
                    Text.H6(self.lang["ui.scanner.reason_label"].upper(), color=Color.DEFAULT_TEXT),
                    self.item_reason
                ], spacing=6),

                self.submit_btn
            ]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def resize(self, page_width: int):
        self.main_container.width = max(page_width, 0)


class InterventionItem(ft.Container):
    def __init__(self, page: Page, lang: dict, title: str, description: str):
        self._page = page
        self.lang = lang
        self.main_container = ft.Column(
            spacing=4,
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=Color.PRIMARY, size=16),
                    Text.MEDIUM(title, weight=ft.FontWeight.BOLD, color=Color.DEFAULT_TEXT)
                ], spacing=6),
                ft.Container(
                    content=Text.P(description, color=Color.SECONDARY_TEXT, size=12),
                    padding=ft.Padding(22, 0, 0, 0)
                )
            ]
        )
        super().__init__(
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=14,
            bgcolor=Color.WHITE,
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.main_container.width = width


class ScannerResult(ft.Container):
    def __init__(self, page: Page, lang: dict):
        self._page = page
        self.lang = lang

        # Empty state display
        self.empty_state = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.SHIELD_OUTLINED, color=Color.PRIMARY, size=52),
                Text.H4(self.lang["ui.scanner.no_results"], color=Color.DEFAULT_TEXT),
                Text.SMALL(
                    self.lang["ui.scanner.fill_info"],
                    color=Color.SECONDARY_TEXT,
                    text_align=ft.TextAlign.CENTER
                )
            ]
        )

        # Dynamic results controls
        self.risk_badge_text = Text.H6("24 giờ", color=Color.LIGHT_ACCENT)
        self.risk_score_text = Text.H1("0%", color=Color.PROGRESS_ACTIVE)
        self.risk_status_text = Text.SMALL(self.lang["ui.scanner.risk_assessment"], color=Color.BLAND_TEXT)
        self.progress_bar = ft.ProgressBar(value=0.0, color=Color.PROGRESS_ACTIVE, bgcolor=Color.DARK_BUTTON, height=8)

        # Gauge Score Header Card
        self.gauge_card = ft.Container(
            bgcolor=Color.DARK_SURFACE,
            border_radius=20,
            padding=18,
            border=ft.Border.all(1, Color.DARK_BUTTON),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text.LABEL(self.lang["ui.scanner.risk_index"].upper(), color=Color.BLAND_TEXT),
                            ft.Container(
                                content=self.risk_badge_text,
                                bgcolor=Color.DARK_BUTTON,
                                padding=ft.Padding(10, 4, 10, 4),
                                border_radius=12
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            self.risk_score_text,
                            self.risk_status_text
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                        spacing=10
                    ),
                    self.progress_bar
                ]
            )
        )

        # Advice Box
        self.advice_text = Text.P("", color=Color.DEFAULT_TEXT)
        self.advice_box = ft.Container(
            bgcolor=Color.GOAL_ITEM_BACKGROUND,
            border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
            border_radius=16,
            padding=14,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=Color.PRIMARY, size=18),
                        Text.SMALL(self.lang["ui.scanner.expert_perspective"], color=Color.PRIMARY)
                    ], spacing=6),
                    self.advice_text
                ]
            )
        )

        self.interventions_col = ft.Column(spacing=10)

        self.result_container = ft.Column(
            spacing=16,
            visible=False,
            controls=[
                self.gauge_card,
                self.advice_box,
                ft.Column([
                    Text.LABEL(self.lang["ui.scanner.intervention_rules"].upper(), color=Color.SECONDARY_TEXT),
                    self.interventions_col
                ], spacing=8)
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[self.empty_state, self.result_container],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.Alignment.CENTER,
            expand=True
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=24,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=Color.SHADOW),
            content=self.main_container
        )

    def resize(self, page_width: int):
        self.main_container.width = max(page_width, 0)

    def set_loading_state(self):
        self.empty_state.visible = False
        self.result_container.visible = True
        self.advice_text.value = self.lang["purchase_scanner.waiting"]
        self.update()

    def update_result(self, risk: int, trigger_display: str, price: float, item_name: str, ai_advice: str = ""):
        self.empty_state.visible = False
        self.result_container.visible = True

        if risk > 65:
            risk_color = Color.NEGATIVE_ACTION
            status_desc = self.lang["ui.scanner.risk_very_high"].upper()
            pause_time = self.lang["ui.scanner.time_24h"]
        elif risk > 35:
            risk_color = "#F59E0B"
            status_desc = self.lang["ui.scanner.risk_moderate"]
            pause_time = self.lang["ui.scanner.time_60s"]
        else:
            risk_color = Color.PROGRESS_ACTIVE
            status_desc = self.lang["ui.scanner.risk_rational"]
            pause_time = self.lang["ui.scanner.time_60s"]

        self.risk_score_text.value = f"{risk}%"
        self.risk_score_text.color = risk_color
        self.risk_status_text.value = status_desc
        self.risk_badge_text.value = pause_time
        self.progress_bar.value = risk / 100.0
        self.progress_bar.color = risk_color

        self.advice_text.value = ai_advice if ai_advice else f"Món đồ {item_name} đang chịu ảnh hưởng từ {trigger_display}."

        formatted_price = f"{int(price):,}đ" if price > 0 else "chưa nhập"

        interventions = [
            InterventionItem(self._page, self.lang, self.lang["ui.scanner.pause_rule"], f"Đợi ít nhất {pause_time} trước khi thanh toán."),
            InterventionItem(self._page, self.lang, self.lang["ui.scanner.budget_check"], f"Món này có giá {formatted_price}. Hãy so với mục tiêu tiết kiệm."),
            InterventionItem(self._page, self.lang, self.lang["ui.scanner.reflection"], f"Bạn mua vì cần thật, hay vì {trigger_display}?")
        ]

        self.interventions_col.controls = interventions
        self.update()