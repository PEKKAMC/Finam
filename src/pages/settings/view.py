# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.settings.components import SettingsHeader, SettingCard, SettingRow, SettingDropdown
from src.utils import Color, Page, get_safe_page_size, UISettings, Text

Logger.info("Initializing Settings page...")


class SettingsView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE COMPONENTS
        self.done_btn = ft.Container(
            content=Text.H4(self.lang["ui.settings.done"], color=Color.WHITE),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._page.navigate_to("/user_management")
        )

        WORLD_CURRENCIES = [ # Temporary
            "AED (د.إ)", "AFN (؋)", "ALL (L)", "AMD (֏)", "ANG (ƒ)", "AOA (Kz)",
            "ARS ($)", "AUD (A$)", "AWG (ƒ)", "AZN (₼)", "BAM (KM)", "BBD ($)",
            "BDT (৳)", "BGN (лв)", "BHD (.د.ب)", "BIF (FBu)", "BMD ($)", "BND (B$)",
            "BOB (Bs.)", "BRL (R$)", "BSD (B$)", "BTN (Nu.)", "BWP (P)", "BYN (Br)",
            "BZD (BZ$)", "CAD (C$)", "CDF (FC)", "CHF (CHF)", "CLP ($)", "CNY (¥)",
            "COP ($)", "CRC (₡)", "CUP ($)", "CVE (Esc)", "CZK (Kč)", "DJF (Fdj)",
            "DKK (kr)", "DOP (RD$)", "DZD (د.ج)", "EGP (£)", "ERN (Nfk)", "ETB (Br)",
            "EUR (€)", "FJD (FJ$)", "FKP (£)", "GBP (£)", "GEL (₾)", "GHS (GH₵)",
            "GIP (£)", "GMD (D)", "GNF (FG)", "GTQ (Q)", "GYD (G$)", "HKD (HK$)",
            "HNL (L)", "HTG (G)", "HUF (Ft)", "IDR (Rp)", "ILS (₪)", "INR (₹)",
            "IQD (ع.د)", "IRR (﷼)", "ISK (kr)", "JMD (J$)", "JOD (د.ا)", "JPY (¥)",
            "KES (KSh)", "KGS (с)", "KHR (៛)", "KMF (CF)", "KPW (₩)", "KRW (₩)",
            "KWD (د.ك)", "KYD (CI$)", "KZT (₸)", "LAK (₭)", "LBP (ل.ل)", "LKR (Rs)",
            "LRD (L$)", "LSL (L)", "LYD (ل.د)", "MAD (د.م.)", "MDL (L)", "MGA (Ar)",
            "MKD (ден)", "MMK (K)", "MNT (₮)", "MOP (MOP$)", "MRU (UM)", "MUR (₨)",
            "MVR (Rf)", "MWK (MK)", "MXN ($)", "MYR (RM)", "MZN (MT)", "NAD (N$)",
            "NGN (₦)", "NIO (C$)", "NOK (kr)", "NPR (रु)", "NZD (NZ$)", "OMR (ر.ع.)",
            "PAB (B/.)", "PEN (S/.)", "PGK (K)", "PHP (₱)", "PKR (₨)", "PLN (zł)",
            "PYG (₲)", "QAR (ر.ق)", "RON (lei)", "RSD (дин.)", "RUB (₽)", "RWF (FRw)",
            "SAR (ر.س)", "SBD (SI$)", "SCR (₨)", "SDG (ج.س.)", "SEK (kr)", "SGD (S$)",
            "SHP (£)", "SLL (Le)", "SOS (Sh)", "SRD ($)", "SSP (£)", "STN (Db)",
            "SYP (£S)", "SZL (L)", "THB (฿)", "TJS (ЅМ)", "TMT (T)", "TND (د.ت)",
            "TOP (T$)", "TRY (₺)", "TTD (TT$)", "TWD (NT$)", "TZS (TSh)", "UAH (₴)",
            "UGX (USh)", "USD ($)", "UYU ($U)", "UZS (сўм)", "VES (Bs.S)", "VND (đ)",
            "VUV (VT)", "WST (WS$)", "XAF (FCFA)", "XCD (EC$)", "XOF (CFA)", "XPF (₣)",
            "YER (﷼)", "ZAR (R)", "ZMW (ZK)", "ZWL (Z$)"
        ]

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
                                SettingsHeader(lang=self.lang),
                                ft.Divider(height=10, thickness=1, color=Color.INPUT_BORDER),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.LANGUAGE,
                                            title=self.lang["ui.settings.language"],
                                            subtitle=self.lang["ui.settings.language_options"],
                                            control=SettingDropdown(["Tiếng Việt", "English"], active_index=0)
                                        )
                                    ]
                                ),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.PAID_OUTLINED,
                                            title=self.lang["ui.settings.currency"],
                                            subtitle=self.lang["ui.settings.currency_format"],
                                            control=SettingDropdown(WORLD_CURRENCIES, active_index=WORLD_CURRENCIES.index("VND (đ)"))
                                        )
                                    ]
                                ),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.FINGERPRINT,
                                            title=self.lang["ui.settings.app_lock"],
                                            subtitle=self.lang["ui.settings.lock_requirement"],
                                            control=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                                        ),
                                        ft.Container(height=4),
                                        SettingRow(
                                            icon=ft.Icons.VOLUME_UP_OUTLINED,
                                            title=self.lang["ui.settings.sound_haptic"],
                                            subtitle=self.lang["ui.settings.touch_effect"],
                                            control=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                                        )
                                    ]
                                ),

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
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def on_page_resize(self, e=None) -> None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        self.main_container.width = page_width
        self.main_container.height = page_height

        return e

def get_settings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    return SettingsView(page, lang, user_info)