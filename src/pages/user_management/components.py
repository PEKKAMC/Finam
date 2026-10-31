# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
from collections.abc import Callable

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings


class ProfileCard(ft.Container):
    def __init__(self, username: str, lang: dict, on_change_user: Callable):
        self.username = username
        self.lang = lang
        self.on_change_user = on_change_user

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.account_type_text = Text.SMALL(self.lang["user_management.personal_account"], color=Color.LIGHT_ACCENT)
        self.change_btn_text = Text.SMALL(self.lang["user_management.change"], color=Color.WHITE, weight=ft.FontWeight.BOLD)

        # Static icons
        self.avatar_icon = ft.Icon(ft.Icons.PERSON, color=Color.PRIMARY, size=32)
        self.change_user_icon = ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=Color.WHITE, size=16)
        self.chevron_icon = ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.WHITE, size=16)

        # Dynamic texts
        user_display = self.username if self.username else ""
        self.user_name_text = Text.H4(user_display, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.active_user_text = Text.MEDIUM(
            self.username if self.username else self.lang["user_management.no_user_selected"],
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )

        # CONTAINER COMPONENTS
        self.avatar_box = ft.Stack(
            controls=[
                ft.CircleAvatar(
                    radius=26,
                    bgcolor=Color.LIGHT_ACCENT,
                    content=self.avatar_icon
                )
            ]
        )

        self.user_info_column = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.user_name_text]
                ),
                self.account_type_text
            ]
        )

        self.change_user_button = ft.Container(
            content=ft.Row(
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.change_user_icon,
                    self.change_btn_text,
                    self.chevron_icon
                ]
            ),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=16,
            on_click=lambda e: self.on_change_user(),
            ink=True
        )

        self.top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.avatar_box,
                        self.user_info_column
                    ]
                ),
                self.change_user_button
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=14,
                controls=[
                    self.top_row
                ]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            content=self.main_container
        )

    def update_data(self, username: str):
        self.username = username
        self.user_name_text.value = username if username else ""
        self.active_user_text.value = username if username else self.lang["user_management.no_user_selected"]
        self.update()

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class GoogleAccountCard(ft.Container):
    def __init__(self, lang: dict, on_connect: Callable, on_disconnect: Callable):
        self.lang = lang
        self.account_status = Text.SMALL(
            self.lang["user_management.google_not_connected"],
            color=Color.SECONDARY_TEXT,
        )
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)
        self.connect_button = ft.TextButton(
            content=self.lang["user_management.google_sign_in"],
            on_click=on_connect,
        )
        self.disconnect_button = ft.TextButton(
            content=self.lang["user_management.google_disconnect"],
            on_click=on_disconnect,
            visible=False,
        )
        self.main_container = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=Color.PRIMARY_ACTION, size=22),
                            bgcolor=Color.AGGREGATE_BACKGROUND,
                            padding=10,
                            border_radius=14,
                        ),
                        ft.Column(
                            expand=True,
                            spacing=2,
                            controls=[
                                Text.MEDIUM(
                                    self.lang["user_management.google_title"],
                                    color=Color.PRIMARY_TEXT,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                self.account_status,
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=0,
                    controls=[self.connect_button, self.disconnect_button],
                ),
                self.error_text,
            ],
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            padding=UISettings.CARD_PADDING,
            content=self.main_container,
        )

    def set_account(self, email: str | None) -> None:
        self.account_status.value = (
            f"{self.lang['user_management.google_connected']}: {email}"
            if email
            else self.lang["user_management.google_not_connected"]
        )
        self.disconnect_button.visible = bool(email)
        self.error_text.value = ""
        self._update_if_attached()

    def set_busy(self, busy: bool) -> None:
        self.connect_button.disabled = busy
        self.disconnect_button.disabled = busy
        self._update_if_attached()

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self._update_if_attached()

    def _update_if_attached(self) -> None:
        if self.page is not None:
            self.update()

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width


class MenuItem(ft.Container):
    def __init__(self, icon, icon_color: str, icon_bg_color: str, title: str, subtitle: str, badge_text: str | None = None, badge_bg: str | None = None, badge_color: Color | None = None, trailing: ft.Control | None = None, on_click: Callable | None = None):
        # TEXT AND ICON COMPONENTS
        self.title_text = Text.MEDIUM(title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.subtitle_text = Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)
        self.main_icon = ft.Icon(icon, color=icon_color, size=20)
        self.trailing_control = trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SUBTITLE_TEXT, size=20)

        # CONTAINER COMPONENTS
        self.badge_control = None
        if badge_text:
            self.badge_control = ft.Container(
                content=Text.SMALL(badge_text, color=badge_color or Color.PRIMARY, weight=ft.FontWeight.BOLD),
                bgcolor=badge_bg or Color.LIGHT_ACCENT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            )

        self.title_row_controls: list[ft.Control] = [self.title_text]
        if self.badge_control:
            self.title_row_controls.append(self.badge_control)

        self.icon_container = ft.Container(
            content=self.main_icon,
            bgcolor=icon_bg_color,
            padding=10,
            border_radius=14
        )

        self.text_column = ft.Column(
            spacing=2,
            expand=True,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.title_row_controls
                ),
                self.subtitle_text
            ]
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        self.icon_container,
                        self.text_column
                    ]
                ),
                self.trailing_control
            ]
        )

        super().__init__(
            padding=ft.Padding.symmetric(vertical=14, horizontal=16),
            on_click=on_click,
            ink=True if on_click else False,
            content=self.main_row
        )


class MenuSectionCard(ft.Container):
    def __init__(self, items: list[ft.Control]):
        self.items = items

        # CONTAINER COMPONENTS
        self.controls = []
        for i, item in enumerate(self.items):
            self.controls.append(item)
            if i < len(self.items) - 1:
                self.controls.append(ft.Divider(height=1, color=Color.CARD_DIVIDER, thickness=1))

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=0,
                controls=self.controls
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            content=self.main_container
        )

    def resize(self, width: int):
        self.width = width
        self.main_container.width = width
        self.main_container.content.width = width


class DeleteAllDataDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_confirm_callback: Callable):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm_callback

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["user_management.confirm_delete_all_data_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.content_text = Text.P(self.lang["user_management.confirm_delete_all_data_content"], color=Color.SECONDARY_TEXT)
        self.cancel_text = Text.BUTTON(self.lang["generic.cancel"], color=Color.SECONDARY_TEXT)
        self.delete_text = Text.BUTTON(self.lang["generic.delete"], color=Color.DELETE_ACTION, weight=ft.FontWeight.BOLD)

        self.main_container = ft.Container(
            padding=12,
            content=ft.Column(
                spacing=16,
                tight=True,
                controls=[
                    self.title_text,
                    self.content_text,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                        controls=[
                            ft.TextButton(
                                content=self.cancel_text,
                                on_click=lambda e: self.dismiss()
                            ),
                            ft.TextButton(
                                content=self.delete_text,
                                on_click=self._handle_confirm
                            )
                        ]
                    )
                ]
            )
        )

        super().__init__(
            color=Color.DIALOG_BACKGROUND,
            dialog_content=self.main_container
        )

    async def _handle_confirm(self, e=None):
        self.dismiss()
        if self.on_confirm:
            res = self.on_confirm(e)
            if asyncio.iscoroutine(res):
                await res

    def resize(self, width: int) -> None:
        self.main_container.width = width