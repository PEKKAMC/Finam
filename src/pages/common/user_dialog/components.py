# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.common.user_dialog.logic import (
    format_created_date_label,
    get_user_initial,
)
from src.utils import Color, DefaultSettings, Dialog, Page, Text, scale_width


class UserManagementDialog(Dialog):
    def __init__(self, page: Page, lang: dict, user_list: UserList, add_form, on_close_callback: Callable, has_cancel_button: bool = True):
        self._page = page
        self.lang = lang
        self.user_list = user_list
        self.add_form = add_form
        self._close_dialog = on_close_callback

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.selection_heading = Text.SMALL(self.lang["user_management.select_account"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.add_user_heading = Text.SMALL(self.lang["user_management.add_new_user"], color=Color.SECONDARY_TEXT, weight=ft.FontWeight.BOLD)
        self.dialog_title = Text.H5(self.lang["user_management.header_title"], color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)

        # Static icons
        self.dialog_title_icon = ft.Icon(ft.Icons.PEOPLE_ALT, color=Color.PRIMARY, size=22)

        # CONTAINER COMPONENTS
        self.selection_section = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                self.selection_heading,
                user_list
            ]
        )

        self.add_user_section = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                self.add_user_heading,
                add_form
            ]
        )

        header_controls = []
        if has_cancel_button:
            header_controls.append(
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=Color.SECONDARY_TEXT,
                    tooltip=self.lang["generic.close"],
                    on_click=self._close_dialog
                )
            )

        self.main_container = ft.Container(
            border_radius=24,
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    ft.Row(
                        height=48,
                        alignment=ft.MainAxisAlignment.END,
                        controls=header_controls
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(
                                        content=self.dialog_title_icon,
                                        bgcolor=Color.LIGHT_ACCENT,
                                        padding=10,
                                        border_radius=14
                                    ),
                                    self.dialog_title
                                ]
                            )
                        ]
                    ),
                    self.selection_section,
                    self.add_user_section,
                ]
            )
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND
        )

    def resize(self, width: int, list_height: int) -> None:
        self.main_container.width = width
        self.selection_section.width = width
        self.add_user_section.width = width
        self.add_form.resize(width)
        self.user_list.resize(width, list_height)

class UserList(ft.Container):
    def __init__(self, page: Page, lang: dict, current_user: str, on_select_callback, on_delete_callback):
        self._page = page
        self.lang = lang
        self.current_user = current_user
        self.on_select = on_select_callback
        self.on_delete = on_delete_callback

        # TEXT AND ICON COMPONENTS
        # Dynamic texts and icons are created for each user in create_user_box.
        self.user_created_at = {}
        self._list_width: int | None = None
        self.user_boxes: list[ft.Container] = []

        self.list_column = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )
        self.main_container = ft.Container(
            content=self.list_column,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )

        super().__init__(content=self.main_container)

    def create_user_box(self, username: str) -> ft.Container:
        is_active = (username == self.current_user)
        initial = get_user_initial(username)
        created_at = self.user_created_at[username]
        created_prefix = self.lang["user_management.created_date"]

        def handle_select(e: ft.ControlEvent | None = None, name = username) -> ft.ControlEvent | None:
            self.on_select(name)
            return e

        avatar_label = Text.MEDIUM(
            initial, color=Color.WHITE, weight=ft.FontWeight.BOLD
        )
        username_label = Text.MEDIUM(
            username,
            color=Color.PRIMARY_TEXT,
            weight=ft.FontWeight.BOLD,
        )
        created_at_label = Text.SMALL(
            format_created_date_label(created_prefix, created_at),
            color=Color.SECONDARY_TEXT,
        )
        avatar = ft.Container(
            content=avatar_label,
            bgcolor=Color.PRIMARY,
            width=40,
            height=40,
            border_radius=14,
            alignment=ft.Alignment.CENTER,
        )
        user_info = ft.Column(
            spacing=2,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[username_label, created_at_label],
        )
        # Dynamic icons
        active_user_icon = ft.Icon(
            ft.Icons.PERSON_PIN,
            color=Color.PRIMARY,
            size=20,
        )
        user_actions = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=40,
            controls=[
                *(
                    [
                        active_user_icon
                    ] if is_active else []
                ),
                *(
                    [
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=Color.DELETE_ACTION,
                            icon_size=18,
                            on_click=lambda e, u=username: self.on_delete(u),
                            tooltip=self.lang["user_management.delete_user_tooltip"],
                        )
                    ] if not is_active else []
                ),
            ],
        )

        user_box = ft.Container(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=20,
            padding=14,
            border=ft.Border.all(2 if is_active else 1, Color.PRIMARY if is_active else Color.INPUT_BORDER),
            ink=True,
            on_click=handle_select,
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar,
                    user_info,
                    user_actions,
                ]
            ),
        )
        user_box.content.width = scale_width(self._list_width, 404) if self._list_width is not None else None
        return user_box

    def update_data(self, users: list[dict[str, str] | str], current_user: str = "", user_created_at: dict[str, str] | None = None) -> None:
        self.current_user = current_user
        self.list_column.controls.clear()
        self.user_boxes.clear()
        if user_created_at is not None:
            self.user_created_at = user_created_at
        else:
            self.user_created_at = {}

        if not users:
            self.list_column.controls.append(
                Text.P(self.lang["user_management.no_user"], color=Color.SECONDARY_TEXT, text_align=ft.TextAlign.CENTER)
            )
        else:
            for username in users:
                if isinstance(username, dict):
                    username_name = username["name"]
                    if username_name:
                        self.user_created_at.setdefault(username_name, username["created_at"])
                        user_box = self.create_user_box(username_name)
                        self.user_boxes.append(user_box)
                        self.list_column.controls.append(user_box)
                else:
                    username_name = str(username)
                    self.user_created_at.setdefault(username_name, self.user_created_at.get(username_name, ""))
                    user_box = self.create_user_box(username_name)
                    self.user_boxes.append(user_box)
                    self.list_column.controls.append(user_box)

        try:
            self.main_container.update()
            self.update()
            if self._page:
                self._page.update()
        except RuntimeError:
            pass

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self._list_width = width
        self.main_container.width = width
        self.list_column.width = width
        self.list_column.height = height
        for user_box in self.user_boxes:
            user_box.width = width
            user_box.content.width = scale_width(width, 404)


class AddUserField(ft.Container):
    def __init__(self, page: Page, lang: dict, on_submit_callback, currencies: list[str], default_currency: str = DefaultSettings.CURRENCY):
        self._page = page
        self.lang = lang
        self.on_submit_callback = on_submit_callback
        self.currencies = currencies
        self.default_currency = default_currency

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.submit_button_label = Text.BUTTON(self.lang["user_management.create_button"], color=Color.WHITE, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, no_wrap=False)

        # Dynamic texts
        self.error_message = Text.SMALL("", color=Color.ERROR_TEXT)

        # CONTAINER COMPONENTS
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

        self.currency_dropdown = ft.Dropdown(
            value=self.default_currency,
            options=[ft.dropdown.Option(currency) for currency in self.currencies],
            enable_filter=True,
            editable=True,
            color=Color.DEFAULT_TEXT,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            border_radius=16,
            text_size=13,
            content_padding=12,
            filled=True,
            expand=True,
            menu_height=240
        )

        self.submit_button = ft.Container(
            content=self.submit_button_label,
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=25,
            margin=ft.Margin.only(top=10),
            on_click=self._handle_submit,
            expand=True,
        )
        self.create_button_row = ft.Row(
            expand=True,
            controls=[self.submit_button],
        )
        self.input_row = ft.Row(
            spacing=12,
            controls=[self.input_field],
        )
        self.currency_row = ft.Row(
            controls=[self.currency_dropdown],
        )
        self.main_container = ft.Column(
            tight=True,
            spacing=6,
            controls=[
                self.input_row,
                self.currency_row,
                self.create_button_row,
                self.error_message
            ]
        )

        super().__init__(
            content=self.main_container
        )

    def _handle_submit(self, e: ft.ControlEvent | None = None) -> ft.ControlEvent | None:
        input_username = self.input_field.value.strip()
        selected_currency = self.currency_dropdown.value or self.default_currency
        self.on_submit_callback(input_username, selected_currency)
        return e

    def show_error(self, message: str):
        self.error_message.value = message
        try:
            self.update()
        except RuntimeError as ex:
            Logger.debug(f"Render skipped: {ex}")

    def clear(self):
        self.input_field.value = ""
        self.currency_dropdown.value = self.default_currency
        self.error_message.value = ""
        try:
            self.update()
        except RuntimeError as ex:
            Logger.debug(f"Render skipped: {ex}")

    def resize(self, width: int):
        self.main_container.width = width
        self.input_row.width = width
        self.currency_row.width = width
        self.input_field.width = width
        self.currency_dropdown.width = width
        self.submit_button.width = width
        self.create_button_row.width = width


class DeleteUserDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_confirm_callback: Callable):
        self._page = page
        self.lang = lang
        self.on_confirm = on_confirm_callback
        self.selected_user: str = ""

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H3(self.lang["user_management.confirm_delete_user_title"], color=Color.PRIMARY_TEXT)
        self.content_text = Text.P(self.lang["user_management.confirm_delete_user_content"], color=Color.SECONDARY_TEXT)
        self.cancel_text = Text.BUTTON(self.lang["generic.cancel"], color=Color.SECONDARY_TEXT)
        self.delete_text = Text.BUTTON(self.lang["generic.delete"], color=Color.DELETE_ACTION, weight=ft.FontWeight.BOLD)

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
                                on_click=lambda e: self.dismiss()
                            ),
                            ft.TextButton(
                                content=self.delete_text,
                                on_click=self.confirm
                            )
                        ]
                    )
                ]
            )
        )

        super().__init__(
            dialog_content=self.main_container,
            color=Color.DIALOG_BACKGROUND
        )

    def confirm(self, e: ft.ControlEvent | None = None) -> ft.ControlEvent | None:
        if self.selected_user and self.on_confirm:
            self.on_confirm(self.selected_user)
        self.dismiss()

        return e

    def resize(self, width: int) -> None:
        self.main_container.width = width