# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable
from typing import Any

import flet as ft

from src.utils import Color, Dialog, Page, Text, UISettings


class SettingsHeader(ft.Container):
    def __init__(self, lang: dict[str, str]) -> None:
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H2(self.lang["settings.title"], color=Color.LIGHT_ACCENT)
        self.desc_text = Text.P(self.lang["settings.desc"], color=Color.LIGHT_ACCENT)

        # CONTAINER COMPONENTS
        self.text_column = ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.title_text],
                ),
                self.desc_text,
            ],
        )

        self.main_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[self.text_column],
        )

        self.main_container = ft.Container(content=self.main_row)

        super().__init__(
            bgcolor=Color.PRIMARY,
            border_radius=24,
            padding=16,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW,
            ),
            content=self.main_container,
        )

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        if isinstance(self.main_container.content, ft.Row):
            self.main_container.content.width = content_width


class SettingDropdown(ft.Container):
    def __init__(self, options: list[str], active_index: int = 0, menu_height: int | None = None, searchable: bool = False) -> None:
        # CONTAINER COMPONENTS
        self.dropdown_control = ft.Dropdown(
            options=[ft.dropdown.Option(opt) for opt in options],
            value=options[active_index],
            menu_height=menu_height,
            enable_filter=searchable,
            editable=searchable,
            border=ft.InputBorder.NONE,
            bgcolor=Color.CARD_BACKGROUND,
            text_style=ft.TextStyle(
                size=12, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.W_600
            ),
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=8),
        )

        self.main_container = ft.Container(content=self.dropdown_control)

        super().__init__(
            bgcolor=Color.USER_TILE_BACKGROUND,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=8, vertical=0),
            content=self.main_container,
        )

    def resize(self, width: int) -> None:
        self.width = width
        self.main_container.width = width
        self.dropdown_control.width = width


class SettingRow(ft.Container):
    def __init__(self, icon: ft.IconData, title: str, subtitle: str, control: ft.Control, on_click: Callable[..., None] | None = None) -> None:
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.title_text = Text.H5(title, color=Color.PRIMARY_TEXT)
        self.subtitle_text = Text.SMALL(subtitle, color=Color.SECONDARY_TEXT)

        # Static icons
        self.row_icon = ft.Icon(icon, color=Color.PRIMARY_ACTION, size=24)


        # CONTAINER COMPONENTS
        self.action_control = control

        self.text_column = ft.Column(
            spacing=2,
            expand=True,
            controls=[
                self.title_text,
                self.subtitle_text
            ]
        )

        self.left_group = ft.Row(
            spacing=15,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.row_icon,
                self.text_column
            ]
        )

        self.left_container = ft.Container(
            content=self.left_group,
            expand=1
        )

        self.right_container = ft.Container(
            content=self.action_control,
            alignment=ft.Alignment.CENTER_RIGHT,
            expand=1
        )

        self.main_row = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.left_container,
                self.right_container
            ]
        )

        self.main_container = ft.Container(content=self.main_row)

        super().__init__(
            padding=ft.Padding.symmetric(vertical=6),
            content=self.main_container,
            on_click=on_click,
            ink=on_click is not None
        )

    def resize(self, width: int, text_width: int, action_width: int) -> None:
        self.width = width
        self.main_container.width = width
        self.main_row.width = width
        self.left_container.width = text_width
        self.right_container.width = action_width
        if isinstance(self.action_control, SettingDropdown):
            self.action_control.resize(action_width)


class SettingCard(ft.Container):
    def __init__(self, controls: list[ft.Control]) -> None:
        # Child controls supply their own text and icon components.
        self.card_controls = controls

        # CONTAINER COMPONENTS
        self.main_container = ft.Container(
            content=ft.Column(spacing=6, controls=self.card_controls)
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            border=ft.Border.all(1, Color.INPUT_BORDER),
            padding=16,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW,
            ),
            content=self.main_container,
        )

    def resize(self, width: int, content_width: int, text_width: int, action_width: int) -> None:
        self.width = width
        self.main_container.width = content_width
        for control in self.card_controls:
            if isinstance(control, SettingRow):
                control.resize(content_width, text_width, action_width)


class SettingsPageContent(ft.Container):
    def __init__(self, header: SettingsHeader, header_divider: ft.Divider, cards: list[ft.Control], done_button: ft.Container) -> None:
        self.header = header
        self.header_divider = header_divider
        self.cards = cards
        self.done_button = done_button

        # CONTAINER COMPONENTS
        self.content_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=20,
            content=ft.Column(
                spacing=18,
                expand=True,
                controls=[
                    self.header,
                    self.header_divider,
                    *self.cards,
                    ft.Container(height=20 * 2 + 56)
                ]
            )
        )

        self.done_button_wrapper = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=self.done_button
        )

        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO, controls=[self.content_container]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=0)
        )

        self.bottom_button_container = ft.Container(
            left=0,
            right=0,
            bottom=0,
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.PAGE_BACKGROUND,
            content=self.done_button_wrapper,
        )

        super().__init__(
            content=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.bottom_button_container
                    ]
                )
            )
        )

    def resize(self,page_width: int, page_height: int, content_width: int, card_content_width: int, text_width: int, action_width: int) -> None:
        self.main_container.width = page_width
        self.main_container.height = page_height
        self.content_container.width = page_width
        self.done_button_wrapper.width = page_width
        self.done_button.width = content_width
        self.header.resize(
            width=content_width,
            content_width=card_content_width,
        )
        for card in self.cards:
            if isinstance(card, SettingCard):
                card.resize(
                    width=content_width,
                    content_width=card_content_width,
                    text_width=text_width,
                    action_width=action_width,
                )


class SettingsDialogs:
    def __init__(self, page: Page, lang: dict[str, str], on_clear_cache: Callable[..., Any]) -> None:
        self._page = page
        self.lang = lang

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.clear_cache_title = Text.H4(self.lang["settings.clear_cache_confirm_title"], color=Color.PRIMARY_TEXT)
        self.clear_cache_description = Text.P(self.lang["settings.clear_cache_confirm_desc"], color=Color.SECONDARY_TEXT)
        self.separator_title = Text.H4(self.lang["settings.separator_conflict_title"], color=Color.PRIMARY_TEXT)
        self.separator_description = Text.P(self.lang["settings.separator_conflict_desc"], color=Color.SECONDARY_TEXT)
        self.cancel_button_text = Text.BUTTON(self.lang["generic.cancel"])
        self.clear_cache_button_text = Text.BUTTON(self.lang["settings.clear_cache"])
        self.close_button_text = Text.BUTTON(self.lang["generic.close"])
        self.pin_cancel_text = Text.BUTTON(self.lang["generic.cancel"])
        self.pin_save_text = Text.BUTTON(self.lang["generic.save"])
        self.pin_title_text = Text.H4(self.lang["settings.pin_title"], color=Color.PRIMARY_TEXT)

        # Dynamic texts
        self.result_text = Text.H4("", color=Color.PRIMARY_TEXT)
        self.pin_error_text = Text.SMALL("", color=Color.NEGATIVE_ACTION)

        # CONTAINER COMPONENTS
        self.clear_cache_dialog = Dialog(
            dialog_content=ft.Column(
                tight=True,
                controls=[
                    self.clear_cache_title,
                    self.clear_cache_description
                ]
            ),
            color=Color.DIALOG_BACKGROUND,
            options=[
                ft.TextButton(
                    content=self.cancel_button_text,
                    on_click=lambda _event: self.clear_cache_dialog.dismiss()
                ),
                ft.TextButton(
                    content=self.clear_cache_button_text,
                    on_click=on_clear_cache
                )
            ]
        )

        self.clear_cache_result_dialog = Dialog(
            dialog_content=ft.Column(tight=True, controls=[self.result_text]),
            color=Color.DIALOG_BACKGROUND,
            options=[
                ft.TextButton(
                    content=self.close_button_text,
                    on_click=lambda _event: self.clear_cache_result_dialog.dismiss()
                )
            ]
        )

        self.separator_warning_dialog = Dialog(
            dialog_content=ft.Column(
                tight=True,
                controls=[self.separator_title, self.separator_description],
            ),
            color=Color.DIALOG_BACKGROUND,
            options=[
                ft.TextButton(
                    content=self.close_button_text,
                    on_click=lambda _event: self.separator_warning_dialog.dismiss(),
                )
            ]
        )

        self.clear_cache_dialog._dialog_page = self._page
        self.clear_cache_result_dialog._dialog_page = self._page
        self.separator_warning_dialog._dialog_page = self._page

    def show_pin_setup(self, integer_regex: str, on_save_pin: Callable[[str, str], int], on_cancel: Callable[..., Any], on_saved: Callable[..., Any]) -> None:
        pin_field = ft.TextField(
            label=self.lang["settings.pin"],
            input_filter=ft.InputFilter(allow=True, regex_string=integer_regex),
            password=True,
            max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=Color.CARD_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            color=Color.PRIMARY_TEXT,
            label_style=ft.TextStyle(color=Color.SECONDARY_TEXT),
        )

        confirm_pin_field = ft.TextField(
            label=self.lang["settings.confirm_pin"],
            input_filter=ft.InputFilter(allow=True, regex_string=integer_regex),
            password=True,
            max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=Color.CARD_BACKGROUND,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            color=Color.PRIMARY_TEXT,
            label_style=ft.TextStyle(color=Color.SECONDARY_TEXT),
        )

        self.pin_error_text.value = ""

        def close_dialog(_event: ft.ControlEvent | None = None) -> None:
            pin_dialog.dismiss()
            on_cancel()

        def save_pin(_event: ft.ControlEvent | None = None) -> None:
            status = on_save_pin(
                pin_field.value or "",
                confirm_pin_field.value or "",
            )
            error_messages = {
                1: self.lang["settings.pin_invalid"],
                2: self.lang["settings.pin_mismatch"],
            }
            if status != 0:
                self.pin_error_text.value = error_messages.get(
                    status, self.lang["settings.pin_invalid"]
                )
                self.pin_error_text.update()
                return

            pin_dialog.dismiss()
            on_saved()

        pin_dialog = Dialog(
            dialog_content=ft.Column(
                tight=True,
                controls=[
                    self.pin_title_text,
                    pin_field,
                    confirm_pin_field,
                    self.pin_error_text,
                ],
            ),
            color=Color.DIALOG_BACKGROUND,
            options=[
                ft.TextButton(content=self.pin_cancel_text, on_click=close_dialog),
                ft.TextButton(content=self.pin_save_text, on_click=save_pin),
            ],
        )
        pin_dialog._dialog_page = self._page
        pin_dialog.show()
