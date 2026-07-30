# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from types import NoneType

import openpyxl

from src.database import db


class LogicController:
    def __init__(self, current_user: str):
        self.current_user = current_user

    def get_dashboard_totals(self) -> tuple[float, float, float, str]:
        total_savings = db.saving.get_total_savings(self.current_user)
        total_target = db.saving.get_total_target_amount(self.current_user)

        if total_target > 0:
            progress_value = min(total_savings / total_target, 1.0)
            percentage = f"{(float(progress_value) * 100):.2f}%"
        else:
            progress_value = 1.0
            percentage = "100%"
        return total_savings, total_target, progress_value, percentage

    def get_user_objectives(self):
        return db.saving.get_user_objectives(self.current_user)

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

    def get_recent_activity(self, lang: dict):
        activities = db.saving.get_user_activity_raw(self.current_user)
        for item in activities:
            if item["type"] == "saving":
                target = item.get("target_name")
                if target:
                    action = lang["saving.added_to"] if item.get("amount", 0) > 0 else lang["saving.removed_from"]
                    item["desc"] = f"{action} {target}"
                else:
                    item["desc"] = f"{lang['saving.transaction']} ({item.get('amount'):,} VND)"

            match item["type"]:
                case "completed":
                    item["desc"] = f"{lang['saving.completed_objective']} {item.get('title')}"
                case "deleted":
                    item["desc"] = f"{lang['saving.deleted_objective']} {item.get('title')}"
                case "objective":
                    item["desc"] = f"{lang['saving.created_objective']} {item.get('title')}"

            if len(item.get("date", "")) > 16:
                item["date"] = item["date"][:16]
        return activities

    def add_new_objective(self, title: str, reason: str, target_amount: int) -> bool:
        return db.saving.add_objective(self.current_user, title, reason, target_amount)

    @staticmethod
    def complete_objective(objective_id: int):
        db.saving.complete_objective(objective_id)

    @staticmethod
    def delete_objective(objective_id: int):
        db.saving.delete_objective(objective_id)

    def process_quick_action(self, objective_id: int, action: str, amount: int, note: str, time: str) -> tuple[bool, str]:
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

    def clear_activity_history(self):
        db.saving.clear_activity_history(self.current_user)

    def export_ledger_to_excel(self, file_path: str, lang: dict) -> tuple[bool, str]:
        activities = self.get_recent_activity(lang)
        try:
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            if isinstance(worksheet, NoneType): raise RuntimeError(worksheet)
            worksheet.title = lang["saving.savings_ledger"]
            worksheet.append([lang["generic.date"], lang["saving.ledger.action_type"], lang["saving.ledger.description"]])
            for activity in activities:
                worksheet.append([activity["date"], activity["type"], activity["desc"]])
            workbook.save(file_path)
            return True, ""
        except Exception as error:
            return False, str(error)