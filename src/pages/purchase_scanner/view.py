# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime, timezone

import flet as ft

from src.logger import Logger
from src.database import db
from src.pages.global_components import Menu
from src.pages.purchase_scanner.logic import LogicController, ScannerApiError
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

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.form_card = ScannerForm(
            page=self._page,
            lang=self.lang,
            currency=self.currency,
            on_scan_click=self.handle_scan_click
        )

        self.result_card = ScannerResult(
            page=self._page,
            lang=self.lang,
            currency=self.currency
        )

        self.history_card = ScannerHistoryCard(
            page=self._page,
            lang=self.lang,
            on_delete_entry=self.handle_delete_history_entry,
            on_clear_all=self.handle_clear_history,
            currency=self.currency,
        )

        self.history_card.set_history(self.scan_history)
        self.google_required_message = Text.SMALL(
            self.lang["purchase_scanner.google_required"],
            color=Color.SECONDARY_TEXT,
        )
        self.google_required_card = ft.Container(
            visible=not db.app_settings.has_google_account_session(),
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Row(
                spacing=12,
                wrap=True,
                controls=[
                    ft.Icon(
                        ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                        color=Color.PRIMARY_ACTION,
                        size=24,
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            Text.MEDIUM(
                                self.lang["purchase_scanner.google_required_title"],
                                color=Color.PRIMARY_TEXT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            self.google_required_message,
                        ],
                    ),
                    ft.TextButton(
                        content=self.lang["purchase_scanner.google_login_action"],
                        on_click=self._open_google_settings,
                    ),
                ],
            ),
        )
        self.usage_label = Text.MEDIUM(
            self.lang["purchase_scanner.usage_loading"],
            color=Color.PRIMARY_TEXT,
        )
        self.usage_progress = ft.ProgressBar(
            value=1,
            color=Color.PROGRESS_ACTIVE,
            bgcolor=Color.DARK_BUTTON,
            height=8,
        )
        self.usage_card = ft.Container(
            visible=db.app_settings.has_google_account_session(),
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=18,
            padding=18,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Column(
                spacing=10,
                controls=[self.usage_label, self.usage_progress],
            ),
        )
        self.scanner_locked_overlay = ft.Container(
            visible=not db.app_settings.has_google_account_session(),
            left=0,
            top=0,
            right=0,
            bottom=0,
            blur=ft.Blur(6, 6),
            bgcolor=ft.Colors.with_opacity(0.45, Color.DARK_SURFACE),
            alignment=ft.Alignment.CENTER
        )

        self.header_banner = ft.Container(
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

        self.scan_cards_row = ft.Column(
            spacing=20,
            controls=[
                self.form_card,
                self.result_card,
            ],
        )
        self.scan_cards_stack = ft.Stack(
            expand=True,
            controls=[self.scan_cards_row, self.scanner_locked_overlay],
        )

        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                spacing=20,
                expand=True,
                controls=[
                    self.header_banner,
                    self.google_required_card,
                    self.usage_card,
                    self.scan_cards_stack,
                    ft.Container(
                        self.history_card,
                        margin=ft.Margin.only(top=4)
                    )
                ]
            )
        )
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
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
        self._update_google_access()

    def _open_google_settings(self, e=None):
        self._page.navigate_to("/user_management")()

    def _update_google_access(self):
        signed_in = db.app_settings.has_google_account_session()
        self.google_required_card.visible = not signed_in
        self.usage_card.visible = signed_in
        self.scanner_locked_overlay.visible = not signed_in
        if signed_in and self._is_cached_developer():
            self._show_unlimited_usage()
            self.form_card.set_enabled(True)
        else:
            self.form_card.set_enabled(False)

    @staticmethod
    def _is_cached_developer() -> bool:
        account = db.app_settings.get_google_account()
        return bool(
            account
            and db.app_settings.get_google_account_tier(account["uid"])
            == "developer"
        )

    def _show_unlimited_usage(self) -> None:
        self.usage_label.value = self.lang["purchase_scanner.usage_unlimited"]
        self.usage_progress.value = 1
        self.usage_progress.color = Color.PROGRESS_ACTIVE

    def _load_monthly_usage(self):
        if self._is_cached_developer():
            self._show_unlimited_usage()
            self.form_card.set_enabled(db.app_settings.has_google_account_session())
            self._page.update()
            return
        refresh_token = db.app_settings.get_google_refresh_token()
        try:
            usage = self.controller.get_monthly_usage(refresh_token or "")
            remaining = usage["remaining"]
            limit = usage["limit"]
            if limit is None:
                if remaining is not None:
                    raise ValueError("Unlimited scanner usage must not have a remaining count")
                self.usage_label.value = self.lang[
                    "purchase_scanner.usage_unlimited"
                ]
                progress = 1.0
            else:
                if (
                    not isinstance(remaining, int)
                    or not isinstance(limit, int)
                    or not 0 <= remaining <= limit
                ):
                    raise ValueError("Invalid monthly usage counts")
                reset_at = datetime.fromisoformat(usage["reset_at"])
                if reset_at.tzinfo is None:
                    reset_at = reset_at.replace(tzinfo=timezone.utc)
                reset_label = reset_at.astimezone().strftime("%Y-%m-%d %H:%M")
                remaining_label = self.lang[
                    "purchase_scanner.usage_remaining"
                ].format(remaining=remaining, limit=limit, reset=reset_label)
                progress = remaining / limit
                self.usage_label.value = remaining_label
            self.usage_progress.value = progress
            self.form_card.set_enabled(
                (limit is None or remaining > 0)
                and db.app_settings.has_google_account_session()
            )
            self.usage_progress.color = (
                Color.PROGRESS_ACTIVE
                if limit is None or remaining
                else Color.WARNING_COLOR
            )
        except ScannerApiError as ex:
            Logger.warning(f"Could not load purchase scanner monthly usage: {ex}")
            self.usage_label.value = self.lang["purchase_scanner.usage_unavailable"]
            self.form_card.set_enabled(False)
            if ex.status_code in (401, 403):
                self.google_required_message.value = self.lang[
                    "purchase_scanner.google_session_expired"
                ]
                self.google_required_card.visible = True
                self.usage_card.visible = False
                self.scanner_locked_overlay.visible = True
                self.form_card.set_enabled(False)
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(f"Invalid purchase scanner usage response: {ex}")
            self.usage_label.value = self.lang["purchase_scanner.usage_unavailable"]
            self.form_card.set_enabled(False)
        try:
            self.usage_card.update()
            self.google_required_card.update()
            self.form_card.update()
        except RuntimeError:
            pass

    def handle_scan_click(self, name, price, reason, trigger, time):
        if not db.app_settings.has_google_account_session():
            return
        self.form_card.set_scanning(True)
        self._page.update()
        request_generation = self.result_card.set_loading_state()
        item_name = name if name else self.lang["purchase_scanner.item"]

        def worker():
            try:
                risk, trigger_display, price_val, ai_advice = self.controller.analyze_purchase(
                    item_name,
                    price,
                    reason,
                    trigger,
                    time,
                    db.app_settings.get_google_refresh_token() or "",
                )

                if risk is not None:
                    self.controller.save_scan_result(item_name, price_val, trigger, reason, time, risk, trigger_display, ai_advice)
                    self.history_card.set_history(self.controller.get_scan_history())

                if risk is None:
                    self._page.run_task(
                        self.result_card.show_troll_result,
                        request_generation,
                        risk,
                        trigger_display,
                        price_val,
                        item_name,
                        ai_advice,
                    )
                else:
                    self.result_card.update_result(
                        risk,
                        trigger_display,
                        price_val,
                        item_name,
                        ai_advice,
                    )

            except ScannerApiError as ex:
                Logger.warning(f"Purchase scanner request rejected: {ex}")
                if ex.status_code == 429:
                    error_message = self.lang["purchase_scanner.monthly_limit"]
                    self.form_card.set_enabled(False)
                elif ex.status_code in (401, 403):
                    error_message = self.lang["purchase_scanner.sign_in_required"]
                    self.google_required_card.visible = True
                    self.usage_card.visible = False
                    self.scanner_locked_overlay.visible = True
                    self.form_card.set_enabled(False)
                elif ex.status_code == 0:
                    error_message = self.lang["purchase_scanner.connection_error"]
                else:
                    error_message = self.lang["purchase_scanner.service_error"]
                self.result_card.show_error(error_message)
            except Exception as ex:
                Logger.error(f"Error during background analysis: {ex}")
                self.result_card.show_error(
                    self.lang["purchase_scanner.service_error"]
                )
            finally:
                if db.app_settings.get_google_refresh_token():
                    self._load_monthly_usage()
                self.form_card.set_scanning(False)
                self._page.update()

        self._page.run_thread(worker)

    def handle_delete_history_entry(self, entry):
        self.controller.delete_scan_result(entry)
        self.history_card.set_history(self.controller.get_scan_history())

    def handle_clear_history(self):
        self.controller.clear_scan_history()
        self.history_card.set_history(self.controller.get_scan_history())

    def _refresh_view(self) -> int:
        try:
            self._update_google_access()
            self._on_page_resize()
            self.scan_history = self.controller.get_scan_history()
            self.history_card.set_history(self.scan_history)
            if db.app_settings.has_google_account_session():
                self._page.run_thread(self._load_monthly_usage)
            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_item_size = page_width // self.menu.items_count
            menu_item_height = max(48, menu_item_size)
            menu_inside_size = menu_item_size // 6 * 5
            menu_inside_height = menu_item_height // 6 * 5
            menu_label_size = 8 if menu_item_size < 48 else 10
            menu_icon_size = 18 if menu_item_size < 48 else 20
            menu_label_spacing = 2 if menu_item_size < 48 else 4
            menu_label_visible = menu_item_size >= 48
            banner_height = (
                self.menu.BANNER_HEIGHT
                if self.menu.ad_banner is not None
                and page_width >= self.menu.BANNER_WIDTH
                else 0
            )
            menu_total_height = menu_item_height + banner_height
            content_width = max(0, page_width - UISettings.CARD_PADDING * 2)
            component_content_width = max(0, content_width - 48)
            intervention_width = max(0, component_content_width - 28)
            illustration_size = min(240, component_content_width)
            thinking_unit_width = min(150, component_content_width // 2)
            thinking_value_width = max(
                0, component_content_width - thinking_unit_width - 10
            )
            history_content_width = max(0, content_width - 24)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            self.content_container.width = page_width
            self.header_banner.width = content_width
            self.google_required_card.width = content_width
            self.usage_card.width = content_width
            self.scan_cards_stack.width = content_width
            self.scan_cards_row.width = content_width
            self.scanner_locked_overlay.width = content_width
            self.scanner_locked_overlay.height = page_height
            self.form_card.resize(
                width=content_width,
                content_width=component_content_width,
                thinking_value_width=thinking_value_width,
                thinking_unit_width=thinking_unit_width,
            )
            self.result_card.resize(
                width=content_width,
                content_width=component_content_width,
                intervention_width=intervention_width,
                illustration_size=illustration_size,
            )
            self.history_card.resize(
                width=content_width,
                content_width=history_content_width,
            )

            # Resizing other components
            self.menu.resize(
                width=page_width,
                item_size=menu_item_size,
                item_height=menu_item_height,
                inside_size=menu_inside_size,
                inside_height=menu_inside_height,
                banner_height=banner_height,
                total_height=menu_total_height,
                label_size=menu_label_size,
                icon_size=menu_icon_size,
                label_spacing=menu_label_spacing,
                label_visible=menu_label_visible,
            )
            self.main_container.margin.bottom = self.menu.reserved_height

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