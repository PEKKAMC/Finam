# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

import requests

from src.database import db
from src.logger import Logger
from src.pages.global_components.financial_chart import get_financial_chart_data
from src.utils import Data, format_number

BACKEND_URL = (
    os.getenv("FINAM_BACKEND_URL", "").strip()
    or "https://finam-backend.vercel.app/"
)


class SpendingAnalysisApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class LogicController:
    """Business logic for the Spending page."""

    def __init__(self, current_user: str):
        self.current_user = current_user
        self.data = Data()

    def get_category_icon_map(self) -> dict[str, str]:
        categories = (
            self.data.get_default_expense_categories()
            + self.data.get_default_income_categories()
            + db.categories.get_custom_categories(self.current_user, "expense")
            + db.categories.get_custom_categories(self.current_user, "income")
        )
        return {
            category["name"]: category["icon"]
            for category in categories
        }

    def get_transaction_data(self) -> tuple[dict, dict]:
        expenses = db.spending.get_user_expenses(self.current_user) or []
        incomes = db.spending.get_user_incomes(self.current_user) or []

        total_income = sum(float(item.get("amount", 0)) for item in incomes)
        total_expense = sum(float(item.get("amount", 0)) for item in expenses)
        net_balance = total_income - total_expense
        currency = db.users.get_currency(self.current_user)

        balance_data = {
            "incomes": f"+{format_number(total_income)} {currency}",
            "expenses": f"-{format_number(total_expense)} {currency}",
            "current": f"{format_number(net_balance)} {currency}",
        }

        transactions: dict[str, list[dict]] = {}
        for item in incomes:
            tx = {
                "id": item.get("id"),
                "title": item.get("category", "Lương"),
                "subtitle": item.get("note") or "",
                "amount": float(item.get("amount", 0)),
                "date": item.get("date", ""),
                "positive": True,
            }
            transactions.setdefault(str(tx["date"])[:10], []).append(tx)

        for item in expenses:
            tx = {
                "id": item.get("id"),
                "title": item.get("category", "Khác"),
                "subtitle": item.get("note") or "",
                "amount": float(item.get("amount", 0)),
                "date": item.get("date", ""),
                "positive": False,
            }
            transactions.setdefault(str(tx["date"])[:10], []).append(tx)

        for day_key in transactions:
            transactions[day_key].sort(key=lambda t: str(t.get("date", "")), reverse=True)

        return balance_data, transactions

    def get_dashboard_data(self, chart_type: str = "daily", date_offset: int = 0, target_year: int | None = None) -> tuple[dict, list, str]:
        chart_date, chart_data = get_financial_chart_data(
            username=self.current_user,
            chart_type=chart_type,
            date_offset=date_offset,
            target_year=target_year,
        )
        return chart_date, chart_data, chart_type

    @staticmethod
    def filter_transactions(raw_transactions: dict, filter_type: str, sort_by: str, search_query: str) -> list:
        filtered: list[dict] = []
        query = (search_query or "").strip().lower()

        for txs in raw_transactions.values():
            for tx in txs:
                if filter_type != "all":
                    is_income = bool(tx.get("positive"))
                    if filter_type == "income" and not is_income:
                        continue
                    if filter_type == "expense" and is_income:
                        continue

                if query:
                    category_name = str(tx.get("title", ""))
                    haystack = f"{category_name} {tx.get('subtitle', '')}".lower()
                    if query not in haystack:
                        continue

                filtered.append(tx)

        reverse_sort = (sort_by != "oldest")
        filtered.sort(key=lambda t: str(t.get("date", "")), reverse=reverse_sort)
        return filtered

    def delete_transaction(self, transaction_id: int) -> bool:
        try:
            return db.spending.delete_entry(self.current_user, int(transaction_id))
        except (TypeError, ValueError):
            Logger.warning(f"Invalid transaction id: {transaction_id}")
            return False

    def get_spending_analysis_inputs(self) -> tuple[list[dict], list[dict]]:
        def compact(records: list[dict]) -> list[dict]:
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

    def get_weekly_analysis_usage(self, refresh_token: str) -> dict:
        firebase_id_token = self._refresh_firebase_id_token(refresh_token)
        return self._request_json(
            "GET",
            "/api/v1/spending-analysis/usage",
            firebase_id_token,
            timeout=15,
        )

    def analyze_spending(self, refresh_token: str) -> dict:
        firebase_id_token = self._refresh_firebase_id_token(refresh_token)
        incomes, expenses = self.get_spending_analysis_inputs()
        payload = {
            "income": incomes,
            "expenses": expenses,
            "currency": db.users.get_currency(self.current_user).split(" ", 1)[0],
            "language": db.users.get_language(self.current_user),
        }
        return self._request_json(
            "POST",
            "/api/v1/spending-analysis",
            firebase_id_token,
            json=payload,
            timeout=60,
        )

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
        if not firebase_id_token:
            raise SpendingAnalysisApiError(
                502, "Authentication service returned no Firebase ID token."
            )
        rotated_refresh_token = token_data.get("refresh_token")
        if rotated_refresh_token and not db.app_settings.update_google_refresh_token(
            rotated_refresh_token
        ):
            raise SpendingAnalysisApiError(
                500, "Could not persist the refreshed Google sign-in."
            )
        return firebase_id_token

    @staticmethod
    def _request_json(
        method: str,
        path: str,
        firebase_id_token: str,
        timeout: int,
        **kwargs,
    ) -> dict:
        try:
            response = requests.request(
                method,
                f"{BACKEND_URL.rstrip('/')}{path}",
                headers={"Authorization": f"Bearer {firebase_id_token}"},
                timeout=timeout,
                **kwargs,
            )
        except requests.RequestException as ex:
            Logger.warning(f"Spending analysis request failed: {ex}")
            raise SpendingAnalysisApiError(
                0, "Could not connect to the spending analysis service."
            ) from ex
        return LogicController._parse_response(response)

    @staticmethod
    def _parse_response(response: requests.Response) -> dict:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not response.ok:
            detail = data.get("detail", "") if isinstance(data, dict) else ""
            raise SpendingAnalysisApiError(
                response.status_code,
                detail or f"Spending analysis service returned HTTP {response.status_code}.",
            )
        if not isinstance(data, dict):
            raise SpendingAnalysisApiError(
                502, "Spending analysis service returned an invalid response."
            )
        return data

    def save_spending_report(self, report: dict) -> bool:
        return db.spending_analysis_history.add_report(self.current_user, report)

    def get_spending_report_history(self) -> list[dict]:
        return db.spending_analysis_history.get_user_reports(self.current_user)
