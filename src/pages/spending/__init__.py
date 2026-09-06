# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Spending page - Financial metrics, transaction tracking, and filters."""

from src.pages.spending.components import MetricCards, TransactionToolbar, TransactionItemCard
from src.pages.spending.logic import LogicController
from src.pages.spending.view import DialogManager, SpendingView, get_spending_view

__all__ = [
    "MetricCards",
    "TransactionToolbar",
    "TransactionItemCard",
    "LogicController",
    "DialogManager",
    "SpendingView",
    "get_spending_view"
]