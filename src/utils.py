import flet as ft
import json
import os
import sys
from pathlib import Path
from typing import LiteralString


def get_asset_path(relative_path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / "assets"
    else:
        base_path = Path(__file__).resolve().parent.parent / "assets"

    return str(base_path / relative_path)

def resource_path(relative_path) -> LiteralString | str | bytes:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_language(lang=None) -> dict:
    fallback = {
      "generic.cancel": "generic.cancel",
      "generic.change_user": "generic.change_user",
      "generic.character": "generic.character",
      "generic.delete": "generic.delete",
      "generic.expense": "generic.expense",
      "generic.home": "generic.home",
      "generic.hours": "generic.hours",
      "generic.income": "generic.income",
      "generic.lesson": "generic.lesson",
      "generic.menu": "generic.menu",
      "generic.practice": "generic.practice",
      "generic.saving": "generic.saving",
      "generic.shop": "generic.shop",
      "generic.spending": "generic.spending",
      "generic.test": "generic.test",
      "home.greeting_messages": ["home.greeting_messages"],
      "home.recent_lesson": "home.recent_lesson",
      "home.saving_goal": "home.saving_goal",
      "lessons.cat_all": "lessons.cat_all",
      "lessons.certificates": "lessons.certificates",
      "lessons.learning_time": "lessons.learning_time",
      "lessons.overall_completion": "lessons.overall_completion",
      "lessons.previous_lesson": "lessons.previous_lesson",
      "lessons.previous_lesson_head": "lessons.previous_lesson_head",
      "lessons.search": "lessons.search",
      "lessons.title": "lessons.title",
      "login.add_user": "login.add_user",
      "login.confirm_delete_user_content": "login.confirm_delete_user_content",
      "login.confirm_delete_user_title": "login.confirm_delete_user_title",
      "login.delete_user_tooltip": "login.delete_user_tooltip",
      "login.invalid_username": "login.invalid_username",
      "login.msg_error": "login.msg_error",
      "login.no_user": "login.no_user",
      "login.select_user": "login.select_user",
      "login.user_already_exists": "login.user_already_exists",
      "saving.active_objectives": "saving.active_objectives",
      "saving.aggregate_portfolio_value": "saving.aggregate_portfolio_value",
      "saving.create_objectives": "saving.create_objectives",
      "saving.description": "saving.description",
      "saving.export_ledger": "saving.export_ledger",
      "saving.goal_title": "saving.goal_title",
      "saving.no_reason": "saving.no_reason",
      "saving.progression": "saving.progression",
      "saving.reason": "saving.reason",
      "saving.recent_activity": "saving.recent_activity",
      "saving.save_objective": "saving.save_objective",
      "saving.target_amount": "saving.target_amount",
      "saving.title": "saving.title",
      "saving.untitled_goal": "saving.untitled_goal",
      "saving.view_transactions": "saving.view_transactions"
    }
    lang_file = get_asset_path(f"lang/{lang}.json")
    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            loaded_json = json.load(f)
            return {**fallback, **loaded_json}
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback