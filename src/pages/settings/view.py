# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.settings.components import SettingsHeader, SettingCard, SettingRow, SettingDropdown
from src.utils import Color, Page, get_safe_page_size, UISettings

Logger.info("Initializing Settings page...")


class SettingsView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        # Done Button (Xong)
        self.done_btn = ft.Container(
            content=ft.Text("Xong", size=16, weight=ft.FontWeight.BOLD, color=Color.WHITE),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._page.navigate_to("/user_management")
        )

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
                                SettingsHeader(on_close=self._page.navigate_to("/user_management")),
                                ft.Divider(height=10, thickness=1, color=Color.INPUT_BORDER),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.LANGUAGE,
                                            title="Ngôn ngữ hiển thị",
                                            subtitle="Tiếng Việt / English",
                                            control=SettingDropdown(["Tiếng Việt", "English"], active_index=0)
                                        )
                                    ]
                                ),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.PAID_OUTLINED,
                                            title="Đơn vị tiền tệ chính",
                                            subtitle="Định dạng tiền tệ sổ sách",
                                            control=SettingDropdown(["VNĐ (đ)", "USD ($)"], active_index=0)
                                        )
                                    ]
                                ),

                                SettingCard(
                                    controls=[
                                        SettingRow(
                                            icon=ft.Icons.FINGERPRINT,
                                            title="Khóa ứng dụng (Face ID / PIN)",
                                            subtitle="Yêu cầu mở khóa khi vào ứng dụng",
                                            control=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                                        ),
                                        ft.Container(height=4),
                                        SettingRow(
                                            icon=ft.Icons.VOLUME_UP_OUTLINED,
                                            title="Âm thanh & Rung xúc giác",
                                            subtitle="Hiệu ứng khi chạm nút",
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
                    self.main_container,
                    self.menu
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

        self.menu.resize(
            width=page_width
        )

        return e

def get_settings_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    return SettingsView(page, lang, user_info)