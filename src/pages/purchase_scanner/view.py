# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text, UISettings
from src.logger import Logger
from src.pages.global_components import Menu, TopNavigationBar
from src.pages.purchase_scanner.logic import LogicController
from src.pages.purchase_scanner.components import ScannerForm, ScannerResult

Logger.info("Initializing Purchase Scanner page...")


class PurchaseScannerView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController()

        self.menu = None
        self.top_navigation_bar = None
        self.main_container = None
        self.form_card = None
        self.result_card = None

        super().__init__(
            route="/purchase_scanner",
            padding=0,
            bgcolor=Color.WHITE,
            controls=self.create_ui_components()
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def handle_scan_click(self, name, price, reason, trigger, time):
        self.result_card.set_loading_state()
        item_name = name if name else "Món hàng"
        risk, trigger_display, price_val, ai_advice = self.controller.analyze_purchase(item_name, price, reason, trigger, time)
        self.result_card.update_result(risk, trigger_display, price_val, item_name, ai_advice)

    def create_ui_components(self):
        Logger.info("Rendering UI for Purchase Scanner page...")

        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(page=self._page, lang=self.lang, current_user=self.user_info["username"])

        self.form_card = ScannerForm(page=self._page, lang=self.lang, on_scan_click=self.handle_scan_click)
        self.result_card = ScannerResult(page=self._page, lang=self.lang)

        header_banner = ft.Container(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=22,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        content=Text.SMALL("Finam AI Impulse Scanner", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD),
                        bgcolor=Color.DARK_SURFACE,
                        padding=ft.Padding(12, 4, 12, 4),
                        border_radius=16,
                        border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
                    ),
                    Text.H2("Đánh giá mua sắm bốc đồng", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                    Text.SMALL("Nhập thông tin món đồ bạn muốn mua và AI sẽ phân tích mức độ rủi ro trước khi xuống tiền.", color=Color.LIGHT_ACCENT)
                ]
            )
        )

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            margin=ft.Margin(left=16, top=84, right=16, bottom=88),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[
                    header_banner,
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(self.form_card, col={"sm": 12, "md": 6}),
                            ft.Container(self.result_card, col={"sm": 12, "md": 6}),
                        ]
                    )
                ]
            )
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        ]

    def on_page_resize(self, e=None):
        current_width = self._page.width if e is None else e.width
        if not current_width: current_width = UISettings.MAX_APP_WIDTH
        safe_width = int(min(current_width, UISettings.MAX_APP_WIDTH))

        self.main_container.width = max(safe_width - 32, 320)
        self.main_container.margin = ft.Margin(left=16, top=84, right=16, bottom=88)
        self.top_navigation_bar.resize(safe_width)
        self.menu.resize(safe_width)

        card_width = max(safe_width - 48, 320)
        self.form_card.width = card_width
        self.result_card.width = card_width

        return e

def get_scanner_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return PurchaseScannerView(page, lang, user_info)