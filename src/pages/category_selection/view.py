# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from typing import TypedDict

import flet as ft

from src.logger import Logger
from src.pages.category_selection.logic import LogicController
from src.utils import Color, Page, Text, UISettings, get_safe_page_size

Logger.info("Initializing Category Selection page...")


class _Category(TypedDict):
    name: str
    icon: ft.IconData


class CategoryItem(ft.Container):
    def __init__(self, page: Page, lang: dict, name: str, icon: ft.IconData, on_click: Callable, is_selected: bool = False):
        self._page = page
        self.lang = lang
        self.category_name = name
        self.icon = icon
        self._on_click = on_click
        self.is_selected = is_selected

        self.icon_circle = ft.Container(
            width=60,
            height=60,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            bgcolor="#FFEB3B" if self.is_selected else None,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon=self.icon, color=Color.BLACK if self.is_selected else Color.PRIMARY, size=30)
        )

        self.icon_label = Text.LABEL(value=self.category_name, color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER)

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

    def update_selection(self, selected: bool):
        self.is_selected = selected
        self.icon_circle.bgcolor = "#FFEB3B" if self.is_selected else None
        self.icon_circle.content.color = Color.BLACK if self.is_selected else Color.PRIMARY
        try:
            if self.icon_circle.page:
                self.icon_circle.update()
        except Exception:
            pass


class CategorySelectionView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.get_safe_page_size = get_safe_page_size

        self.controller = LogicController(self.user_info["username"])
        self.current_type = "expense"
        self.selected_category = ""
        self.amount_value = "0"
        self.category_items: list[CategoryItem] = []

        self.cancel_button = ft.TextButton(
            content=Text.P(self.lang["generic.cancel"], color=Color.DEFAULT_TEXT),
            on_click=self._page.navigate_to("/home")
        )

        self.title_text = Text.H3(value="Thêm", color=Color.DEFAULT_TEXT)

        self.expense_text = Text.P("Chi tiêu", color=Color.BLACK, weight=ft.FontWeight.BOLD)
        self.income_text = Text.P("Thu nhập", color=Color.DEFAULT_TEXT, weight=ft.FontWeight.NORMAL)

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

        self.amount_display = ft.Text(value="0", size=32, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)

        self.note_input = ft.TextField(
            hint_text="Enter a note...",
            label="Note : Enter a note...",
            label_style=ft.TextStyle(color=ft.Colors.GREY_400, size=13),
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.TRANSPARENT,
            prefix_icon=ft.Icons.NOTES,
            suffix_icon=ft.Icons.CAMERA_ALT,
            text_size=14,
            content_padding=10
        )

        self.keyboard_container = ft.Container(
            bgcolor="#121212",
            padding=10,
            border_radius=ft.BorderRadius.only(top_left=16, top_right=16),
            visible=False,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(icon=ft.Icons.CREDIT_CARD, icon_color=ft.Colors.WHITE, icon_size=20),
                            self.amount_display
                        ]
                    ),
                    ft.Container(
                        bgcolor="#1E1E1E",
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        content=self.note_input
                    ),
                    self._build_keypad()
                ]
            )
        )

        self.load_categories("expense")

        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                tight=True,
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.cancel_button,
                            self.title_text,
                            ft.Container(width=50)
                        ]
                    ),
                    self.segment_control,
                    self.category_list,
                    self.keyboard_container
                ]
            )
        )

        super().__init__(
            route="/category_selection",
            padding=0,
            bgcolor=Color.DIALOG_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=self.main_container
                )
            ]
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    def switch_type(self, category_type: str) -> None:
        self.current_type = category_type
        self.selected_category = ""
        self.keyboard_container.visible = False
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

    def _build_keypad(self) -> ft.Column:
        btn_bg = "#252B36"
        txt_color = ft.Colors.WHITE

        def k_btn(text: str, on_click, bg=btn_bg, fg=txt_color, icon=None):
            content = ft.Icon(icon, color=fg, size=20) if icon else ft.Text(text, size=18, color=fg, weight=ft.FontWeight.BOLD)
            return ft.Container(
                content=content,
                bgcolor=bg,
                alignment=ft.Alignment.CENTER,
                border_radius=8,
                expand=True,
                height=45,
                ink=True,
                on_click=on_click
            )

        return ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn("7", lambda e: self._on_key_press("7")),
                        k_btn("8", lambda e: self._on_key_press("8")),
                        k_btn("9", lambda e: self._on_key_press("9")),
                        ft.Container(
                            expand=True,
                            height=45,
                            bgcolor="#252B36",
                            border_radius=8,
                            alignment=ft.Alignment.CENTER,
                            ink=True,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.CALENDAR_MONTH, color="#FFD700", size=16),
                                    ft.Text("Today", color="#FFD700", size=13, weight=ft.FontWeight.BOLD)
                                ]
                            )
                        )
                    ]
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn("4", lambda e: self._on_key_press("4")),
                        k_btn("5", lambda e: self._on_key_press("5")),
                        k_btn("6", lambda e: self._on_key_press("6")),
                        k_btn("+", lambda e: self._on_key_press("+")),
                        k_btn("-", lambda e: self._on_key_press("-")),
                    ]
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn("1", lambda e: self._on_key_press("1")),
                        k_btn("2", lambda e: self._on_key_press("2")),
                        k_btn("3", lambda e: self._on_key_press("3")),
                        k_btn("×", lambda e: self._on_key_press("*")),
                        k_btn("÷", lambda e: self._on_key_press("/")),
                    ]
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn(".", lambda e: self._on_key_press(".")),
                        k_btn("0", lambda e: self._on_key_press("0")),
                        k_btn("", lambda e: self._on_backspace(), icon=ft.Icons.BACKSPACE),
                        k_btn("", lambda e: self._on_save_clicked(), bg=Color.PRIMARY_ACTION, icon=ft.Icons.CHECK)
                    ]
                )
            ]
        )

    def _on_key_press(self, val: str):
        if self.amount_value == "0" and val not in "+-*/.":
            self.amount_value = val
        else:
            self.amount_value += val
        self.amount_display.value = self.amount_value
        if self._page is not None:
            self.amount_display.update()

    def _on_backspace(self):
        if len(self.amount_value) > 1:
            self.amount_value = self.amount_value[:-1]
        else:
            self.amount_value = "0"
        self.amount_display.value = self.amount_value
        if self._page is not None:
            self.amount_display.update()

    def _on_save_clicked(self):
        vals = {
            "amount": self.amount_value,
            "category": self.selected_category,
            "note": self.note_input.value or ""
        }
        if self.current_type == "expense":
            success, message = self.controller.add_expense_entry(vals)
        else:
            success, message = self.controller.add_income_entry(vals)

        self.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.overlay.append(self.snack_bar)
        self.snack_bar.open = True

        if success:
            self._page.navigate_to("/home")()
        else:
            self.update()

    def _on_page_resize(self, e = None) -> None:
        page_width, page_height = self.get_safe_page_size(page=self._page)
        self.main_container.width = page_width


def get_category_selection_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading Category Selection page...")
    return CategorySelectionView(page, lang, user_info)