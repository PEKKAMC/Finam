# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
from pathlib import Path

import flet as ft

from src.logger import Logger
from src.pages.settings.components import SettingCard, SettingDropdown, SettingRow, SettingsHeader
from src.pages.settings.logic import LogicController
from src.utils import Color, DefaultSettings, Dialog, Page, get_asset_path, get_safe_page_size, Text, UISettings
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
        self.currencies = self.controller.get_currencies()

        # GET CURRENT SETTINGS FROM DATABASE
        username = self.user_info["username"]
        current_language = db.users.get_language(username)
        current_currency = db.users.get_currency(username)

        language_files = sorted(Path(get_asset_path("lang")).glob("*.json"))
        if not language_files:
            raise FileNotFoundError("No language files found in assets/lang")

        language_options = []
        language_name_to_code = {}
        for language_file in language_files:
            with language_file.open("r", encoding="utf-8-sig") as file:
                language_name = json.load(file)["language"]
            language_options.append(language_name)
            language_name_to_code[language_name] = language_file.stem

        language_code_to_name = {code: name for name, code in language_name_to_code.items()}
        current_language_name = language_code_to_name.get(current_language, language_options[0])
        language_index = language_options.index(current_language_name) if current_language_name in language_options else 0

        # Get currency index
        currency_index = self.currencies.index(current_currency) if current_currency in self.currencies else self.currencies.index(DefaultSettings.CURRENCY)

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

        self.currency_dropdown = SettingDropdown(self.currencies, active_index=currency_index, menu_height=240)
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

        self.app_lock_switch = ft.Switch(
            value=db.app_security.is_app_lock_enabled(),
            active_color=Color.PRIMARY_ACTION,
            on_change=self._on_app_lock_changed
        )

        self.system_prefs_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.FINGERPRINT,
                    title=self.lang["settings.app_lock"],
                    subtitle=self.lang["settings.lock_requirement"],
                    control=self.app_lock_switch
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

    def _on_app_lock_changed(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self._show_pin_setup_dialog()
            return

        db.app_security.disable_app_lock()
        self._page.update()

    def _show_pin_setup_dialog(self) -> None:
        pin_field = ft.TextField(
            label=self.lang["settings.pin"],
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            password=True,
            max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        confirm_pin_field = ft.TextField(
            label=self.lang["settings.confirm_pin"],
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            password=True,
            max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        error_text = ft.Text(color=Color.NEGATIVE_ACTION)

        def close_dialog(e=None) -> None:
            self._pin_setup_dialog.dismiss()
            self.app_lock_switch.value = db.app_security.is_app_lock_enabled()
            self._page.update()

        def save_pin(e=None) -> None:
            pin = pin_field.value or ""
            confirm_pin = confirm_pin_field.value or ""
            if len(pin) != 4 or not pin.isascii() or not pin.isdigit():
                error_text.value = self.lang["settings.pin_invalid"]
                error_text.update()
                return
            if pin != confirm_pin:
                error_text.value = self.lang["settings.pin_mismatch"]
                error_text.update()
                return
            if not db.app_security.set_app_lock_pin(pin):
                error_text.value = self.lang["settings.pin_invalid"]
                error_text.update()
                return

            self._pin_setup_dialog.dismiss()
            self.app_lock_switch.value = True
            self._page.update()

        self._pin_setup_dialog = Dialog(
            dialog_content=ft.Column(
                tight=True,
                controls=[
                    Text.H4(self.lang["settings.pin_title"], color=Color.PRIMARY_TEXT),
                    pin_field,
                    confirm_pin_field,
                    error_text
                ]
            ),
            color=Color.WHITE,
            options=[
                ft.TextButton(self.lang["generic.cancel"], on_click=close_dialog),
                ft.TextButton(self.lang["generic.save"], on_click=save_pin)
            ]
        )
        self._pin_setup_dialog._dialog_page = self._page
        self._pin_setup_dialog.show()

    async def _on_done_click(self, e=None):
        """Handle the Done button click - saves settings and navigates."""
        username = self.user_info["username"]

        selected_language_name = self.language_dropdown.dropdown_control.value
        selected_currency = self.currency_dropdown.dropdown_control.value
        selected_language_code = self.language_name_to_code.get(selected_language_name, "vi")

        db.users.set_language(username, selected_language_code)
        db.users.set_currency(username, selected_currency)

        Logger.info(f"Settings saved - Language: {selected_language_code}, Currency: {selected_currency}")

        await self._page.push_route("/user_management")

    def _refresh_view(self) -> int:
        try:
            self._page.update()
            return 0
        except RuntimeError as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e = None) -> int:
        try:
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


def get_settings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Settings page...")
    return SettingsView(page, lang, user_info)