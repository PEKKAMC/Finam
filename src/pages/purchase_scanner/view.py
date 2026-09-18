# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.purchase_scanner.logic import LogicController
from src.pages.purchase_scanner.components import ScannerForm, ScannerResult
from src.utils import Color, get_safe_page_size, Text, UISettings

Logger.info("Initializing Purchase Scanner page...")


class PurchaseScannerView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController()

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # Global components
        self.menu = Menu(self._page, self.lang, self.user_info)

        self.form_card = ScannerForm(page=self._page, lang=self.lang, on_scan_click=self.handle_scan_click)
        self.result_card = ScannerResult(page=self._page, lang=self.lang)

        # Header banner matching React header card styling
        header_banner = ft.Container(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=28,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=Color.SHADOW),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.AUTO_AWESOME, color=Color.PROGRESS_ACTIVE, size=14),
                                        Text.SMALL("Finam AI Impulse Scanner", color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
                                    ],
                                    tight=True,
                                    spacing=6
                                ),
                                bgcolor=Color.DARK_SURFACE,
                                padding=ft.Padding(12, 6, 12, 6),
                                border_radius=20,
                                border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
                            )
                        ]
                    ),
                    Text.H2("Đánh Giá Mua Sắm Bốc Đồng", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                    Text.SMALL(
                        "Nhập thông tin món đồ bạn đang muốn xuống tiền để AI phân tích chỉ số rủi ro phung phí và đưa ra quy tắc trì hoãn mua sắm thông minh.",
                        color=Color.LIGHT_ACCENT
                    )
                ]
            )
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=20,
                            expand=True,
                            controls=[
                                header_banner,
                                ft.ResponsiveRow(
                                    spacing=20,
                                    run_spacing=20,
                                    controls=[
                                        ft.Container(self.form_card, col={"sm": 12, "md": 6}),
                                        ft.Container(self.result_card, col={"sm": 12, "md": 6}),
                                    ]
                                )
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/purchase_scanner",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(expand=True, controls=[self.main_container, self.menu])
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def handle_scan_click(self, name, price, reason, trigger, time):
        self.result_card.set_loading_state()
        item_name = name if name else "Món hàng"
        risk, trigger_display, price_val, ai_advice = self.controller.analyze_purchase(item_name, price, reason, trigger, time)
        self.result_card.update_result(risk, trigger_display, price_val, item_name, ai_advice)

    def _on_page_resize(self, e = None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        self.main_container.width = page_width
        self.main_container.height = page_height

        self.menu.resize(
            width=page_width
        )

        return e

def get_scanner_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return PurchaseScannerView(page, lang, user_info)