# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from __future__ import annotations

from datetime import datetime

from src.database import db
from src.logger import Logger
from src.pages.global_components.financial_chart import get_financial_chart_data


class LogicController:
    """Business logic for the Spending page."""

    def __init__(self, current_user: str):
        self.current_user = current_user

    def get_transaction_data(self) -> tuple[dict, dict]:
        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = sum(int(item.get("amount", 0)) for item in incomes)
        total_expense = sum(int(item.get("amount", 0)) for item in expenses)
        net_balance = total_income - total_expense

        balance_data = {
            "incomes": f"+{total_income:,} VND",
            "expenses": f"-{total_expense:,} VND",
            "current": f"{net_balance:,} VND",
        }

        transactions: dict[str, list[dict]] = {}
        for item in incomes:
            tx = {
                "id": item.get("id"),
                "title": item.get("category", "Lương"),
                "subtitle": item.get("note") or "",
                "amount": int(item.get("amount", 0)),
                "date": item.get("date", ""),
                "positive": True,
            }
            transactions.setdefault(str(tx["date"])[:10], []).append(tx)

        for item in expenses:
            tx = {
                "id": item.get("id"),
                "title": item.get("category", "Khác"),
                "subtitle": item.get("note") or "",
                "amount": int(item.get("amount", 0)),
                "date": item.get("date", ""),
                "positive": False,
            }
            transactions.setdefault(str(tx["date"])[:10], []).append(tx)

        for day_key in transactions:
            transactions[day_key].sort(key=lambda tx: str(tx.get("date", "")), reverse=True)

        return balance_data, transactions

    def get_dashboard_data(self, chart_type: str = "daily", date_offset: int = 0, target_year: int | None = None) -> tuple[dict, list, str]:
        chart_date, chart_data = get_financial_chart_data(
            username=self.current_user,
            chart_type=chart_type,
            date_offset=date_offset,
            target_year=target_year,
        )
        return chart_date, chart_data, chart_type

    def filter_transactions(self, raw_transactions: dict, filter_type: str, selected_category: str, search_query: str) -> list:
        filtered: list[dict] = []
        query = (search_query or "").strip().lower()

        for txs in raw_transactions.values():
            for tx in txs:
                if filter_type != "all":
                    is_income = bool(tx.get("positive"))
                    if filter_type == "income" and not is_income:
                        continue
                    if filter_type == "expense" and is_income:
                        continue

                category_name = str(tx.get("title", ""))
                if selected_category not in ("all", "") and category_name != selected_category:
                    continue

                if query:
                    haystack = f"{category_name} {tx.get('subtitle', '')}".lower()
                    if query not in haystack:
                        continue

                filtered.append(tx)

        filtered.sort(key=lambda tx: str(tx.get("date", "")), reverse=True)
        return filtered

    def delete_transaction(self, transaction_id: int) -> bool:
        try:
            return db.spending.delete_entry(self.current_user, int(transaction_id))
        except (TypeError, ValueError):
            Logger.warning(f"Invalid transaction id: {transaction_id}")
            return False

    def add_income_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", "0")
        category = vals.get("category")
        note = vals.get("note", "")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "home.error.missing_amount_category"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "home.error.amount_less_than_zero"
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return False, "home.error.invalid_amount"

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_income_entry(self.current_user, amount_val, category, date, note):
            return True, "spending.income_added_success"
        return False, "home.error.save_income_failed"

    def add_expense_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", "0")
        category = vals.get("category")
        note = vals.get("note", "")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "home.error.missing_amount_category"

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "home.error.amount_less_than_zero"
        except (TypeError, ValueError):
            Logger.error("Invalid amount provided")
            return False, "home.error.invalid_amount"

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_expense_entry(self.current_user, amount_val, category, date, note):
            return True, "spending.expense_added_success"
        return False, "home.error.save_expense_failed"


__all__ = ["LogicController"]
