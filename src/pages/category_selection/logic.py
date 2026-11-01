# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.database import db
from src.logger import Logger
from src.utils import Data


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user
        self.data = Data()

    def get_default_categories(self, category_type: str) -> list[dict]:
        if category_type == "expense":
            return self.data.default_expense_categories
        return self.data.default_income_categories

    def get_custom_categories(self, category_type: str) -> list[dict]:
        return db.categories.get_custom_categories(self.current_user, category_type)

    def save_custom_category(
        self,
        category_type: str,
        name: str,
        icon_name: str,
        category_id: int | None = None,
    ) -> tuple[bool, str]:
        name = name.strip()
        if not name or len(name) > 40:
            return False, "INVALID_NAME"
        if icon_name not in self.data.category_icons:
            return False, "INVALID_ICON"

        categories = (
            self.get_default_categories(category_type)
            + self.get_custom_categories(category_type)
        )
        for category in categories:
            is_same_category = (
                category_id is not None
                and category.get("id") == category_id
            )
            if (
                category["name"].casefold() == name.casefold()
                and not is_same_category
            ):
                return False, "DUPLICATE_NAME"

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
                icon_name,
            )
        return (True, "") if saved else (False, "SAVE_FAILED")

    def get_category_transaction_count(
        self, category_type: str, name: str
    ) -> int:
        return db.categories.get_category_transaction_count(
            self.current_user, category_type, name
        )

    def delete_custom_category(
        self, category_id: int, category_type: str
    ) -> bool:
        return db.categories.delete_custom_category(
            self.current_user, category_id, category_type
        )

    def add_income_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")

        time = vals.get("date")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "MISSING_AMOUNT_CATEGORY"

        try:
            amount_val = float(amount)
            if amount_val <= 0.0:
                return False, "AMOUNT_LESS_THAN_ZERO"
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return False, "INVALID_AMOUNT"

        if db.spending.add_income_entry(self.current_user, amount_val, category, time, note):
            return True, "INCOME_ADDED_SUCCESS"
        return False, "SAVE_INCOME_FAILED"

    def add_expense_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")
        time = vals.get("date")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "MISSING_AMOUNT_CATEGORY"

        try:
            amount_val = float(amount)
            if amount_val <= 0.0:
                return False, "AMOUNT_LESS_THAN_ZERO"
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return False, "INVALID_AMOUNT"

        if db.spending.add_expense_entry(self.current_user, amount_val, category, time, note):
            return True, "EXPENSE_ADDED_SUCCESS"
        return False, "SAVE_EXPENSE_FAILED"