# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.settings.components import SettingCard, SettingDropdown, SettingRow, SettingsDialogs, SettingsHeader, SettingsPageContent
from src.pages.settings.logic import LogicController
from src.utils import Color, DefaultSettings, Data, Page, Text, ThemeManager, UISettings, get_safe_page_size, scale_width

Logger.info("Initializing Settings page...")

INTEGER_REGEX = Data().get_regex_string("integer")


class SettingsView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
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
        initial_settings = self.controller.get_initial_settings(username)
        current_language = initial_settings["language"]
        current_currency = initial_settings["currency"]
        current_theme = initial_settings["theme"]
        current_digit_separator = initial_settings["digit_separator"]
        current_decimal_separator = initial_settings["decimal_separator"]
        language_name_to_code = initial_settings["language_name_to_code"]
        language_options = list(language_name_to_code)

        language_code_to_name = {
            code: name for name, code in language_name_to_code.items()
        }
        current_language_name = language_code_to_name.get(
            current_language, language_options[0]
        )
        language_index = (
            language_options.index(current_language_name)
            if current_language_name in language_options
            else 0
        )

        # Get currency index
        currency_index = (
            self.currencies.index(current_currency)
            if current_currency in self.currencies
            else self.currencies.index(DefaultSettings.CURRENCY)
        )

        theme_names = initial_settings["theme_names"]
        theme_name_to_label = {
            name: (
                self.lang[f"settings.theme.{name}"]
                if f"settings.theme.{name}" in self.lang
                else name.replace("_", " ").title()
            )
            for name in theme_names
        }
        theme_label_to_name = {
            label: name for name, label in theme_name_to_label.items()
        }
        theme_options = [theme_name_to_label[name] for name in theme_names]
        theme_index = theme_names.index(current_theme)
        digit_separator_options = ["None", ".", ",", "_"]
        digit_separator_values = ["", ".", ",", "_"]
        digit_separator_index = digit_separator_values.index(current_digit_separator)
        decimal_separator_options = [".", ","]
        decimal_separator_index = decimal_separator_options.index(
            current_decimal_separator
        )

        # INITIALIZE PAGE COMPONENTS
        self.settings_header = SettingsHeader(
            lang=self.lang
        )

        self.language_dropdown = SettingDropdown(
            options=language_options,
            active_index=language_index
        )

        self.language_row = SettingRow(
            icon=ft.Icons.LANGUAGE,
            title=self.lang["settings.language"],
            control=self.language_dropdown
        )

        self.theme_dropdown = SettingDropdown(
            options=theme_options,
            active_index=theme_index
        )

        self.theme_row = SettingRow(
            icon=ft.Icons.PALETTE_OUTLINED,
            title=self.lang["settings.theme"],
            control=self.theme_dropdown
        )

        self.currency_dropdown = SettingDropdown(
            self.currencies,
            active_index=currency_index,
            menu_height=240,
            searchable=True
        )

        self.currency_row = SettingRow(
            icon=ft.Icons.PAID_OUTLINED,
            title=self.lang["settings.currency"],
            control=self.currency_dropdown
        )

        self.digit_separator_dropdown = SettingDropdown(
            digit_separator_options,
            active_index=digit_separator_index
        )
        self.digit_separator_row = SettingRow(
            icon=ft.Icons.FORMAT_LIST_NUMBERED,
            title=self.lang["settings.digit_separator"],
            control=self.digit_separator_dropdown,
            compact_action_width=True,
        )

        self.decimal_separator_dropdown = SettingDropdown(
            decimal_separator_options,
            active_index=decimal_separator_index
        )

        self.decimal_separator_row = SettingRow(
            icon=ft.Icons.NUMBERS,
            title=self.lang["settings.decimal_separator"],
            control=self.decimal_separator_dropdown,
            compact_action_width=True,
        )

        self.app_lock_switch = ft.Switch(
            value=initial_settings["app_lock"],
            active_color=Color.PRIMARY_ACTION,
            on_change=self._on_app_lock_changed
        )

        self.app_lock_row = SettingRow(
            icon=ft.Icons.FINGERPRINT,
            title=self.lang["settings.app_lock"],
            control=self.app_lock_switch,
            compact_action_width=True,
        )

        self.settings_card = SettingCard(
            controls=[
                self.language_row,
                self.theme_row,
                self.currency_row,
                self.digit_separator_row,
                self.decimal_separator_row,
                self.app_lock_row,
            ]
        )

        self.dialogs = SettingsDialogs(
            page=self._page,
            lang=self.lang,
        )

        self.done_button = ft.Container(
            content=Text.H4(self.lang["settings.done"], color=Color.WHITE),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._on_done_click
        )

        self.done_button_wrapper = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=ft.Padding.symmetric(
                horizontal=20,
                vertical=12
            ),
            content=self.done_button
        )

        # Store helpers for saving settings
        self.language_name_to_code = language_name_to_code
        self.theme_label_to_name = theme_label_to_name

        # INITIALIZE MAIN CONTAINER
        self.page_content = SettingsPageContent(
            header=self.settings_header,
            cards=[self.settings_card],
            done_button=self.done_button
        )

        super().__init__(
            route="/settings",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=self.page_content
                )
            ]
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

    def _on_app_lock_changed(self, e: ft.Event[ft.Switch]) -> None:
        if e.control.value:
            self._show_pin_setup_dialog()
            return

        self.controller.disable_app_lock()
        self._page.update()

    def _show_pin_setup_dialog(self) -> None:
        def cancel_pin_setup() -> None:
            self.app_lock_switch.value = self.controller.is_app_lock_enabled()
            self._page.update()

        def pin_setup_saved() -> None:
            self.app_lock_switch.value = True
            self._page.update()

        self.dialogs.show_pin_setup(
            integer_regex=INTEGER_REGEX,
            on_save_pin=self.controller.save_app_lock_pin,
            on_cancel=cancel_pin_setup,
            on_saved=pin_setup_saved
        )
        return

    async def _on_done_click(self, _e: ft.Event[ft.Container] | None = None) -> None:
        """Handle the Done button click - saves settings and navigates."""
        username = self.user_info["username"]

        selected_language_name = self.language_dropdown.dropdown_control.value or ""
        selected_currency = (
            self.currency_dropdown.dropdown_control.value or DefaultSettings.CURRENCY
        )
        selected_language_code = self.language_name_to_code.get(
            selected_language_name,
            DefaultSettings.LANGUAGE
        )
        selected_theme_label = self.theme_dropdown.dropdown_control.value or ""
        selected_theme = self.theme_label_to_name.get(
            selected_theme_label, DefaultSettings.THEME
        )
        selected_separator_label = (
            self.digit_separator_dropdown.dropdown_control.value or "None"
        )
        selected_separator = {
            "None": "",
            ".": ".",
            ",": ",",
            "_": "_",
        }[selected_separator_label]
        selected_decimal_separator = (
            self.decimal_separator_dropdown.dropdown_control.value or "."
        )

        status = self.controller.save_settings(
            username=username,
            language=selected_language_code,
            currency=selected_currency,
            theme=selected_theme,
            digit_separator=selected_separator,
            decimal_separator=selected_decimal_separator
        )
        if status == 1:
            self.dialogs.separator_warning_dialog.show()
            return
        if status != 0:
            return

        ThemeManager.set_theme(
            selected_theme,
            system_dark=self._page.platform_brightness == ft.Brightness.DARK
        )
        self._page.theme_mode = (
            ft.ThemeMode.SYSTEM
            if selected_theme == "system"
            else (
                ft.ThemeMode.DARK
                if ThemeManager.get_theme().dark_mode
                else ft.ThemeMode.LIGHT
            )
        )
        Logger.info(
            f"Settings saved - Language: {selected_language_code}, "
            f"Currency: {selected_currency}, Theme: {selected_theme}"
        )

        await self._page.push_route("/user_management")

    def _refresh_view(self) -> int:
        try:
            self._resize_page()
            self._page.update()
        except RuntimeError as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1
        else:
            return 0

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)

            content_width = scale_width(page_width, 392)
            card_content_width = scale_width(page_width, 360)
            action_width = scale_width(page_width, 160)
            compact_action_width = scale_width(page_width, 130)

            # Resizing main container
            self.page_content.resize(
                page_width=page_width,
                page_height=page_height,
                content_width=content_width,
                card_content_width=card_content_width,
                action_width=action_width,
                compact_action_width=compact_action_width,
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_settings_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Settings page...")
    return SettingsView(page, lang, user_info)
