# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.category_selection.components import CategoryEditorDialog, CategoryItem, DeleteCategoryDialog
from src.pages.category_selection.logic import LogicController
from src.pages.global_components import KeyboardContainer
from src.utils import Color, Page, Text, UISettings, get_safe_page_size

Logger.info("Initializing Category Selection page...")


class CategorySelectionView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.get_safe_page_size = get_safe_page_size

        self.controller = LogicController(self.user_info["username"])
        self.current_type = "expense"
        self.selected_category = ""
        self.category_items: list[CategoryItem] = []

        self.cancel_button = ft.TextButton(
            content=ft.Icon(ft.Icons.ARROW_BACK, color=Color.DEFAULT_BUTTON),
            on_click=self._on_cancel_clicked
        )

        self.expense_text = Text.P(
            self.lang["generic.expense"],
            color=Color.NAVIGATION_ACTIVE_TEXT,
            weight=ft.FontWeight.BOLD,
        )
        self.income_text = Text.P(
            self.lang["generic.income"],
            color=Color.DEFAULT_TEXT,
            weight=ft.FontWeight.NORMAL,
        )

        self.expense_button = ft.Container(
            content=self.expense_text,
            bgcolor=Color.CARD_BACKGROUND,
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e: self.switch_type("expense"),
            expand=True
        )

        self.income_button = ft.Container(
            content=self.income_text,
            bgcolor=Color.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e: self.switch_type("income"),
            expand=True
        )

        self.segment_control = ft.Container(
            bgcolor=Color.INPUT_BORDER,
            border_radius=10,
            padding=3,
            content=ft.Row(
                controls=[self.expense_button, self.income_button],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=400
        )

        self.category_list = ft.Column(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        self.keyboard_container = KeyboardContainer(
            page=self._page,
            lang=self.lang,
            on_save=self._on_save_clicked,
        )
        self.keyboard_container.bottom = None
        self.category_editor = CategoryEditorDialog(
            self._page,
            self.lang,
            self.controller.data.category_icons,
            self._save_custom_category,
            self._confirm_delete_category,
        )
        self.delete_category_dialog = DeleteCategoryDialog(
            self._page,
            self.lang,
            self._delete_custom_category,
        )
        self.load_categories("expense")

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            expand=True,
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                spacing=15,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        controls=[
                            self.cancel_button
                        ]
                    ),
                    self.segment_control,
                    self.category_list
                ]
            )
        )

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
                        self.main_container,
                        self.keyboard_container
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

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
        if category_type == "expense":
            self.expense_button.bgcolor = Color.EXPENSE_BACKGROUND
            self.expense_text.color = Color.NAVIGATION_ACTIVE_TEXT
            self.expense_text.weight = ft.FontWeight.BOLD

            self.income_button.bgcolor = Color.TRANSPARENT
            self.income_text.color = Color.DEFAULT_TEXT
            self.income_text.weight = ft.FontWeight.NORMAL
        elif category_type == "income":
            self.income_button.bgcolor = Color.INCOME_BACKGROUND
            self.income_text.color = Color.NAVIGATION_ACTIVE_TEXT
            self.income_text.weight = ft.FontWeight.BOLD

            self.expense_button.bgcolor = Color.TRANSPARENT
            self.expense_text.color = Color.DEFAULT_TEXT
            self.expense_text.weight = ft.FontWeight.NORMAL

        self.category_list.controls.clear()
        self.category_items.clear()
        categories = self.controller.get_default_categories(
            category_type
        ) + self.controller.get_custom_categories(category_type)
        grid_items = [
            (
                category,
                "id" in category,
                False,
            )
            for category in categories
        ]
        grid_items.append(
            (
                {
                    "name": self.lang["category_selection.add_category"],
                    "icon": "ADD",
                },
                False,
                True,
            )
        )
        for start in range(0, len(grid_items), 4):
            category_row = ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER)
            for category, is_custom, is_add_action in grid_items[start : start + 4]:
                icon_name = category["icon"]
                item = CategoryItem(
                    page=self._page,
                    lang=self.lang,
                    name=category["name"],
                    icon=getattr(ft.Icons, icon_name),
                    on_click=(
                        self._open_add_category
                        if is_add_action
                        else self._create_category_handler(category["name"])
                    ),
                    is_selected=(
                        not is_add_action
                        and category["name"] == self.selected_category
                    ),
                    icon_color=(
                        Color.EXPENSE_COLOR
                        if category_type == "expense"
                        else Color.INCOME_COLOR
                    ),
                    selected_background_color=(
                        Color.EXPENSE_BACKGROUND
                        if category_type == "expense"
                        else Color.INCOME_BACKGROUND
                    ),
                    on_edit=(
                        lambda e, custom_category=category: self._edit_custom_category(
                            custom_category
                        )
                    )
                    if is_custom
                    else None,
                )
                if not is_add_action:
                    self.category_items.append(item)
                category_row.controls.append(item)

            while len(category_row.controls) < 4:
                category_row.controls.append(ft.Container(expand=True))

            self.category_list.controls.append(category_row)

    def _create_category_handler(self, name: str):
        def handler(e=None) -> None:
            self.set_category(name)
        return handler

    def _open_add_category(self, e=None) -> None:
        self.category_editor.show_editor()

    def _edit_custom_category(self, category: dict) -> None:
        self.category_editor.show_editor(category)

    def _save_custom_category(self, name: str, icon_name: str, category_id: int | None) -> str | None:
        success, code = self.controller.save_custom_category(self.current_type, name, icon_name, category_id)
        if not success:
            error_keys = {
                "INVALID_NAME": "category_selection.category_name_invalid",
                "INVALID_ICON": "category_selection.category_icon_invalid",
                "DUPLICATE_NAME": "category_selection.category_name_exists",
                "SAVE_FAILED": "category_selection.category_save_error",
            }
            return error_keys.get(code, "category_selection.category_save_error")

        if (
            category_id is not None
            and self.selected_category == self.category_editor.original_name
        ):
            self.selected_category = name.strip()
        self.load_categories(self.current_type)
        self.update()
        return None

    def _confirm_delete_category(self, category: dict) -> None:
        transaction_count = self.controller.get_category_transaction_count(
            self.current_type,
            category["name"],
        )
        self.delete_category_dialog.show_confirmation(
            category, transaction_count
        )

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

    def set_category(self, category_name: str):
        self.selected_category = category_name
        for item in self.category_items:
            item.update_selection(item.category_name == category_name)

        self.keyboard_container.visible = True
        if self._page is not None:
            self.update()

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self.load_categories(self.current_type)
            for item in self.category_items:
                item.update_selection(item.category_name == self.selected_category)
            self.update()
            return 0
        except Exception as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_save_clicked(self, values: dict):
        values["category"] = self.selected_category

        if self.current_type == "expense":
            success, code = self.controller.add_expense_entry(values)
        else:
            success, code = self.controller.add_income_entry(values)

        if code == "MISSING_AMOUNT_CATEGORY":
            message = self.lang["category_selection.error.missing_amount_category"]
        elif code == "AMOUNT_LESS_THAN_ZERO":
            message = self.lang["category_selection.error.amount_less_than_zero"]
        elif code == "INCOME_ADDED_SUCCESS":
            message = self.lang["category_selection.income_added_success"]
        elif code == "EXPENSE_ADDED_SUCCESS":
            message = self.lang["category_selection.expense_added_success"]
        elif code == "SAVE_INCOME_FAILED":
            message = self.lang["category_selection.error.save_income_failed"]
        elif code == "SAVE_EXPENSE_FAILED":
            message = self.lang["category_selection.error.save_expense_failed"]
        else:
            message = ""

        if success:
            self.keyboard_container.reset_inputs()
            self.keyboard_container.show_status_message(message, is_success=True)
        else:
            self.keyboard_container.show_status_message(message)

        self.update()

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        try:
            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = None

            # Resizing other components
            self.keyboard_container.resize(
                width=page_width
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


def get_category_selection_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Category Selection page...")
    return CategorySelectionView(page, lang, user_info)