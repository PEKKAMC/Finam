# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

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
        self.update_styles()

    def _select(self, val_id: str):
        self.value = val_id
        self.update_styles()
        self.update()

    def update_styles(self):
        for val_id, btn in self.button_controls.items():
            is_selected = (val_id == self.value)
            text_ctrl: ft.Control | None = btn.content

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


class ThinkingTimeUnitContainer(ft.Container):
    """Input field for thinking time value combined with a time unit dropdown."""
    def __init__(self, lang: dict, default_val, default_unit):
        self.lang = lang

        self.value_field = ft.TextField(
            hint_text="0",
            value=default_val,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$", replacement_string=""),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=13,
            content_padding=ft.Padding(16, 12, 16, 12),
            expand=True
        )

        self.unit_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("minute", self.lang["generic.minute"]),
                ft.dropdown.Option("hour", self.lang["generic.hour"]),
                ft.dropdown.Option("day", self.lang["generic.day"]),
                ft.dropdown.Option("week", self.lang["generic.week"]),
            ],
            value=default_unit,
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            width=150,
            text_size=13,
            content_padding=ft.Padding(16, 12, 16, 12)
        )
        row = ft.Row(
            spacing=10,
            controls=[self.value_field, self.unit_dropdown]
        )
        super().__init__(content=row)

    @property
    def value(self):
        val = self.value_field.value.strip() if self.value_field.value else "1"
        unit = self.unit_dropdown.value or "hour"
        return f"{val} {unit}"


class ScannerForm(ft.Container):
    def __init__(self, page: Page, lang: dict, currency: str, on_scan_click: Callable):
        self._page = page
        self.lang = lang
        self.currency = currency
        self.on_scan_click = on_scan_click

        self.item_name = ft.TextField(
            hint_text=self.lang["purchase_scanner.product_hint"],
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
            hint_text=self.lang["purchase_scanner.item_price_hint"].format(currency=self.currency),
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$", replacement_string=""),
            border_color=Color.INPUT_BORDER,
            color=Color.DEFAULT_TEXT,
            border_radius=16,
            filled=True,
            bgcolor=Color.PAGE_BACKGROUND,
            height=48,
            text_size=13,
            content_padding=ft.Padding(16, 12, 16, 12)
        )

        self.item_reason = ft.TextField(
            hint_text=self.lang["purchase_scanner.reason_hint"],
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
            ("need", self.lang["purchase_scanner.trigger_actual_need"]),
            ("sale", self.lang["purchase_scanner.trigger_flash_sale"]),
            ("tiktok", self.lang["purchase_scanner.trigger_social_media"]),
            ("social", self.lang["purchase_scanner.trigger_friends"]),
            ("emotion", self.lang["purchase_scanner.trigger_emotion"])
        ]
        self.trigger = SelectableOptionGroup(trigger_options, initial_value="", is_dark_selected=False)

        self.thinking_time = ThinkingTimeUnitContainer(lang=self.lang, default_val="0", default_unit="hour")

        self.submit_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.LIGHT_ACCENT, size=18),
                    Text.BUTTON(self.lang["purchase_scanner.scan_assess"], color=Color.WHITE)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            bgcolor=Color.PRIMARY,
            border_radius=16,
            padding=ft.Padding(0, 14, 0, 14),
            on_click=self._handle_scan_click
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
                    Text.H6(self.lang["purchase_scanner.product_name"].upper(), color=Color.DEFAULT_TEXT),
                    self.item_name
                ], spacing=6),

                # Price
                ft.Column([
                    Text.H6(self.lang["purchase_scanner.price"].upper(), color=Color.DEFAULT_TEXT),
                    self.item_price
                ], spacing=6),

                # Trigger
                ft.Column([
                    Text.H6(self.lang["purchase_scanner.trigger_question"].upper(), color=Color.DEFAULT_TEXT),
                    self.trigger
                ], spacing=6),

                # Thinking time
                ft.Column([
                    Text.H6(self.lang["purchase_scanner.thinking_time_question"].upper(), color=Color.DEFAULT_TEXT),
                    self.thinking_time
                ], spacing=6),

                # Reason
                ft.Column([
                    Text.H6(self.lang["purchase_scanner.reason_label"].upper(), color=Color.DEFAULT_TEXT),
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

    def _handle_scan_click(self):
        self.on_scan_click(
            self.item_name.value,
            self.item_price.value,
            self.item_reason.value,
            self.trigger.value,
            self.thinking_time.value
        )
        self.reset()

    def reset(self):
        self.item_name.value = ""
        self.item_price.value = ""
        self.item_reason.value = ""
        self.trigger.value = ""
        self.trigger.update_styles()
        self.thinking_time.value_field.value = "0"
        self.thinking_time.unit_dropdown.value = "hour"
        self._page.update()

    def resize(self, page_width: int):
        self.main_container.width = max(page_width, 0)


class InterventionItem(ft.Container):
    def __init__(self, page: Page, title: str, description: str):
        self._page = page
        self.main_container = ft.Column(
            spacing=4,
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=Color.PRIMARY, size=16),
                    Text.MEDIUM(title, weight=ft.FontWeight.BOLD, color=Color.DEFAULT_TEXT)
                ], spacing=6),
                ft.Container(
                    content=Text.P(description, color=Color.SECONDARY_TEXT),
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


class ScannerHistoryCard(ft.Container):
    def __init__(self, page: Page, lang: dict, currency: str, on_delete_entry=None, on_clear_all=None):
        self._page = page
        self.lang = lang
        self.currency = currency
        self.on_delete_entry = on_delete_entry or (lambda *_: None)
        self.on_clear_all = on_clear_all or (lambda: None)

        self.history_collapsed = False
        self.history_expander = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_UP,
            on_click=lambda e: self.toggle_history_panel(),
            style=ft.ButtonStyle(shape=ft.CircleBorder()),
        )
        self.clear_all_button = ft.TextButton(
            content=self.lang["purchase_scanner.clear_history"],
            icon=ft.Icons.DELETE_SWEEP_OUTLINED,
            on_click=lambda e: self._handle_clear_all(),
            style=ft.ButtonStyle(color=Color.NEGATIVE_ACTION),
        )
        self.history_list = ft.Column(spacing=8)
        self.history_content = ft.Column(
            spacing=10,
            controls=[self.history_list],
            visible=True,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        super().__init__(
            visible=True,
            bgcolor=Color.WHITE,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text.LABEL(self.lang["purchase_scanner.history"].upper(), color=Color.SECONDARY_TEXT),
                            ft.Row(
                                controls=[self.clear_all_button, self.history_expander],
                                spacing=0,
                            ),
                        ],
                    ),
                    self.history_content,
                ],
            ),
        )

    def _handle_delete(self, scan_id):
        if scan_id is not None:
            self.on_delete_entry(scan_id)

    def _handle_clear_all(self):
        self.on_clear_all()

    def set_history(self, history_entries: list[dict]):
        self.history_list.controls.clear()
        self.history_content.visible = not self.history_collapsed
        self.clear_all_button.visible = bool(history_entries)

        if not history_entries:
            self.history_list.controls.append(
                Text.SMALL(self.lang["purchase_scanner.no_history"], color=Color.SECONDARY_TEXT)
            )
            if self.parent:
                self.update()
            return

        for entry in history_entries:
            item_name = entry.get("item_name") or "Item"
            risk_score_raw = entry.get("risk_score")
            risk_score = int(risk_score_raw or 0)
            created_at = entry.get("created_at", "")
            trigger_display = entry.get("trigger_display") or entry.get("trigger") or "-"
            advice = entry.get("ai_advice") or "-"
            price = entry.get("price", 0)
            scan_id = entry.get("id")

            details = ft.Column(
                spacing=4,
                visible=False,
                controls=[
                    Text.SMALL(f"{price:,.2f} {self.currency} • {trigger_display}", color=Color.SECONDARY_TEXT),
                    Text.SMALL(created_at, color=Color.SECONDARY_TEXT),
                    Text.SMALL(advice, color=Color.DEFAULT_TEXT),
                ],
            )
            expander = ft.IconButton(
                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                tooltip=self.lang["purchase_scanner.history"],
            )
            item_card = ft.Container(
                bgcolor=Color.GOAL_ITEM_BACKGROUND,
                border=ft.Border.all(1, Color.GOAL_ITEM_BORDER),
                border_radius=14,
                padding=12,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                Text.MEDIUM(item_name, weight=ft.FontWeight.BOLD, color=Color.DEFAULT_TEXT),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=Text.SMALL(f"{risk_score}", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                                            bgcolor=Color.PRIMARY if risk_score < 60 else (Color.NEGATIVE_ACTION if risk_score > 75 else "#F59E0B"),
                                            border_radius=12,
                                            padding=ft.Padding(8, 4, 8, 4),
                                        ),
                                        expander,
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            tooltip=self.lang["purchase_scanner.delete_item"],
                                            on_click=lambda e, sid=scan_id: self._handle_delete(sid),
                                            icon_color=Color.NEGATIVE_ACTION,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ]
                        ),
                        details,
                    ]
                )
            )

            def toggle_entry(e: ft.ControlEvent | None = None, entry_details: ft.Column = details, entry_expander: ft.IconButton = expander, entry_card: ft.Container = item_card):
                entry_details.visible = not entry_details.visible
                entry_expander.icon = (
                    ft.Icons.KEYBOARD_ARROW_UP if entry_details.visible else ft.Icons.KEYBOARD_ARROW_DOWN
                )
                entry_card.update()
                return e

            expander.on_click = toggle_entry
            self.history_list.controls.append(item_card)

        self.history_content.visible = not self.history_collapsed
        if self.parent:
            self.update()

    def toggle_history_panel(self):
        self.history_collapsed = not self.history_collapsed
        self.history_content.visible = not self.history_collapsed
        self.history_expander.icon = ft.Icons.KEYBOARD_ARROW_DOWN if self.history_collapsed else ft.Icons.KEYBOARD_ARROW_UP
        self.update()


class ScannerResult(ft.Container):
    def __init__(self, page: Page, lang: dict, currency: str):
        self._page = page
        self.lang = lang
        self.currency = currency

        # Empty state display
        self.empty_state = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.SHIELD_OUTLINED, color=Color.PRIMARY, size=52),
                Text.H4(self.lang["purchase_scanner.no_results"], color=Color.DEFAULT_TEXT),
                Text.SMALL(
                    self.lang["purchase_scanner.fill_info"],
                    color=Color.SECONDARY_TEXT,
                    text_align=ft.TextAlign.CENTER
                )
            ]
        )

        # Loading display while AI is evaluating the purchase
        self.loading_container = ft.Container(
            visible=False,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.ProgressRing(width=48, height=48, stroke_width=5, color=Color.PRIMARY),
                    Text.H5(self.lang["purchase_scanner.waiting"], color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER),
                    Text.SMALL(
                        self.lang["purchase_scanner.fill_info"],
                        color=Color.SECONDARY_TEXT,
                        text_align=ft.TextAlign.CENTER
                    )
                ]
            )
        )

        # Dynamic results controls
        self.risk_badge_text = Text.H6("24 giờ", color=Color.LIGHT_ACCENT)
        self.risk_score_text = Text.H1("0%", color=Color.PROGRESS_ACTIVE)
        self.risk_status_text = Text.SMALL(self.lang["purchase_scanner.risk_assessment"], color=Color.BLAND_TEXT)
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
                            Text.LABEL(self.lang["purchase_scanner.risk_index"].upper(), color=Color.BLAND_TEXT),
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
                        vertical_alignment=ft.CrossAxisAlignment.END,
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
                        Text.SMALL(self.lang["purchase_scanner.expert_perspective"], color=Color.PRIMARY)
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
                    Text.LABEL(self.lang["purchase_scanner.intervention_rules"].upper(), color=Color.SECONDARY_TEXT),
                    self.interventions_col
                ], spacing=8),
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[self.empty_state, self.loading_container, self.result_container],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
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

    def set_loading_state(self):
        self.empty_state.visible = False
        self.loading_container.visible = True
        self.result_container.visible = False
        self.advice_text.value = ""
        self.interventions_col.controls.clear()
        self.update()

    def update_result(self, risk: int | None, trigger_display: str, price: float, item_name: str, ai_advice: str = ""):
        self.empty_state.visible = False
        self.loading_container.visible = False
        self.result_container.visible = True

        if risk is None:
            self.risk_score_text.value = "—"
            self.risk_score_text.color = Color.BLAND_TEXT
            self.risk_status_text.value = "Nội dung troll / không hợp lệ"
            self.risk_badge_text.value = "Bỏ qua"
            self.progress_bar.value = 0.0
            self.progress_bar.color = Color.BLAND_TEXT
            self.advice_text.value = ai_advice or "Đầu vào này bị xác định là troll hoặc không hợp lệ nên không được lưu vào lịch sử."
            self.interventions_col.controls.clear()
            self.update()
            return

        risk_val = max(0, min(100, int(risk)))

        if risk_val > 65:
            risk_color = Color.NEGATIVE_ACTION
            status_desc = self.lang["purchase_scanner.risk_very_high"]
            pause_time = f"24 {self.lang['generic.hour']}"
        elif risk_val > 35:
            risk_color = "#F59E0B"
            status_desc = self.lang["purchase_scanner.risk_moderate"]
            pause_time = f"60 {self.lang['generic.second']}"
        else:
            risk_color = Color.PROGRESS_ACTIVE
            status_desc = self.lang["purchase_scanner.risk_rational"]
            pause_time = f"60 {self.lang['generic.second']}"

        self.risk_score_text.value = f"{risk_val}%"
        self.risk_score_text.color = risk_color
        self.risk_status_text.value = status_desc
        self.risk_badge_text.value = pause_time
        self.progress_bar.value = risk_val / 100.0
        self.progress_bar.color = risk_color
        self.advice_text.value = ai_advice if ai_advice else f"Món đồ {item_name} đang chịu ảnh hưởng từ {trigger_display}."

        formatted_price = f"{price:,.2f} {self.currency}" if price > 0 else "chưa nhập"
        interventions = [
            InterventionItem(self._page, self.lang["purchase_scanner.pause_rule"], f"Đợi ít nhất {pause_time} trước khi thanh toán."),
            InterventionItem(self._page, self.lang["purchase_scanner.budget_check"], f"Món này có giá {formatted_price}. Hãy so với mục tiêu tiết kiệm."),
            InterventionItem(self._page, self.lang["purchase_scanner.reflection"], f"Bạn mua vì cần thật, hay vì {trigger_display}?")
        ]

        self.interventions_col.controls.clear()
        self.interventions_col.controls.extend(interventions)
        self.update()

    def resize(self, width: int):
        self.main_container.width = width