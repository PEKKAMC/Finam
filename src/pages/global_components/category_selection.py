# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from typing import TypedDict

import flet as ft

from src.utils import Color, Text, UISettings


class _Category(TypedDict):
    name: str
    icon: ft.IconData


class CategoryItem(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, name: str, icon: ft.IconData, on_click: Callable):
        self._page = page
        self.lang = lang
        self.category_name = name
        self.icon = icon
        self._on_click = on_click

        self.icon_circle = ft.Container(
            width=60,
            height=60,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon=self.icon, color=Color.PRIMARY, size=30)
        )

        self.icon_label = Text.LABEL(value=self.category_name, color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER)

        # ITEM CONTAINER
        self.main_container = ft.Container(
            width=75,
            height=75,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=-10,
                controls=[
                    self.icon_circle,
                    self.icon_label
                ],
            ),
            on_click=self._on_click,
            ink=True,
            border_radius=UISettings.CARD_BORDER_RADIUS
        )

        super().__init__(
            content=self.main_container,
            expand=True,
            alignment=ft.Alignment.CENTER
        )


class CategorySelectionDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, lang: dict, on_select: Callable):
        self._page = page
        self.lang = lang
        self._on_select = on_select

        self.category_list = ft.Column(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )

        self.cancel_button = ft.TextButton(
            content=self.lang["generic.cancel"],
            on_click=lambda e: self.close_dialog(),
            style=ft.ButtonStyle(color=Color.DEFAULT_TEXT)
        )

        self.main_container = ft.Container(
            content=self.category_list
        )

        super().__init__(
            title=Text.H3(value=self.lang["spending.select_category"], color=Color.DEFAULT_TEXT),
            bgcolor=Color.DIALOG_BACKGROUND,
            content_padding=20,
            content=self.main_container,
            actions=[
                self.cancel_button
            ]
        )

    # TODO: Use language instead of hardcoding name.
    def load_categories(self, category_type: str) -> None:
        categories: list[list[_Category]] = []

        match category_type: # Categories divided into rows of 4 for organization (temporary)
            case "expense":
                self.title.value = self.lang["spending.expense_category"]
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
                self.title.value = self.lang["spending.income_category"]
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
        for row in categories:
            category_row = ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            for category in row:
                category_row.controls.append(CategoryItem(
                    page=self._page,
                    lang=self.lang,
                    name=category["name"],
                    icon=category["icon"],
                    on_click=self._create_handler(category["name"])
                ))

            while len(category_row.controls) < 4:
                category_row.controls.append(ft.Container(expand=True))

            self.category_list.controls.append(category_row)

    def _create_handler(self, name: str):
        def handler(e):
            self._on_select(name)
            return e
        return handler

    def close_dialog(self):
        self.open = False
        self.update()

    def resize(self, dialog_width: int) -> None:
        self.content.width = dialog_width

class IncomeInputDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, lang: dict, on_save=None, on_cancel=None, on_category_click=None):
        self._page = page
        self.lang = lang

        # INTIAL VALUES
        self.category_value = ""
        self.category_text = Text.P(self.lang["spending.select_category"], color=Color.SECONDARY_TEXT)
        self.income_icon = ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=Color.SECONDARY_TEXT)

        # DIALOG FIELDS
        self.amount_input = ft.TextField(
            label=lang["generic.amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,12}$", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            width=400,
            focused_border_color=Color.PRIMARY_ACTION
        )

        self.category_button = ft.Container(
            content=ft.Row(
                controls=[
                    self.category_text,
                    self.income_icon
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=400,
            height=55,
            border_radius=10,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            padding=ft.Padding.symmetric(horizontal=12),
            ink=True,
            on_click=on_category_click,
            alignment=ft.Alignment.CENTER_LEFT
        )

        self.note_input = ft.TextField(
            label="Note (Optional)",
            color=Color.DEFAULT_TEXT,
            prefix_icon=ft.Icons.NOTES,
            border_radius=10,
            width=400,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION
        )

        # MAIN DIALOG CONTAINER
        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH * 0.9,
            padding=25,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=20,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.PRIMARY_TEXT),
                            Text.H3("Add Income", color=Color.DEFAULT_TEXT), ft.Container(width=40)
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Column(
                        spacing=15,
                        controls=[
                            self.amount_input,
                            self.category_button,
                            self.note_input
                        ]
                    ),
                    ft.Container(height=25),
                    ft.Button(
                        content="Save Income",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=on_save,
                        bgcolor=Color.PRIMARY_ACTION,
                        color=Color.WHITE,
                        width=400,
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                    ),
                    ft.Container(height=10)
                ]
            )
        )
        super().__init__(
            content_padding=0,
            bgcolor=Color.TRANSPARENT,
            content=self.main_container
        )

    def set_category(self, category_name: str):
        self.category_value = category_name
        self.category_text.value = category_name
        self.category_text.color = Color.DEFAULT_TEXT
        self.category_button.update()

    def get_values(self):
        return {"amount": self.amount_input.value, "category": self.category_value, "note": self.note_input.value}

    def clear(self):
        self.amount_input.value = ""
        self.category_value = ""
        self.category_text.value = self.lang["spending.select_category"]
        self.category_text.color = Color.SECONDARY_TEXT
        self.note_input.value = ""

    def resize(self, width: int) -> None:
        self.main_container.width = width

class ExpenseInputDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, lang: dict, on_save=None, on_cancel=None, on_category_click=None):
        self._page = page
        self.lang = lang

        # INTIAL VALUES
        self.category_value = ""
        self.category_text = Text.P(self.lang["spending.select_category"], color=Color.SECONDARY_TEXT)
        self.expense_icon = ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=Color.SECONDARY_TEXT)

        # DIALOG FIELDS
        self.amount_input = ft.TextField(
            label=self.lang["generic.amount"],
            color=Color.DEFAULT_TEXT,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,12}$", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            width=400,
            focused_border_color=Color.PRIMARY_ACTION
        )

        self.category_button = ft.Container(
            content=ft.Row(
                controls=[
                    self.category_text,
                    self.expense_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            width=400,
            height=55,
            border_radius=10,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            padding=ft.Padding.symmetric(horizontal=12),
            ink=True,
            on_click=on_category_click,
            alignment=ft.Alignment.CENTER_LEFT
        )

        self.note_input = ft.TextField(
            label="Note (Optional)",
            color=Color.DEFAULT_TEXT,
            prefix_icon=ft.Icons.NOTES,
            border_radius=10,
            border_color=Color.INPUT_BORDER,
            width=400,
            focused_border_color=Color.PRIMARY_ACTION
        )

        # MAIN DIALOG CONTAINER
        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            bgcolor=Color.DIALOG_BACKGROUND,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.PRIMARY_TEXT),
                            Text.H3(value="Add Expense", color=Color.DEFAULT_TEXT)
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Column(
                        spacing=15,
                        controls=[
                            self.amount_input,
                            self.category_button,
                            self.note_input
                        ]
                    ),
                    ft.Container(height=25),
                    ft.Button(
                        content="Save Expense",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=on_save,
                        bgcolor=Color.PRIMARY_ACTION,
                        color=Color.WHITE,
                        width=400,
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                    )
                ]
            )
        )
        super().__init__(
            content_padding=0,
            bgcolor=Color.TRANSPARENT,
            content=self.main_container
        )

    def set_category(self, category_name: str):
        self.category_value = category_name
        self.category_text.value = category_name
        self.category_text.color = Color.DEFAULT_TEXT
        self.category_button.update()

    def get_values(self):
        return {"amount": self.amount_input.value, "category": self.category_value, "note": self.note_input.value}

    def clear(self):
        self.amount_input.value = ""
        self.category_value = ""
        self.category_text.value = self.lang["spending.select_category"]
        self.category_text.color = Color.SECONDARY_TEXT
        self.note_input.value = ""

    def resize(self, width: int) -> None:
        self.main_container.width = width