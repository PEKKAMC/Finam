# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Any

import flet as ft

from src.logger import Logger
from src.pages.category_selection.components import CategoryEditorDialog, CategorySelectionContent, DeleteCategoryDialog
from src.pages.category_selection.logic import LogicController
from src.pages.common import KeyboardContainer
from src.utils import Color, Page, get_safe_page_size, scale_width

Logger.info("Initializing Category Selection page...")


class CategorySelectionView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info["username"], self.lang)
        self.current_type = "expense"
        self.selected_category = ""

        # INITIALIZE PAGE COMPONENTS
        self.keyboard_container = KeyboardContainer(
            page=self._page,
            lang=self.lang,
            on_save=self._on_save_clicked,
        )

        self.keyboard_container.bottom = None

        self.category_editor = CategoryEditorDialog(
            self._page,
            self.lang,
            self.controller.data.get_category_icons(),
            self._save_custom_category,
            self._confirm_delete_category,
        )

        self.delete_category_dialog = DeleteCategoryDialog(
            self._page,
            self.lang,
            self._delete_custom_category,
        )

        self.content_component = CategorySelectionContent(
            page=self._page,
            lang=self.lang,
            on_cancel=self._on_cancel_clicked,
            on_type_change=self.switch_type,
        )

        self.load_categories("expense")

        super().__init__(
            route="/category_selection",
            padding=0,
            bgcolor=Color.DIALOG_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        self.content_component,
                        self.keyboard_container
                    ],
                ),
            ),
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

    def switch_type(self, category_type: str) -> None:
        self.current_type = category_type
        self.selected_category = ""
        self.keyboard_container.visible = False
        self.keyboard_container.reset_inputs()
        self.load_categories(category_type)
        if self._page is not None:
            self.update()

    def _get_return_route(self) -> str:
        previous_route = getattr(self._page, "previous_route", "")
        return previous_route if previous_route in ("/home", "/spending") else "/home"

    def _on_cancel_clicked(self, e: ft.ControlEvent) -> None:
        self._page.navigate_to(self._get_return_route())(e)

    def load_categories(self, category_type: str) -> None:
        categories = self.controller.get_default_categories(
            category_type
        ) + self.controller.get_custom_categories(category_type)
        self.content_component.category_type_selector.set_type(category_type)
        self.content_component.category_grid.set_categories(
            categories,
            category_type,
            self.selected_category,
            self.set_category,
            self._open_add_category,
            self._edit_custom_category,
        )

    def _open_add_category(self) -> None:
        self.category_editor.show_editor()

    def _edit_custom_category(self, category: dict[str, Any]) -> None:
        self.category_editor.show_editor(category)

    def _save_custom_category(self, name: str, icon_name: str, category_id: int | None) -> str | None:
        status = self.controller.save_custom_category(
            self.current_type, name, icon_name, category_id
        )
        error_keys = {
            1: "category_selection.category_name_invalid",
            2: "category_selection.category_icon_invalid",
            3: "category_selection.category_name_exists",
            -1: "category_selection.category_save_error",
        }
        if status != 0:
            return error_keys.get(status, "category_selection.category_save_error")

        if (
            category_id is not None
            and self.selected_category == self.category_editor.original_name
        ):
            self.selected_category = name.strip()
        self.load_categories(self.current_type)
        self.update()
        return None

    def _confirm_delete_category(self, category: dict[str, Any]) -> None:
        transaction_count = self.controller.get_category_transaction_count(
            self.current_type,
            category["name"],
        )
        self.delete_category_dialog.show_confirmation(category, transaction_count)

    def _delete_custom_category(self, category_id: int) -> bool:
        category = self.delete_category_dialog.category
        success = self.controller.delete_custom_category(
            category_id,
            self.current_type,
        )
        if not success:
            return False
        if category and self.selected_category == category["name"]:
            self.selected_category = ""
            self.keyboard_container.visible = False
            self.keyboard_container.reset_inputs()
        self.load_categories(self.current_type)
        self.update()
        return True

    def set_category(self, category_name: str) -> None:
        self.selected_category = category_name
        self.content_component.category_grid.set_selected_category(category_name)

        self.keyboard_container.visible = True
        if self._page is not None:
            self.update()

    def _refresh_view(self) -> int:
        self._resize_page()
        self.load_categories(self.current_type)
        self.update()
        return 0

    def _on_save_clicked(self, values: dict[str, Any], e: ft.ControlEvent | None = None) -> None:
        values["category"] = self.selected_category

        status = (
            self.controller.add_expense_entry(values)
            if self.current_type == "expense"
            else self.controller.add_income_entry(values)
        )
        if status == 0:
            self.switch_type("expense")
            self._page.navigate_to(self._get_return_route())(e)
            return

        message_keys = {
            1: "category_selection.error.missing_amount_category",
            2: "category_selection.error.amount_less_than_zero",
            3: "category_selection.error.invalid_amount",
            -1: (
                "category_selection.error.save_expense_failed"
                if self.current_type == "expense"
                else "category_selection.error.save_income_failed"
            ),
        }
        default_error_key = (
            "category_selection.error.save_expense_failed"
            if self.current_type == "expense"
            else "category_selection.error.save_income_failed"
        )
        message = self.lang[message_keys.get(status, default_error_key)]
        self.keyboard_container.show_status_message(message)

        self.update()

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, _page_height = self.get_safe_page_size(page=self._page)

            content_width = scale_width(page_width, 412)
            category_columns = (
                1
                if content_width < 160
                else 2
                if content_width < 240
                else 3
                if content_width < 320
                else 4
            )
            self.content_component.resize(page_width, content_width, category_columns)
            dialog_width = page_width * 6 // 7
            self.category_editor.resize(dialog_width)
            self.delete_category_dialog.resize(dialog_width)

            self.keyboard_container.resize(width=page_width)

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")


def get_category_selection_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading Category Selection page...")
    return CategorySelectionView(page, lang, user_info)
