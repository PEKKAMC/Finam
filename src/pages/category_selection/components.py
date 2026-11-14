# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from typing import Any

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings


class CategoryItem(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], name: str, icon: ft.IconData, on_click: Callable[..., None], is_selected: bool = False, on_edit: Callable[..., None] | None = None, icon_color: str = Color.PRIMARY, selected_background_color: str = Color.NAVIGATION_ACTIVE_BACKGROUND) -> None:
        self._page = page
        self.lang = lang
        self.category_name = name
        self.icon = icon
        self._on_click = on_click
        self.is_selected = is_selected
        self.selected_background_color = selected_background_color

        # TEXT AND ICON COMPONENTS
        # Dynamic texts
        self.icon_label = Text.LABEL(
            value=self.category_name,
            color=Color.NAVIGATION_ACTIVE_TEXT
            if self.is_selected
            else Color.DEFAULT_TEXT,
            text_align=ft.TextAlign.CENTER
        )

        # Dynamic icons
        self.icon_control = ft.Icon(icon=self.icon, color=icon_color)

        # CONTAINER COMPONENTS
        self.icon_circle = ft.Container(
            border_radius=8,
            bgcolor=(self.selected_background_color if self.is_selected else None),
            alignment=ft.Alignment.CENTER,
            content=self.icon_control
        )

        self.main_container = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    self.icon_circle,
                    self.icon_label
                ]
            ),
            border_radius=8,
            bgcolor=(
                self.selected_background_color
                if self.is_selected
                else Color.TRANSPARENT
            )
        )

        super().__init__(
            content=ft.GestureDetector(
                content=self.main_container,
                on_tap=self._on_click,
                on_long_press=on_edit,
                on_secondary_tap=on_edit
            ),
            expand=True,
            alignment=ft.Alignment.CENTER
        )

    def resize(self, width: int, height: int, icon_size: int, glyph_size: int) -> None:
        self.main_container.width = width
        self.main_container.height = height
        self.icon_circle.width = icon_size
        self.icon_circle.height = icon_size
        self.icon_control.size = glyph_size
        self.icon_label.width = width

    def update_selection(self, selected: bool) -> None:
        self.is_selected = selected
        self.main_container.bgcolor = (
            self.selected_background_color if self.is_selected else Color.TRANSPARENT
        )
        self.icon_circle.bgcolor = (
            self.selected_background_color if self.is_selected else None
        )
        self.icon_label.color = (
            Color.NAVIGATION_ACTIVE_TEXT if self.is_selected else Color.DEFAULT_TEXT
        )


class CategoryTypeSelector(ft.Container):
    def __init__(self, lang: dict[str, str], on_change: Callable[[str], None]) -> None:
        self.on_change = on_change

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.expense_text = Text.P(lang["generic.expense"], color=Color.NAVIGATION_ACTIVE_TEXT, weight=ft.FontWeight.BOLD)
        self.income_text = Text.P(lang["generic.income"], color=Color.DEFAULT_TEXT, weight=ft.FontWeight.NORMAL)

        # CONTAINER COMPONENTS
        self.expense_button = ft.Container(
            content=self.expense_text,
            bgcolor=Color.EXPENSE_BACKGROUND,
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e: self.on_change("expense"),
            expand=True
        )

        self.income_button = ft.Container(
            content=self.income_text,
            bgcolor=Color.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e: self.on_change("income"),
            expand=True
        )

        super().__init__(
            bgcolor=Color.INPUT_BORDER,
            border_radius=10,
            padding=3,
            content=ft.Row(
                controls=[self.expense_button, self.income_button],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def set_type(self, category_type: str) -> None:
        is_expense = category_type == "expense"
        self.expense_button.bgcolor = (
            Color.EXPENSE_BACKGROUND if is_expense else Color.TRANSPARENT
        )
        self.expense_text.color = (
            Color.NAVIGATION_ACTIVE_TEXT if is_expense else Color.DEFAULT_TEXT
        )
        self.expense_text.weight = (
            ft.FontWeight.BOLD if is_expense else ft.FontWeight.NORMAL
        )
        self.income_button.bgcolor = (
            Color.TRANSPARENT if is_expense else Color.INCOME_BACKGROUND
        )
        self.income_text.color = (
            Color.DEFAULT_TEXT if is_expense else Color.NAVIGATION_ACTIVE_TEXT
        )
        self.income_text.weight = (
            ft.FontWeight.NORMAL if is_expense else ft.FontWeight.BOLD
        )


class CategoryGrid(ft.Column):
    def __init__(self, page: Page, lang: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.category_items: list[CategoryItem] = []
        self._categories: list[dict[str, Any]] = []
        self._category_type = "expense"
        self._selected_category = ""
        self._on_select: Callable[[str], None] = lambda _name: None
        self._on_add: Callable[[], None] = lambda: None
        self._on_edit: Callable[[dict[str, Any]], None] = lambda _category: None
        self._rows: list[ft.Row] = []
        self._columns = 4
        self._content_width = 300
        self._item_width = 75
        self._item_height = 75
        self._icon_size = 52
        self._glyph_size = 30

        # CONTAINER COMPONENTS
        super().__init__(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def set_categories(self, categories: list[dict[str, Any]], category_type: str, selected_category: str, on_select: Callable[[str], None], on_add: Callable[[], None], on_edit: Callable[[dict[str, Any]], None]) -> None:
        self._categories = categories
        self._category_type = category_type
        self._selected_category = selected_category
        self._on_select = on_select
        self._on_add = on_add
        self._on_edit = on_edit
        self._render()

    def set_selected_category(self, name: str) -> None:
        self._selected_category = name
        for item in self.category_items:
            item.update_selection(item.category_name == name)

    def resize(self, content_width: int, columns: int, item_width: int, item_height: int, icon_size: int, glyph_size: int) -> None:
        columns_changed = columns != self._columns
        self._columns = columns
        self._content_width = content_width
        self._item_width = item_width
        self._item_height = item_height
        self._icon_size = icon_size
        self._glyph_size = glyph_size
        if columns_changed:
            self._render()
            return
        for row in self._rows:
            row.width = content_width
        for item in self.category_items:
            item.resize(item_width, item_height, icon_size, glyph_size)

    def _render(self) -> None:
        self.controls.clear()
        self.category_items.clear()
        self._rows.clear()
        grid_items: list[tuple[dict[str, Any], bool, bool]] = [
            *((category, "id" in category, False) for category in self._categories),
            (
                {
                    "name": self.lang["category_selection.add_category"],
                    "icon": "ADD",
                },
                False,
                True
            )
        ]

        for start in range(0, len(grid_items), self._columns):
            category_row = ft.Row(
                width=self._content_width,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            for category, is_custom, is_add_action in grid_items[
                start : start + self._columns
            ]:
                category_name = category["name"]
                item = CategoryItem(
                    page=self._page,
                    lang=self.lang,
                    name=category_name,
                    icon=getattr(ft.Icons, category["icon"]),
                    on_click=(
                        self._on_add
                        if is_add_action
                        else lambda _event, name=category_name: self._on_select(name)
                    ),
                    is_selected=(
                        not is_add_action
                        and category_name == self._selected_category
                    ),
                    icon_color=(
                        Color.EXPENSE_COLOR
                        if self._category_type == "expense"
                        else Color.INCOME_COLOR
                    ),
                    selected_background_color=(
                        Color.EXPENSE_BACKGROUND
                        if self._category_type == "expense"
                        else Color.INCOME_BACKGROUND
                    ),
                    on_edit=self._create_edit_handler(category) if is_custom else None
                )
                item.resize(
                    self._item_width,
                    self._item_height,
                    self._icon_size,
                    self._glyph_size
                )
                if not is_add_action:
                    self.category_items.append(item)
                category_row.controls.append(item)

            while len(category_row.controls) < self._columns:
                category_row.controls.append(ft.Container(expand=True))
            self.controls.append(category_row)
            self._rows.append(category_row)

    def _create_edit_handler(self, category: dict[str, Any]) -> Callable[[ft.ControlEvent | None], None]:
        def handle_edit(_event: ft.ControlEvent | None = None) -> None:
            self._on_edit(category)

        return handle_edit


class CategorySelectionContent(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str], on_cancel: Callable[..., None], on_type_change: Callable[[str], None]) -> None:
        self._page = page
        self.lang = lang

        self.category_type_selector = CategoryTypeSelector(
            lang=self.lang,
            on_change=on_type_change
        )

        self.category_grid = CategoryGrid(
            page=self._page,
            lang=self.lang
        )

        # CONTAINER COMPONENTS
        self.back_button = ft.TextButton(
            content=ft.Icon(ft.Icons.ARROW_BACK, color=Color.DEFAULT_BUTTON),
            on_click=on_cancel
        )
        super().__init__(
            width=UISettings.MAX_APP_WIDTH,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=10, vertical=20),
            content=ft.Column(
                spacing=15,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        controls=[self.back_button]
                    ),
                    self.category_type_selector,
                    self.category_grid
                ]
            )
        )

    def resize(self, page_width: int, content_width: int, columns: int) -> None:
        self.width = page_width
        self.category_type_selector.width = content_width
        self.category_grid.resize(content_width, columns, 75, 75, 52, 30)


class CategoryEditorDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], icon_names: list[str], on_save: Callable[[str, str, int | None], str | None], on_delete: Callable[[dict[str, Any]], None]) -> None:
        self._page = page
        self.lang = lang
        self.icon_names = icon_names
        self.on_save = on_save
        self.on_delete = on_delete
        self.category_id: int | None = None
        self.original_name = ""
        self.category: dict[str, Any] | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)
        self.save_button_label = Text.BUTTON(self.lang["generic.save"])
        self.cancel_button_label = Text.BUTTON(self.lang["generic.cancel"])
        self.delete_button_label = Text.BUTTON(self.lang["generic.delete"])
        self.title_text = Text.H3(self.lang["category_selection.add_category"], color=Color.PRIMARY_TEXT)

        # Dynamic icons
        self.icon_preview = ft.Icon(
            icon=getattr(ft.Icons, self.icon_names[0]),
            color=Color.PRIMARY,
            size=28
        )

        # CONTAINER COMPONENTS
        self.name_field = ft.TextField(
            label=self.lang["category_selection.category_name"],
            max_length=30,
            autofocus=True
        )

        self.icon_dropdown = ft.Dropdown(
            label=self.lang["category_selection.category_icon"],
            value=self.icon_names[0],
            options=[
                ft.dropdown.Option(
                    key=name,
                    text=name.replace("_", " ").title(),
                    leading_icon=getattr(ft.Icons, name)
                )
                for name in self.icon_names
            ],
            on_select=self._on_icon_changed,
            enable_filter=True,
            editable=True,
            menu_height=320,
            expand=True
        )

        self.save_button = ft.TextButton(
            content=self.save_button_label,
            on_click=self._save
        )

        self.cancel_button = ft.TextButton(
            content=self.cancel_button_label,
            on_click=lambda e: self.dismiss()
        )

        self.delete_button = ft.TextButton(
            content=self.delete_button_label,
            style=ft.ButtonStyle(color=Color.NEGATIVE_ACTION),
            on_click=self._request_delete,
            visible=False
        )

        self.content_container = ft.Column(
            tight=True,
            spacing=14,
            controls=[
                self.title_text,
                self.name_field,
                ft.Row(
                    spacing=12,
                    controls=[self.icon_dropdown, self.icon_preview]
                ),
                self.error_text
            ]
        )

        super().__init__(
            dialog_content=self.content_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.delete_button, self.cancel_button, self.save_button]
        )

        self._dialog_page = page

    def resize(self, width: int) -> None:
        self.content_container.width = width
        self.name_field.width = width

    def show_editor(self, category: dict[str, Any] | None = None) -> None:
        self.category = category
        self.category_id = category["id"] if category else None
        self.original_name = category["name"] if category else ""
        self.title_text.value = self.lang[
            "category_selection.edit_category"
            if category
            else "category_selection.add_category"
        ]
        self.name_field.value = category["name"] if category else ""
        icon_name = category["icon"] if category else self.icon_names[0]
        self.icon_dropdown.value = (
            icon_name if icon_name in self.icon_names else self.icon_names[0]
        )
        self.icon_preview.icon = getattr(ft.Icons, self.icon_dropdown.value or self.icon_names[0])
        self.error_text.value = ""
        self.delete_button.visible = category is not None
        self.show()
        self.update()

    def _request_delete(self) -> None:
        if self.category:
            category = self.category
            self.dismiss()
            self.on_delete(category)

    def _on_icon_changed(self) -> None:
        if self.icon_dropdown.value in self.icon_names:
            self.icon_preview.icon = getattr(ft.Icons, self.icon_dropdown.value or self.icon_names[0])
            self.icon_preview.update()

    def _save(self) -> None:
        error_key = self.on_save(
            self.name_field.value or "",
            self.icon_dropdown.value or "",
            self.category_id
        )
        if error_key is None:
            self.dismiss()
        else:
            self.error_text.value = self.lang[error_key]
            self.error_text.update()


class DeleteCategoryDialog(Dialog):
    def __init__(self, page: Page, lang: dict[str, str], on_delete: Callable[[int], bool]) -> None:
        self._page = page
        self.lang = lang
        self.on_delete = on_delete
        self.category: dict[str, Any] | None = None

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.dialog_title = Text.H3(self.lang["category_selection.delete_category"], color=Color.PRIMARY_TEXT)
        self.delete_button_label = Text.BUTTON(self.lang["generic.delete"])
        self.cancel_button_label = Text.BUTTON(self.lang["generic.cancel"])

        # Dynamic texts
        self.description = Text.P("", color=Color.SECONDARY_TEXT)
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)

        # CONTAINER COMPONENTS
        self.delete_button = ft.TextButton(
            content=self.delete_button_label,
            on_click=self._delete
        )
        self.cancel_button = ft.TextButton(
            content=self.cancel_button_label,
            on_click=lambda e: self.dismiss()
        )
        self.content_container = ft.Column(
            tight=True,
            spacing=12,
            controls=[
                self.dialog_title,
                self.description,
                self.error_text
            ]
        )
        super().__init__(
            dialog_content=self.content_container,
            color=Color.DIALOG_BACKGROUND,
            options=[self.cancel_button, self.delete_button]
        )
        self._dialog_page = page

    def resize(self, width: int) -> None:
        self.content_container.width = width
        self.description.width = width
        self.error_text.width = width

    def show_confirmation(self, category: dict[str, Any], transaction_count: int) -> None:
        self.category = category
        message_key = (
            "category_selection.delete_category_used"
            if transaction_count
            else "category_selection.delete_category_unused"
        )
        self.description.value = self.lang[message_key].format(
            name=category["name"],
            count=transaction_count
        )
        self.error_text.value = ""
        self.show()
        self.update()

    def _delete(self,) -> None:
        if self.category and self.on_delete(self.category["id"]):
            self.dismiss()
        else:
            self.error_text.value = self.lang["category_selection.category_delete_error"]
            self.error_text.update()
