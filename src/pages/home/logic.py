# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from typing import NamedTuple, TypedDict

from src.database import db
from src.logger import Logger
from src.pages.common.logic import get_user_currency
from src.utils import Data, format_number


MAX_SAVINGS_GOALS_ON_HOME = 3
MINIMUM_GOAL_TARGET = 1.0


class SavingsObjective(NamedTuple):
    objective_id: int
    title: str | None
    reason: str | None
    target_amount: float
    completed_at: str | None


class DashboardData(TypedDict):
    total_income: float
    total_expense: float
    net_balance: float
    total_savings: float
    total_target: float
    category_expenses: dict[str, float]


class SavingsProgressItem(TypedDict):
    id: int
    title: str
    current_amount: float
    target_amount: float
    progress_ratio: float
    progress_text: str
    completed: bool
    contributed_label: str
    target_label: str


class LogicController:
    def __init__(self, current_user: str) -> None:
        self.current_user = current_user

    def get_currency(self) -> str:
        return get_user_currency(self.current_user)

    def get_dashboard_data(self) -> DashboardData:
        Logger.info("Loading dashboard data...")
        total_savings = db.savings.get_total_savings(self.current_user)
        total_target = db.savings.get_total_target_amount(self.current_user)

        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = 0.0
        total_expense = 0.0
        category_expenses: dict[str, float] = {}

        for expense in expenses:
            amount = float(expense.get("amount", 0))
            category = str(expense.get("category") or "")
            total_expense += amount
            category_expenses[category] = category_expenses.get(category, 0.0) + amount

        for income in incomes:
            total_income += float(income.get("amount", 0))

        net_balance = total_income - total_expense

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "total_savings": total_savings,
            "total_target": total_target,
            "category_expenses": category_expenses
        }

    def get_advice(self) -> str:
        return Data().get_advice(db.users.get_language(self.current_user))

    def get_user_objectives(self) -> list[SavingsObjective]:
        return [
            SavingsObjective(*objective)
            for objective in db.savings.get_user_objectives(self.current_user)
        ]

    @staticmethod
    def get_saving_progress_items(objectives: list[SavingsObjective], lang: dict[str, str], currency: str = "") -> tuple[list[SavingsProgressItem], int]:
        goal_items: list[SavingsProgressItem] = []
        if not objectives:
            return goal_items, 0

        for objective in objectives[:MAX_SAVINGS_GOALS_ON_HOME]:
            current_amount = float(
                db.savings.get_objective_progress(objective.objective_id)
            )
            target_value = max(
                float(objective.target_amount or 0),
                MINIMUM_GOAL_TARGET,
            )

            # Keep progress calculations defined for goals without a target.
            progress_ratio = min(1.0, current_amount / target_value)
            display_title = objective.title or lang["home.default_goal_title"]

            goal_items.append({
                "id": objective.objective_id,
                "title": display_title,
                "current_amount": current_amount,
                "target_amount": target_value,
                "progress_ratio": progress_ratio,
                "progress_text": f"{int(progress_ratio * 100)}%",
                "completed": objective.completed_at is not None,
                "contributed_label": f"{lang['home.contributed']}: {format_number(current_amount)} {currency}",
                "target_label": f"{lang['home.target']}: {format_number(target_value)} {currency}",
            })

        return goal_items, len(objectives)