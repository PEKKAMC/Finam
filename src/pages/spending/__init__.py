# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Spending page - Financial metrics, transaction tracking, and filters."""

from src.pages.spending.view import SpendingView, get_spending_view
from src.pages.spending.logic import LogicController
from src.pages.spending.components import MetricCards, TransactionToolbar, TransactionItemCard

__all__ = [
    "SpendingView",
    "get_spending_view",
    "LogicController",
    "MetricCards",
    "TransactionToolbar",
    "TransactionItemCard"
]