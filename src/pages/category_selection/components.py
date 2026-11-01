# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings


class CategoryItem(ft.Container):
    def __init__(
        self,
        page: Page,
        lang: dict,
        name: str,
        icon: ft.IconData,
        on_click: Callable,
        is_selected: bool = False,
        on_edit: Callable | None = None,
        icon_color: str = Color.PRIMARY,
        selected_background_color: str = Color.NAVIGATION_ACTIVE_BACKGROUND,
    ):
        self._page = page
        self.lang = lang
        self.category_name = name
        self.icon = icon
        self._on_click = on_click
        self.is_selected = is_selected
        self.selected_background_color = selected_background_color
        self.icon_circle = ft.Container(
            width=52,
            height=52,
            border_radius=UISettings.CARD_BORDER_RADIUS,
            bgcolor=(
                self.selected_background_color if self.is_selected else None
            ),
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(
                icon=self.icon,
                color=icon_color,
                size=30,
            )
        )

        self.icon_label = Text.LABEL(
            value=self.category_name,
            color=Color.NAVIGATION_ACTIVE_TEXT if self.is_selected else Color.DEFAULT_TEXT,
            text_align=ft.TextAlign.CENTER,
        )

        self.main_container = ft.Container(
            width=75,
            height=76,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    self.icon_circle,
                    self.icon_label,
                ],
            ),
            border_radius=UISettings.CARD_BORDER_RADIUS,
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
                on_secondary_tap=on_edit,
            ),
            expand=True,
            alignment=ft.Alignment.CENTER
        )

    def update_selection(self, selected: bool):
        self.is_selected = selected
        self.main_container.bgcolor = (
            self.selected_background_color
            if self.is_selected
            else Color.TRANSPARENT
        )
        self.icon_circle.bgcolor = (
            self.selected_background_color if self.is_selected else None
        )
        self.icon_label.color = (
            Color.NAVIGATION_ACTIVE_TEXT if self.is_selected else Color.DEFAULT_TEXT
        )


class CategoryEditorDialog(Dialog):
    def __init__(self, page: Page, lang: dict, icon_names: list[str], on_save: Callable[[str, str, int | None], str | None], on_delete: Callable[[dict], None]):
        self._page = page
        self.lang = lang
        self.icon_names = icon_names
        self.on_save = on_save
        self.on_delete = on_delete
        self.category_id: int | None = None
        self.original_name = ""
        self.category: dict | None = None
        self.name_field = ft.TextField(
            label=self.lang["category_selection.category_name"],
            max_length=30,
            autofocus=True,
        )
        self.icon_dropdown = ft.Dropdown(
            label=self.lang["category_selection.category_icon"],
            value=self.icon_names[0],
            options=[
                ft.dropdown.Option(
                    key=name,
                    text=name.replace("_", " ").title(),
                    leading_icon=getattr(ft.Icons, name),
                )
                for name in self.icon_names
            ],
            on_select=self._on_icon_changed,
            menu_height=320,
            expand=True,
        )
        self.icon_preview = ft.Icon(
            getattr(ft.Icons, self.icon_names[0]),
            color=Color.PRIMARY,
            size=28,
        )
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)
        self.save_button = ft.TextButton(
            content=self.lang["generic.save"],
            on_click=self._save,
        )
        self.cancel_button = ft.TextButton(
            content=self.lang["generic.cancel"],
            on_click=lambda e: self.dismiss(),
        )
        self.delete_button = ft.TextButton(
            content=self.lang["generic.delete"],
            style=ft.ButtonStyle(color=Color.NEGATIVE_ACTION),
            on_click=self._request_delete,
            visible=False,
        )
        self.title_text = Text.H3(
            self.lang["category_selection.add_category"],
            color=Color.PRIMARY_TEXT,
        )
        content = ft.Column(
            tight=True,
            spacing=14,
            controls=[
                self.title_text,
                self.name_field,
                ft.Row(
                    spacing=12,
                    controls=[self.icon_dropdown, self.icon_preview],
                ),
                self.error_text,
            ],
        )
        super().__init__(
            dialog_content=content,
            color=Color.DIALOG_BACKGROUND,
            options=[self.delete_button, self.cancel_button, self.save_button],
        )
        self._dialog_page = page

    def show_editor(self, category: dict | None = None) -> None:
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
        self.icon_preview.name = getattr(ft.Icons, self.icon_dropdown.value)
        self.error_text.value = ""
        self.delete_button.visible = category is not None
        self.show()
        self.update()

    def _request_delete(self, e=None) -> None:
        if self.category:
            category = self.category
            self.dismiss()
            self.on_delete(category)

    def _on_icon_changed(self, e: ft.ControlEvent) -> None:
        if self.icon_dropdown.value in self.icon_names:
            self.icon_preview.name = getattr(ft.Icons, self.icon_dropdown.value)
            self.icon_preview.update()

    def _save(self, e=None) -> None:
        error_key = self.on_save(
            self.name_field.value or "",
            self.icon_dropdown.value or "",
            self.category_id,
        )
        if error_key is None:
            self.dismiss()
        else:
            self.error_text.value = self.lang[error_key]
            self.error_text.update()


class DeleteCategoryDialog(Dialog):
    def __init__(self, page: Page, lang: dict, on_delete: Callable[[int], bool]):
        self._page = page
        self.lang = lang
        self.on_delete = on_delete
        self.category: dict | None = None
        self.description = Text.P("", color=Color.SECONDARY_TEXT)
        self.error_text = Text.SMALL("", color=Color.ERROR_TEXT)
        self.delete_button = ft.TextButton(
            content=self.lang["generic.delete"],
            on_click=self._delete,
        )
        self.cancel_button = ft.TextButton(
            content=self.lang["generic.cancel"],
            on_click=lambda e: self.dismiss(),
        )
        content = ft.Column(
            tight=True,
            spacing=12,
            controls=[
                Text.H3(
                    self.lang["category_selection.delete_category"],
                    color=Color.PRIMARY_TEXT,
                ),
                self.description,
                self.error_text,
            ],
        )
        super().__init__(
            dialog_content=content,
            color=Color.DIALOG_BACKGROUND,
            options=[self.cancel_button, self.delete_button],
        )
        self._dialog_page = page

    def show_confirmation(self, category: dict, transaction_count: int) -> None:
        self.category = category
        message_key = (
            "category_selection.delete_category_used"
            if transaction_count
            else "category_selection.delete_category_unused"
        )
        self.description.value = self.lang[message_key].format(
            name=category["name"],
            count=transaction_count,
        )
        self.error_text.value = ""
        self.show()
        self.update()

    def _delete(self, e=None) -> None:
        if self.category and self.on_delete(self.category["id"]):
            self.dismiss()
        else:
            self.error_text.value = self.lang[
                "category_selection.category_delete_error"
            ]
            self.error_text.update()
