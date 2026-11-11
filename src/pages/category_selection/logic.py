# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import Any

from src.database import db
from src.logger import Logger
from src.utils import Data, to_decimal


class LogicController:
    def __init__(self, current_user: str, lang: dict[str, str]) -> None:
        self.current_user = current_user
        self.lang = lang
        self.data = Data()

    def get_default_categories(self, category_type: str) -> list[dict[str, Any]]:
        if category_type == "expense":
            return self.data.get_default_expense_categories(self.lang)
        return self.data.get_default_income_categories(self.lang)

    def get_custom_categories(self, category_type: str) -> list[dict[str, Any]]:
        return db.categories.get_custom_categories(self.current_user, category_type)

    def save_custom_category(self, category_type: str, name: str, icon_name: str, category_id: int | None = None) -> int:
        """Return 0 on success; 1 invalid name, 2 invalid icon, 3 duplicate, or -1 on save failure."""
        name = name.strip()
        if not name or len(name) > 40:
            return 1
        if icon_name not in self.data.get_category_icons():
            return 2

        default_names = {
            default_name.casefold()
            for default_name in self.data.get_default_category_aliases(
                self.lang
            )
        }
        if name.casefold() in default_names:
            return 3

        categories = self.get_default_categories(category_type) + self.get_custom_categories(category_type)
        for category in categories:
            is_same_category = (
                category_id is not None and category.get("id") == category_id
            )
            if category["name"].casefold() == name.casefold() and not is_same_category:
                return 3

        if category_id is None:
            saved = db.categories.add_custom_category(
                self.current_user, category_type, name, icon_name
            )
        else:
            saved = db.categories.update_custom_category(
                self.current_user,
                category_id,
                category_type,
                name,
                icon_name
            )
        return 0 if saved else -1

    def get_category_transaction_count(self, category_type: str, name: str) -> int:
        return db.categories.get_category_transaction_count(
            self.current_user, category_type, name
        )

    def delete_custom_category(self, category_id: int, category_type: str) -> bool:
        return db.categories.delete_custom_category(
            self.current_user, category_id, category_type
        )

    def add_income_entry(self, vals: dict[str, Any]) -> int:
        """
        Return values:
        0: saved; 1: missing amount/category; 2: amount is not positive;
        3: invalid amount; -1: failed to save.
        """
        amount = vals.get("amount", "0")
        category = vals.get("category")
        note = vals.get("note", "")

        time = vals.get("date")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return 1

        try:
            amount_val = to_decimal(amount)
            if amount_val <= 0:
                return 2
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return 3

        if db.spending.add_income_entry(self.current_user, amount_val, category, time, note):
            return 0

        return -1

    def add_expense_entry(self, vals: dict[str, Any]) -> int:
        """
        Return values:
        0: saved; 1: missing amount/category; 2: amount is not positive;
        3: invalid amount; -1: failed to save.
        """
        amount = vals.get("amount", "0")
        category = vals.get("category")
        note = vals.get("note", "")
        time = vals.get("date")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return 1

        try:
            amount_val = to_decimal(amount)
            if amount_val <= 0:
                return 2
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return 3

        if db.spending.add_expense_entry(self.current_user, amount_val, category, time, note):
            return 0

        return -1
