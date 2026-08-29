# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime

from src.database import db
from src.logger import Logger


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    def get_dashboard_data(self):
        Logger.info("Loading dashboard & chart data...")
        total_savings = db.saving.get_total_savings(self.current_user)
        total_target = db.saving.get_total_target_amount(self.current_user)
        now = datetime.now()
        chart_date = {"month": now.month, "year": now.year, "week": now.isocalendar().week}
        chart_data = [{"day": i + 1, "income": 0, "expense": 0} for i in range(7)]

        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = 0
        total_expense = 0
        category_expenses = {} # Add this dictionary to map categories

        try:
            for expense in expenses:
                amount = int(expense.get("amount", 0))
                category = expense.get("category", "Khác")
                total_expense += amount

                # Aggregate for the Pie Chart
                category_expenses[category] = category_expenses.get(category, 0) + amount

                exp_date = datetime.strptime(str(expense["date"])[:16], "%Y-%m-%d %H:%M")
                chart_data[exp_date.weekday()]["expense"] += amount

            for income in incomes:
                amount = int(income.get("amount", 0))
                total_income += amount
                inc_date = datetime.strptime(str(income["date"])[:16], "%Y-%m-%d %H:%M")
                chart_data[inc_date.weekday()]["income"] += amount

        except Exception as e:
            Logger.error(f"Error formatting dashboard data: {e}")

        net_balance = total_income - total_expense

        metrics = {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "total_savings": total_savings,
            "total_target": total_target,
            "category_expenses": category_expenses
        }

        return metrics, chart_date, chart_data, "daily"

    @staticmethod
    def get_ai_advice(net_balance: float, total_income: float, total_expense: float) -> str:
        if total_income == 0 and total_expense == 0:
            return "Hãy bắt đầu ghi chép các khoản thu chi hàng ngày để Finam AI phân tích sức khỏe tài chính cho bạn!"
        if net_balance < 0:
            return "Cảnh báo: Chi tiêu đang vượt quá thu nhập! Hãy cắt giảm các khoản mua sắm không thiết yếu."
        return "Hãy đảm bảo bạn trích ít nhất 10-20% thu nhập hàng tháng cho quỹ tiết kiệm khẩn cấp!"

    def add_income_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "Vui lòng nhập đủ số tiền và danh mục."

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "Số tiền phải lớn hơn 0."
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "Số tiền không hợp lệ. Vui lòng nhập số."

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_income_entry(self.current_user, amount_val, category, date, note):
            return True, "Thu nhập đã được thêm thành công!"
        return False, "Đã xảy ra lỗi khi lưu thu nhập."

    def add_expense_entry(self, vals: dict) -> tuple[bool, str]:
        amount = vals.get("amount", '0')
        category = vals.get("category")
        note = vals.get("note", "")

        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return False, "Vui lòng nhập đủ số tiền và danh mục."

        try:
            amount_val = int(amount)
            if amount_val <= 0:
                return False, "Số tiền phải lớn hơn 0."
        except ValueError:
            Logger.error("Invalid amount provided")
            return False, "Số tiền không hợp lệ. Vui lòng nhập số."

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if db.spending.add_expense_entry(self.current_user, amount_val, category, date, note):
            return True, "Chi tiêu đã được thêm thành công!"
        return False, "Đã xảy ra lỗi khi lưu chi tiêu."

    def get_user_objectives(self):
        return db.saving.get_user_objectives(self.current_user)

    @staticmethod
    def get_saving_progress_items(objectives: list, lang: dict):
        goal_items = []
        if not objectives:
            return goal_items

        for objective in objectives[:3]:
            objective_id, objective_title, objective_reason, target_amount, completed_at = objective
            current_amount = float(db.saving.get_objective_progress(objective_id))
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
                "contributed_label": f"{lang['home.contributed']}: {int(current_amount):,} {lang['generic.currency']}",
                "target_label": f"{lang['home.target']}: {int(target_value):,} {lang['generic.currency']}",
            })

        return goal_items

    @staticmethod
    def get_objective_progress_data(objective_id: int, target_amount: float) -> tuple[float, float, str]:
        objective_savings = db.saving.get_objective_progress(objective_id)
        if target_amount > 0:
            raw_progress = objective_savings / target_amount
            progress_value = min(raw_progress, 1.0)
            percentage = f"{int(progress_value * 100)}%"
        else:
            progress_value = 1.0
            percentage = "100%"
        return objective_savings, progress_value, percentage

    @staticmethod
    def get_objective_history(objective_id: int):
        return db.saving.get_objective_activity(objective_id)

    def process_quick_action(self, objective_id: int, action: str, amount: int, time: str, note: str = "") -> tuple[bool, str]:
        current_saved = db.saving.get_objective_progress(objective_id)
        if action == "remove":
            if amount > current_saved:
                return False, "saving.error.not_enough_balance"
            amount = -amount
        else:
            remaining = db.saving.get_objective_target(objective_id) - current_saved
            if amount > remaining:
                return False, "saving.error.exceeding_amount"

        db.saving.add_saving_entry(self.current_user, amount, time, objective_id, note)
        return True, ""

    @staticmethod
    def complete_objective(objective_id: int):
        db.saving.complete_objective(objective_id)

    @staticmethod
    def delete_objective(objective_id: int):
        db.saving.delete_objective(objective_id)