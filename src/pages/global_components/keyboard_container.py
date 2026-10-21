# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import ast
from datetime import datetime
import math
from typing import Callable, Optional

import flet as ft

from src.logger import Logger
from src.utils import Color, Page


class KeyboardContainer(ft.Container):
    def __init__(self, page: Page, lang: dict, on_save: Callable[[dict], None], on_date_changed_callback: Optional[Callable[[str], None]] = None):
        self._page = page
        self.lang = lang
        self.on_save = on_save
        self.on_date_changed_callback = on_date_changed_callback

        self.amount_value = "0"
        self.selected_date = datetime.now().strftime("%Y-%m-%d")

        self.amount_display = ft.Text(
            value="0", size=32, color=Color.DEFAULT_TEXT, weight=ft.FontWeight.BOLD
        )

        self.note_input = ft.TextField(
            hint_text=self.lang["category_selection.note_hint"],
            label=self.lang["generic.note"],
            label_style=ft.TextStyle(color=Color.SECONDARY_TEXT, size=13),
            color=Color.DEFAULT_TEXT,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.TRANSPARENT,
            bgcolor=Color.WHITE,
            prefix_icon=ft.Icons.NOTES,
            text_size=14,
            content_padding=10,
        )

        self.date_display = ft.Text(
            value=self.selected_date,
            color=Color.DEFAULT_TEXT,
            size=13,
            weight=ft.FontWeight.BOLD,
        )

        self.date_picker = ft.DatePicker(
            value=datetime.strptime(self.selected_date, "%Y-%m-%d").date(),
            on_change=self._on_date_changed,
        )
        if self._page.overlay is not None and self.date_picker not in self._page.overlay:
            self._page.overlay.append(self.date_picker)

        self.today_button = ft.Container(
            expand=2,
            height=45,
            bgcolor=Color.PAGE_BACKGROUND,
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=self._handle_date_toggle,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=Color.DEFAULT_TEXT, size=16),
                    self.date_display,
                ],
            ),
        )

        self.main_container = ft.Container(
            padding=10,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CREDIT_CARD,
                                icon_color=Color.PRIMARY,
                                icon_size=20,
                            ),
                            self.amount_display,
                        ],
                    ),
                    ft.Container(
                        bgcolor=Color.PAGE_BACKGROUND,
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        content=self.note_input,
                    ),
                    self._build_keypad(),
                ]
            ),
        )

        super().__init__(
            bgcolor=Color.WHITE,
            bottom=0,
            border_radius=ft.BorderRadius.only(top_left=16, top_right=16),
            visible=False,
            alignment=ft.Alignment.BOTTOM_CENTER,
            content=self.main_container
        )

    def _build_keypad(self) -> ft.Column:
        btn_bg = Color.DEFAULT_CONTAINER_BACKGROUND
        txt_color = Color.PRIMARY_TEXT

        def k_btn(text: str, on_click, icon=None, expand=1):
            content = (
                ft.Icon(icon, color=txt_color, size=20)
                if icon
                else ft.Text(text, size=18, color=txt_color, weight=ft.FontWeight.BOLD)
            )
            return ft.Container(
                content=content,
                bgcolor=btn_bg,
                alignment=ft.Alignment.CENTER,
                border_radius=8,
                expand=expand,
                height=45,
                ink=True,
                on_click=on_click,
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
                        self.today_button,
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn("4", lambda e: self._on_key_press("4")),
                        k_btn("5", lambda e: self._on_key_press("5")),
                        k_btn("6", lambda e: self._on_key_press("6")),
                        k_btn("+", lambda e: self._on_key_press("+")),
                        k_btn("-", lambda e: self._on_key_press("-")),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn("1", lambda e: self._on_key_press("1")),
                        k_btn("2", lambda e: self._on_key_press("2")),
                        k_btn("3", lambda e: self._on_key_press("3")),
                        k_btn("×", lambda e: self._on_key_press("*")),
                        k_btn("÷", lambda e: self._on_key_press("/")),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        k_btn(".", lambda e: self._on_key_press(".")),
                        k_btn("0", lambda e: self._on_key_press("0")),
                        k_btn("", lambda e: self._on_backspace(), icon=ft.Icons.BACKSPACE),
                        k_btn("=", lambda e: self._on_equal_pressed()),
                        k_btn("", lambda e: self._handle_save_click(), icon=ft.Icons.CHECK),
                    ],
                ),
            ],
        )

    @staticmethod
    def _eval_expression(expression: str):
        try:
            if not expression:
                return None
            cleaned = expression.replace("×", "*").replace("÷", "/")
            parsed = ast.parse(cleaned, mode="eval")
            for node in ast.walk(parsed):
                if isinstance(node, ast.BinOp):
                    if not isinstance(
                        node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
                    ):
                        raise ValueError
                elif isinstance(node, ast.UnaryOp):
                    if not isinstance(node.op, (ast.UAdd, ast.USub)):
                        raise ValueError
                elif isinstance(node, ast.Constant):
                    if not isinstance(node.value, (int, float)):
                        raise ValueError
                elif isinstance(
                    node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.UAdd, ast.USub)
                ):
                    pass
                elif isinstance(node, ast.Expression):
                    pass
                else:
                    raise ValueError

            value = eval(
                compile(parsed, "<expr>", "eval"), {"__builtins__": {}}, {"math": math}
            )
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)
        except Exception as ex:
            Logger.error(f"Failed to evaluate expression '{expression}': {ex}")
            return None

    def _on_key_press(self, val: str):
        operators = "+-*/."
        if val in operators and self.amount_value and self.amount_value[-1] in operators:
            self.amount_value = self.amount_value[:-1] + val
        elif self.amount_value == "0" and val not in "+-*/.":
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

    def _on_equal_pressed(self):
        result = self._eval_expression(self.amount_value)
        if result is None:
            return
        self.amount_value = result
        self.amount_display.value = self.amount_value
        if self._page is not None:
            self.amount_display.update()

    def _handle_save_click(self):
        if any(ch in self.amount_value for ch in "+-*/"):
            evaluated = self._eval_expression(self.amount_value)
            if evaluated is not None:
                self.amount_value = evaluated
                self.amount_display.value = self.amount_value
                self.update()

        values = {
            "amount": self.amount_value,
            "note": self.note_input.value or "",
            "date": self.selected_date,
        }
        self.on_save(values)

    def _handle_date_toggle(self, e=None):
        if self._page is not None:
            if self.date_picker not in self._page.overlay:
                self._page.overlay.append(self.date_picker)
            self.date_picker.open = True

    def _on_date_changed(self, e):
        if e.control.value:
            self.selected_date = e.control.value.strftime("%Y-%m-%d")
            self.date_display.value = self.selected_date
            self.update()
            if self.on_date_changed_callback:
                self.on_date_changed_callback(self.selected_date)

    def reset_inputs(self):
        self.amount_value = "0"
        self.note_input.value = "0"
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.date_display.value = self.selected_date
        self.date_picker.value = datetime.strptime(self.selected_date, "%Y-%m-%d").date()

    def resize(self, width: int):
        self.main_container.width = width