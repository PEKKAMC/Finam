# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.pages.common import AddUserField, DeleteUserDialog, UserList, UserManagementDialog
from src.pages.common.logic import change_user, close_user_management_dialog, save_last_user, show_user_management_dialog
from src.pages.starter.logic import LogicController
from src.utils import Color, Data, DefaultSettings, Page, Text

SINGLE_INTEGER_REGEX = Data().get_regex_string("single_integer")
FLOAT_REGEX = Data().get_regex_string("float")

class DialogManager:
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str], controller: LogicController, refresh_callback: Callable[..., int]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = controller
        self.refresh_view = refresh_callback

        self.user_list = UserList(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info["username"],
            on_select_callback=self.handle_change_user,
            on_delete_callback=self.show_delete_prompt
        )

        self.add_form = AddUserField(
            page=self._page,
            lang=self.lang,
            on_submit_callback=self.handle_add_user,
            currencies=self.controller.get_currencies(),
            default_currency=DefaultSettings.CURRENCY
        )

        self.user_dialog = UserManagementDialog(
            page=self._page,
            lang=self.lang,
            user_list=self.user_list,
            add_form=self.add_form,
            on_close_callback=self._close_user_management_dialog,
            has_cancel_button=False
        )

        self.delete_dialog = DeleteUserDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self._handle_delete_confirm
        )

    def show_user_management_dialog(self) -> int:
        return show_user_management_dialog(self._page, self.user_list, self.user_dialog, self.controller.get_all_users(), self.user_info["username"])

    def show_delete_prompt(self, username: str = '') -> int:
        if username:
            self.delete_dialog.selected_user = username
        return self.delete_dialog.show()

    def _close_user_management_dialog(self) -> None:
        close_user_management_dialog(self.user_dialog)

    def _handle_delete_confirm(self, username: str) -> None:
        self.controller.delete_user(username)
        self.refresh_view()

    def handle_add_user(self, input_username: str, currency: str) -> None:
        if not input_username: return

        status = self.controller.add_user(input_username, currency)

        if status == 0:
            self.add_form.clear()
            self.refresh_view()
        elif status == 1:
            self.add_form.show_error(self.lang["user_management.user_already_exists"])
        else:
            self.add_form.show_error(self.lang["generic.unknown_error"])

    def handle_change_user(self, username: str, e: ft.ControlEvent | None = None) -> None:
        self.user_dialog.dismiss()
        change_user(self.user_info, username)
        self._page.run_task(
            save_last_user,
            self._page.last_user_preferences,
            username
        )
        self._page.navigate_to("/home")(e)


class AppLockCard(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], on_unlock: Callable[[str], None]) -> None:
        self._page = page
        self.on_unlock = on_unlock
        self._submitting = False
        self._active_index = 0

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.pin_title_text = Text.H3(lang["app_lock.title"], color=Color.PRIMARY_TEXT)

        # Static icons
        self.pin_lock_icon = ft.Icon(ft.Icons.LOCK_OUTLINE, color=Color.PRIMARY, size=40)

        # Dynamic texts
        self.error_text = Text.H1("", color=Color.NEGATIVE_ACTION)

        # CONTAINER COMPONENTS
        self.fields: list[ft.TextField] = [
            ft.TextField(
                autofocus=index == 0,
                input_filter=ft.InputFilter(allow=True, regex_string=SINGLE_INTEGER_REGEX),
                password=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_align=ft.TextAlign.CENTER,
                height=64,
                bgcolor=Color.CARD_BACKGROUND,
                border_color=Color.INPUT_BORDER,
                focused_border_color=Color.PRIMARY_ACTION,
                color=Color.PRIMARY_TEXT,
                text_size=24,
                on_change=lambda e, field_index=index: self._on_digit_change(field_index, e.control.value or ""),
                on_focus=lambda e, field_index=index: self._on_field_focus(field_index)
            )
            for index in range(4)
        ]

        self.pin_fields = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=self.fields
        )

        self.main_container = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                self.pin_lock_icon,
                self.pin_title_text,
                self.pin_fields,
                self.error_text
            ]
        )

        super().__init__(
            padding=24,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=self.main_container
        )

    def resize(self, width: int, pin_field_width: int) -> None:
        self.width = width
        self.error_text.width = width
        for field in self.fields:
            field.width = pin_field_width

    def _on_field_focus(self, index: int) -> None:
        if index != self._active_index:
            self._page.run_task(self.fields[self._active_index].focus)

    def _focus_field(self, index: int) -> None:
        self._active_index = index
        self._page.run_task(self.fields[index].focus)

    def _on_digit_change(self, index: int, value: str) -> None:
        if self._submitting:
            return

        value = next((character for character in value if character.isdigit()), "")

        if value and index < len(self.fields) - 1:
            self._focus_field(index + 1)
        elif not value and index > 0:
            self._focus_field(index - 1)
        else:
            self._active_index = index

        pin = "".join(field.value or "" for field in self.fields)
        if len(pin) == 4:
            self._submitting = True
            self.on_unlock(pin)

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self._submitting = False
        for field in self.fields:
            field.value = ""
        self.update()
        self._focus_field(0)

    def clear(self) -> None:
        for field in self.fields:
            field.value = ""
        self.error_text.value = ""
        self._active_index = 0
