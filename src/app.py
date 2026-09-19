# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import flet as ft

from src.database import db
from src.utils import Page, UISettings, get_language
from src.logger import Logger
from src.pages.fallback import get_fallback_view
from src.pages.home import get_home_view
from src.pages.lesson import get_lesson_view
from src.pages.lesson_player import get_lesson_player_view
from src.pages.saving import get_savings_view
from src.pages.settings import get_settings_view
from src.pages.spending import get_spending_view
from src.pages.purchase_scanner import get_scanner_view
from src.pages.starter.view import get_starter_view
from src.pages.user_management import get_user_management_view

ENABLE_EDITOR: bool = os.getenv("ENABLE_EDITOR") == "1"

# DEVELOPER EDITOR PAGE, ONLY INITIALIZE WHEN ENABLE_EDITOR IS SET TO TRUE
if ENABLE_EDITOR:
    from src.pages.lesson_editor import get_lesson_editor_view


async def redirect_to_fallback(page: Page, lang: dict, fallback_reason: str) -> None:
    Logger.info("Redirecting to fallback page")
    await page.push_route("/fallback")
    page.views.append(get_fallback_view(page, lang, fallback_reason))


async def main(page: Page):
    db.initialize_database()

    lang: dict = get_language("vi")
    user_info: dict[str, str] = {
        "username": ""
    }

    page.title = "Finam"
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.FADE_UPWARDS,
            ios=ft.PageTransitionTheme.CUPERTINO,
            linux=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        )
    )
    page.padding = 0
    page.window.resizable = True
    page.window.width = UISettings.MAX_APP_WIDTH
    page.window.height = UISettings.MAX_APP_HEIGHT

    page.update()

    async def route_change(e: ft.RouteChangeEvent) -> ft.RouteChangeEvent:
        try:
            page.views.clear()
            troute = ft.TemplateRoute(page.route)

            if troute.match("/user_management"):
                Logger.info("Redirecting to user management page")
                page.views.append(get_user_management_view(page, lang, user_info))

            elif troute.match("/home"):
                Logger.info("Redirecting to home page")
                page.views.append(get_home_view(page, lang, user_info))

            elif troute.match("/lessons"):
                Logger.info("Redirecting to lessons page")
                page.views.append(get_lesson_view(page, lang, user_info))

            elif troute.match("/saving"):
                Logger.info("Redirecting to saving page")
                page.views.append(get_savings_view(page, lang, user_info))

            elif troute.match("/lesson-player/:lesson_id"):
                lesson_id = troute.lesson_id
                Logger.info(f"Redirecting to {lesson_id} page")
                page.views.append(get_lesson_player_view(page, lang, user_info, lesson_id))

            elif troute.match("/lesson-player"):
                Logger.info("Redirecting to lesson loader page")
                page.views.append(get_lesson_player_view(page, lang, user_info))

            elif troute.match("/spending"):
                Logger.info("Redirecting to spending page")
                page.views.append(get_spending_view(page, lang, user_info))

            elif troute.match("/purchase_scanner"):
                Logger.info("Redirecting to purchase scanner page")
                page.views.append(get_scanner_view(page, lang, user_info))

            elif troute.match("/settings"):
                Logger.info("Redirecting to settings page")
                page.views.append(get_settings_view(page, lang, user_info))

            elif ENABLE_EDITOR and troute.match("/lesson-editor"):
                Logger.info("Redirecting to lesson editor page")
                page.views.append(get_lesson_editor_view(page, lang, user_info))

            elif troute.match("/starter"):
                Logger.info("Redirecting to starter page")
                page.views.append(get_starter_view(page, lang, user_info))

            else:
                Logger.info("Page not found")
                await redirect_to_fallback(page, lang, "page_not_found")

            page.update()
            return e

        except Exception as ex:
            Logger.critical(f"Failed to change route: {ex}")
            await on_error(e)
            return e

    async def on_error(e: ft.ControlEvent) -> ft.ControlEvent:
        if e == ft.Event(name='error', data='Bad state: No element', control=page):
            print("there is like 5-15% chance you'll see this message on launch, depends on")
            print("your computer. it's because of a bug that makes 2 processes racing for control,")
            print("and if that one specifically wins the race, it causes this to happen.")
            print("currently the bug doesn't affect the application much, so i'll be fixing")
            print("it later. consider yourself lucky.\n")
            Logger.error("PEKKAMC")
        else:
            Logger.critical(f"Unexpected error occurred: {e.control}")
            Logger.info("Attempting to restart application...")

            os.environ["RESTART_FINAM"] = "1"

            await page.window.close()

        return e

    page.on_error = on_error
    page.on_route_change = route_change

    await page.push_route("/starter")
