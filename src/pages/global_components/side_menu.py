# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

import flet as ft

from src.utils import Color, Text


class SideMenu(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self.app_page = page
        self.lang = lang
        self.user_state = user_state

        self.menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=Color.MENU_ICON,
            icon_size=32,
            on_click=self.open_menu
        )

        def navigate_to(route):
            async def handler():
                await self.app_page.push_route(route)
            return handler

        menu_content = ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(src="/icon.png", height=40, border_radius=5),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color=Color.WHITE, on_click=self.close_menu),
                    ],
                ),
                padding=ft.Padding(50, 30, 30, 10)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.HOME),
                title=Text.H4(self.lang["generic.home"], color=Color.WHITE),
                on_click=navigate_to("/home")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BOOK),
                title=Text.H4(self.lang["generic.lesson"], color=Color.WHITE),
                on_click=navigate_to("/lessons")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SAVINGS),
                title=Text.H4(self.lang["generic.saving"], color=Color.WHITE),
                on_click=navigate_to("/saving")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.MONEY_ROUNDED),
                title=Text.H4(self.lang["generic.spending"], color=Color.WHITE),
                on_click=navigate_to("/spending")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SHOPPING_CART),
                title=Text.H4(self.lang["generic.purchase_scanner"], color=Color.WHITE),
                on_click=navigate_to("/purchase_scanner")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=Text.H4(self.lang["generic.change_user"], color=Color.WHITE),
                on_click=self.change_user
            )
        ])

        if os.getenv("ENABLE_EDITOR") == "1":
            menu_content.controls.append(
                ft.ListTile(
                    leading=Text.SMALL("dev", color=Color.WHITE),
                    title=Text.H4("Lesson Editor", color=Color.WHITE),
                    on_click=navigate_to("/lesson-editor"),
                ),
            )

        initial_width = self.get_menu_width()

        self.view = ft.Container(
            width=initial_width,
            left=-initial_width,
            top=0,
            bottom=0,
            bgcolor=Color.MENU_BACKGROUND,
            padding=0,
            animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=menu_content
        )

    def get_menu_width(self) -> int:
        current_width = self.app_page.window.width if hasattr(self.app_page, 'window') else self.app_page.width
        if not current_width:
            current_width = 650

        if current_width >= 650:
            return 200
        elif current_width >= 400:
            return int(current_width // 3)
        else:
            return 100

    def open_menu(self) -> None:
        self.view.width = self.get_menu_width()
        self.view.left = 0
        self.view.update()

    def close_menu(self) -> None:
        self.view.left = -self.get_menu_width()
        self.view.update()

    async def change_user(self) -> None:
        await self.app_page.push_route("/login")
        self.user_state["current_user"] = None

