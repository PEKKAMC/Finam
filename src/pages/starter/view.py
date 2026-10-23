# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger
from src.pages.global_components import AddUserField, DeleteUserDialog, UserList, UserManagementDialog
from src.pages.starter.logic import LogicController
from src.utils import Color, Page, get_safe_page_size

Logger.info("Initializing Starter page...")


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
        return self.user_dialog.show(self._page)

    def show_delete_prompt(self, username: str = "") -> int:
        if username:
            self.delete_dialog.selected_user = username
        return self.delete_dialog.show(self._page)

    def _close_user_management_dialog(self):
        self.user_dialog.dismiss(self._page)

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
        self.user_dialog.dismiss(self._page)
        self.controller.change_user(username)
        self._page.navigate_to("/home")()

class StarterView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
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
            refresh_callback=self._refresh_view
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=0
        )

        super().__init__(
            route="/starter",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def show_user_management_dialog(self) -> int:
        return self.dialogs.show_user_management_dialog()

    def _refresh_view(self) -> int:
        try:
            self.dialogs.user_list.update_data(
                self.controller.get_all_users(),
                self.user_info["username"]
            )
            self.dialogs.user_list.main_container.update()
            self.dialogs.user_dialog.update()
            self._page.update()
            return 0

        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e = None) -> int:
        try:
            page_width, page_height = self.get_safe_page_size(
                page=self._page
            )

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

            # Resizing other components
            self.dialogs.user_dialog.resize(
                width=page_width // 3 * 2,
                height=page_height // 2,
            )

            return 0

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")
            return 1

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")
            return 2

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")
            return -1


def get_starter_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Starter page...")
    return StarterView(page, lang, user_info)