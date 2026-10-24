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
    def __init__(self, lang: dict, on_unlock: Callable[[str], None]):
        self.on_unlock = on_unlock
        self.pin_field = ft.TextField(
            label=lang["app_lock.pin"],
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            password=True,
            max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=self._on_unlock
        )
        self.error_text = ft.Text(
            color=Color.NEGATIVE_ACTION,
            text_align=ft.TextAlign.CENTER
        )
        unlock_button = ft.Container(
            content=Text.H4(lang["app_lock.unlock"], color=Color.WHITE),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PRIMARY_ACTION,
            padding=16,
            border_radius=20,
            on_click=self._on_unlock
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
                    self.pin_field,
                    self.error_text,
                    unlock_button
                ]
            )
        )

    def _on_unlock(self, e=None) -> None:
        self.on_unlock(self.pin_field.value or "")

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self.pin_field.value = ""
        self.update()

    def clear(self) -> None:
        self.pin_field.value = ""
        self.error_text.value = ""
