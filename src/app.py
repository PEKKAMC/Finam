# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

import flet as ft

from src.database import db
from src.utils import DefaultSettings, Page, ThemeManager, UISettings, get_language, set_decimal_separator, set_digit_separator
from src.logger import Logger
from src.pages.category_selection import get_category_selection_view
from src.pages.fallback import get_fallback_view
from src.pages.home import get_home_view
from src.pages.lessons import get_lessons_view
#from src.pages.lesson_player import get_lesson_player_view
from src.pages.savings import get_savings_view
from src.pages.settings import get_settings_view
from src.pages.spending import get_spending_view
from src.pages.purchase_scanner import get_scanner_view
from src.pages.starter.view import StarterView, get_starter_view
from src.pages.user_management import get_user_management_view

ENABLE_EDITOR: bool = os.getenv("ENABLE_EDITOR") == "1"

# DEVELOPER EDITOR PAGE, ONLY INITIALIZE WHEN ENABLE_EDITOR IS SET TO TRUE
if ENABLE_EDITOR:
    from src.pages.lesson_editor import get_lesson_editor_view


def initial_setup() -> None:
    _original_control_update = ft.Control.update

    def _safe_control_update(self) -> None:
        """Ignore detached-control updates until the control is actually attached to a page."""
        try:
            if self is None:
                return None

            page_ref = getattr(self, "page", None)
            if page_ref is None:
                return None

            return _original_control_update(self)
        except Exception as exc:  # pragma: no cover - Flet raises this before page attaches in some race cases
            message = str(exc).lower()
            if "must be added to the page" in message or "no element" in message:
                Logger.debug(f"Skipping control update for detached control: {exc}")
                return None
            raise

    ft.Control.update = _safe_control_update

async def redirect_to_fallback(page: Page, lang: dict, fallback_reason: str) -> None:
    Logger.info("Redirecting to fallback page...")
    await page.push_route("/fallback")
    view = get_fallback_view(page, lang, fallback_reason)
    page.views.append(view)
    page.update()
    refresh_handler = getattr(view, "_refresh_view", None)
    if callable(refresh_handler):
        # noinspection PyCallingNonCallable
        refresh_handler()


async def main(page: Page) -> None:
    initial_setup()
    db.initialize_database()

    info: dict[str, str] = {
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
    page.window.icon = "icon.ico"
    page.window.resizable = True
    page.window.width = UISettings.MAX_APP_WIDTH
    page.window.height = UISettings.MAX_APP_HEIGHT

    page.update()

    views_cache: dict[str, tuple[ft.View, str]] = {}

    def get_view_cache_key(route: str, language_code: str, currency: str, theme: str, digit_separator: str, decimal_separator: str, username: str) -> str:
        return f"{route}|{language_code}|{currency}|{theme}|{digit_separator}|{decimal_separator}|{username}"

    def build_view_for_route(route: str, lang: dict, user_info: dict) -> ft.View | None:
        troute = ft.TemplateRoute(route)

        if troute.match("/user_management"):
            return get_user_management_view(page, lang, user_info)

        if troute.match("/home"):
            return get_home_view(page, lang, user_info)

        if troute.match("/lessons"):
            return get_lessons_view(page, lang, user_info)

        if troute.match("/savings"):
            return get_savings_view(page, lang, user_info)

        #if troute.match("/lesson-player/:lesson_id"):
        #    lesson_id = getattr(troute, "lesson_id", None)
        #    return get_lesson_player_view(page, lang, user_info, lesson_id)

        #if troute.match("/lesson-player"):
        #    return get_lesson_player_view(page, lang, user_info)

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

    def delete_cached_view(route: str) -> None:
        if route in views_cache:
            del views_cache[route]
            Logger.info(f"Deleted cached view for route: {route}")
        else:
            Logger.info(f"No cached view found for route: {route}")

    def delete_all_cached_views() -> None:
        views_cache.clear()
        Logger.info("Deleted all cached views")

    page.delete_cached_view = delete_cached_view
    page.delete_all_cached_views = delete_all_cached_views

    async def route_change(e: ft.RouteChangeEvent) -> None:
        try:
            page.views.clear()
            if page.route:
                Logger.info(f"Redirecting to {page.route} route...")
            else:
                Logger.info("Page not found")

            current_username = info.get("username", "")
            current_language_code = db.users.get_language(current_username) if current_username else DefaultSettings.LANGUAGE
            current_currency = db.users.get_currency(current_username) if current_username else DefaultSettings.CURRENCY
            current_theme = db.app_settings.get_theme()
            current_digit_separator = db.app_settings.get_digit_separator()
            current_decimal_separator = db.app_settings.get_decimal_separator()
            set_digit_separator(current_digit_separator)
            set_decimal_separator(current_decimal_separator)
            ThemeManager.set_theme(current_theme)
            page.theme_mode = ft.ThemeMode.DARK if ThemeManager.get_theme().dark_mode else ft.ThemeMode.LIGHT
            lang = get_language(current_language_code)

            route_name = page.route or "/"
            cache_key = get_view_cache_key(
                route_name,
                current_language_code,
                current_currency,
                current_theme,
                current_digit_separator,
                current_decimal_separator,
                current_username,
            )

            if route_name == "/starter":
                view = build_view_for_route(route_name, lang, info)
            else:
                cached_entry = views_cache.get(route_name)

                if cached_entry and cached_entry[1] == cache_key:
                    view = cached_entry[0]
                else:
                    view = build_view_for_route(route_name, lang, info)
                    if view is not None:
                        views_cache[route_name] = (view, cache_key)

            if view is None:
                await redirect_to_fallback(page, lang, "page_not_found")
                return

            page.views.append(view)
            resize_handler = getattr(view, "_on_page_resize", None)
            if callable(resize_handler):
                page.on_resize = resize_handler
            page.update()
            refresh_handler = getattr(view, "_refresh_view", None)
            if callable(refresh_handler):
                # noinspection PyCallingNonCallable
                refresh_handler()
            if isinstance(view, StarterView) and view.is_unlocked:
                view.show_user_management_dialog()

        except Exception as ex:
            await on_error(e, ex)

    async def on_error(e, ex: Exception | None = None) -> None:
        event_data = getattr(e, "data", None)
        Logger.critical(f"Unexpected error occurred: \nEvent data: {event_data}\nException: {ex}", exc_info=True)

        await page.window.destroy()

    page.on_error = on_error
    page.on_route_change = route_change

    await page.push_route("/starter")