# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.purchase_scanner.logic import LogicController
from src.pages.purchase_scanner.components import ScannerForm, ScannerResult, ScannerHistoryCard
from src.utils import Color, Page, get_safe_page_size, Text, UISettings

Logger.info("Initializing Purchase Scanner page...")


class PurchaseScannerView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = LogicController(user_info["username"])
        self.scan_history = self.controller.get_scan_history()
        self.currency = self.controller.get_currency()

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # Global components
        self.menu = Menu(self._page, self.lang, self.user_info)

        self.form_card = ScannerForm(page=self._page, lang=self.lang, on_scan_click=self.handle_scan_click)
        self.result_card = ScannerResult(page=self._page, lang=self.lang, currency=self.currency)
        self.history_card = ScannerHistoryCard(
            page=self._page,
            lang=self.lang,
            on_delete_entry=self.handle_delete_history_entry,
            on_clear_all=self.handle_clear_history,
            currency=self.currency,
        )
        self.history_card.set_history(self.scan_history)

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
                                        Text.SMALL(self.lang["purchase_scanner.ai_title"], color=Color.LIGHT_ACCENT, weight=ft.FontWeight.BOLD)
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
                    Text.H2(self.lang["purchase_scanner.title"], color=Color.WHITE, weight=ft.FontWeight.BOLD),
                    Text.SMALL(
                        self.lang["purchase_scanner.description"],
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
                                ),
                                ft.Container(
                                    self.history_card,
                                    margin=ft.Margin.only(top=4)
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
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.menu
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def handle_scan_click(self, name, price, reason, trigger, time):
        self.result_card.set_loading_state()
        item_name = name if name else self.lang["purchase_scanner.item"]

        def worker():
            try:
                risk, trigger_display, price_val, ai_advice = self.controller.analyze_purchase(
                    item_name, price, reason, trigger, time
                )

                if risk is not None:
                    self.controller.save_scan_result(item_name, price_val, trigger, reason, time, risk, trigger_display, ai_advice)
                    self.history_card.set_history(self.controller.get_scan_history())

                self.result_card.update_result(risk, trigger_display, price_val, item_name, ai_advice)

            except Exception as ex:
                Logger.error(f"Error during background analysis: {ex}")
                self.result_card.update_result(
                    30,
                    "yếu tố bên ngoài",
                    0.0,
                    item_name,
                    "Không thể hiển thị kết quả do lỗi giao diện. Vui lòng thử lại."
                )

        self._page.run_thread(worker)

    def handle_delete_history_entry(self, entry):
        self.controller.delete_scan_result(entry)
        self.history_card.set_history(self.controller.get_scan_history())

    def handle_clear_history(self):
        self.controller.clear_scan_history()
        self.history_card.set_history(self.controller.get_scan_history())

    def _refresh_view(self) -> int:
        try:
            self.scan_history = self.controller.get_scan_history()
            self.history_card.set_history(self.scan_history)
            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        try:
            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

            # Resizing other components
            self.menu.resize(
                width=page_width
            )

            return 0

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")
            return 1

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")
            return 2

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")
            return -1


def get_scanner_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Purchase Scanner page...")
    return PurchaseScannerView(page, lang, user_info)