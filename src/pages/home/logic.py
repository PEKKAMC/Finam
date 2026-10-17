# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.database import db
from src.logger import Logger


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    def get_dashboard_data(self) -> dict:
        Logger.info("Loading dashboard data...")
        total_savings = db.savings.get_total_savings(self.current_user)
        total_target = db.savings.get_total_target_amount(self.current_user)

        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = 0
        total_expense = 0
        category_expenses = {}

        try:
            for expense in expenses:
                amount = int(expense.get("amount", 0))
                category = expense.get("category", "Khác")
                total_expense += amount
                category_expenses[category] = category_expenses.get(category, 0) + amount

            for income in incomes:
                amount = int(income.get("amount", 0))
                total_income += amount

        except Exception as e:
            Logger.error(f"Error formatting dashboard data: {e}")

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

    @staticmethod # Temporary static messages until AI integration is implemented
    def get_ai_advice(net_balance: float, total_income: float, total_expense: float) -> str:
        if total_income == 0 and total_expense == 0:
            return "Hãy bắt đầu ghi chép các khoản thu chi hàng ngày để Finam AI phân tích sức khỏe tài chính cho bạn!"
        if net_balance < 0:
            return "Cảnh báo: Chi tiêu đang vượt quá thu nhập! Hãy cắt giảm các khoản mua sắm không thiết yếu."
        return "Hãy đảm bảo bạn trích ít nhất 10-20% thu nhập hàng tháng cho quỹ tiết kiệm khẩn cấp!"

    def get_user_objectives(self):
        return db.savings.get_user_objectives(self.current_user)

    @staticmethod
    def get_saving_progress_items(objectives: list, lang: dict, username: str = ""):
        goal_items = []
        if not objectives:
            return goal_items

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
                "contributed_label": f"{lang['home.contributed']}: {int(current_amount):,} {currency}",
                "target_label": f"{lang['home.target']}: {int(target_value):,} {currency}",
            })

        return goal_items
