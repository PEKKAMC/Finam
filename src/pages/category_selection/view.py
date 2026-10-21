# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import TypedDict

import flet as ft

from src.logger import Logger
from src.pages.category_selection.components import CategoryItem
from src.pages.category_selection.logic import LogicController
from src.pages.global_components import KeyboardContainer
from src.utils import Color, Page, Text, UISettings, get_safe_page_size

Logger.info("Initializing Category Selection page...")


class _Category(TypedDict):
    name: str
    icon: ft.IconData


class CategorySelectionView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.get_safe_page_size = get_safe_page_size

        self.controller = LogicController(self.user_info["username"])
        self.current_type = "expense"
        self.selected_category = ""
        self.snack_bar = ft.SnackBar
        self.category_items: list[CategoryItem] = []

        self.cancel_button = ft.TextButton(
            content=ft.Icon(ft.Icons.ARROW_BACK, color=Color.DEFAULT_BUTTON),
            on_click=self._page.navigate_to("/home")
        )

        self.expense_text = Text.P(self.lang["generic.expense"], color=Color.BLACK, weight=ft.FontWeight.BOLD)
        self.income_text = Text.P(self.lang["generic.income"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.NORMAL)

        self.expense_button = ft.Container(
            content=self.expense_text,
            bgcolor=Color.WHITE,
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
            height=340
        )

        self.keyboard_container = KeyboardContainer(
            page=self._page,
            lang=self.lang,
            on_save=self._on_save_clicked,
        )

        self.load_categories("expense")

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            expand=True,
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                spacing=15,
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
                content=ft.Stack(
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

    def load_categories(self, category_type: str) -> None:
        if category_type == "expense":
            self.expense_button.bgcolor = Color.WHITE
            self.expense_text.color = Color.BLACK
            self.expense_text.weight = ft.FontWeight.BOLD

            self.income_button.bgcolor = Color.TRANSPARENT
            self.income_text.color = Color.DEFAULT_TEXT
            self.income_text.weight = ft.FontWeight.NORMAL
        elif category_type == "income":
            self.income_button.bgcolor = Color.WHITE
            self.income_text.color = Color.BLACK
            self.income_text.weight = ft.FontWeight.BOLD

            self.expense_button.bgcolor = Color.TRANSPARENT
            self.expense_text.color = Color.DEFAULT_TEXT
            self.expense_text.weight = ft.FontWeight.NORMAL

        categories: list[list[_Category]] = []

        match category_type:
            case "expense":
                categories = [
                    [
                        {"name": "Mua sắm", "icon": ft.Icons.SHOPPING_CART},
                        {"name": "Đồ ăn", "icon": ft.Icons.RESTAURANT},
                        {"name": "Điện thoại", "icon": ft.Icons.SMARTPHONE},
                        {"name": "Giải trí", "icon": ft.Icons.SPORTS_ESPORTS}
                    ],
                    [
                        {"name": "Giáo dục", "icon": ft.Icons.SCHOOL},
                        {"name": "Làm đẹp", "icon": ft.Icons.CONTENT_CUT},
                        {"name": "Thể thao", "icon": ft.Icons.DIRECTIONS_RUN},
                        {"name": "Giao lưu", "icon": ft.Icons.PEOPLE}
                    ],
                    [
                        {"name": "Đi lại", "icon": ft.Icons.DIRECTIONS_BUS},
                        {"name": "Quần áo", "icon": ft.Icons.CHECKROOM},
                        {"name": "Ô tô", "icon": ft.Icons.DIRECTIONS_CAR},
                        {"name": "Thiết bị điện tử", "icon": ft.Icons.COMPUTER}
                    ],
                    [
                        {"name": "Du lịch", "icon": ft.Icons.FLIGHT},
                        {"name": "Sức khỏe", "icon": ft.Icons.FAVORITE},
                        {"name": "Thú cưng", "icon": ft.Icons.PETS},
                        {"name": "Sửa chữa", "icon": ft.Icons.BUILD}
                    ],
                    [
                        {"name": "Nhà ở", "icon": ft.Icons.HOME},
                        {"name": "Nhà", "icon": ft.Icons.CHAIR},
                        {"name": "Quà tặng", "icon": ft.Icons.CARD_GIFTCARD},
                        {"name": "Quyên góp", "icon": ft.Icons.VOLUNTEER_ACTIVISM}
                    ],
                    [
                        {"name": "Vé số", "icon": ft.Icons.CASINO},
                        {"name": "Ăn vặt", "icon": ft.Icons.BAKERY_DINING},
                        {"name": "Trẻ em", "icon": ft.Icons.CHILD_CARE},
                        {"name": "Rau quả", "icon": ft.Icons.LOCAL_FLORIST}
                    ],
                    [
                        {"name": "Hoa quả", "icon": ft.Icons.APPLE},
                        {"name": "Thêm", "icon": ft.Icons.ADD}
                    ]
                ]
            case "income":
                categories = [
                    [
                        {"name": "Lương", "icon": ft.Icons.WORK},
                        {"name": "Khoản đầu tư", "icon": ft.Icons.TRENDING_UP},
                        {"name": "Làm thêm", "icon": ft.Icons.MONEY},
                        {"name": "Tiền thưởng", "icon": ft.Icons.EMOJI_EVENTS}
                    ],
                    [
                        {"name": "Khác", "icon": ft.Icons.MONETIZATION_ON},
                        {"name": "Thêm", "icon": ft.Icons.ADD}
                    ]
                ]

        self.category_list.controls.clear()
        self.category_items.clear()
        for row in categories:
            category_row = ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER)
            for category in row:
                item = CategoryItem(
                    page=self._page,
                    lang=self.lang,
                    name=category["name"],
                    icon=category["icon"],
                    on_click=self._create_category_handler(category["name"]),
                    is_selected=False
                )
                self.category_items.append(item)
                category_row.controls.append(item)

            while len(category_row.controls) < 4:
                category_row.controls.append(ft.Container(expand=True))

            self.category_list.controls.append(category_row)

    def _create_category_handler(self, name: str):
        def handler(e=None) -> None:
            self.set_category(name)
        return handler

    def set_category(self, category_name: str):
        self.selected_category = category_name
        for item in self.category_items:
            item.update_selection(item.category_name == category_name)

        self.keyboard_container.visible = True
        if self._page is not None:
            self.update()

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

        self.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.overlay.append(self.snack_bar)
        self.snack_bar.open = True

        if success:
            if hasattr(self._page, "delete_cached_view"):
                self._page.delete_cached_view("/home")
                self._page.delete_cached_view("/spending")
            self._page.navigate_to("/home")()
        else:
            self.update()

    def _on_page_resize(self, e: ft.PageResizeEvent | None = None) -> int:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        try:
            # Resizing main container
            self.main_container.width = page_width
            self.main_container.height = page_height

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