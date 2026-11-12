import json
from typing import Any

import flet as ft

from src.database import db
from src.logger import Logger


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
    except RuntimeError as ex:
        Logger.error(f"Could not save cached {key}: {ex}")
