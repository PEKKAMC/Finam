# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import apply_responsive_text, UISettings, Color
from src.logger import Logger
from src.pages.global_components import SideMenu, TopNavigationBar
from src.pages.purchase_scanner.logic import LogicController
from src.pages.purchase_scanner.components import ScannerForm, ScannerResult

Logger.info("Initializing Purchase Scanner page...")


class PurchaseScannerView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state
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

        self.menu = SideMenu(self._page, self.lang, self.user_state)
        self.top_navigation_bar = TopNavigationBar(menu_button=self.menu.menu_button, current_user=self.user_state["current_user"])

        self.form_card = ScannerForm(on_scan_click=self.handle_scan_click)
        self.result_card = ScannerResult()

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=20,
                controls=[
                    self.top_navigation_bar,
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
                    ft.Container(
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[self.main_container]
                                )
                            ]
                        ),
                        expand=True,
                        padding=0
                    ),
                    self.menu.view
                ]
            )
        ]

    def on_page_resize(self, e=None):
        current_width = self._page.width if e is None else e.width
        if not current_width: current_width = UISettings.MAX_APP_WIDTH
        safe_width = int(min(current_width, UISettings.MAX_APP_WIDTH))

        self.main_container.width = safe_width
        self.top_navigation_bar.width = safe_width * 0.9

        card_width = safe_width * 0.9
        self.form_card.width = card_width
        self.result_card.width = card_width

        try:
            apply_responsive_text(self.main_container, safe_width)
        except Exception as e:
            Logger.debug(f"Skipped text resizing: {e}")

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Skipped updating during resize: {e}")

def get_scanner_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return PurchaseScannerView(page, lang, user_state)