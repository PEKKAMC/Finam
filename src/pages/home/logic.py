# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.database import db
from src.logger import Logger
from src.utils import Data


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    def get_dashboard_data(self) -> dict:
        Logger.info("Loading dashboard data...")
        total_savings = db.savings.get_total_savings(self.current_user)
        total_target = db.savings.get_total_target_amount(self.current_user)

        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = 0.0
        total_expense = 0.0
        category_expenses = {}

        try:
            for expense in expenses:
                amount = float(expense.get("amount", 0))
                category = expense["category"]
                total_expense += amount
                category_expenses[category] = category_expenses.get(category, 0) + amount

            for income in incomes:
                amount = float(income.get("amount", 0))
                total_income += amount

        except Exception as ex:
            Logger.error(f"Error formatting dashboard data: {ex}")

        net_balance = total_income - total_expense

        data = {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "total_savings": total_savings,
            "total_target": total_target,
            "category_expenses": category_expenses
        }

        return data

    def get_advice(self) -> str:
        return Data().get_advice(db.users.get_language(self.current_user))

    def get_user_objectives(self):
        return db.savings.get_user_objectives(self.current_user)

    @staticmethod
    def get_saving_progress_items(objectives: list, lang: dict, username: str = "") -> tuple[list, int]:
        goal_items = []
        if not objectives:
            return goal_items, 0

        currency = db.users.get_currency(username)

        for objective in objectives[:3]:
            objective_id, objective_title, objective_reason, target_amount, completed_at = objective
            current_amount = float(db.savings.get_objective_progress(objective_id))
            target_value = float(target_amount) if target_amount and float(target_amount) > 0 else 1.0
            progress_ratio = min(1.0, current_amount / target_value) if target_value > 0 else 1.0
            display_title = objective_title if objective_title else lang["home.default_goal_title"]

            goal_items.append({
                "id": objective_id,
                "title": display_title,
                "current_amount": current_amount,
                "target_amount": target_value,
                "progress_ratio": progress_ratio,
                "progress_text": f"{int(progress_ratio * 100)}%",
                "contributed_label": f"{lang['home.contributed']}: {current_amount:,.2f} {currency}",
                "target_label": f"{lang['home.target']}: {target_value:,.2f} {currency}",
            })

        return goal_items, len(objectives)
