# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import base64
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import secrets
import sqlite3
import threading
import time
from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

import flet as ft
import httpx
import requests
from flet.auth import AuthorizationService, GoogleOAuthProvider

from src.database import db
from src.logger import Logger
from src.pages.global_components import AddUserField, DeleteUserDialog, Menu, UserList, UserManagementDialog
from src.pages.user_management.components import GoogleAccountCard, MenuItem, MenuSectionCard, ProfileCard, DeleteAllDataDialog
from src.pages.user_management.logic import LogicController
from src.utils import Color, Page, get_asset_path, get_safe_page_size, Text, UISettings
from src.version_manager import get_version

Logger.info("Initializing User Management page...")

_pending_web_google_auth: dict[
    str, tuple[float, AuthorizationService, str]
] = {}
_web_google_auth_result: str | None = None


def _create_oauth_callback_handler(expected_state: str, loop, result_future):
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            callback_url = urlparse(self.path)
            query = parse_qs(callback_url.query)
            state = query.get("state", [""])[0]
            code = query.get("code", [""])[0]
            error = query.get("error", [""])[0]

            if callback_url.path != "/oauth_callback":
                self.send_error(404)
                return
            if not hmac.compare_digest(state, expected_state):
                self.send_error(400, "Invalid OAuth state")
                return
            if not code and not error:
                self.send_error(400, "Authorization code is missing")
                return

            body = (
                b"Google sign-in complete. You can close this browser window."
                if not error
                else b"Google sign-in was not completed. You can close this browser window."
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

            def finish_callback():
                if not result_future.done():
                    result_future.set_result({"code": code, "error": error})

            loop.call_soon_threadsafe(finish_callback)

        def log_message(self, format, *args):
            return

    return OAuthCallbackHandler


async def complete_google_web_callback(route: str) -> bool:
    global _web_google_auth_result
    callback = urlparse(route)
    if callback.path != "/oauth_callback":
        return False

    query = parse_qs(callback.query)
    state = query.get("state", [""])[0]
    pending = _pending_web_google_auth.pop(state, None)
    if pending is None:
        Logger.warning("Google web callback has no matching pending authorization")
        return False

    expires_at, authorization, backend_url = pending
    result = "failed"
    try:
        if time.monotonic() > expires_at:
            raise RuntimeError("Google web authorization expired")
        if query.get("error"):
            raise RuntimeError(f"Google authorization failed: {query['error'][0]}")

        code = query.get("code", [""])[0]
        if not code:
            raise RuntimeError("Google authorization code is missing")

        await authorization.request_token(code)
        token = await authorization.get_token()
        if token is None:
            raise RuntimeError("Firebase ID token is missing")

        signed_in = await _save_google_account_globally(
            token.access_token,
            backend_url,
            token.refresh_token or "",
        )
        result = "signed_in" if signed_in else "failed"
    except Exception as ex:
        Logger.warning(f"Could not complete Google web authorization: {ex}", exc_info=True)
    _web_google_auth_result = result
    return True


def take_google_web_auth_result() -> str | None:
    global _web_google_auth_result
    result = _web_google_auth_result
    _web_google_auth_result = None
    return result


async def _save_google_account_globally(
    firebase_id_token: str,
    backend_url: str,
    refresh_token: str,
) -> bool:
    def fetch_profile() -> dict:
        response = requests.get(
            f"{backend_url}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {firebase_id_token}"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    profile = await asyncio.to_thread(fetch_profile)
    if not isinstance(profile, dict):
        raise RuntimeError("Firebase returned an invalid user profile")
    google_uid = profile.get("uid", "")
    email = profile.get("email", "")
    if not google_uid or not email:
        raise RuntimeError("Firebase returned an incomplete user profile")
    return db.app_settings.set_google_account(
        google_uid,
        email,
        refresh_token,
    )


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the User Management View."""
    def __init__(self, page: Page, lang: dict, user_info: dict, controller: LogicController, refresh_callback: Callable):
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = controller
        self._refresh_view = refresh_callback

        # INITIALIZE DIALOG COMPONENTS
        self.user_list = UserList(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info["username"],
            on_select_callback=self._handle_change_user,
            on_delete_callback=self.show_delete_prompt
        )

        self.add_form = AddUserField(
            page=self._page,
            lang=self.lang,
            on_submit_callback=self._handle_add_user,
            currencies=self.controller.get_currencies(),
            default_currency=self.controller.get_currency(self.user_info["username"])
        )

        self.user_dialog = UserManagementDialog(
            page=self._page,
            lang=self.lang,
            user_list=self.user_list,
            add_form=self.add_form,
            on_close_callback=self._close_user_management_dialog
        )

        self.delete_dialog = DeleteUserDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self._handle_delete_confirm
        )

        self.delete_all_data_dialog = DeleteAllDataDialog(
            page=self._page,
            lang=self.lang,
            on_confirm_callback=self._handle_delete_all_data_confirm
        )

    # USER MANAGEMENT DIALOG
    def show_user_management_dialog(self) -> int:
        self.user_list.update_data(
            self.controller.get_all_users(),
            self.user_info["username"]
        )
        try:
            self.user_list.main_container.update()
            self.user_dialog.update()
            self._page.update()
        except RuntimeError:
            pass
        return self.user_dialog.show()

    def _close_user_management_dialog(self, e: ft.ControlEvent | None = None) -> None:
        self.user_dialog.dismiss()

    # USER ACTIONS
    def _handle_add_user(self, input_username: str, currency: str):
        if not input_username:
            return
        success, error_msg = self.controller.add_user(input_username, currency)

        if success:
            self.add_form.clear()
            self.user_list.update_data(
                self.controller.get_all_users(),
                self.user_info["username"]
            )
            try:
                self.user_dialog.update()
                self._page.update()
            except RuntimeError:
                pass
            self._refresh_view()
        else:
            self.add_form.show_error("error")

    def _handle_change_user(self, username: str):
        self.user_dialog.dismiss()
        if username != self.user_info["username"] and self._page.auth is not None:
            self._page.logout()
        self.controller.change_user(username)
        self._refresh_view()

    # DELETE USER DIALOG
    def show_delete_prompt(self, username: str = "") -> int:
        try:
            if username:
                self.delete_dialog.selected_user = username
            self.delete_dialog.show()
            return 0
        except Exception as ex:
            Logger.warn(f"Failed to show delete prompt {ex}")
            return -1

    def _handle_delete_confirm(self, username: str) -> int:
        try:
            self.controller.delete_user(username)
            self._refresh_view()
            return 0
        except Exception as ex:
            Logger.warn(f"Cannot delete user {username}, {ex}")
            return -1

    # DELETE ALL DATA DIALOG
    def show_delete_all_data_prompt(self) -> int:
        try:
            self.delete_all_data_dialog.show()
            return 0
        except Exception as ex:
            Logger.warn(f"Failed to show delete all data prompt {ex}")
            return -1

    async def _handle_delete_all_data_confirm(self, e=None) -> int:
        try:
            self.controller.delete_all_data()
            self._page.navigate_to("/starter")()
            self._page.delete_all_cached_views()

            return 0
        except Exception as ex:
            Logger.error(f"Failed to delete all data: {ex}")
            return -1

class UserManagementView(ft.View):
    def __init__(self, page: Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_version = get_version

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info)

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info,
            controller=self.controller,
            refresh_callback=self._refresh_view
        )

        # FETCH DASHBOARD DATA
        self.app_version = self.get_version("Finam")

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info
        )

        self.top_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                Text.SMALL(self.lang["user_management.profile_and_options"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD),
            ]
        )

        self.profile_card = ProfileCard(
            username=self.user_info["username"],
            lang=self.lang,
            on_change_user=self.dialogs.show_user_management_dialog
        )
        self.google_account_card = GoogleAccountCard(
            lang=self.lang,
            on_connect=self._connect_google_account,
            on_disconnect=self._disconnect_google_account,
        )
        self._refresh_google_account()
        google_auth_result = take_google_web_auth_result()
        if google_auth_result == "failed":
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )

        self.services_section_title = Text.SMALL(self.lang["user_management.services_and_features"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        self.services_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.SHIELD_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.disable_ads"],
                    subtitle=self.lang["user_management.smooth_experience"],
                    trailing=ft.Switch(value=True, active_color=Color.PRIMARY_ACTION)
                ),
                MenuItem(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["settings.settings"],
                    subtitle=self.lang["user_management.language_security_currency"],
                    on_click=self._page.navigate_to("/settings")
                )
            ]
        )

        self.support_section_title = Text.SMALL(self.lang["user_management.support_and_info"].upper(), color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)

        self.support_card = MenuSectionCard(
            items=[
                MenuItem(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=Color.PRIMARY_ACTION,
                    icon_bg_color=Color.AGGREGATE_BACKGROUND,
                    title=self.lang["user_management.help_faq"],
                    subtitle=self.lang["user_management.guide_expense_mgmt"]
                ),
                MenuItem(
                    icon=ft.Icons.LOGOUT,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.logout"],
                    subtitle="",
                    on_click=self.logout
                ),
                MenuItem(
                    icon=ft.Icons.DELETE_FOREVER,
                    icon_color=Color.NEGATIVE_ACTION,
                    icon_bg_color=Color.ACTIVITY_BACKGROUND,
                    title=self.lang["user_management.delete_all_data"],
                    subtitle="",
                    on_click=lambda e: self.dialogs.show_delete_all_data_prompt()
                )
            ]
        )

        self.footer = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Container(width=8, height=8, border_radius=4, bgcolor=Color.PRIMARY_ACTION),
                        Text.SMALL(f"{self.lang["user_management.version"]} {self.app_version}", color=Color.AGGREGATE_TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                Text.SMALL(self.lang["user_management.privacy_encryption"], color=Color.SUBTITLE_TEXT, text_align=ft.TextAlign.CENTER)
            ]
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=16,
                            expand=True,
                            controls=[
                                self.top_header,
                                self.profile_card,
                                self.google_account_card,
                                self.services_section_title,
                                self.services_card,
                                self.support_section_title,
                                self.support_card,
                                ft.Container(height=8),
                                self.footer
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/user_management",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.SafeArea(
                expand=True,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        self.main_container,
                        self.menu
                    ]
                )
            )
        )

        self._page.on_resize = self._on_page_resize
        self._on_page_resize()

    async def logout(self, e=None) -> None:
        try:
            self._page.logout()
            self.user_info["username"] = ""
            self._page.navigate_to("/starter")()
        except Exception as ex:
            Logger.warn(f"Failed to logout: {ex}")

    def _refresh_google_account(self) -> None:
        account = db.app_settings.get_google_account()
        signed_in = db.app_settings.has_google_account_session()
        self.google_account_card.set_account(
            account["email"] if account and signed_in else None
        )

    @staticmethod
    def _get_google_auth_config() -> dict:
        with open(get_asset_path("google_auth.json"), encoding="utf-8") as file:
            config = json.load(file)
        if not isinstance(config, dict):
            raise ValueError("Google auth configuration must be a JSON object")
        return config

    async def _connect_google_account(self, e=None) -> None:
        try:
            config = self._get_google_auth_config()
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as ex:
            Logger.error(f"Could not load Google auth configuration: {ex}")
            self.google_account_card.show_error(
                self.lang["user_management.google_not_configured"]
            )
            return

        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip() or str(
            config.get("google_client_id", "")
        ).strip()
        redirect_url = os.getenv("GOOGLE_OAUTH_REDIRECT_URL", "").strip() or str(
            config.get("redirect_url", "")
        ).strip()
        backend_url = os.getenv("FINAM_BACKEND_URL", "").strip() or str(
            config.get("backend_url", "")
        ).strip()
        backend_url = backend_url.rstrip("/")
        missing_settings = [
            setting
            for setting, value in (
                ("google_client_id", client_id),
                ("redirect_url", redirect_url),
                ("backend_url", backend_url),
            )
            if not value
        ]
        if missing_settings:
            self.google_account_card.show_error(
                self.lang["user_management.google_missing_config"].format(
                    ", ".join(missing_settings)
                )
            )
            return

        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        provider = GoogleOAuthProvider(
            client_id=client_id,
            client_secret="",
            redirect_url=redirect_url,
        )
        provider.token_endpoint = f"{backend_url}/api/v1/auth/google/token"
        provider.scopes = ["openid", "email"]
        provider.code_challenge = challenge
        provider.code_challenge_method = "S256"
        provider.code_verifier = verifier
        provider.authorization_params["prompt"] = "select_account"

        self.google_account_card.set_busy(True)
        self.google_account_card.show_error("")
        try:
            authorization = AuthorizationService(
                provider,
                fetch_user=False,
                fetch_groups=False,
            )
            authorization_url, state = authorization.get_authorization_data()
            redirect = urlparse(redirect_url)
            if self._page.web:
                app_origin = urlparse(self._page.url or "")
                if (
                    redirect.scheme not in ("http", "https")
                    or not redirect.hostname
                    or redirect.path != "/oauth_callback"
                    or (redirect.scheme, redirect.netloc)
                    != (app_origin.scheme, app_origin.netloc)
                ):
                    raise ValueError(
                        "Web sign-in requires an /oauth_callback URL on this app's origin"
                    )

                now = time.monotonic()
                for pending_state, pending in list(_pending_web_google_auth.items()):
                    if pending[0] < now:
                        _pending_web_google_auth.pop(pending_state, None)
                _pending_web_google_auth[state] = (
                    now + 300,
                    authorization,
                    backend_url,
                )
                try:
                    await ft.UrlLauncher().launch_url(
                        authorization_url,
                        web_only_window_name="_self",
                    )
                except Exception:
                    _pending_web_google_auth.pop(state, None)
                    raise
                return

            if (
                redirect.scheme != "http"
                or redirect.hostname not in ("localhost", "127.0.0.1")
                or redirect.path != "/oauth_callback"
            ):
                raise ValueError(
                    "Desktop sign-in requires a localhost /oauth_callback redirect URL"
                )

            loop = asyncio.get_running_loop()
            callback_result = loop.create_future()
            callback_handler = _create_oauth_callback_handler(
                state,
                loop,
                callback_result,
            )
            callback_server = ThreadingHTTPServer(
                (redirect.hostname, redirect.port or 80),
                callback_handler,
            )
            callback_thread = threading.Thread(
                target=callback_server.serve_forever,
                daemon=True,
                name="finam-google-oauth-callback",
            )
            callback_thread.start()
            try:
                await ft.UrlLauncher().launch_url(authorization_url)
                result = await asyncio.wait_for(callback_result, timeout=300)
            finally:
                await asyncio.to_thread(callback_server.shutdown)
                callback_server.server_close()
                await asyncio.to_thread(callback_thread.join, 2)

            if result["error"]:
                raise RuntimeError(f"Google authorization failed: {result['error']}")
            await authorization.request_token(result["code"])
            token = await authorization.get_token()
            if token is None:
                raise RuntimeError("Firebase ID token is missing")
            await self._save_google_account(
                token.access_token,
                backend_url,
                token.refresh_token or "",
            )
        except httpx.HTTPStatusError as ex:
            try:
                error_detail = ex.response.json().get("detail", "")
            except (ValueError, AttributeError):
                error_detail = ex.response.text[:500]
            Logger.warning(
                "Google authorization backend rejected the request "
                f"(HTTP {ex.response.status_code}): {error_detail or ex!r}",
                exc_info=True,
            )
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )
            self.google_account_card.set_busy(False)
        except Exception as ex:
            Logger.warning(
                f"Failed to start Google authorization ({type(ex).__name__}): {ex!r}",
                exc_info=True,
            )
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )
            self.google_account_card.set_busy(False)

    async def _save_google_account(
        self,
        firebase_id_token: str,
        backend_url: str,
        refresh_token: str,
    ) -> None:
        try:
            if not refresh_token:
                raise RuntimeError("Firebase refresh token is missing")
            saved = await _save_google_account_globally(
                firebase_id_token,
                backend_url,
                refresh_token,
            )
            if not saved:
                raise RuntimeError("Could not save app-wide Google account")

            account = db.app_settings.get_google_account()
            self.google_account_card.set_account(account["email"] if account else None)
            self._page.delete_cached_view("/purchase_scanner")
            Logger.info("Google account signed in for the app")
        except (requests.RequestException, KeyError, RuntimeError, sqlite3.Error, ValueError) as ex:
            Logger.warning(f"Could not complete Google authorization: {ex}")
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )
        finally:
            self.google_account_card.set_busy(False)

    def _disconnect_google_account(self, e=None) -> None:
        if not db.app_settings.clear_google_account():
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )
            return
        self._page.delete_cached_view("/purchase_scanner")
        self.google_account_card.set_account(None)

    def _refresh_view(self) -> int:
        try:
            self._on_page_resize()
            self.dialogs.user_list.update_data(
                self.controller.get_all_users(),
                self.user_info["username"]
            )
            self.profile_card.update_data(self.user_info["username"])
            self._refresh_google_account()
            return 0
        except RuntimeError as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1

    def _on_page_resize(self, e = None) -> ft.PageResizeEvent | None:
        page_width, page_height = self.get_safe_page_size(
            page=self._page
        )

        # Resizing main container
        self.main_container.width = page_width
        self.main_container.height = page_height

        # Resizing other components
        self.menu.resize(
            width=page_width
        )
        self.profile_card.resize(
            width=page_width
        )
        self.google_account_card.resize(
            width=page_width
        )
        self.services_card.resize(
            width=page_width
        )
        self.support_card.resize(
            width=page_width
        )

        self.dialogs.user_dialog.resize(
            width=page_width // 3 * 2,
            height=page_height // 3 * 2,
        )

        return e

def get_user_management_view(page: Page, lang: dict, user_info: dict) -> ft.View:
    Logger.info("Loading User Management page...")
    return UserManagementView(page, lang, user_info)