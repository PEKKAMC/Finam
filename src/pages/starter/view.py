# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.database import db
from src.logger import Logger
from src.pages.starter.components import AppLockCard, DialogManager
from src.pages.starter.logic import LogicController
from src.utils import Color, Page, get_safe_page_size

Logger.info("Initializing Starter page...")


class StarterView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.is_unlocked = not db.app_security.is_app_lock_enabled()
        self.get_safe_page_size = get_safe_page_size
        self.controller = LogicController(self.user_info)
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info,
            controller=self.controller,
            refresh_callback=self._refresh_view
        )
        self.main_container = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                    controls=[self.main_container]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()
        if not self.is_unlocked:
            self._show_lock_screen()

    def show_user_management_dialog(self) -> int:
        return self.dialogs.show_user_management_dialog()

    def _show_lock_screen(self) -> None:
        self.lock_screen = AppLockCard(self.lang, self._on_unlock_click)
        self.main_container.content.controls = [self.lock_screen]

    def _on_unlock_click(self, pin: str) -> None:
        if not db.app_security.verify_app_lock_pin(pin):
            self.lock_screen.show_error(self.lang["app_lock.incorrect_pin"])
            return

        self.is_unlocked = True
        self.lock_screen.clear()
        self.main_container.content.controls.clear()
        self._page.update()
        self.show_user_management_dialog()

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

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        try:
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
