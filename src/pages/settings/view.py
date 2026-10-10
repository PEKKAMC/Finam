# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.settings.components import SettingCard, SettingDropdown, SettingRow, SettingsHeader
from src.pages.settings.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, Text, UISettings
from src.database import db

Logger.info("Initializing Settings page...")

class SettingsView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info)

        # FETCH DATA
        self.currencies = self.controller.get_world_currencies()

        # GET CURRENT SETTINGS FROM DATABASE
        username = user_info.get("username", "Admin")
        current_language = db.users.get_language(username)
        current_currency = db.users.get_currency(username)

        # Map language code to display name
        language_options = ["Tiếng Việt", "English"]
        language_code_to_name = {"vi": "Tiếng Việt", "en": "English"}
        language_name_to_code = {"Tiếng Việt": "vi", "English": "en"}
        current_language_name = language_code_to_name.get(current_language, "Tiếng Việt")
        language_index = language_options.index(current_language_name) if current_language_name in language_options else 0

        # Get currency index
        currency_index = self.currencies.index(current_currency) if current_currency in self.currencies else self.currencies.index("VND (đ)")

        # INITIALIZE PAGE COMPONENTS
        self.settings_header = SettingsHeader(lang=self.lang)
        self.header_divider = ft.Divider(height=10, thickness=1, color=Color.INPUT_BORDER)

        self.language_dropdown = SettingDropdown(language_options, active_index=language_index)
        self.language_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.LANGUAGE,
                    title=self.lang["settings.language"],
                    subtitle=self.lang["settings.language_options"],
                    control=self.language_dropdown
                )
            ]
        )

        self.currency_dropdown = SettingDropdown(self.currencies, active_index=currency_index)
        self.currency_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.PAID_OUTLINED,
                    title=self.lang["settings.currency"],
                    subtitle=self.lang["settings.currency_format"],
                    control=self.currency_dropdown
                )
            ]
        )

        self.system_prefs_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.FINGERPRINT,
                    title=self.lang["settings.app_lock"],
                    subtitle=self.lang["settings.lock_requirement"],
                    control=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                ),
                ft.Container(height=4),
                SettingRow(
                    icon=ft.Icons.VOLUME_UP_OUTLINED,
                    title=self.lang["settings.sound_haptic"],
                    subtitle=self.lang["settings.touch_effect"],
                    control=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                )
            ]
        )

        self.done_btn_text = Text.H4(self.lang["settings.done"], color=Color.WHITE)

        self.done_btn = ft.Container(
            content=self.done_btn_text,
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._on_done_click
        )

        # Store helpers for saving settings
        self.language_name_to_code = language_name_to_code

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=18,
                            expand=True,
                            controls=[
                                self.settings_header,
                                self.header_divider,
                                self.language_card,
                                self.currency_card,
                                self.system_prefs_card,
                                self.done_btn
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
            route="/settings",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    async def _on_done_click(self, e=None):
        """Handle the Done button click - saves settings and navigates."""
        username = self.user_info.get("username", "Admin")

        selected_language_name = self.language_dropdown.dropdown_control.value
        selected_currency = self.currency_dropdown.dropdown_control.value
        selected_language_code = self.language_name_to_code.get(selected_language_name, "vi")

        db.users.set_language(username, selected_language_code)
        db.users.set_currency(username, selected_currency)

        Logger.info(f"Settings saved - Language: {selected_language_code}, Currency: {selected_currency}")

        await self._page.push_route("/user_management")

    def refresh_view(self) -> int:
        try:
            self._page.update()
            return 0
        except RuntimeError as e:
            Logger.warn(f"Failed to refresh view {e}")
            return -1

    def _on_page_resize(self, e = None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        # Resizing main container
        self.main_container.width = page_width
        self.main_container.height = page_height

        # Resizing other components
        self.settings_header.resize(width=page_width)
        self.language_card.resize(width=page_width)
        self.currency_card.resize(width=page_width)
        self.system_prefs_card.resize(width=page_width)

        return e


def get_settings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Settings page...")
    return SettingsView(page, lang, user_info)