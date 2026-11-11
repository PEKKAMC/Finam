# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Savings page - Objective tracking and portfolio management."""

from src.pages.savings.components import ActivityHistory, AggregateCard, ClearHistoryDialog, CongratulationsDialog, CreateGoalDialog, DeleteConfirmDialog, DepositWithdrawDialog, GoalCard, GoalGrid
from src.pages.savings.logic import LogicController
from src.pages.savings.view import DialogManager, SavingsView, get_savings_view

__all__ = [
    "ActivityHistory",
    "AggregateCard",
    "ClearHistoryDialog",
    "CongratulationsDialog",
    "CreateGoalDialog",
    "DeleteConfirmDialog",
    "DepositWithdrawDialog",
    "DialogManager",
    "GoalCard",
    "GoalGrid",
    "LogicController",
    "SavingsView",
    "get_savings_view"
]
