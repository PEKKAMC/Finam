# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import datetime
from decimal import Decimal

from src.database import db


def get_financial_chart_data(username: str, chart_type: str = "daily", date_offset: int = 0, target_year: int | None = None) -> tuple[dict[str, int], list[dict[str, Decimal | int]]]:
    """Fetch and aggregate database totals for the requested chart period."""
    now = datetime.datetime.now()

    if chart_type == "daily":
        target_date = now + datetime.timedelta(weeks=date_offset)
    elif chart_type == "weekly":
        total_months = (now.year * 12 + (now.month - 1)) + date_offset
        year = total_months // 12
        month = (total_months % 12) + 1
        target_date = now.replace(year=year, month=month, day=1)
    elif chart_type == "monthly":
        year = target_year if target_year is not None else now.year
        month = now.month if year == now.year else 1
        target_date = now.replace(year=year, month=month, day=1)
    else:
        target_date = now

    _, iso_week, _ = target_date.isocalendar()
    chart_date = {
        "month": target_date.month,
        "year": target_date.year,
        "week": iso_week,
    }

    if chart_type == "daily":
        chart_data = [{"day": index + 1, "income": Decimal(0), "expense": Decimal(0)} for index in range(7)]
        start_date = (
            target_date - datetime.timedelta(days=target_date.weekday())
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + datetime.timedelta(days=7)
    elif chart_type == "weekly":
        chart_data = [{"week": index + 1, "income": Decimal(0), "expense": Decimal(0)} for index in range(4)]
        start_date = target_date.replace(day=1)
        end_date = (start_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    elif chart_type == "monthly":
        chart_data = [{"month": index + 1, "income": Decimal(0), "expense": Decimal(0)} for index in range(12)]
        start_date = target_date.replace(year=target_date.year, month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")

    totals = db.spending.get_user_chart_totals(
        username,
        chart_type,
        start_date.strftime("%Y-%m-%d %H:%M"),
        end_date.strftime("%Y-%m-%d %H:%M"),
    )
    for bucket, kind, amount in totals:
        if bucket is not None and 0 <= bucket < len(chart_data):
            chart_data[bucket][kind] = Decimal(amount or "0")

    return chart_date, chart_data
