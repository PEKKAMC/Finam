# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Saving page - Objective tracking and portfolio management."""

from src.pages.saving.view import SavingView, get_savings_view
from src.pages.saving.logic import LogicController
from src.pages.saving.components import ObjectiveCard, ObjectiveGrid, AggregateCard, ActivityListTile, ActivityHistoryBoard

__all__ = [
    "SavingView",
    "get_savings_view",
    "LogicController",
    "ObjectiveCard",
    "ObjectiveGrid",
    "AggregateCard",
    "ActivityListTile",
    "ActivityHistoryBoard"
]