# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.pages.global_components import AddUserField, DeleteUserDialog, UserList, UserManagementDialog
from src.pages.starter.logic import LogicController
from src.utils import Color, Page, Text, UISettings


class DialogManager:
    def __init__(self, page: Page, lang: dict, user_info: dict, controller: LogicController, refresh_callback: Callable):
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
            currencies=self.controller.get_currencies()
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
        self.user_list.update_data(
            self.controller.get_all_users(),
            self.user_info["username"]
        )
        try:
            self.user_list.main_container.update()
            self.user_dialog.update()
            self._page.update()
        except RuntimeError:
            pass
        return self.user_dialog.show()

    def show_delete_prompt(self, username: str = "") -> int:
        if username:
            self.delete_dialog.selected_user = username
        return self.delete_dialog.show()

    def _close_user_management_dialog(self):
        self.user_dialog.dismiss()

    def _handle_delete_confirm(self, username: str) -> int:
        self.controller.delete_user(username)
        self.refresh_view()
        return 0

    def handle_add_user(self, input_username: str, currency: str):
        if not input_username:
            return
        success, error_msg = self.controller.add_user(input_username, currency)
        if success:
            self.add_form.clear()
            self.refresh_view()
        else:
            self.add_form.show_error("error")

    def handle_change_user(self, username: str):
        self.user_dialog.dismiss()
        self.controller.change_user(username)
        self._page.navigate_to("/home")()


class AppLockCard(ft.Container):
    def __init__(
        self, page: Page, lang: dict, on_unlock: Callable[[str], None]
    ):
        self._page = page
        self.on_unlock = on_unlock
        self._submitting = False
        self._active_index = 0
        self.pin_fields = [
            ft.TextField(
                autofocus=index == 0,
                input_filter=ft.InputFilter(
                    allow=True,
                    regex_string=r"^[0-9]$",
                    replacement_string="",
                ),
                password=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_align=ft.TextAlign.CENTER,
                width=56,
                height=64,
                bgcolor=Color.CARD_BACKGROUND,
                border_color=Color.INPUT_BORDER,
                focused_border_color=Color.PRIMARY_ACTION,
                color=Color.PRIMARY_TEXT,
                text_size=24,
                on_change=lambda e, field_index=index: self._on_digit_change(
                    field_index, e.control.value or ""
                ),
                on_focus=lambda e, field_index=index: self._on_field_focus(
                    field_index
                ),
            )
            for index in range(4)
        ]
        self.error_text = ft.Text(
            color=Color.NEGATIVE_ACTION,
            text_align=ft.TextAlign.CENTER,
        )

        super().__init__(
            width=min(UISettings.MAX_APP_WIDTH - 40, 360),
            padding=24,
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, color=Color.PRIMARY, size=40),
                    Text.H3(lang["app_lock.title"], color=Color.PRIMARY_TEXT),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=self.pin_fields,
                    ),
                    self.error_text,
                ],
            ),
        )

    def _on_field_focus(self, index: int) -> None:
        if index != self._active_index:
            self._page.run_task(self.pin_fields[self._active_index].focus)

    def _focus_field(self, index: int) -> None:
        self._active_index = index
        self._page.run_task(self.pin_fields[index].focus)

    def _on_digit_change(self, index: int, value: str) -> None:
        if self._submitting:
            return

        value = next((character for character in value if character.isdigit()), "")
        if len(value) > 1:
            value = value[0]
            self.pin_fields[index].value = value

        if value and index < len(self.pin_fields) - 1:
            self._focus_field(index + 1)
        elif not value and index > 0:
            self._focus_field(index - 1)
        else:
            self._active_index = index

        pin = "".join(field.value or "" for field in self.pin_fields)
        if len(pin) == 4:
            self._submitting = True
            self.on_unlock(pin)

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self._submitting = False
        for field in self.pin_fields:
            field.value = ""
        self.update()
        self._focus_field(0)

    def clear(self) -> None:
        for field in self.pin_fields:
            field.value = ""
        self.error_text.value = ""
        self._active_index = 0
