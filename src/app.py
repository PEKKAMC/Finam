# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.database import db
from src.utils import UISettings, get_language, Color
from src.logger import Logger
from src.pages.fallback import get_fallback_view
from src.pages.home import get_home_view
from src.pages.login import get_login_view
from src.pages.lesson import get_lesson_view
from src.pages.lesson_editor import get_lesson_editor_view
from src.pages.lesson_player import get_lesson_player_view
from src.pages.saving import get_savings_view
from src.pages.spending import get_spending_view
from src.pages.purchase_scanner import get_scanner_view

async def redirect_to_fallback(page: ft.Page, lang: dict, fallback_reason: str) -> None:
    Logger.info("Redirecting to fallback page")
    await page.push_route("/fallback")
    page.views.append(get_fallback_view(page, lang, fallback_reason))

async def main(page: ft.Page) -> None:
    db.initialize_database()

    lang: dict = get_language("vi")
    user_info: dict[str, str] = {
        "username": ""
    }

    page.bgcolor = Color.WHITE
    page.title = "Finam"
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.CUPERTINO,
            ios=ft.PageTransitionTheme.CUPERTINO,
            linux=ft.PageTransitionTheme.CUPERTINO,
            macos=ft.PageTransitionTheme.CUPERTINO,
            windows=ft.PageTransitionTheme.CUPERTINO,
        )
    )
    page.padding = 0
    page.window.resizable = True
    page.window.width = UISettings.MAX_APP_WIDTH
    page.window.height = UISettings.MAX_APP_HEIGHT

    page.update()


    async def route_change(e: ft.RouteChangeEvent) -> ft.RouteChangeEvent:
        page.views.clear()
        username = user_info["username"]
        troute = ft.TemplateRoute(page.route)

        if troute.match("/login"):
            if username: Logger.info(f"User {username} logged out")
            page.views.append(get_login_view(page, lang, user_info))

        elif troute.match("/home"):
            Logger.info(f"{username}: Redirecting to home page")
            page.views.append(get_home_view(page, lang, user_info))

        elif troute.match("/lessons"):
            Logger.info(f"{username}: Redirecting to lessons page")
            page.views.append(get_lesson_view(page, lang, user_info))

        elif troute.match("/saving"):
            Logger.info(f"{username}: Redirecting to saving page")
            page.views.append(get_savings_view(page, lang, user_info))

        elif troute.match("/lesson-editor"):
            Logger.info(f"{username}: Redirecting to lesson editor page")
            page.views.append(get_lesson_editor_view(page, lang, user_info))

        elif troute.match("/lesson-player/:lesson_id"):
            lesson_id = troute.lesson_id
            Logger.info(f"{username}: Redirecting to {lesson_id} page")
            page.views.append(get_lesson_player_view(page, lang, user_info, lesson_id))

        elif troute.match("/lesson-player"):
            Logger.info(f"{username}: Redirecting to lesson loader page")
            page.views.append(get_lesson_player_view(page, lang, user_info))

        elif troute.match("/spending"):
            Logger.info(f"{username}: Redirecting to spending page")
            page.views.append(get_spending_view(page, lang, user_info))

        elif troute.match("/purchase_scanner"):
            Logger.info(f"{username}: Redirecting to purchase scanner page")
            page.views.append(get_scanner_view(page, lang, user_info))

        else:
            Logger.info(f"{username}: Page not found")
            await redirect_to_fallback(page, lang, "page_not_found")
            return e

        page.update()
        return e

    async def view_pop(e: ft.ViewPopEvent) -> ft.ViewPopEvent:
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)
        return e

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await page.push_route("/login")