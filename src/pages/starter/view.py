# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.database import db
from src.logger import Logger
from src.pages.starter.components import AppLockCard, DialogManager
from src.pages.starter.logic import LogicController
from src.utils import Color, Page, get_safe_page_size, scale_height, scale_width

Logger.info("Initializing Starter page...")


class StarterView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        self._page.skip_app_lock_once = False
        self.is_unlocked = not db.app_security.is_app_lock_enabled()

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
            refresh_callback=self._refresh_view,
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=0,
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
                ),
            ),
        )

        self._page.on_resize = self._resize_page
        self._resize_page()
        if not self.is_unlocked:
            self._show_lock_screen()

    def show_user_management_dialog(self) -> int:
        return self.dialogs.show_user_management_dialog()

    def _show_lock_screen(self) -> None:
        self.lock_screen = AppLockCard(
            page=self._page,
            lang=self.lang,
            on_unlock=self._on_unlock_click,
        )
        self.main_container.content.controls = [self.lock_screen]
        self._resize_page()

    def _on_unlock_click(self, pin: str) -> None:
        if not db.app_security.verify_app_lock_pin(pin):
            self.lock_screen.show_error(self.lang["app_lock.incorrect_pin"])
            return

        self.is_unlocked = True
        self.lock_screen.clear()
        self.main_container.content.controls = []
        self._page.update()
        self.show_user_management_dialog()

    def _refresh_view(self) -> int:
        self._resize_page()
        self.dialogs.user_list.update_data(
            users=self.controller.get_all_users(),
            username=self.user_info["username"]
        )
        self.dialogs.user_list.main_container.update()
        self.dialogs.user_dialog.update()
        self._page.update()
        return 0

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            dialog_width = page_width // 3 * 2
            user_list_height = scale_height(page_height, 300)
            lock_card_width = scale_width(page_width, 360)
            pin_field_width = scale_width(page_width, 70)

            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height
            if hasattr(self, "lock_screen"):
                self.lock_screen.resize(
                    width=lock_card_width,
                    pin_field_width=pin_field_width,
                )

            # Resizing other components
            self.dialogs.user_dialog.resize(
                width=dialog_width,
                list_height=user_list_height,
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")

def get_starter_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Starter page...")
    return StarterView(page, lang, user_info)
