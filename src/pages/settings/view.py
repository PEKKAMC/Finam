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
        self.settings_header = SettingsHeader(lang=self.lang)
        self.header_divider = ft.Divider(
            height=10, thickness=1, color=Color.INPUT_BORDER
        )

        self.language_dropdown = SettingDropdown(
            language_options, active_index=language_index
        )
        self.language_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.LANGUAGE,
                    title=self.lang["settings.language"],
                    subtitle=self.lang["settings.language_options"],
                    control=self.language_dropdown,
                )
            ]
        )

        self.theme_dropdown = SettingDropdown(theme_options, active_index=theme_index)
        self.theme_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.PALETTE_OUTLINED,
                    title=self.lang["settings.theme"],
                    subtitle=self.lang["settings.theme_options"],
                    control=self.theme_dropdown,
                )
            ]
        )

        self.currency_dropdown = SettingDropdown(
            self.currencies,
            active_index=currency_index,
            menu_height=240,
            searchable=True,
        )

        self.currency_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.PAID_OUTLINED,
                    title=self.lang["settings.currency"],
                    subtitle=self.lang["settings.currency_format"],
                    control=self.currency_dropdown,
                )
            ]
        )

        self.digit_separator_dropdown = SettingDropdown(
            digit_separator_options,
            active_index=digit_separator_index,
        )

        self.digit_separator_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.FORMAT_LIST_NUMBERED,
                    title=self.lang["settings.digit_separator"],
                    subtitle=self.lang["settings.digit_separator_options"],
                    control=self.digit_separator_dropdown,
                )
            ]
        )

        self.decimal_separator_dropdown = SettingDropdown(
            decimal_separator_options,
            active_index=decimal_separator_index,
        )

        self.decimal_separator_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.NUMBERS,
                    title=self.lang["settings.decimal_separator"],
                    subtitle=self.lang["settings.decimal_separator_options"],
                    control=self.decimal_separator_dropdown,
                )
            ]
        )

        self.app_lock_switch = ft.Switch(
            value=initial_settings["app_lock"],
            active_color=Color.PRIMARY_ACTION,
            on_change=self._on_app_lock_changed,
        )

        self.system_prefs_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.FINGERPRINT,
                    title=self.lang["settings.app_lock"],
                    subtitle=self.lang["settings.lock_requirement"],
                    control=self.app_lock_switch,
                ),
                ft.Container(height=4),
            ]
        )

        self.cache_card = SettingCard(
            controls=[
                SettingRow(
                    icon=ft.Icons.DELETE_OUTLINE,
                    title=self.lang["settings.clear_cache_title"],
                    subtitle=self.lang["settings.clear_cache_desc"],
                    control=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SECONDARY_TEXT),
                    on_click=self._show_clear_cache_dialog,
                )
            ]
        )

        self.dialogs = SettingsDialogs(
            page=self._page,
            lang=self.lang,
            on_clear_cache=self._clear_cached_views,
        )

        self.done_button = ft.Container(
            content=Text.H4(self.lang["settings.done"], color=Color.WHITE),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._on_done_click,
        )

        self.done_button_wrapper = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=ft.Padding.symmetric(
                horizontal=20,
                vertical=12,
            ),
            content=self.done_button,
        )

        # Store helpers for saving settings
        self.language_name_to_code = language_name_to_code
        self.theme_label_to_name = theme_label_to_name

        # INITIALIZE MAIN CONTAINER
        self.page_content = SettingsPageContent(
            header=self.settings_header,
            header_divider=self.header_divider,
            cards=[
                self.language_card,
                self.theme_card,
                self.currency_card,
                self.digit_separator_card,
                self.decimal_separator_card,
                self.system_prefs_card,
                self.cache_card,
            ],
            done_button=self.done_button,
        )

        super().__init__(
            route="/settings",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.page_content
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

    def _show_clear_cache_dialog(self, _e: ft.ControlEvent | None = None) -> None:
        self.dialogs.clear_cache_dialog.show()

    def _clear_cached_views(self, e: ft.ControlEvent | None = None) -> None:
        try:
            self._page.delete_all_cached_views()
        except RuntimeError as ex:
            Logger.error(f"Failed to clear cached views: {ex}. Event: {e}")
            self.dialogs.clear_cache_dialog.dismiss()
            self.dialogs.result_text.value = self.lang[
                "settings.clear_cache_failed"
            ]
        else:
            self.dialogs.clear_cache_dialog.dismiss()
            self.dialogs.result_text.value = self.lang[
                "settings.clear_cache_success"
            ]

        self.dialogs.clear_cache_result_dialog.show()

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
            on_saved=pin_setup_saved,
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
            DefaultSettings.LANGUAGE,
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
            decimal_separator=selected_decimal_separator,
        )
        if status == 1:
            self.dialogs.separator_warning_dialog.show()
            return
        if status != 0:
            return

        ThemeManager.set_theme(
            selected_theme,
            system_dark=self._page.platform_brightness == ft.Brightness.DARK,
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
            action_width = scale_width(page_width, 130)
            text_width = scale_width(page_width, 230)

            # Resizing main container
            self.page_content.resize(
                page_width=page_width,
                page_height=page_height,
                content_width=content_width,
                card_content_width=card_content_width,
                text_width=text_width,
                action_width=action_width,
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
