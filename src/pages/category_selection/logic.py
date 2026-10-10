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

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "home.error.missing_amount_category"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "home.error.amount_less_than_zero"
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "home.error.invalid_amount"

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_income_entry(self.current_user, amount_val, category, date, note):
            return True, "spending.income_added_success"
        return False, "home.error.save_income_failed"

    def add_expense_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "home.error.missing_amount_category"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "home.error.amount_less_than_zero"
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "home.error.invalid_amount"

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_expense_entry(self.current_user, amount_val, category, date, note):
            return True, "spending.expense_added_success"
        return False, "home.error.save_expense_failed"