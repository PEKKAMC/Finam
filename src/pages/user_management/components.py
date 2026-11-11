# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable, Sequence
from contextlib import suppress
from inspect import isawaitable
from typing import Any

import flet as ft

from src.pages.common import AddUserField, DeleteUserDialog, UserList, UserManagementDialog
from src.utils import Color, Dialog, Page, Text, UISettings


class ProfileCard(ft.Container):
    def __init__(self, username: str, lang: dict[str, str], on_change_user: Callable[..., Any]) -> None:
        self.username = username
        self.lang = lang
        self.on_change_user = on_change_user

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.change_button_text = Text.SMALL(self.lang["user_management.change"], color=Color.WHITE, weight=ft.FontWeight.BOLD)

        # Static icons
        self.avatar_icon = ft.Icon(ft.Icons.PERSON, color=Color.PRIMARY, size=32)
        self.change_user_icon = ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=Color.WHITE, size=16)
        self.chevron_icon = ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.WHITE, size=16)

        # Dynamic texts
        user_display = self.username if self.username else ""
        self.user_name_text = Text.H4(user_display, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.active_user_text = Text.MEDIUM(
            self.username
            if self.username
            else self.lang["user_management.no_user_selected"],
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )

        self.account_type_text = Text.MEDIUM(self.lang["user_management.tier_guest"], color=Color.LIGHT_ACCENT)

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
                    self.change_button_text,
                    self.chevron_icon
                ]
            ),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=16,
            on_click=lambda _event: self.on_change_user(),
            ink=True
        )

        self.top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.avatar_box, self.user_info_column]
                ),
                self.change_user_button
            ]
        )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=14,
                controls=[self.top_row]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.main_container
        )

    def update_data(self, username: str) -> None:
        self.username = username
        self.user_name_text.value = username if username else ""
        self.active_user_text.value = (
            username if username else self.lang["user_management.no_user_selected"]
        )
        self.update()

    def set_account_tier(self, tier: str) -> None:
        tier_keys = {
            "guest": "tier_guest",
            "free": "tier_free",
            "premium": "tier_premium",
            "developer": "tier_developer",
            "unavailable": "tier_unavailable",
            "loading": "tier_loading",
        }
        key = tier_keys.get(tier, "tier_unavailable")
        self.account_type_text.value = self.lang[f"user_management.{key}"]
        self.account_type_text.color = (
            Color.NEGATIVE_ACTION if tier == "developer" else Color.LIGHT_ACCENT
        )
        # A detached account card can no longer be updated.
        with suppress(RuntimeError):
            self.account_type_text.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        if isinstance(self.main_container.content, ft.Column):
            self.main_container.content.width = content_width


class GoogleAccountCard(ft.Container):
    def __init__(self, lang: dict[str, str], on_connect: Callable[..., Any] | None, on_disconnect: Callable[..., Any]) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.connect_button_label = Text.BUTTON(self.lang["user_management.google_sign_in"])
        self.disconnect_button_label = Text.BUTTON(self.lang["user_management.google_disconnect"])
        self.google_account_title = Text.MEDIUM(self.lang["user_management.google_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.google_account_icon = ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=Color.PRIMARY_ACTION, size=22)

        # Dynamic texts
        self.account_status = Text.SMALL(self.lang["user_management.google_not_connected"], color=Color.SECONDARY_TEXT)
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)

        # CONTAINER COMPONENTS
        self.connect_button = ft.TextButton(
            content=self.connect_button_label,
            on_click=on_connect
        )

        self.disconnect_button = ft.TextButton(
            content=self.disconnect_button_label,
            on_click=on_disconnect,
            visible=False
        )

        self.main_container = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=self.google_account_icon,
                            bgcolor=Color.AGGREGATE_BACKGROUND,
                            padding=10,
                            border_radius=14
                        ),
                        ft.Column(
                            expand=True,
                            spacing=2,
                            controls=[self.google_account_title, self.account_status]
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=0,
                    controls=[self.connect_button, self.disconnect_button]
                ),
                self.error_text
            ]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.main_container
        )

    def set_account(self, email: str | None) -> None:
        self.account_status.value = (
            f"{self.lang['user_management.google_connected']}: {email}"
            if email
            else self.lang["user_management.google_not_connected"]
        )
        self.connect_button_label.value = (
            self.lang["user_management.google_switch_account"]
            if email
            else self.lang["user_management.google_sign_in"]
        )
        self.disconnect_button.visible = bool(email)
        self.error_text.value = ""
        self._update_if_attached()

    def set_busy(self, busy: bool) -> None:
        self.disconnect_button.disabled = busy
        self._update_if_attached()

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self._update_if_attached()

    def _update_if_attached(self) -> None:
        try:
            if self.page is not None:
                self.update()
        except RuntimeError:
            return

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width


class ConfirmationDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], title: str, content: str, confirm_label: str, on_confirm: Callable[..., Any]) -> None:
        self._page = page
        self.on_confirm = on_confirm

        self.title_text = Text.H3(
            title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD
        )
        self.content_text = Text.P(content, color=Color.SECONDARY_TEXT)
        self.cancel_text = Text.BUTTON(
            lang["generic.cancel"], color=Color.SECONDARY_TEXT
        )
        self.confirm_text = Text.BUTTON(
            confirm_label, color=Color.NEGATIVE_ACTION, weight=ft.FontWeight.BOLD
        )

        self.main_container = ft.Container(
            padding=12,
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    self.title_text,
                    self.content_text,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                        controls=[
                            ft.TextButton(
                                content=self.cancel_text,
                                on_click=lambda _event: self.dismiss()
                            ),
                            ft.TextButton(
                                content=self.confirm_text,
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

    async def _handle_confirm(self, event: ft.ControlEvent | None = None) -> None:
        self.dismiss()
        result = self.on_confirm(event)
        if isawaitable(result):
            await result


class MenuItem(ft.Container):
    def __init__(self, icon: ft.IconData, icon_color: str, icon_bg_color: str, title: str, badge_text: str | None = None, badge_bg: str | None = None, badge_color: Color | None = None, trailing: ft.Control | None = None, on_click: Callable[..., Any] | None = None) -> None:
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.MEDIUM(title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.badge_text_control = (
            Text.SMALL(
                badge_text,
                color=badge_color or Color.PRIMARY,
                weight=ft.FontWeight.BOLD
            )
            if badge_text
            else None
        )

        # Dynamic icons
        self.main_icon = ft.Icon(icon, color=icon_color, size=18)
        self.trailing_control = trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SUBTITLE_TEXT, size=20)

        # CONTAINER COMPONENTS
        self.badge_control = None
        if self.badge_text_control:
            self.badge_control = ft.Container(
                content=self.badge_text_control,
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
            padding=8,
            border_radius=14
        )

        self.text_column = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=self.title_row_controls
                )
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
                    controls=[self.icon_container, self.text_column]
                ),
                self.trailing_control
            ]
        )

        super().__init__(
            padding=ft.Padding.symmetric(vertical=8, horizontal=16),
            on_click=on_click,
            ink=bool(on_click),
            content=self.main_row
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_row.width = width
        self.text_column.width = width


class MenuSectionCard(ft.Container):
    def __init__(self, items: Sequence[ft.Control]) -> None:
        self.items = list(items)

        # CONTAINER COMPONENTS
        self.controls = []
        for i, item in enumerate(self.items):
            self.controls.append(item)
            if i < len(self.items) - 1:
                self.controls.append(
                    ft.Divider(height=1, color=Color.CARD_DIVIDER, thickness=1)
                )

        self.main_container = ft.Container(
            content=ft.Column(
                spacing=0,
                controls=self.controls
            )
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.main_container
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width
        if isinstance(self.main_container.content, ft.Column):
            self.main_container.content.width = width
        for item in self.items:
            resize = getattr(item, "resize", None)
            if resize is not None:
                # noinspection PyCallingNonCallable
                resize(width)


class DeleteAllDataDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], on_confirm_callback: Callable[..., Any]) -> None:
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm_callback

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["user_management.confirm_delete_all_data_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.content_text = Text.P(self.lang["user_management.confirm_delete_all_data_content"], color=Color.SECONDARY_TEXT)
        self.cancel_text = Text.BUTTON(self.lang["generic.cancel"], color=Color.SECONDARY_TEXT)
        self.delete_text = Text.BUTTON(self.lang["generic.delete"], color=Color.DELETE_ACTION, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
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
            color=Color.DIALOG_BACKGROUND, dialog_content=self.main_container
        )

    async def _handle_confirm(self, event: ft.ControlEvent | None = None) -> None:
        self.dismiss()
        if self.on_confirm:
            res = self.on_confirm(event)
            if isawaitable(res):
                await res

    def resize(self, width: int) -> None:
        self.main_container.width = width


class UserManagementDialogs:
    def __init__(self, page: Page, lang: dict[str, str], current_user: str, currencies: list[str], default_currency: str, on_change_user: Callable[[str], Any], on_delete_user: Callable[[str], Any], on_add_user: Callable[[str, str], Any], on_close_user_dialog: Callable[..., Any], on_delete_all_data: Callable[..., Any]) -> None:
        self.user_list = UserList(
            page=page,
            lang=lang,
            current_user=current_user,
            on_select_callback=on_change_user,
            on_delete_callback=on_delete_user
        )

        self.add_form = AddUserField(
            page=page,
            lang=lang,
            on_submit_callback=on_add_user,
            currencies=currencies,
            default_currency=default_currency
        )

        self.user_dialog = UserManagementDialog(
            page=page,
            lang=lang,
            user_list=self.user_list,
            add_form=self.add_form,
            on_close_callback=on_close_user_dialog
        )

        self.delete_dialog = DeleteUserDialog(
            page=page,
            lang=lang,
            on_confirm_callback=on_delete_user
        )

        self.delete_all_data_dialog = DeleteAllDataDialog(
            page=page,
            lang=lang,
            on_confirm_callback=on_delete_all_data
        )


class UserManagementPageContent(ft.Container):
    def __init__(self, lang: dict[str, str], app_version: str, profile_card: ProfileCard, google_account_card: GoogleAccountCard, on_disable_ads_change: Callable[..., Any], on_open_settings: Callable[..., Any], on_open_help: Callable[..., Any], on_logout: Callable[..., Any], on_delete_all_data: Callable[..., Any]) -> None:
        self.lang = lang
        self.profile_card = profile_card
        self.google_account_card = google_account_card

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.top_header_text = Text.SMALL(lang["user_management.profile_and_options"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
        self.services_section_title = Text.SMALL(lang["user_management.services_and_features"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
        self.support_section_title = Text.SMALL(lang["user_management.support_and_info"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
        self.version_text = Text.SMALL(f"{lang['user_management.version']} {app_version}", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        # CONTAINER COMPONENTS
        self.version_status_icon = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=Color.PRIMARY_ACTION
        )

        self.disable_ads_switch = ft.Switch(
            value=False,
            active_color=Color.PRIMARY_ACTION,
            on_change=on_disable_ads_change
        )

        self.services_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.SHIELD_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.disable_ads"],
                    trailing=self.disable_ads_switch
                ),
                MenuItem(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["settings.settings"],
                    on_click=on_open_settings
                )
            ]
        )

        self.support_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.help_faq"],
                    on_click=on_open_help
                ),
                MenuItem(
                    icon=ft.Icons.LOGOUT,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.logout"],
                    on_click=on_logout
                ),
                MenuItem(
                    icon=ft.Icons.DELETE_FOREVER,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.delete_all_data"],
                    on_click=on_delete_all_data
                )
            ]
        )

        self.top_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.top_header_text]
        )

        self.footer = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[self.version_status_icon, self.version_text]
                )
            ]
        )

        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=16,
                expand=True,
                controls=[
                    self.top_header,
                    self.profile_card,
                    self.google_account_card,
                    self.services_section_title,
                    self.services_card,
                    self.support_section_title,
                    self.support_card,
                    ft.Container(height=8),
                    self.footer
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
            content=self.main_container
        )

    def resize(self, page_width: int, page_height: int, content_width: int, card_content_width: int) -> None:
        self.main_container.width = page_width
        self.main_container.height = page_height
        self.content_container.width = page_width
        self.top_header.width = content_width
        self.services_section_title.width = content_width
        self.support_section_title.width = content_width
        self.footer.width = content_width
        self.profile_card.resize(content_width, card_content_width)
        self.google_account_card.resize(content_width, card_content_width)
        self.services_card.resize(content_width)
        self.support_card.resize(content_width)

    def set_bottom_margin(self, height: int) -> None:
        self.main_container.margin = ft.Margin(bottom=height)
