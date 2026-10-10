# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import flet as ft

from src.database import db
from src.utils import Page, UISettings, get_language
from src.logger import Logger
from src.pages.category_selection import get_category_selection_view
from src.pages.fallback import get_fallback_view
from src.pages.home import get_home_view
from src.pages.lessons import get_lessons_view
from src.pages.lesson_player import get_lesson_player_view
from src.pages.savings import get_savings_view
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
    Logger.info("Redirecting to fallback page...")
    await page.push_route("/fallback")
    page.views.append(get_fallback_view(page, lang, fallback_reason))


async def main(page: Page):
    db.initialize_database()

    user_info: dict[str, str] = {
        "username": ""
    }

    page.title = "Finam"
    page.theme_mode = ft.ThemeMode.LIGHT
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

    views_cache: dict[str, tuple[ft.View, str]] = {}

    def get_view_cache_key(route: str, language_code: str, currency: str) -> str:
        return f"{route}|{language_code}|{currency}"

    def build_view_for_route(route: str, lang: dict, user_info: dict) -> ft.View | None:
        troute = ft.TemplateRoute(route)

        if troute.match("/user_management"):
            return get_user_management_view(page, lang, user_info)

        if troute.match("/home"):
            return get_home_view(page, lang, user_info)

        if troute.match("/lessons"):
            return get_lessons_view(page, lang, user_info)

        if troute.match("/saving"):
            return get_savings_view(page, lang, user_info)

        if troute.match("/lesson-player/:lesson_id"):
            lesson_id = getattr(troute, "lesson_id", None)
            return get_lesson_player_view(page, lang, user_info, lesson_id)

        if troute.match("/lesson-player"):
            return get_lesson_player_view(page, lang, user_info)

        if troute.match("/spending"):
            return get_spending_view(page, lang, user_info)

        if troute.match("/purchase_scanner"):
            return get_scanner_view(page, lang, user_info)

        if troute.match("/settings"):
            return get_settings_view(page, lang, user_info)

        if troute.match("/category_selection"):
            return get_category_selection_view(page, lang, user_info)

        if ENABLE_EDITOR and troute.match("/lesson-editor"):
            return get_lesson_editor_view(page, lang, user_info)

        if troute.match("/starter"):
            return get_starter_view(page, lang, user_info)

        return None

    async def route_change(e: ft.RouteChangeEvent) -> None:
        try:
            page.views.clear()
            if page.route:
                Logger.info(f"Redirecting to {page.route} route...")
            else:
                Logger.info("Page not found")

            current_username = user_info.get("username", "") or "Admin"
            current_language_code = db.users.get_language(current_username) if current_username else "vi"
            current_currency = db.users.get_currency(current_username) if current_username else "VND (đ)"
            lang = get_language(current_language_code)

            route_name = page.route or "/"
            cache_key = get_view_cache_key(route_name, current_language_code, current_currency)
            cached_entry = views_cache.get(route_name)

            if cached_entry and cached_entry[1] == cache_key:
                view = cached_entry[0]
            else:
                view = build_view_for_route(route_name, lang, user_info)
                if view is not None:
                    views_cache[route_name] = (view, cache_key)

            if view is None:
                await redirect_to_fallback(page, lang, "page_not_found")
                return

            page.views.append(view)
            page.update()

        except Exception as ex:
            Logger.critical(f"Failed to change route: {ex}")
            await on_error(e)

    async def on_error(e) -> None:
        if e == ft.Event(name='error', data='Bad state: No element', control=page):
            print("\nthere is like 5-15% chance you'll see this message on launch, depends on")
            print("your computer. it's because of a bug that makes 2 processes racing for control,")
            print("and if that one specifically wins the race, it causes this to happen.")
            print("currently the bug doesn't affect the application much, so i'll be fixing")
            print("it later. consider yourself lucky if this happens first try.\n")
            Logger.error("PEKKAMC")
        else:
            Logger.critical(f"Unexpected error occurred: {e.data}")
            Logger.info("Attempting to restart application...")

            os.environ["RESTART_FINAM"] = "1"

            await page.window.close()

    page.on_error = on_error
    page.on_route_change = route_change

    page.navigate_to("/starter")()