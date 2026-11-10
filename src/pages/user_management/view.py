# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import socket
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import flet as ft
import httpx
import requests
from flet.auth import AuthorizationService, GoogleOAuthProvider

from src.database import db
from src.logger import Logger
from src.pages.common import Menu
from src.pages.common.logic import (
    close_user_management_dialog,
    show_user_management_dialog,
)
from src.pages.purchase_scanner.logic import ScannerApiError
from src.pages.user_management.components import (
    GoogleAccountCard,
    ProfileCard,
    UserManagementDialogs,
    UserManagementPageContent,
)
from src.pages.user_management.logic import LogicController
from src.utils import (
    Color,
    DefaultSettings,
    MenuResizeValues,
    Page,
    get_menu_resize_values,
    get_safe_page_size,
    scale_height,
    scale_width,
)
from src.version_manager import get_version

Logger.info("Initializing User Management page...")

_pending_web_google_auth: dict[str, tuple[float, AuthorizationService, str]] = {}
_pending_mobile_google_auth: dict[str, tuple[float, AuthorizationService, str]] = {}
_web_google_auth_result: str | None = None


def is_google_oauth_callback_route(route: str) -> bool:
    """Match OAuth callback paths in both browser and native deep-link routes."""
    path = urlparse(route).path.rstrip("/")
    return bool(path) and path.rsplit("/", maxsplit=1)[-1] == "oauth_callback"


def _parse_oauth_query(query_string: str | bytes) -> dict[str, str]:
    if isinstance(query_string, bytes):
        query_string = query_string.decode("utf-8")
    return {
        key: values[0]
        for key, values in parse_qs(query_string).items()
        if values
    }


def _create_oauth_callback_handler(expected_state: str, loop: asyncio.AbstractEventLoop, result_future: asyncio.Future[dict[str, str]]) -> type[BaseHTTPRequestHandler]:
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            callback_url = urlparse(self.path)
            query = _parse_oauth_query(callback_url.query)
            state = query.get("state", "")
            code = query.get("code", "")
            error = query.get("error", "")

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

            def finish_callback() -> None:
                if not result_future.done():
                    _ = result_future.set_result({"code": code, "error": error})

            _ = loop.call_soon_threadsafe(finish_callback)

        def log_message(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            return

    return OAuthCallbackHandler


async def complete_google_web_callback(route: str) -> bool:
    global _web_google_auth_result
    callback = urlparse(route)
    if not is_google_oauth_callback_route(route):
        return False

    query = _parse_oauth_query(callback.query)
    state = query.get("state", "")
    pending = _pending_web_google_auth.pop(state, None)
    if pending is None:
        Logger.warning("Google web callback has no matching pending authorization")
        _web_google_auth_result = "failed"
        return True

    expires_at, authorization, backend_url = pending
    result = "failed"
    try:
        if time.monotonic() > expires_at:
            raise RuntimeError("Google web authorization expired")
        if query.get("error"):
            raise RuntimeError(f"Google authorization failed: {query['error']}")

        code = query.get("code", "")
        if not code:
            raise RuntimeError("Google authorization code is missing")

        await authorization.request_token(code)
        token = await authorization.get_token()
        if token is None:
            raise RuntimeError("Firebase ID token is missing")

        signed_in = await LogicController.save_google_account(
            token.access_token,
            backend_url,
            token.refresh_token or "",
        )
        result = "signed_in" if signed_in else "failed"
    except (httpx.HTTPError, KeyError, OSError, requests.RequestException, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
        Logger.warning(f"Could not complete Google web authorization: {ex}", exc_info=True)
    _web_google_auth_result = result
    return True


async def complete_google_mobile_callback(route: str) -> bool:
    global _web_google_auth_result
    callback = urlparse(route)
    if not is_google_oauth_callback_route(route):
        return False

    query = _parse_oauth_query(callback.query)
    state = query.get("state", "")
    Logger.info(
        "Google mobile OAuth callback received "
        f"(path={callback.path!r}, has_code={bool(query.get('code'))}, "
        f"has_error={bool(query.get('error'))}, has_state={bool(state)})"
    )
    pending = _pending_mobile_google_auth.pop(state, None)
    if pending is None:
        persisted = db.app_settings.take_mobile_google_oauth(state)
        if persisted is None:
            Logger.warning(
                "Google mobile callback has no matching pending authorization "
                "(state may be missing, expired, or app data was unavailable)"
            )
            _web_google_auth_result = "failed"
            return True
        try:
            provider = GoogleOAuthProvider(
                client_id=persisted["client_id"],
                client_secret="",
                redirect_url=persisted["redirect_url"],
            )
            provider.token_endpoint = (
                f"{persisted['backend_url']}/api/v1/auth/google/token"
            )
            provider.code_verifier = persisted["verifier"]
            authorization = AuthorizationService(
                provider,
                fetch_user=False,
                fetch_groups=False,
            )
            pending = (
                float(persisted["expires_at"]),
                authorization,
                persisted["backend_url"],
            )
            Logger.info("Restored pending mobile Google authorization from SQLite")
        except (KeyError, TypeError, ValueError) as ex:
            Logger.warning(
                f"Could not restore pending mobile Google authorization: {ex}",
                exc_info=True,
            )
            _web_google_auth_result = "failed"
            return True
    else:
        db.app_settings.clear_mobile_google_oauth()

    expires_at, authorization, backend_url = pending
    result = "failed"
    try:
        if time.time() > expires_at:
            raise RuntimeError("Google mobile authorization expired")
        if query.get("error"):
            raise RuntimeError(f"Google authorization failed: {query['error']}")

        code = query.get("code", "")
        if not code:
            raise RuntimeError("Google mobile authorization code is missing")

        Logger.info("Exchanging mobile Google authorization code with backend")
        await authorization.request_token(code)
        Logger.info("Mobile Google token exchange succeeded")
        token = await authorization.get_token()
        if token is None:
            raise RuntimeError("Firebase ID token is missing")

        Logger.info(
            "Received Firebase credentials "
            f"(has_id_token={bool(token.access_token)}, "
            f"has_refresh_token={bool(token.refresh_token)})"
        )
        Logger.info("Validating Google account and saving app-wide session")
        signed_in = await LogicController.save_google_account(
            token.access_token,
            backend_url,
            token.refresh_token or "",
        )
        result = "signed_in" if signed_in else "failed"
        Logger.info(f"Mobile Google OAuth account save result: {result}")
    except (httpx.HTTPError, KeyError, OSError, requests.RequestException, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
        Logger.warning(f"Could not complete Google mobile authorization: {ex}", exc_info=True)
    _web_google_auth_result = result
    Logger.info(f"Mobile Google OAuth callback processing finished: {result}")
    return True


def take_google_web_auth_result() -> str | None:
    global _web_google_auth_result
    result = _web_google_auth_result
    _web_google_auth_result = None
    return result


class DialogManager:
    """Handles all dialog instantiation, states, and callbacks for the User Management View."""

    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str], controller: LogicController, refresh_callback: Callable[..., int]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info
        self.controller = controller
        self._refresh_view = refresh_callback

        self.dialog_components = UserManagementDialogs(
            page=self._page,
            lang=self.lang,
            current_user=self.user_info["username"],
            currencies=self.controller.get_currencies(),
            default_currency=DefaultSettings.CURRENCY,
            on_change_user=self._handle_change_user,
            on_delete_user=self._handle_delete_confirm,
            on_add_user=self._handle_add_user,
            on_close_user_dialog=self._close_user_management_dialog,
            on_delete_all_data=self._handle_delete_all_data_confirm,
        )
        self.user_list = self.dialog_components.user_list
        self.add_form = self.dialog_components.add_form
        self.user_dialog = self.dialog_components.user_dialog
        self.delete_dialog = self.dialog_components.delete_dialog
        self.delete_all_data_dialog = self.dialog_components.delete_all_data_dialog

    # USER MANAGEMENT DIALOG
    def show_user_management_dialog(self) -> int:
        return show_user_management_dialog(
            self._page,
            self.user_list,
            self.user_dialog,
            self.controller.get_all_users(),
            self.user_info["username"],
        )

    def _close_user_management_dialog(self, _e: ft.ControlEvent | None = None) -> None:
        close_user_management_dialog(self.user_dialog)

    # USER ACTIONS
    def _handle_add_user(self, input_username: str, currency: str) -> None:
        if not input_username:
            return
        status = self.controller.add_user(input_username, currency)

        if status == 0:
            self.add_form.clear()
            users: list[dict[str, str] | str] = [
                user for user in self.controller.get_all_users()
            ]
            self.user_list.update_data(users, self.user_info["username"])
            try:
                self.user_dialog.update()
                self._page.update()
            except RuntimeError:
                pass
            self._refresh_view()
        else:
            self.add_form.show_error("error")

    def _handle_change_user(self, username: str) -> None:
        self.user_dialog.dismiss()
        if username != self.user_info["username"] and self._page.auth is not None:
            self._page.logout()
        self.controller.change_user(username)
        self._refresh_view()

    # DELETE USER DIALOG
    def show_delete_prompt(self, username: str = '') -> int:
        try:
            if username:
                self.delete_dialog.selected_user = username
            self.delete_dialog.show()
        except RuntimeError as ex:
            Logger.warn(f"Failed to show delete prompt {ex}")
            return -1
        else:
            return 0

    def _handle_delete_confirm(self, username: str) -> int:
        try:
            self.controller.delete_user(username)
            self._refresh_view()
        except (RuntimeError, sqlite3.Error) as ex:
            Logger.warn(f"Cannot delete user {username}, {ex}")
            return -1
        else:
            return 0

    # DELETE ALL DATA DIALOG
    def show_delete_all_data_prompt(self) -> int:
        try:
            self.delete_all_data_dialog.show()
        except RuntimeError as ex:
            Logger.warn(f"Failed to show delete all data prompt {ex}")
            return -1
        else:
            return 0

    async def _handle_delete_all_data_confirm(self, _e: ft.ControlEvent | None = None) -> int:
        try:
            self.controller.delete_all_data()
            self._page.navigate_to("/starter")()
            self._page.delete_all_cached_views()
        except (RuntimeError, sqlite3.Error) as ex:
            Logger.error(f"Failed to delete all data: {ex}")
            return -1
        else:
            return 0


class UserManagementView(ft.View):
    def __init__(self, page: Page, lang: dict[str, str], user_info: dict[str, str]) -> None:
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # IMPORTED FUNCTIONS
        self.get_safe_page_size = get_safe_page_size
        self.get_menu_resize_values = get_menu_resize_values
        self.get_version = get_version

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info)

        # INITIALIZE DIALOG MANAGER
        self.dialogs = DialogManager(
            page=self._page,
            lang=self.lang,
            user_info=self.user_info,
            controller=self.controller,
            refresh_callback=self._refresh_view,
        )

        # FETCH DASHBOARD DATA
        self.app_version = self.get_version("Finam")

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(page=self._page, lang=self.lang, user_info=self.user_info)

        self.profile_card = ProfileCard(
            username=self.user_info["username"],
            lang=self.lang,
            on_change_user=self.dialogs.show_user_management_dialog,
        )
        self.google_account_card = GoogleAccountCard(
            lang=self.lang,
            on_connect=(None if self._page.web else self._connect_google_account),
            on_disconnect=self._disconnect_google_account,
        )
        self._tier_request_uid: str | None = None
        self._tier_loaded_uid: str | None = None
        if self._page.web:
            self._prepare_web_google_authorization()
        self._refresh_google_account()
        google_auth_result = take_google_web_auth_result()
        if google_auth_result == "failed":
            self.google_account_card.show_error(
                self.lang["user_management.google_auth_failed"]
            )

        self._disable_ads_generation = 0
        self.page_content = UserManagementPageContent(
            lang=self.lang,
            app_version=self.app_version,
            profile_card=self.profile_card,
            google_account_card=self.google_account_card,
            on_disable_ads_change=self._on_disable_ads_change,
            on_open_settings=self._page.navigate_to("/settings"),
            on_open_help=self._page.navigate_to("/help"),
            on_logout=self.logout,
            on_delete_all_data=lambda _event: (
                self.dialogs.show_delete_all_data_prompt()
            ),
        )
        self.disable_ads_switch = self.page_content.disable_ads_switch

        super().__init__(
            route="/user_management",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Stack(
                        expand=True, controls=[self.page_content, self.menu]
                    ),
                )
            ],
        )

        self._page.on_resize = self._resize_page
        self._resize_page()

    async def _on_disable_ads_change(self, _event: ft.Event[ft.Switch]) -> None:
        self._disable_ads_generation += 1
        generation = self._disable_ads_generation
        if not self.disable_ads_switch.value:
            return

        await asyncio.sleep(3)
        if generation == self._disable_ads_generation and self.disable_ads_switch.value:
            self.disable_ads_switch.value = False
            self.disable_ads_switch.update()

    def _on_navigate_away(self) -> None:
        self._disable_ads_generation += 1
        if self.disable_ads_switch.value:
            self.disable_ads_switch.value = False
            self.disable_ads_switch.update()

    async def logout(self, _event: ft.ControlEvent | None = None) -> None:
        try:
            if not self.controller.save_starter_language_for_logout(
                self.user_info["username"]
            ):
                Logger.error("Failed to persist starter language on logout")
                return
            self._page.logout()
            self.user_info["username"] = ""
            self._page.skip_app_lock_once = True
            self._page.navigate_to("/starter")()
        except (KeyError, RuntimeError, sqlite3.Error) as ex:
            Logger.warn(f"Failed to logout: {ex}")

    def _refresh_google_account(self) -> None:
        account, signed_in, cached_tier = self.controller.get_google_account_state()
        self.google_account_card.set_account(
            account["email"] if account and signed_in else None
        )
        if not signed_in:
            self._tier_request_uid = None
            self._tier_loaded_uid = None
            self.profile_card.set_account_tier("guest")
            return
        if cached_tier:
            self.profile_card.set_account_tier(cached_tier)
        if account and account["uid"] in (
            self._tier_request_uid,
            self._tier_loaded_uid,
        ):
            return
        if not cached_tier:
            self.profile_card.set_account_tier("loading")
        self._tier_request_uid = account["uid"] if account else None
        self._page.run_thread(self._load_account_tier)

    def _load_account_tier(self) -> None:
        try:
            uid, tier = self.controller.fetch_google_account_tier()
            if uid:
                self.profile_card.set_account_tier(tier)
                self._tier_loaded_uid = uid
            else:
                self.profile_card.set_account_tier("guest")
        except ScannerApiError as ex:
            Logger.warning(f"Could not load Google account tier: {ex}")
            self.profile_card.set_account_tier("unavailable")
        except (KeyError, RuntimeError, sqlite3.Error) as ex:
            Logger.error(f"Could not display Google account tier: {ex}")
            self.profile_card.set_account_tier("unavailable")
        finally:
            self._tier_request_uid = None

    @staticmethod
    def _get_google_auth_config() -> dict[str, Any]:
        return LogicController.get_google_auth_config()

    def _prepare_web_google_authorization(self) -> None:
        try:
            config = self._get_google_auth_config()
            client_id = (
                os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
                or str(config.get("google_client_id", "")).strip()
            )
            backend_url = (
                os.getenv("FINAM_BACKEND_URL", "").strip()
                or str(config.get("backend_url", "")).strip()
            )
            backend_url = backend_url.rstrip("/")
            redirect_url = (
                os.getenv("GOOGLE_OAUTH_REDIRECT_URL", "").strip()
                or str(config.get("redirect_url", "")).strip()
            )
            if not client_id or not backend_url or not redirect_url:
                raise ValueError("Google client, backend, and redirect URLs are required")

            redirect = urlparse(redirect_url)
            app_origin = urlparse(self._page.url or "")
            if (
                redirect.scheme not in ("http", "https")
                or not redirect.hostname
                or redirect.path != "/oauth_callback"
                or (redirect.scheme, redirect.netloc)
                != (app_origin.scheme, app_origin.netloc)
            ):
                raise ValueError("Web sign-in requires an /oauth_callback URL on this app's origin")

            verifier = secrets.token_urlsafe(64)
            challenge = (
                base64.urlsafe_b64encode(
                    hashlib.sha256(verifier.encode("ascii")).digest()
                )
                .rstrip(b"=")
                .decode("ascii")
            )
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
            authorization = AuthorizationService(
                provider,
                fetch_user=False,
                fetch_groups=False,
            )
            authorization_url, state = authorization.get_authorization_data()

            now = time.monotonic()
            for pending_state, pending in list(_pending_web_google_auth.items()):
                if pending[0] < now:
                    _pending_web_google_auth.pop(pending_state, None)
            _pending_web_google_auth[state] = (
                now + 300,
                authorization,
                backend_url,
            )
            self.google_account_card.connect_button.action = ft.OpenUrl(
                authorization_url,
                target=ft.UrlTarget.BLANK,
            )
        except (FileNotFoundError, json.JSONDecodeError, RuntimeError, ValueError) as ex:
            Logger.warning(f"Could not prepare Google web authorization: {ex}")
            self.google_account_card.show_error(self.lang["user_management.google_not_configured"])

    async def _connect_google_account(self, _event: ft.ControlEvent | None = None) -> None:
        try:
            config = self._get_google_auth_config()
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as ex:
            Logger.error(f"Could not load Google auth configuration: {ex}")
            self.google_account_card.show_error(
                self.lang["user_management.google_not_configured"]
            )
            return

        client_id = (
            os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
            or str(config.get("google_client_id", "")).strip()
        )
        backend_url = (
            os.getenv("FINAM_BACKEND_URL", "").strip()
            or str(config.get("backend_url", "")).strip()
        )
        backend_url = backend_url.rstrip("/")
        is_mobile = bool(
            not self._page.web
            and self._page.platform
            and self._page.platform.is_mobile()
        )
        if is_mobile:
            redirect_url = (
                os.getenv("GOOGLE_OAUTH_MOBILE_REDIRECT_URL", "").strip()
                or str(
                    config.get(
                        "mobile_redirect_url",
                        f"{backend_url}/api/v1/auth/google/mobile-callback",
                    )
                ).strip()
            )
        else:
            redirect_url = (
                os.getenv("GOOGLE_OAUTH_REDIRECT_URL", "").strip()
                or str(config.get("redirect_url", "")).strip()
            )
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
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
            .rstrip(b"=")
            .decode("ascii")
        )
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
                    raise ValueError("Web sign-in requires an /oauth_callback URL on this app's origin")

                now = time.monotonic()
                for pending_state, pending in list(_pending_web_google_auth.items()):
                    if pending[0] < now:
                        _pending_web_google_auth.pop(pending_state, None)
                _pending_web_google_auth[state] = (
                    now + 300,
                    authorization,
                    backend_url,
                )
                self.google_account_card.set_busy(False)
                self._page.update()
                try:
                    await ft.UrlLauncher().launch_url(
                        authorization_url,
                        web_only_window_name="_blank",
                    )
                except (OSError, RuntimeError):
                    _pending_web_google_auth.pop(state, None)
                    raise
                finally:
                    self.google_account_card.set_busy(False)
                return

            if is_mobile:
                Logger.info("Starting mobile Google OAuth handoff")
                backend_origin = urlparse(backend_url)
                if (
                    redirect.scheme != "https"
                    or backend_origin.scheme != "https"
                    or not redirect.hostname
                    or redirect.netloc != backend_origin.netloc
                    or redirect.path != "/api/v1/auth/google/mobile-callback"
                    or redirect.query
                    or redirect.fragment
                ):
                    raise ValueError("Mobile sign-in requires the HTTPS backend mobile callback URL")

                now = time.time()
                for pending_state, pending in list(_pending_mobile_google_auth.items()):
                    if pending[0] < now:
                        _pending_mobile_google_auth.pop(pending_state, None)
                expires_at = now + 300
                if not db.app_settings.save_mobile_google_oauth(
                    state,
                    verifier,
                    expires_at,
                    backend_url,
                    client_id,
                    redirect_url,
                ):
                    raise RuntimeError("Could not persist pending mobile Google authorization")
                Logger.info("Persisted pending mobile Google OAuth state")
                _pending_mobile_google_auth[state] = (
                    expires_at,
                    authorization,
                    backend_url,
                )
                self.google_account_card.set_busy(False)
                self._page.update()
                try:
                    await ft.UrlLauncher().launch_url(
                        authorization_url,
                        mode=ft.LaunchMode.EXTERNAL_APPLICATION,
                    )
                    Logger.info("Returned from external Google sign-in browser")
                except Exception:
                    _pending_mobile_google_auth.pop(state, None)
                    db.app_settings.clear_mobile_google_oauth()
                    raise
                finally:
                    self.google_account_card.set_busy(False)
                return

            redirect_host = redirect.hostname
            if (
                redirect.scheme != "http"
                or redirect_host is None
                or redirect_host not in ("localhost", "127.0.0.1")
                or redirect.path != "/oauth_callback"
            ):
                raise ValueError("Desktop sign-in requires a localhost /oauth_callback redirect URL")

            loop = asyncio.get_running_loop()
            callback_result = loop.create_future()
            callback_handler_class = _create_oauth_callback_handler(
                state,
                loop,
                callback_result,
            )

            def callback_handler_factory(request: socket.socket, client_address: tuple[str, int], server: ThreadingHTTPServer) -> BaseHTTPRequestHandler:
                return callback_handler_class(request, client_address, server)

            callback_server = ThreadingHTTPServer(
                (redirect_host, redirect.port or 80),
                callback_handler_factory,
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
            except ValueError, AttributeError:
                error_detail = ex.response.text[:500]
            Logger.warning(f"Google authorization backend rejected the request\n(HTTP {ex.response.status_code}): {error_detail or ex!r}",exc_info=True)
            self.google_account_card.show_error(self.lang["user_management.google_auth_failed"])
            self.google_account_card.set_busy(False)
        except (httpx.HTTPError, KeyError, OSError, requests.RequestException, RuntimeError, sqlite3.Error, TypeError, ValueError) as ex:
            Logger.warning(f"Failed to start Google authorization ({type(ex).__name__}): {ex!r}", exc_info=True)
            self.google_account_card.show_error(self.lang["user_management.google_auth_failed"])
            self.google_account_card.set_busy(False)

    async def _save_google_account(self, firebase_id_token: str, backend_url: str, refresh_token: str) -> None:
        try:
            if not refresh_token:
                raise RuntimeError("Firebase refresh token is missing")
            saved = await self.controller.save_google_account(
                firebase_id_token,
                backend_url,
                refresh_token,
            )
            if not saved:
                raise RuntimeError("Could not save app-wide Google account")

            self._refresh_google_account()
            self._page.delete_cached_view("/purchase_scanner")
            Logger.info("Google account signed in for the app")
        except (requests.RequestException, KeyError, RuntimeError, sqlite3.Error, ValueError) as ex:
            Logger.warning(f"Could not complete Google authorization: {ex}")
            self.google_account_card.show_error(self.lang["user_management.google_auth_failed"])
        finally:
            self.google_account_card.set_busy(False)

    def _disconnect_google_account(self, _event: ft.ControlEvent | None = None) -> None:
        if not self.controller.clear_google_account():
            self.google_account_card.show_error(self.lang["user_management.google_auth_failed"])
            return
        self._page.delete_cached_view("/purchase_scanner")
        self._refresh_google_account()

    def _refresh_view(self) -> int:
        try:
            self._resize_page()
            users: list[dict[str, str] | str] = [
                user for user in self.controller.get_all_users()
            ]
            self.dialogs.user_list.update_data(
                users, self.user_info["username"]
            )
            self.profile_card.update_data(self.user_info["username"])
            self._refresh_google_account()
        except RuntimeError as ex:
            Logger.warn(f"Failed to refresh view {ex}")
            return -1
        else:
            return 0

    def _resize_page(self, e: ft.PageResizeEvent | None = None) -> None:
        try:
            # Get page size
            page_width, page_height = self.get_safe_page_size(page=self._page)
            menu_resize_values: MenuResizeValues = self.get_menu_resize_values(
                page_width, self.menu
            )

            content_width = scale_width(page_width, 392)
            card_content_width = scale_width(page_width, 352)

            dialog_width = page_width // 3 * 2
            user_list_height = scale_height(page_height, 300)

            self.page_content.resize(
                page_width=page_width,
                page_height=page_height,
                content_width=content_width,
                card_content_width=card_content_width,
            )

            self.menu.resize(
                width=page_width,
                **menu_resize_values,
            )

            self.page_content.set_bottom_margin(
                self.menu.reserved_height
            )

            self.dialogs.user_dialog.resize(
                width=dialog_width,
                list_height=user_list_height,
            )

        except AttributeError as ex:
            Logger.error(f"Failed to get width/height of the page: {ex}")

        except (TypeError, ValueError) as ex:
            Logger.error(f"Value of width/height of the page is invalid: {ex}")

        except Exception as ex:
            Logger.error(f"Error during page resize: {ex}, event: {e}")


def get_user_management_view(page: Page, lang: dict[str, str], user_info: dict[str, str]) -> ft.View:
    Logger.info("Loading User Management page...")
    return UserManagementView(page, lang, user_info)
