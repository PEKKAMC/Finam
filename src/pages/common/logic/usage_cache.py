import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import flet as ft

from src.database import db
from src.logger import Logger

UsageT = TypeVar("UsageT", bound=dict[str, Any])


def get_usage_cache_key(feature: str) -> str | None:
    account = db.app_settings.get_google_account()
    if not account:
        return None
    return f"finam_usage:{feature}:{account['uid']}"


async def load_usage_cache(
    preferences: ft.SharedPreferences, key: str
) -> dict[str, Any] | None:
    try:
        value = await preferences.get(key)
    except RuntimeError as ex:
        Logger.warning(f"Could not read cached {key}: {ex}")
        return None

    if not isinstance(value, str):
        return None
    try:
        cached = json.loads(value)
    except json.JSONDecodeError as ex:
        Logger.warning(f"Discarding invalid cached {key}: {ex}")
        await _remove_invalid_cache(preferences, key)
        return None
    if not isinstance(cached, dict):
        Logger.warning(f"Discarding invalid cached {key}: expected an object")
        await _remove_invalid_cache(preferences, key)
        return None
    return cached


async def _remove_invalid_cache(
    preferences: ft.SharedPreferences, key: str
) -> None:
    try:
        if not await preferences.remove(key):
            Logger.error(f"Could not remove invalid cached {key}")
    except RuntimeError as ex:
        Logger.error(f"Could not remove invalid cached {key}: {ex}")


async def save_usage_cache(
    preferences: ft.SharedPreferences, key: str, value: dict[str, Any]
) -> None:
    try:
        serialized = json.dumps(value)
    except (TypeError, ValueError) as ex:
        Logger.error(f"Could not serialize cached {key}: {ex}")
        return
    try:
        if not await preferences.set(key, serialized):
            Logger.error(f"Could not save cached {key}")
    except Exception as ex:
        Logger.error(f"Could not save cached {key}: {ex}")


class UsageCache:
    """Shares cached usage values and in-flight refreshes across app pages."""

    _FRESH_FOR_SECONDS = 60

    def __init__(self, preferences: ft.SharedPreferences) -> None:
        self._preferences = preferences
        self._values: dict[str, dict[str, Any]] = {}
        self._refresh_tasks: dict[str, asyncio.Task[dict[str, Any]]] = {}
        self._refreshed_at: dict[str, float] = {}

    async def get(self, key: str) -> dict[str, Any] | None:
        if key in self._values:
            return self._values[key]
        try:
            value = await asyncio.wait_for(
                load_usage_cache(self._preferences, key),
                timeout=3,
            )
        except TimeoutError:
            Logger.warning(f"Timed out reading cached {key}")
            return None
        except Exception as ex:
            Logger.error(f"Could not load cached {key}: {ex}")
            return None
        if value is not None:
            self._values[key] = value
        return value

    async def refresh(
        self,
        key: str,
        fetch: Callable[[], Awaitable[UsageT]],
        force: bool = False,
    ) -> dict[str, Any]:
        task = self._refresh_tasks.get(key)
        if task is None and not force and key in self._values:
            refreshed_at = self._refreshed_at.get(key)
            if (
                refreshed_at is not None
                and time.monotonic() - refreshed_at < self._FRESH_FOR_SECONDS
            ):
                return self._values[key]
        if task is None:
            task = asyncio.create_task(self._fetch_and_save(key, fetch))
            self._refresh_tasks[key] = task
        try:
            return await task
        finally:
            if task.done() and self._refresh_tasks.get(key) is task:
                del self._refresh_tasks[key]

    async def _fetch_and_save(
        self,
        key: str,
        fetch: Callable[[], Awaitable[UsageT]],
    ) -> dict[str, Any]:
        value = await fetch()
        self._values[key] = value
        self._refreshed_at[key] = time.monotonic()
        await save_usage_cache(self._preferences, key, value)
        return value
