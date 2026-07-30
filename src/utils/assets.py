# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
import sys
from pathlib import Path


class TranslationDict(dict):
    def __missing__(self, key):
        return key

    def get(self, key, default=None):
        return self[key] if key not in self else super().get(key)


def get_asset_path(relative_path) -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / "assets"
    else:
        base_path = Path(__file__).resolve().parent.parent.parent / "assets"

    return str(base_path / relative_path)


def get_language(lang=None) -> dict:
    lang_file = get_asset_path(f"lang/{lang}.json")
    translations = TranslationDict()

    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            loaded_json = json.load(f)
            translations.update(loaded_json)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return translations

