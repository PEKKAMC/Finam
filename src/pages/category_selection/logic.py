# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime

from src.database import db
from src.logger import Logger


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    def add_income_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")
        selected_date = vals.get("date") or datetime.now().strftime("%Y-%m-%d")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "MISSING_AMOUNT_CATEGORY"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "AMOUNT_LESS_THAN_ZERO"
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "INVALID_AMOUNT"

        date = f"{selected_date} 00:00"
        if db.spending.add_income_entry(self.current_user, amount_val, category, date, note):
            return True, "INCOME_ADDED_SUCCESS"
        return False, "SAVE_INCOME_FAILED"

    def add_expense_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")
        selected_date = vals.get("date") or datetime.now().strftime("%Y-%m-%d")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "MISSING_AMOUNT_CATEGORY"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "AMOUNT_LESS_THAN_ZERO"
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "INVALID_AMOUNT"

        date = f"{selected_date} 00:00"
        if db.spending.add_expense_entry(self.current_user, amount_val, category, date, note):
            return True, "EXPENSE_ADDED_SUCCESS"
        return False, "SAVE_EXPENSE_FAILED"