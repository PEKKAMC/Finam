# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import Menu
from src.pages.user_management.components import AddUserField, DeleteUserDialog, MenuItem, MenuSectionCard, ProfileCard, UserList, UserManagementDialog
from src.pages.user_management.logic import LogicController
from src.utils import Color, Text, UISettings, get_safe_page_size

Logger.info("Initializing User Management page...")


class DialogManager:
    def __init__(self, page: ft.Page, lang: dict, user_info: dict, controller: LogicController, refresh_callback):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = controller
        self.refresh_view = refresh_callback

        self.user_list = UserList(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info.get("username", ""),
            on_select_callback=self.handle_change_user,
            on_delete_callback=self.show_delete_prompt
        )

        self.add_form = AddUserField(page=self._page, lang=self.lang, on_submit_callback=self.handle_add_user)

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

    def show_user_management_dialog(self) -> int:
        try:
            self.user_dialog.show(self._page)
            return 0

        except Exception as e:
            Logger.warn(f"Failed to show user management prompt {e}")
            return -1

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
            self.refresh_view()
            return 0

        except Exception as e:
            Logger.warn(f"Cannot delete user {username}, {e}")
            return -1

    def _close_user_management_dialog(self):
        self.user_dialog.close_most_recent_dialog(self._page)

    def handle_add_user(self, input_username: str):
        if not input_username:
            return
        success, error_msg = self.controller.add_user(input_username)
        if success:
            self.add_form.clear()
            self.refresh_view()
        else:
            self.add_form.show_error(self.lang.get(error_msg, error_msg))

    def handle_change_user(self, username: str):
        self.user_dialog.close_most_recent_dialog(self._page)
        self.controller.change_user(username)
        self.refresh_view()


class UserManagementView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

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
                Text.SMALL("HỒ SƠ & TUỲ CHỌN", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD),
            ]
        )

        # Profile Card
        self.profile_card = ProfileCard(
            username=self.user_info.get("username", ""),
            lang=self.lang,
            on_change_user=self.dialogs.show_user_management_dialog
        )

        # Section 1: Services & Features
        services_section_title = Text.SMALL("DỊCH VỤ & TÍNH NĂNG", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        services_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.THUMB_UP_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title="Giới thiệu cho bạn bè",
                    subtitle="Nhận ngay 30 ngày VIP cho cả hai",
                    badge_text="+30 Ngày",
                    badge_bg=Color.LIGHT_ACCENT,
                    badge_color=Color.PRIMARY
                ),
                MenuItem(
                    icon=ft.Icons.SHIELD_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title="Tắt quảng cáo",
                    subtitle="Trải nghiệm mượt mà không quảng cáo",
                    trailing=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                ),
                MenuItem(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title="Cài đặt",
                    subtitle="Ngôn ngữ (VI), bảo mật, tiền tệ",
                    on_click=lambda e: self._page.go("/settings")
                )
            ]
        )

        support_section_title = Text.SMALL("HỖ TRỢ & THÔNG TIN", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        current_username = self.user_info.get("username", "minhkhang").lower().replace(" ", "")
        user_email = f"{current_username}.finance@gmail.com" if current_username else "minhkhang.finance@gmail.com"

        support_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.STAR_OUTLINE,
                    icon_color=Color.GOAL_HEADER_ICON_COLOR,
                    icon_bg_color=Color.GOAL_HEADER_ICON_BACKGROUND,
                    title="Đánh giá ứng dụng",
                    subtitle="Góp ý 5 sao trên cửa hàng ứng dụng"
                ),
                MenuItem(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title="Trung tâm trợ giúp & FAQ",
                    subtitle="Hướng dẫn quản lý chi tiêu hiệu quả"
                ),
                MenuItem(
                    icon=ft.Icons.LOGOUT,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title="Đăng xuất tài khoản",
                    subtitle=user_email
                ),
            ]
        )

        # Footer
        footer = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Container(
                            width=8,
                            height=8,
                            border_radius=4,
                            bgcolor=Color.PRIMARY_ACTION
                        ),
                        Text.SMALL("Phiên bản v0.2.2-alpha", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                Text.SMALL("Bảo vệ quyền riêng tư & Mã hóa dữ liệu an toàn", color=Color.SUBTITLE_TEXT, text_align=ft.TextAlign.CENTER)
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
                                services_section_title,
                                services_card,
                                support_section_title,
                                support_card,
                                ft.Container(height=8),
                                footer
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
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

        # INITIAL DATA LOAD
        self.refresh_view()
        self._initial_launch()

    def _initial_launch(self):
        if self.user_info.get("username", "") == "":
            self.dialogs.show_user_management_dialog()

    def refresh_view(self):
        self.dialogs.user_list.refresh(self.controller.get_all_users(), self.user_info.get("username", ""))
        self.profile_card.update_user(self.user_info.get("username", ""))
        try:
            self._page.update()
        except RuntimeError:
            pass

    def _on_page_resize(self, e=None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        self.main_container.width = page_width
        self.main_container.height = page_height

        self.menu.resize(
            width=page_width
        )

        return e


def get_user_management_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return UserManagementView(page, lang, user_info)