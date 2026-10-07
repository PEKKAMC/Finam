# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import AddUserField, DeleteUserDialog, Menu, UserList, UserManagementDialog
from src.pages.user_management.components import MenuItem, MenuSectionCard, ProfileCard, DeleteAllDataDialog
from src.pages.user_management.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, Text, UISettings
from src.version_manager import get_version

Logger.info("Initializing User Management page...")


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the User Management View."""
    def __init__(self, page: Page, lang: dict, user_info: dict, controller: LogicController, refresh_callback: Callable):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = controller
        self._refresh_view = refresh_callback

        # INITIALIZE DIALOG COMPONENTS
        self.user_list = UserList(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info.get("username", ""),
            on_select_callback=self._handle_change_user,
            on_delete_callback=self.show_delete_prompt
        )

        self.add_form = AddUserField(
            page=self._page,
            lang=self.lang,
            on_submit_callback=self._handle_add_user
        )

        self.user_dialog = UserManagementDialog(
            page=self._page,
            lang=self.lang,
            user_list=self.user_list,
            add_form=self.add_form,
            on_close_callback=self._close_user_management_dialog
        )

        self.delete_dialog = DeleteUserDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self._handle_delete_confirm
        )

        self.delete_all_data_dialog = DeleteAllDataDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self._handle_delete_all_data_confirm
        )

        self._add_dialogs_to_overlay()

    # USER MANAGEMENT DIALOG
    def show_user_management_dialog(self) -> int:
        self.user_list.update_data(self.controller.get_all_users(), self.user_info.get("username", ""))
        return self.user_dialog.show(self._page)

    def _close_user_management_dialog(self, e: ft.ControlEvent | None = None) -> ft.ControlEvent | None:
        self.user_dialog.close_most_recent_dialog(self._page)
        return e

    # USER ACTIONS
    def _handle_add_user(self, input_username: str):
        if not input_username:
            return
        success, error_msg = self.controller.add_user(input_username)

        if success:
            self.add_form.clear()
            self._refresh_view()
        else:
            self.add_form.show_error("error")

    def _handle_change_user(self, username: str):
        self.user_dialog.close_most_recent_dialog(self._page)
        self.controller.change_user(username)
        self._refresh_view()

    # DELETE USER DIALOG
    def show_delete_prompt(self, username: str = "") -> int:
        try:
            if username:
                self.delete_dialog.selected_user = username
            self.delete_dialog.show(self._page)
            return 0
        except Exception as e:
            Logger.warn(f"Failed to show delete prompt {e}")
            return -1

    def _handle_delete_confirm(self, username: str) -> int:
        try:
            self.controller.delete_user(username)
            self._refresh_view()
            return 0
        except Exception as e:
            Logger.warn(f"Cannot delete user {username}, {e}")
            return -1

    # DELETE ALL DATA DIALOG
    def show_delete_all_data_prompt(self) -> int:
        try:
            self.delete_all_data_dialog.show(self._page)
            return 0
        except Exception as e:
            Logger.warn(f"Failed to show delete all data prompt {e}")
            return -1

    async def _handle_delete_all_data_confirm(self, e=None) -> int:
        try:
            self.controller.delete_all_data()
            os.environ["RESTART_FINAM"] = "1"
            await self._page.window.close()
            return 0
        except Exception as e:
            Logger.error(f"Failed to delete all data and restart app: {e}")
            return -1

    # OVERLAY MANAGEMENT
    def _add_dialogs_to_overlay(self) -> None:
        dialogs = [
            self.user_dialog,
            self.delete_dialog,
            self.delete_all_data_dialog
        ]
        for d in dialogs:
            d.add_to_overlay(self._page)

    def _remove_dialogs_from_overlay(self) -> None:
        dialogs = [
            self.user_dialog,
            self.delete_dialog,
            self.delete_all_data_dialog
        ]
        for d in dialogs:
            d.remove_from_overlay(self._page)


class UserManagementView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_version = get_version

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info)

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info,
            controller=self.controller,
            refresh_callback=self.refresh_view
        )

        # FETCH DASHBOARD DATA
        self.app_version = self.get_version("Finam")

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.top_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                Text.SMALL(self.lang["user_management.profile_and_options"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD),
            ]
        )

        self.profile_card = ProfileCard(
            username=self.user_info.get("username", ""),
            lang=self.lang,
            on_change_user=self.dialogs.show_user_management_dialog
        )

        self.services_section_title = Text.SMALL(self.lang["user_management.services_and_features"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        self.services_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.THUMB_UP_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.refer_friend"],
                    subtitle=self.lang["user_management.get_vip_30_days"],
                    badge_text=self.lang["user_management.badge_30days"],
                    badge_bg=Color.LIGHT_ACCENT,
                    badge_color=Color.PRIMARY
                ),
                MenuItem(
                    icon=ft.Icons.SHIELD_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.disable_ads"],
                    subtitle=self.lang["user_management.smooth_experience"],
                    trailing=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                ),
                MenuItem(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["settings.settings"],
                    subtitle=self.lang["user_management.language_security_currency"],
                    on_click=self._page.navigate_to("/settings")
                )
            ]
        )

        self.support_section_title = Text.SMALL(self.lang["user_management.support_and_info"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        self.support_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.STAR_OUTLINE,
                    icon_color=Color.GOAL_HEADER_ICON_COLOR,
                    icon_bg_color=Color.GOAL_HEADER_ICON_BACKGROUND,
                    title=self.lang["user_management.rate_app"],
                    subtitle=self.lang["user_management.rate_5_stars"]
                ),
                MenuItem(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.help_faq"],
                    subtitle=self.lang["user_management.guide_expense_mgmt"]
                ),
                MenuItem(
                    icon=ft.Icons.LOGOUT,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.logout"],
                    subtitle="",
                    on_click=self.logout
                ),
                MenuItem(
                    icon=ft.Icons.DELETE_FOREVER,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.delete_all_data"],
                    subtitle="",
                    on_click=lambda e: self.dialogs.show_delete_all_data_prompt()
                )
            ]
        )

        self.footer = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Container(width=8, height=8, border_radius=4, bgcolor=Color.PRIMARY_ACTION),
                        Text.SMALL(f"{self.lang["user_management.version"]} {self.app_version}", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                Text.SMALL(self.lang["user_management.privacy_encryption"], color=Color.SUBTITLE_TEXT, text_align=ft.TextAlign.CENTER)
            ]
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
                            spacing=16,
                            expand=True,
                            controls=[
                                self.top_header,
                                self.profile_card,
                                self.services_section_title,
                                self.services_card,
                                self.support_section_title,
                                self.support_card,
                                ft.Container(height=8),
                                self.footer
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
            route="/user_management",
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

    async def logout(self, e=None) -> None:
        try:
            self.user_info["username"] = ""
            await self._page.navigate_to("/starter")(e)
        except Exception as ex:
            Logger.warn(f"Failed to logout: {ex}")

    def refresh_view(self) -> int:
        try:
            self.dialogs.user_list.update_data(self.controller.get_all_users(), self.user_info.get("username", ""))
            self.profile_card.update_data(self.user_info.get("username", ""))
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
        self.menu.resize(
            width=page_width
        )
        self.profile_card.resize(
            width=page_width
        )
        self.services_card.resize(
            width=page_width
        )
        self.support_card.resize(
            width=page_width
        )

        return e

def get_user_management_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading User Management page...")
    return UserManagementView(page, lang, user_info)