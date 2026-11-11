# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from io import BytesIO
from decimal import Decimal
from typing import Any

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from src.database import db
from src.pages.common.logic import get_user_currency
from src.utils import format_number


class LogicController:
    def __init__(self, current_user: str) -> None:
        self.current_user = current_user

    def get_currency(self) -> str:
        return get_user_currency(self.current_user)

    def get_dashboard_totals(self) -> tuple[Decimal, Decimal, float, str]:
        total_savings = db.savings.get_total_savings(self.current_user)
        total_target = db.savings.get_total_target_amount(self.current_user)

        if total_target > 0:
            progress_value = float(min(total_savings / total_target, Decimal(1)))
            percentage = f"{(int(progress_value * 100))}%"
        else:
            progress_value = 1.0
            percentage = "--%"
        return total_savings, total_target, progress_value, percentage

    def get_user_objectives(self) -> list[tuple[int, str, str | None, Decimal, str | None]]:
        return db.savings.get_user_objectives(self.current_user)

    @staticmethod
    def get_objective_progress_data(objective_id: int, target_amount: Decimal) -> tuple[Decimal, float, str]:
        objective_savings = db.savings.get_objective_progress(objective_id)
        if target_amount > 0:
            raw_progress = objective_savings / target_amount
            progress_value = float(min(raw_progress, Decimal(1)))
            percentage = f"{int(progress_value * 100)}%"
        else:
            progress_value = 1.0
            percentage = "100%"
        return objective_savings, progress_value, percentage

    @staticmethod
    def get_objective_amounts(objective_id: int) -> tuple[Decimal, Decimal]:
        current = db.savings.get_objective_progress(objective_id)
        target = db.savings.get_objective_target(objective_id)
        return current, target

    def get_recent_activity(self, lang: dict[str, str]) -> list[dict[str, Any]]:
        activities = db.savings.get_user_activity_raw(self.current_user)
        currency = self.get_currency()
        for item in activities:
            if item["type"] in ("saving", "savings"):
                item["type"] = "saving"
                target = item.get("target_name")
                if target:
                    action = (
                        lang["savings.added_to"]
                        if item.get("amount", 0) > 0
                        else lang["savings.removed_from"]
                    )
                    item["desc"] = f"{action} {target}"
                else:
                    item["desc"] = f"{lang['savings.transaction']} ({format_number(item.get('amount'))} {currency})"

            match item["type"]:
                case "completed":
                    item["desc"] = (
                        f"{lang['savings.completed_objective']} {item.get('title')}"
                    )
                case "deleted":
                    item["desc"] = (
                        f"{lang['savings.deleted_objective']} {item.get('title')}"
                    )
                case "objective":
                    item["desc"] = (
                        f"{lang['savings.created_objective']} {item.get('title')}"
                    )

            if len(item.get("date", "")) > 16:
                item["date"] = item["date"][:16]
        return activities

    def add_new_objective(self, title: str, reason: str, target_amount: Decimal) -> bool:
        return db.savings.add_objective(self.current_user, title, reason, target_amount)

    def create_goal_with_surplus(self, title: str, reason: str, target_amount: Decimal, surplus_amount: Decimal) -> bool:
        return db.savings.create_goal_with_initial_deposit(
            self.current_user, title, reason, target_amount, surplus_amount
        )

    def transfer_surplus(self, source_id: int, target_id: int, amount: Decimal) -> tuple[bool, Decimal]:
        current_saved, target_amount = self.get_objective_amounts(target_id)
        amount_to_transfer = min(amount, max(Decimal(0), target_amount - current_saved))
        remaining_surplus = amount - amount_to_transfer
        success = db.savings.transfer_surplus(
            self.current_user,
            source_id,
            target_id,
            amount_to_transfer
        )
        return success, remaining_surplus if success else Decimal(0)

    @staticmethod
    def delete_objective(objective_id: int) -> None:
        db.savings.delete_objective(objective_id)

    def process_quick_action(self, objective_id: int, action: str, amount: Decimal, time: str, note: str = '') -> tuple[bool, str, Decimal, Decimal, bool]:
        current_saved = db.savings.get_objective_progress(objective_id)
        target = db.savings.get_objective_target(objective_id)
        surplus = Decimal(0)
        reached_target = False

        if action in ("remove", "withdraw"):
            if amount > current_saved:
                return False, "savings.error.not_enough_balance", current_saved, Decimal(0), False
            amount = -amount
        else:
            remaining = max(Decimal(0), target - current_saved)
            reached_target = amount >= remaining
            if amount > remaining:
                surplus = amount - remaining
                amount = remaining

        if not db.savings.add_saving_entry(self.current_user, amount, time, objective_id, note):
            return False, "savings.error.action_failed", current_saved, Decimal(0), False

        return True, "", current_saved + amount, surplus, reached_target

    def clear_activity_history(self) -> None:
        db.users.clear_activity_history(self.current_user)

    def get_ledger_excel_bytes(self, lang: dict[str, str]) -> tuple[bytes | None, str]:
        activities = self.get_recent_activity(lang)
        try:
            workbook = openpyxl.Workbook()
            worksheet: Worksheet = workbook.active or workbook.create_sheet()
            worksheet.title = lang["savings.savings_ledger"]
            worksheet.append(
                [
                    lang["generic.date"],
                    lang["savings.ledger.action_type"],
                    lang["savings.ledger.description"]
                ]
            )
            for activity in activities:
                worksheet.append(
                    [
                        activity["date"],
                        lang[f"savings.activity.{activity['type']}"],
                        activity["desc"]
                    ]
                )
            output = BytesIO()
            workbook.save(output)
        except (AttributeError, KeyError, OSError, TypeError, ValueError) as error:
            return None, str(error)
        else:
            return output.getvalue(), ""

    def export_ledger_to_excel(self, file_path: str, lang: dict[str, str]) -> tuple[bool, str]:
        data, error = self.get_ledger_excel_bytes(lang)
        if data is None:
            return False, error
        try:
            with open(file_path, "wb") as file:
                file.write(data)
        except OSError as error:
            return False, str(error)
        else:
            return True, ""
