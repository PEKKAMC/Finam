# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime, timedelta

import flet as ft

from src.database import db
from src.logger import Logger
from src.utils import Text


class LogicController:
    def __init__(self, current_user: str, page: ft.Page, lang: dict, user_info: dict, refresh_callback):
        self.cached_expenses = None
        self.cached_incomes = None
        self.page = page
        self.lang = lang
        self.current_user = current_user
        self.user_info = user_info
        self.refresh_callback = refresh_callback

        self.current_chart_type = "daily"
        self.current_category_type = None

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

    def get_dashboard_data(self):
        now = datetime.now()
        iso_year, iso_week, iso_day = now.isocalendar()

        chart_date = {"month": now.month, "year": now.year, "week": iso_week}
        chart_data = []

        if self.current_chart_type == "daily":
            chart_data = [{"day": i + 1, "income": 0, "expense": 0} for i in range(7)]
        elif self.current_chart_type == "weekly":
            chart_data = [{"week": i + 1, "income": 0, "expense": 0} for i in range(4)]
        elif self.current_chart_type == "monthly":
            chart_data = [{"month": i + 1, "income": 0, "expense": 0} for i in range(12)]

        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

        expenses = getattr(self, 'cached_expenses', None) or db.spending.get_user_expenses(self.current_user)
        incomes = getattr(self, 'cached_incomes', None) or db.spending.get_user_incomes(self.current_user)

        try:
            for expense in expenses:
                try:
                    exp_date = datetime.strptime(str(expense["date"])[:16], "%Y-%m-%d %H:%M")
                    if self.current_chart_type == "daily" and start_of_week <= exp_date <= end_of_week:
                        chart_data[exp_date.weekday()]["expense"] += expense["amount"]
                    elif self.current_chart_type == "weekly" and exp_date.year == now.year and exp_date.month == now.month:
                        week_of_month = min((exp_date.day - 1) // 7, 3)
                        chart_data[week_of_month]["expense"] += expense["amount"]
                    elif self.current_chart_type == "monthly" and exp_date.year == now.year:
                        chart_data[exp_date.month - 1]["expense"] += expense["amount"]
                except (ValueError, TypeError): pass

            for income in incomes:
                try:
                    inc_date = datetime.strptime(str(income["date"])[:16], "%Y-%m-%d %H:%M")
                    if self.current_chart_type == "daily" and start_of_week <= inc_date <= end_of_week:
                        chart_data[inc_date.weekday()]["income"] += income["amount"]
                    elif self.current_chart_type == "weekly" and inc_date.year == now.year and inc_date.month == now.month:
                        week_of_month = min((inc_date.day - 1) // 7, 3)
                        chart_data[week_of_month]["income"] += income["amount"]
                    elif self.current_chart_type == "monthly" and inc_date.year == now.year:
                        chart_data[inc_date.month - 1]["income"] += income["amount"]
                except (ValueError, TypeError): pass
        except Exception as e:
            Logger.error(f"Error formatting dashboard data: {e}")

        return chart_date, chart_data, self.current_chart_type

    def get_transaction_data(self):
        username = self.user_info.get("username")
        total_incomes = db.spending.get_total_income(username)
        total_expenses = db.spending.get_total_expense(username)
        current_balance = total_incomes - total_expenses

        balance_data = {
            "current": f"{current_balance:,} VND",
            "growth": "Active",
            "incomes": f"+{total_incomes:,} VND",
            "expenses": f"-{total_expenses:,} VND"
        }

        expenses = db.spending.get_user_expenses(username)
        incomes = db.spending.get_user_incomes(username)
        self.cached_expenses = expenses
        self.cached_incomes = incomes

        transactions = {}
        combined_list = []
        for expense in expenses:
            combined_list.append({"id": expense["id"], "date": expense["date"], "title": expense["category"], "subtitle": expense["note"] if expense["note"] else "Expense", "amount": expense["amount"], "is_income": False})
        for income in incomes:
            combined_list.append({"id": income["id"], "date": income["date"], "title": income["category"], "subtitle": income.get("note", ""), "amount": income.get("amount", 0), "is_income": True})

        combined_list.sort(key=lambda x: x["date"], reverse=True)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        for item in combined_list:
            try:
                item_date = datetime.strptime(item["date"][:16] if len(item["date"]) > 16 else item["date"], "%Y-%m-%d %H:%M").date()
                if item_date == today: date_key = "TODAY"
                elif item_date == yesterday: date_key = "YESTERDAY"
                else: date_key = item_date.strftime("%b %d").upper()
            except ValueError:
                date_key = "UNKNOWN DATE"

            if date_key not in transactions: transactions[date_key] = []
            title, subtitle = item["title"], item["subtitle"]
            icon = ft.Icons.ACCOUNT_BALANCE

            transactions[date_key].append({
                "id": item["id"],
                "title": title, "subtitle": subtitle,
                "amount": f"+{item['amount']:,} VND" if item["is_income"] else f"-{item['amount']:,} VND",
                "icon": icon, "positive": item["is_income"]
            })

        return balance_data, transactions

    def delete_transaction(self, transaction_id):
        """Deletes an expense or income entry by ID."""
        username = self.user_info.get("username")
        try:
            # Attempt to delete from both tables or handle based on ID type
            success = db.spending.delete_entry(username, transaction_id)
            if success:
                if self.refresh_callback:
                    self.refresh_callback()
                self.page.snack_bar = ft.SnackBar(Text.MEDIUM("Xóa giao dịch thành công!"))
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as e:
            Logger.error(f"Error deleting transaction: {e}")