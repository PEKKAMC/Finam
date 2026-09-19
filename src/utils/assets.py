# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
import sys
from pathlib import Path

from src.logger import Logger

class TranslationDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in list(self.items()):
            if isinstance(value, dict) and not isinstance(value, TranslationDict):
                self[key] = TranslationDict(value)

    def __missing__(self, key):
        Logger.warn(f"Missing translation key: '{key}'")
        return key

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            Logger.warn(f"Missing translation key: '{item}'")
            return item

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            Logger.warn(f"Missing translation key to delete: '{key}'")
            raise AttributeError(key)

    def get(self, key, default=None):
        if key not in self:
            Logger.warn(f"Missing translation key: '{key}'")
            return default if default is not None else key
        return super().get(key)


def get_asset_path(relative_path) -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / "assets"
    else:
        base_path = Path(__file__).resolve().parent.parent.parent / "assets"

    return str(base_path / relative_path)


def get_language(lang=None) -> dict:
    lang_file = get_asset_path(f"lang/{lang}.json")

    try:
        with open(lang_file, "r", encoding="utf-8-sig") as f:
            loaded_json = json.load(f)
            translation_data = loaded_json.get("translate", {})
            return TranslationDict(translation_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        Logger.error(f"Error loading language file {lang_file}: {e}")
        return TranslationDict()

