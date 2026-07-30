# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.utils import Color, Text, UISettings

def get_categories(tab_type: str):
    if tab_type == "expense":
        return [
            {"name": "Mua sắm", "icon": ft.Icons.SHOPPING_CART},
            {"name": "Đồ ăn", "icon": ft.Icons.RESTAURANT},
            {"name": "Điện thoại", "icon": ft.Icons.SMARTPHONE},
            {"name": "Giải trí", "icon": ft.Icons.SPORTS_ESPORTS},
            {"name": "Giáo dục", "icon": ft.Icons.SCHOOL},
            {"name": "Làm đẹp", "icon": ft.Icons.CONTENT_CUT},
            {"name": "Thể thao", "icon": ft.Icons.DIRECTIONS_RUN},
            {"name": "Giao lưu", "icon": ft.Icons.PEOPLE},
            {"name": "Đi lại", "icon": ft.Icons.DIRECTIONS_BUS},
            {"name": "Quần áo", "icon": ft.Icons.CHECKROOM},
            {"name": "Ô tô", "icon": ft.Icons.DIRECTIONS_CAR},
            {"name": "Thiết bị điện tử", "icon": ft.Icons.COMPUTER},
            {"name": "Du lịch", "icon": ft.Icons.FLIGHT},
            {"name": "Sức khỏe", "icon": ft.Icons.FAVORITE},
            {"name": "Thú cưng", "icon": ft.Icons.PETS},
            {"name": "Sửa chữa", "icon": ft.Icons.BUILD},
            {"name": "Nhà ở", "icon": ft.Icons.HOME},
            {"name": "Nhà", "icon": ft.Icons.CHAIR},
            {"name": "Quà tặng", "icon": ft.Icons.CARD_GIFTCARD},
            {"name": "Quyên góp", "icon": ft.Icons.VOLUNTEER_ACTIVISM},
            {"name": "Vé số", "icon": ft.Icons.CASINO},
            {"name": "Ăn vặt", "icon": ft.Icons.BAKERY_DINING},
            {"name": "Trẻ em", "icon": ft.Icons.CHILD_CARE},
            {"name": "Rau quả", "icon": ft.Icons.LOCAL_FLORIST},
            {"name": "Hoa quả", "icon": ft.Icons.APPLE},
            {"name": "Thêm", "icon": ft.Icons.ADD},
        ]
    elif tab_type == "income":
        return [
            {"name": "Lương", "icon": ft.Icons.WORK},
            {"name": "Khoản đầu tư", "icon": ft.Icons.TRENDING_UP},
            {"name": "Làm thêm", "icon": ft.Icons.MONEY},
            {"name": "Tiền thưởng", "icon": ft.Icons.EMOJI_EVENTS},
            {"name": "Khác", "icon": ft.Icons.MONETIZATION_ON},
            {"name": "Thêm", "icon": ft.Icons.ADD},
        ]
    return []

class CategoryItem(ft.Container):
    def __init__(self, name: str, icon_name: str | ft.IconData, on_click=None):
        # Convert string icon names to IconData if needed (useful for home.py compatibility)
        actual_icon = getattr(ft.Icons, icon_name.upper()) if isinstance(icon_name, str) else icon_name
        super().__init__(
            on_click=on_click,
            ink=True,
            border_radius=10,
            width=85,
            height=115,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Container(
                        width=55,
                        height=55,
                        bgcolor=Color.MENU_BACKGROUND,
                        border_radius=30,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icon=actual_icon, color=Color.WHITE, size=26)
                    ),
                    Text.LABEL(value=name, color=Color.DEFAULT_TEXT, text_align=ft.TextAlign.CENTER)
                ]
            )
        )

class CategorySelectionDialog(ft.AlertDialog):
    def __init__(self, on_select):
        self.on_select = on_select
        self.grid_view = ft.Row(wrap=True, spacing=15, run_spacing=15, alignment=ft.MainAxisAlignment.CENTER)
        super().__init__(
            title=Text.H3("Select Category", color=Color.DEFAULT_TEXT),
            bgcolor=Color.WHITE,
            inset_padding=0,
            content_padding=20,
            content=ft.Container(
                width=UISettings.MAX_APP_WIDTH,
                height=UISettings.MAX_APP_HEIGHT,
                content=ft.Column([self.grid_view], scroll=ft.ScrollMode.AUTO)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(), style=ft.ButtonStyle(color=Color.DEFAULT_TEXT))
            ]
        )

    def load_categories(self, category_type: str):
        self.title.value = "Expense Category" if category_type == "expense" else "Income Category"
        categories = get_categories(category_type)
        self.grid_view.controls.clear()
        for cat in categories:
            self.grid_view.controls.append(CategoryItem(name=cat["name"], icon_name=cat["icon"], on_click=self._create_handler(cat["name"])))
        if self.page:
            self.update()

    def _create_handler(self, name: str):
        def handler(e):
            self.on_select(name)
            return e
        return handler

    def close_dialog(self):
        self.open = False
        self.update()

class IncomeInputDialog(ft.AlertDialog):
    def __init__(self, on_save, on_cancel, on_category_click):
        self.amount_input = ft.TextField(
            label="Amount", color=Color.DEFAULT_TEXT, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, border_color=Color.INPUT_BORDER, width=400, focused_border_color=Color.PRIMARY_ACTION
        )
        self.category_value = ""
        self.category_text = Text.P("Select Category", color=Color.SECONDARY_TEXT)
        self.category_button = ft.Container(
            content=ft.Row(controls=[self.category_text, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=Color.SECONDARY_TEXT)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=400, height=55, border_radius=10, border=ft.Border.all(1, Color.INPUT_BORDER), padding=ft.Padding.symmetric(horizontal=12),
            ink=True, on_click=on_category_click, alignment=ft.Alignment.CENTER_LEFT
        )
        self.note_input = ft.TextField(
            label="Note (Optional)", color=Color.DEFAULT_TEXT, prefix_icon=ft.Icons.NOTES, border_radius=10, width=400, border_color=Color.INPUT_BORDER, focused_border_color=Color.PRIMARY_ACTION
        )
        submit_button = ft.Button(
            "Save Income", icon=ft.Icons.ADD_CIRCLE, on_click=on_save, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE, width=400, height=55,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )
        super().__init__(
            content_padding=0, bgcolor=Color.TRANSPARENT,
            content=ft.Container(
                width=UISettings.MAX_APP_WIDTH * 0.9, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
                content=ft.Column(tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.PRIMARY_TEXT), Text.H3("Add Income", color=Color.DEFAULT_TEXT), ft.Container(width=40)]),
                    ft.Container(height=10),
                    ft.Column(spacing=15, controls=[self.amount_input, self.category_button, self.note_input]),
                    ft.Container(height=25), submit_button, ft.Container(height=10),
                ])
            )
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
        self.category_text.value = "Select Category"
        self.category_text.color = Color.SECONDARY_TEXT
        self.note_input.value = ""

class ExpenseInputDialog(ft.AlertDialog):
    def __init__(self, on_save, on_cancel, on_category_click):
        self.amount_input = ft.TextField(
            label="Amount", color=Color.DEFAULT_TEXT, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, border_color=Color.INPUT_BORDER, width=400, focused_border_color=Color.PRIMARY_ACTION
        )
        self.category_value = ""
        self.category_text = Text.P("Select Category", color=Color.SECONDARY_TEXT)
        self.category_button = ft.Container(
            content=ft.Row(controls=[self.category_text, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=Color.SECONDARY_TEXT)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=400, height=55, border_radius=10, border=ft.Border.all(1, Color.INPUT_BORDER), padding=ft.Padding.symmetric(horizontal=12),
            ink=True, on_click=on_category_click, alignment=ft.Alignment.CENTER_LEFT
        )
        self.note_input = ft.TextField(
            label="Note (Optional)", color=Color.DEFAULT_TEXT, prefix_icon=ft.Icons.NOTES, border_radius=10, border_color=Color.INPUT_BORDER, width=400, focused_border_color=Color.PRIMARY_ACTION
        )
        submit_button = ft.Button(
            "Save Expense", icon=ft.Icons.ADD_CIRCLE, on_click=on_save, bgcolor=Color.PRIMARY_ACTION, color=Color.WHITE, width=400, height=55,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )
        super().__init__(
            content_padding=0, bgcolor=Color.TRANSPARENT,
            content=ft.Container(
                width=UISettings.MAX_APP_WIDTH * 0.9, padding=25, bgcolor=Color.DIALOG_BACKGROUND, border_radius=20,
                content=ft.Column(tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.IconButton(ft.Icons.CLOSE, on_click=on_cancel, icon_color=Color.PRIMARY_TEXT), Text.H3("Add Expense", color=Color.DEFAULT_TEXT), ft.Container(width=40)]),
                    ft.Container(height=10),
                    ft.Column(spacing=15, controls=[self.amount_input, self.category_button, self.note_input]),
                    ft.Container(height=25), submit_button, ft.Container(height=10),
                ])
            )
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
        self.category_text.value = "Select Category"
        self.category_text.color = Color.SECONDARY_TEXT
        self.note_input.value = ""