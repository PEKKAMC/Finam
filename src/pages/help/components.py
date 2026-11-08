# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re

import flet as ft

from src.utils import Color, Page, Text, UISettings


class FaqItem(ft.Container):
    def __init__(self, question: str, answer: str):
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW,
            ),
            content=ft.Column(
                spacing=8,
                controls=[
                    Text.MEDIUM(
                        question,
                        color=Color.PRIMARY_TEXT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    Text.P(answer, color=Color.SECONDARY_TEXT),
                ],
            ),
        )

    def resize(self, width: int) -> None:
        self.width = width


class HelpForm(ft.Container):
    _EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$"
    )

    def __init__(self, page: Page, lang: dict):
        self._page = page
        self.lang = lang
        self.name_input = ft.TextField(
            label=self.lang["help.form_name"],
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12,
        )
        self.name_error_row = self._build_error_row()
        self.email_input = ft.TextField(
            label=self.lang["help.form_email"],
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12,
        )
        self.email_error_row = self._build_error_row()
        self.subject_input = ft.TextField(
            label=self.lang["help.form_subject"],
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12,
        )
        self.subject_error_row = self._build_error_row()
        self.message_input = ft.TextField(
            label=self.lang["help.form_message"],
            multiline=True,
            min_lines=4,
            max_lines=6,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12,
        )
        self.message_error_row = self._build_error_row()
        self.status_text = Text.SMALL(
            self.lang["help.form_sent"],
            color=Color.SECONDARY_TEXT,
            visible=False,
        )
        self.submit_button = ft.Button(
            content=self.lang["help.form_send"],
            icon=ft.Icons.SEND_OUTLINED,
            on_click=self._on_submit,
            bgcolor=Color.PRIMARY_ACTION,
            color=Color.WHITE,
        )
        self.form_column = ft.Column(
            spacing=14,
            controls=[
                Text.H3(
                    self.lang["help.form_title"],
                    color=Color.PRIMARY_TEXT,
                ),
                Text.P(
                    self.lang["help.form_description"],
                    color=Color.SECONDARY_TEXT,
                ),
                self.name_input,
                self.name_error_row,
                self.email_input,
                self.email_error_row,
                self.subject_input,
                self.subject_error_row,
                self.message_input,
                self.message_error_row,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[self.submit_button],
                ),
                self.status_text,
            ],
        )
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=28,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW,
            ),
            content=self.form_column,
        )

    def _build_error_row(self) -> ft.Row:
        return ft.Row(
            spacing=6,
            visible=False,
            controls=[
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    color=Color.NEGATIVE_ACTION,
                    size=16,
                ),
                Text.SMALL(
                    self.lang["help.form_required"],
                    color=Color.NEGATIVE_ACTION,
                ),
            ],
        )

    def _on_submit(self, e: ft.ControlEvent) -> None:
        email = (self.email_input.value or "").strip()
        is_name_empty = not (self.name_input.value or "").strip()
        is_email_empty = not email
        is_subject_empty = not (self.subject_input.value or "").strip()
        is_message_empty = not (self.message_input.value or "").strip()
        is_email_invalid = bool(email) and not self._EMAIL_PATTERN.fullmatch(email)

        self.name_error_row.visible = is_name_empty
        self.email_error_row.visible = is_email_empty or is_email_invalid
        self.subject_error_row.visible = is_subject_empty
        self.message_error_row.visible = is_message_empty
        self.email_error_row.controls[1].value = (
            self.lang["help.form_required"]
            if is_email_empty
            else self.lang["help.form_invalid_email"]
        )

        if any((is_name_empty, is_email_empty, is_email_invalid, is_subject_empty, is_message_empty)):
            self.status_text.visible = False
            self._page.update()
            return

        self.name_input.value = ""
        self.email_input.value = ""
        self.subject_input.value = ""
        self.message_input.value = ""
        self.status_text.visible = True
        self._page.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.form_column.width = content_width


class FaqSection(ft.Column):
    def __init__(self, lang: dict):
        super().__init__(
            spacing=12,
            controls=[
                Text.H3(lang["help.faq_title"], color=Color.PRIMARY_TEXT),
                FaqItem(
                    "Does the form below work?",
                    "Yes"
                )
            ],
        )

    def resize(self, width: int) -> None:
        self.width = width
        for control in self.controls:
            if isinstance(control, FaqItem):
                control.resize(width)
