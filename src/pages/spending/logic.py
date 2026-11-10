# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
from datetime import date
from typing import Any

import requests

from src.database import db
from src.logger import Logger
from src.pages.common.logic import get_user_currency
from src.utils import Data, format_display_number, get_language

BACKEND_URL = (
    os.getenv("FINAM_BACKEND_URL", "").strip() or "https://finam-backend.vercel.app/"
)
Transaction = dict[str, int | float | str | bool | None]
BalanceData = dict[str, str]
TransactionGroups = dict[str, list[Transaction]]
MIN_SPENDING_ANALYSIS_TRANSACTIONS = 10


class SpendingAnalysisApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class LogicController:
    """Business logic for the Spending page."""

    def __init__(self, current_user: str) -> None:
        self.current_user = current_user
        self.data = Data()
        self.lang = get_language(db.users.get_language(current_user))
        self.default_category_aliases = self.data.get_default_category_aliases(self.lang)

    @staticmethod
    def has_google_account_session() -> bool:
        return db.app_settings.has_google_account_session()

    @staticmethod
    def is_cached_developer() -> bool:
        return db.app_settings.is_cached_developer()

    @staticmethod
    def get_google_refresh_token() -> str | None:
        return db.app_settings.get_google_refresh_token()

    def get_category_icon_map(self) -> dict[str, str]:
        categories = (
            self.data.get_default_expense_categories(self.lang)
            + self.data.get_default_income_categories(self.lang)
            + db.categories.get_custom_categories(self.current_user, "expense")
            + db.categories.get_custom_categories(self.current_user, "income")
        )
        icons = {category["name"]: category["icon"] for category in categories}
        for name, category in self.default_category_aliases.items():
            icons[name] = category["icon"]
        return icons

    def get_transaction_data(self) -> tuple[BalanceData, TransactionGroups]:
        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = sum(float(item.get("amount", 0)) for item in incomes)
        total_expense = sum(float(item.get("amount", 0)) for item in expenses)
        net_balance = total_income - total_expense
        currency = get_user_currency(self.current_user)

        balance_data = {
            "incomes": f"+{format_display_number(total_income, self.lang)} {currency}",
            "expenses": f"-{format_display_number(total_expense, self.lang)} {currency}",
            "current": f"{format_display_number(net_balance, self.lang)} {currency}",
        }

        localized_incomes = self._localize_default_categories(incomes)
        localized_expenses = self._localize_default_categories(expenses)
        transactions = self._group_transactions(
            localized_incomes, True, self.lang["category_selection.defaults.income.salary"]
        )
        for date_key, daily_transactions in self._group_transactions(
            localized_expenses,
            False,
            self.lang["category_selection.defaults.income.other"],
        ).items():
            transactions.setdefault(date_key, []).extend(daily_transactions)

        for day_key in transactions:
            transactions[day_key].sort(
                key=lambda t: str(t.get("date", "")), reverse=True
            )

        return balance_data, transactions

    def _localize_default_categories(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        localized = []
        for record in records:
            item = record.copy()
            category = self.default_category_aliases.get(str(item.get("category") or ""))
            if category:
                item["category"] = category["name"]
            localized.append(item)
        return localized

    @staticmethod
    def _group_transactions(records: list[dict[str, Any]], is_income: bool, default_category: str) -> TransactionGroups:
        transactions: TransactionGroups = {}
        for record in records:
            transaction: Transaction = {
                "id": record.get("id"),
                "title": record.get("category", default_category),
                "subtitle": record.get("note") or "",
                "amount": float(record.get("amount", 0)),
                "date": record.get("date", ""),
                "positive": is_income,
            }
            date_key = str(transaction["date"])[:10]
            transactions.setdefault(date_key, []).append(transaction)
        return transactions

    @staticmethod
    def filter_transactions(raw_transactions: TransactionGroups, filter_type: str, sort_by: str, search_query: str) -> list[Transaction]:
        filtered: list[Transaction] = []
        query = (search_query or "").strip().lower()

        for txs in raw_transactions.values():
            for tx in txs:
                is_income = bool(tx.get("positive"))
                if filter_type == "income" and not is_income:
                    continue
                if filter_type == "expense" and is_income:
                    continue

                search_text = f"{tx.get('title', '')} {tx.get('subtitle', '')}".lower()
                if query and query not in search_text:
                    continue

                filtered.append(tx)

        reverse_sort = sort_by != "oldest"
        filtered.sort(key=lambda t: str(t.get("date", "")), reverse=reverse_sort)
        return filtered

    def delete_transaction(self, transaction_id: int) -> bool:
        try:
            return db.spending.delete_entry(self.current_user, int(transaction_id))
        except TypeError, ValueError:
            Logger.warning(f"Invalid transaction id: {transaction_id}")
            return False

    def get_spending_analysis_inputs(self) -> tuple[list[dict[str, str | float]], list[dict[str, str | float]]]:
        def compact(records: list[dict[str, Any]]) -> list[dict[str, str | float]]:
            return [
                {
                    "category": str(item.get("category") or ""),
                    "amount": float(item.get("amount") or 0),
                    "date": str(item.get("date") or ""),
                }
                for item in records
            ]

        return (
            compact(db.spending.get_user_incomes(self.current_user)),
            compact(db.spending.get_user_expenses(self.current_user)),
        )

    def get_month_transaction_count(self, month: str) -> int:
        month_start = date.fromisoformat(f"{month}-01")
        if month_start.strftime("%Y-%m") != month:
            raise ValueError("Month must use YYYY-MM format.")

        incomes, expenses = self.get_spending_analysis_inputs()
        count = 0
        for transaction in incomes + expenses:
            try:
                transaction_month = date.fromisoformat(
                    str(transaction["date"])[:10]
                ).strftime("%Y-%m")
            except ValueError:
                continue
            if transaction_month == month:
                count += 1
        return count

    def get_monthly_analysis_usage(self, refresh_token: str) -> dict[str, Any]:
        firebase_id_token = self._refresh_firebase_id_token(refresh_token)
        return self._request_json(
            "GET",
            "/api/v1/spending-analysis/usage",
            firebase_id_token,
            timeout=15,
        )

    @staticmethod
    def get_monthly_usage_counts(usage: dict[str, Any]) -> tuple[int | None, int | None]:
        remaining = usage["remaining"]
        limit = usage["limit"]
        # bool is an int subclass, but API counts must be JSON integers.
        if limit is None and remaining is None:
            return None, None
        if (
            limit is None
            or remaining is None
            or type(remaining) is not int
            or type(limit) is not int
            or not 0 <= remaining <= limit
        ):
            raise ValueError("Invalid monthly spending usage counts")
        return remaining, limit

    def analyze_spending(self, refresh_token: str, month: str) -> dict[str, Any]:
        transaction_count = self.get_month_transaction_count(month)
        if transaction_count < MIN_SPENDING_ANALYSIS_TRANSACTIONS:
            raise SpendingAnalysisApiError(
                422,
                f"At least {MIN_SPENDING_ANALYSIS_TRANSACTIONS} transactions are required.",
            )
        firebase_id_token = self._refresh_firebase_id_token(refresh_token)
        incomes, expenses = self.get_spending_analysis_inputs()
        payload = {
            "income": incomes,
            "expenses": expenses,
            "currency": get_user_currency(self.current_user).split(" ", 1)[0],
            "language": db.users.get_language(self.current_user),
            "current_month": month,
        }
        return self._request_json(
            "POST",
            "/api/v1/spending-analysis",
            firebase_id_token,
            timeout=60,
            payload=payload,
        )

    def analyze_and_save_spending(self, refresh_token: str, month: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        report = self.analyze_spending(refresh_token, month)
        if not self.save_spending_report(report):
            raise RuntimeError("Could not save generated spending report.")
        history = self.get_spending_report_history()
        if not history:
            raise RuntimeError("Saved spending report was not returned in history.")
        return report, history

    @staticmethod
    def _refresh_firebase_id_token(refresh_token: str) -> str:
        if not refresh_token:
            raise SpendingAnalysisApiError(401, "Google sign-in is required.")
        base_url = BACKEND_URL.rstrip("/")
        try:
            response = requests.post(
                f"{base_url}/api/v1/auth/google/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                timeout=15,
            )
        except requests.RequestException as ex:
            Logger.warning(f"Google session refresh failed: {ex}")
            raise SpendingAnalysisApiError(
                0, "Could not refresh the Google sign-in."
            ) from ex
        token_data = LogicController._parse_response(response)
        firebase_id_token = token_data.get("access_token")
        if not isinstance(firebase_id_token, str) or not firebase_id_token:
            raise SpendingAnalysisApiError(502, "Authentication service returned no Firebase ID token.")
        rotated_refresh_token = token_data.get("refresh_token")
        if rotated_refresh_token and not db.app_settings.update_google_refresh_token(
            rotated_refresh_token
        ):
            raise SpendingAnalysisApiError(500, "Could not persist the refreshed Google sign-in.")
        return firebase_id_token

    @staticmethod
    def _request_json(
        method: str,
        path: str,
        firebase_id_token: str,
        timeout: int,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = requests.request(
                method,
                f"{BACKEND_URL.rstrip('/')}{path}",
                headers={"Authorization": f"Bearer {firebase_id_token}"},
                timeout=timeout,
                json=payload,
            )
        except requests.RequestException as ex:
            Logger.warning(f"Spending analysis request failed: {ex}")
            raise SpendingAnalysisApiError(
                0, "Could not connect to the spending analysis service."
            ) from ex
        return LogicController._parse_response(response)

    @staticmethod
    def _parse_response(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not response.ok:
            detail = data.get("detail", "") if isinstance(data, dict) else ""
            raise SpendingAnalysisApiError(
                response.status_code,
                detail
                or f"Spending analysis service returned HTTP {response.status_code}.",
            )
        if not isinstance(data, dict):
            raise SpendingAnalysisApiError(502, "Spending analysis service returned an invalid response.")
        return data

    def save_spending_report(self, report: dict[str, Any]) -> bool:
        return db.spending_analysis_history.add_report(self.current_user, report)

    def get_spending_report_history(self) -> list[dict[str, Any]]:
        return db.spending_analysis_history.get_user_reports(self.current_user)

    def delete_spending_report(self, report_id: int) -> bool:
        try:
            return db.spending_analysis_history.delete_report(
                self.current_user,
                int(report_id),
            )
        except (TypeError, ValueError):
            Logger.warning(f"Invalid spending report id: {report_id}")
            return False
