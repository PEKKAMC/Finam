# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft
from src.logger import Logger
from src.utils import Color, Dialog, Text


class ProfileCard(ft.Container):
    def __init__(self, username: str, lang: dict, on_change_user: Callable):
        self.username = username
        self.lang = lang
        self.on_change_user = on_change_user

        user_display = self.username if self.username else ""

        self.user_name_text = Text.H4(user_display, color=Color.WHITE, weight=ft.FontWeight.BOLD)
        self.active_user_text = Text.MEDIUM(
            self.username if self.username else "Chưa chọn người dùng",
            color=Color.WHITE,
            weight=ft.FontWeight.BOLD
        )

        avatar_box = ft.Stack(
            controls=[
                ft.CircleAvatar(
                    radius=26,
                    bgcolor=Color.LIGHT_ACCENT,
                    content=ft.Icon(ft.Icons.PERSON, color=Color.PRIMARY, size=32)
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, color=Color.SAVINGS_VALUE_TEXT, size=12),
                    bgcolor=Color.PRIMARY,
                    border_radius=10,
                    padding=2,
                    bottom=0,
                    right=0
                )
            ]
        )

        vip_badge = ft.Container(
            content=Text.SMALL("VIP", color=Color.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        )

        user_info = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.user_name_text,
                        vip_badge
                    ]
                ),
                Text.SMALL("Tài khoản Cá nhân (Chính)", color=Color.LIGHT_ACCENT)
            ]
        )

        change_user_btn = ft.Container(
            content=ft.Row(
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=Color.WHITE, size=16),
                    Text.SMALL("Đổi", color=Color.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.WHITE, size=16)
                ]
            ),
            bgcolor=Color.METRIC_PILL_BACKGROUND,
            border=ft.Border.all(1, Color.METRIC_PILL_BORDER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=16,
            on_click=lambda e: self.on_change_user(),
            ink=True
        )

        top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        avatar_box,
                        user_info
                    ]
                ),
                change_user_btn
            ]
        )

        active_user_card = ft.Container(
            bgcolor=Color.DARK_SURFACE,
            border_radius=16,
            padding=14,
            content=ft.Column(
                spacing=8,
                controls=[
                    Text.SMALL("HỒ SƠ ĐANG CHỌN", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.PERSON_OUTLINE, color=Color.WHITE, size=20),
                                        bgcolor=Color.METRIC_PILL_BACKGROUND,
                                        padding=8,
                                        border_radius=12
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            self.active_user_text,
                                        ]
                                    )
                                ]
                            ),
                            ft.Container(
                                content=ft.Row(
                                    spacing=2,
                                    controls=[
                                        Text.SMALL("Thay đổi", color=Color.LIGHT_ACCENT),
                                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.LIGHT_ACCENT, size=16)
                                    ]
                                ),
                                on_click=lambda e: self.on_change_user(),
                                ink=True
                            )
                        ]
                    )
                ]
            )
        )

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=16,
            content=ft.Column(
                spacing=14,
                controls=[
                    top_row,
                    active_user_card
                ]
            )
        )

    def update_user(self, username: str):
        self.username = username
        display_name = username if username else ""
        self.user_name_text.value = display_name
        self.active_user_text.value = username if username else "Chưa chọn người dùng"


class MenuItem(ft.Container):
    def __init__(self, icon, icon_color: Color, icon_bg_color: Color, title: str, subtitle: str, badge_text: str | None = None, badge_bg: Color | None = None, badge_color: Color | None = None, trailing: ft.Control | None = None, on_click: Callable | None = None):
        badge_control = None
        if badge_text:
            badge_control = ft.Container(
                content=Text.SMALL(badge_text, color=badge_color or Color.PRIMARY, weight=ft.FontWeight.BOLD),
                bgcolor=badge_bg or Color.LIGHT_ACCENT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            )

        title_row_controls = [
            Text.MEDIUM(title, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        ]
        if badge_control:
            title_row_controls.append(badge_control)

        trailing_control = trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=Color.SUBTITLE_TEXT, size=20)

        super().__init__(
            padding=ft.Padding.symmetric(vertical=14, horizontal=16),
            on_click=on_click,
            ink=True if on_click else False,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color=icon_color, size=20),
                                bgcolor=icon_bg_color,
                                padding=10,
                                border_radius=14
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=title_row_controls
                                    ),
                                    Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)
                                ]
                            )
                        ]
                    ),
                    trailing_control
                ]
            )
        )


class MenuSectionCard(ft.Container):
    def __init__(self, items: list[ft.Control]):
        controls = []
        for i, item in enumerate(items):
            controls.append(item)
            if i < len(items) - 1:
                controls.append(ft.Divider(height=1, color=Color.CARD_DIVIDER, thickness=1))

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=20,
            content=ft.Column(
                spacing=0,
                controls=controls
            )
        )


class UserManagementCard(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, user_list, add_form, on_close_callback: Callable):
        self._page = page
        self.lang = lang
        self._close_dialog = on_close_callback

        self.main_container = ft.Column(
            height=375,
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=Color.SECONDARY_TEXT,
                            tooltip=self.lang["generic.close"],
                            on_click=self._close_dialog
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.PEOPLE_ALT, color=Color.PRIMARY, size=22),
                                    bgcolor=Color.LIGHT_ACCENT,
                                    padding=10,
                                    border_radius=14
                                ),
                                Text.H5(self.lang["user_management.header_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ]
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        Text.SMALL(self.lang["user_management.select_account"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        user_list
                    ]
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        Text.SMALL(self.lang["user_management.add_new_user"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD),
                        add_form
                    ]
                )
            ]
        )

        super().__init__(
            bgcolor=Color.WHITE,
            border_radius=24,
            padding=0,
            content=self.main_container
        )

    def resize(self, width: int):
        self.main_container.width = width


class UserManagementDialog(Dialog):
    def __init__(self, page: ft.Page, lang: dict, user_list: UserList, add_form, on_close_callback: Callable):
        self.card = UserManagementCard(
            page=page,
            lang=lang,
            user_list=user_list,
            add_form=add_form,
            on_close_callback=on_close_callback
        )
        super().__init__(dialog_content=self.card, color=Color.WHITE)


class UserList(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, current_user: str, on_select_callback, on_delete_callback):
        self._page = page
        self.lang = lang
        self.current_user = current_user
        self.on_select = on_select_callback
        self.on_delete = on_delete_callback

        self.list_column = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            height=160
        )
        self.main_container = ft.Container(
            content=self.list_column,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        super().__init__(content=self.main_container)

    def refresh(self, current_users: list, current_user: str = ""):
        self.current_user = current_user
        self.list_column.controls.clear()

        if not current_users:
            self.list_column.controls.append(
                Text.P(self.lang["user_management.no_user"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
            )
        else:
            for username in current_users:
                self.list_column.controls.append(self.create_user_box(username))

    def create_user_box(self, username: str):
        is_active = (username == self.current_user)
        initial = username[0].upper() if username else ""
        created_prefix = self.lang["user_management.created_date"]

        def handle_select(e, name=username):
            self.on_select(name)
            return e

        return ft.Container(
            bgcolor=Color.WHITE,
            border_radius=20,
            padding=14,
            border=ft.Border.all(2 if is_active else 1, Color.PRIMARY if is_active else Color.INPUT_BORDER),
            ink=True,
            on_click=handle_select,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=Text.MEDIUM(initial, color=Color.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=Color.PRIMARY,
                                width=40,
                                height=40,
                                border_radius=14,
                                alignment=ft.Alignment.CENTER
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    Text.MEDIUM(username, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                    Text.SMALL(f"{created_prefix} 2026-01-01 08:00", color=Color.SECONDARY_TEXT)
                                ]
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            *(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.PERSON_PIN, color=Color.PRIMARY, size=20),
                                        padding=4
                                    )
                                ] if is_active else []
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=Color.DELETE_ACTION,
                                icon_size=18,
                                on_click=lambda e, u=username: self.on_delete(u),
                                tooltip="Xóa người dùng"
                            )
                        ]
                    )
                ]
            )
        )

    def resize(self, height: int):
        pass


class AddUserField(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, on_submit_callback):
        self._page = page
        self.lang = lang
        self.on_submit_callback = on_submit_callback

        self.input_field = ft.TextField(
            hint_text=self.lang["user_management.username_hint"],
            color=Color.DEFAULT_TEXT,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True,
            expand=True,
            on_submit=self._handle_submit
        )
        self.error_message = Text.SMALL("", color=Color.ERROR_TEXT)
        self.submit_button = ft.Button(
            content=ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.ADD, color=Color.LIGHT_ACCENT, size=16),
                    Text.MEDIUM(self.lang["user_management.create_btn"], color=Color.WHITE, weight=ft.FontWeight.BOLD)
                ],
                tight=True
            ),
            bgcolor=Color.PRIMARY,
            on_click=self._handle_submit,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=16
            )
        )
        self.main_container = ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        self.input_field,
                        self.submit_button
                    ]
                ),
                self.error_message
            ]
        )

        super().__init__(content=self.main_container)

    def _handle_submit(self, e=None):
        input_username = self.input_field.value.strip()
        self.on_submit_callback(input_username)

    def show_error(self, message: str):
        self.error_message.value = message
        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def clear(self):
        self.input_field.value = ""
        self.error_message.value = ""
        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Render skipped: {e}")

    def resize(self, width: int):
        pass


class DeleteUserDialog(Dialog):
    def __init__(self, page: ft.Page, lang: dict, on_confirm_callback):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm_callback
        self.selected_user: str = ""

        cancel_text = self.lang["generic.cancel"]
        delete_text = self.lang["generic.delete"]

        self.main_container = ft.AlertDialog(
            modal=True,
            bgcolor=Color.WHITE,
            title=Text.H3(self.lang["user_management.confirm_delete_user_title"], color=Color.PRIMARY_TEXT),
            content=Text.P(self.lang["user_management.confirm_delete_user_content"], color=Color.SECONDARY_TEXT),
            actions=[
                ft.TextButton(Text.BUTTON(cancel_text, color=Color.SECONDARY_TEXT), on_click=lambda e: self.close_most_recent_dialog),
                ft.TextButton(Text.BUTTON(delete_text, color=Color.DELETE_ACTION), on_click=lambda e: self.confirm()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        super().__init__(
            color=Color.DIALOG_BACKGROUND,
            dialog_content=self.main_container
        )

    def confirm(self):
        if self.selected_user and self.on_confirm:
            self.on_confirm(self.selected_user)
        self.close_most_recent_dialog(self._page)

    def resize(self, width: int) -> None:
        self.main_container.width = width