# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.pages.help.logic import HelpFormLogic, HelpFormValidation
from src.utils import Color, Page, Text, UISettings

MINIMUM_MESSAGE_LINES = 4
MAXIMUM_MESSAGE_LINES = 6
FAQ_CARD_PADDING = 20


class FaqItem(ft.Container):
    def __init__(self, question: str, answer: str) -> None:
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.question_text = Text.MEDIUM(question, color=Color.PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        self.answer_text = Text.P(answer, color=Color.SECONDARY_TEXT)

        # CONTAINER COMPONENTS
        self.content_column = ft.Column(
            spacing=8,
            controls=[self.question_text, self.answer_text]
        )

        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=8,
            padding=FAQ_CARD_PADDING,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.content_column
        )

    def resize(self, width: int) -> None:
        self.width = width
        # Match the inner column to the card's usable area rather than its padded outer width.
        self.content_column.width = max(0, width - 2 * FAQ_CARD_PADDING)


class HelpForm(ft.Container):
    def __init__(self, page: Page, lang: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.logic = HelpFormLogic()

        # TEXT AND ICON COMPONENTS
        # Static texts
        self.email_input_label_text = Text.P(self.lang["help.form_email"], color=Color.SECONDARY_TEXT)
        self.subject_input_label_text = Text.P(self.lang["help.form_subject"], color=Color.SECONDARY_TEXT)
        self.message_input_label_text = Text.P(self.lang["help.form_message"], color=Color.SECONDARY_TEXT)
        self.form_title_text = Text.H3(self.lang["help.form_title"], color=Color.PRIMARY_TEXT)
        self.form_description_text = Text.P(self.lang["help.form_description"], color=Color.SECONDARY_TEXT)
        self.status_text = Text.SMALL(self.lang["help.form_sent"], color=Color.SECONDARY_TEXT, visible=False)
        self.submit_button_label = Text.BUTTON(self.lang["help.form_send"], color=Color.WHITE)

        # Static icons
        self.submit_button_icon = ft.Icon(ft.Icons.SEND_OUTLINED, color=Color.WHITE)

        # CONTAINER COMPONENTS
        self.email_input = ft.TextField(
            label=self.email_input_label_text,
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12
        )

        self.subject_input = ft.TextField(
            label=self.subject_input_label_text,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12
        )

        self.message_input = ft.TextField(
            label=self.message_input_label_text,
            multiline=True,
            min_lines=MINIMUM_MESSAGE_LINES,
            max_lines=MAXIMUM_MESSAGE_LINES,
            border_color=Color.INPUT_BORDER,
            focused_border_color=Color.PRIMARY_ACTION,
            border_radius=12
        )

        self.email_error_row, self.email_error_text = self._build_error_row()
        self.subject_error_row, self.subject_error_text = self._build_error_row()
        self.message_error_row, self.message_error_text = self._build_error_row()

        self.submit_button = ft.Button(
            content=ft.Row(
                controls=[
                    self.submit_button_icon,
                    self.submit_button_label
                ],
                tight=True,
                spacing=8
            ),
            on_click=self._on_submit,
            bgcolor=Color.PRIMARY_ACTION
        )

        self.input_fields: dict[str, ft.TextField] = {
            "email": self.email_input,
            "subject": self.subject_input,
            "message": self.message_input,
        }

        self.error_rows: dict[str, ft.Row] = {
            "email": self.email_error_row,
            "subject": self.subject_error_row,
            "message": self.message_error_row,
        }

        self.submit_button_row = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[self.submit_button]
        )

        self.form_column = ft.Column(
            spacing=14,
            controls=[
                self.form_title_text,
                self.form_description_text,
                self.email_input,
                self.email_error_row,
                self.subject_input,
                self.subject_error_row,
                self.message_input,
                self.message_error_row,
                self.submit_button_row,
                self.status_text
            ]
        )
        super().__init__(
            bgcolor=Color.CARD_BACKGROUND,
            border_radius=8,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=UISettings.SHADOW_SPREAD,
                blur_radius=UISettings.SHADOW_BLUR,
                color=Color.SHADOW
            ),
            content=self.form_column
        )

    def _build_error_row(self) -> tuple[ft.Row, ft.Text]:
        error_text = Text.SMALL(
            self.lang["help.form_required"],
            color=Color.NEGATIVE_ACTION
        )
        error_row = ft.Row(
            spacing=6,
            visible=False,
            controls=[
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    color=Color.NEGATIVE_ACTION,
                    size=16
                ),
                error_text
            ]
        )
        return error_row, error_text

    def _validate_fields(self) -> HelpFormValidation:
        return self.logic.validate_submission(
            email=self.email_input.value or "",
            subject=self.subject_input.value or "",
            message=self.message_input.value or ""
        )

    def _show_validation_errors(self, validation: HelpFormValidation) -> None:
        for field_name, error_row in self.error_rows.items():
            error_row.visible = validation["field_errors"][field_name]
        email_error = (
            self.lang[validation["email_error_key"]]
            if validation["field_errors"]["email"]
            else self.lang["help.form_required"]
        )
        self.email_error_text.value = email_error

    def _clear_fields(self) -> None:
        for text_field in self.input_fields.values():
            text_field.value = ""

    def _on_submit(self) -> None:
        validation = self._validate_fields()
        self._show_validation_errors(validation)
        if not validation["is_valid"]:
            self.status_text.visible = False
            self._page.update()
            return

        self._clear_fields()
        self.status_text.visible = True
        self._page.update()

    def resize(self, width: int, content_width: int) -> None:
        self.width = width
        self.form_column.width = content_width


class FaqSection(ft.Column):
    def __init__(self, lang: dict[str, str]) -> None:
        # TEXT AND ICON COMPONENTS
        # Static texts
        self.section_title = Text.H3(lang["help.faq_title"], color=Color.PRIMARY_TEXT)
        self.faq_items: list[FaqItem] = [FaqItem("Does the form below work?", "Yes")]

        # CONTAINER COMPONENTS
        super().__init__(
            spacing=12,
            controls=[self.section_title, *self.faq_items]
        )

    def resize(self, width: int) -> None:
        self.width = width
        for faq_item in self.faq_items:
            faq_item.resize(width)
