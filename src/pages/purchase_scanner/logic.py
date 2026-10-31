# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import requests

from src.database import db
from src.logger import Logger

BACKEND_URL = "https://finam-backend.vercel.app/"


class ScannerApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class LogicController:
    def __init__(self, username: str = "Admin"):
        self.current_user = username or "Admin"

    def get_currency(self) -> str:
        return db.users.get_currency(self.current_user)

    def analyze_purchase(
        self,
        name: str,
        price: str,
        reason: str,
        trigger: str,
        time: str,
        refresh_token: str,
    ):
        if not refresh_token:
            raise ScannerApiError(401, "Google sign-in is required.")

        try:
            price = float(price.strip()) if price and str(price).strip() else 0.0
        except (ValueError, AttributeError):
            price = 0.0

        trigger_texts = {
            "need": "nhu cầu thật sự",
            "social": "áp lực bạn bè",
            "tiktok": "nội dung social media",
            "sale": "flash sale/giảm giá",
            "emotion": "cảm xúc nhất thời",
        }
        trigger_display = trigger_texts.get(trigger, "yếu tố bên ngoài")

        try:
            base_url = BACKEND_URL.rstrip("/")
            firebase_id_token = self._refresh_firebase_id_token(
                base_url,
                refresh_token,
            )

            payload = {
                "item_name": name or "Sản phẩm",
                "price": price if price > 0 else 1.0,
                "currency": self.get_currency().split(" ", 1)[0],
                "category": trigger_display,
                "monthly_budget_remaining": 5000000.0,
                "user_notes": f"Lý do: {reason or 'Không có'}. Thời gian suy nghĩ: {time}.",
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {firebase_id_token}",
            }

            response = requests.post(
                f"{base_url}/api/v1/purchase-advice",
                json=payload,
                headers=headers,
                timeout=30,
            )
            data = self._parse_response(response)
            raw_risk = data.get("risk")
            risk = int(raw_risk) if raw_risk is not None else None
            ai_advice = data.get("advice", "")
        except requests.RequestException as ex:
            Logger.warn(f"Purchase scanner request failed: {ex}")
            raise ScannerApiError(
                0,
                "Could not connect to the purchase scanner service.",
            ) from ex

        if risk is None:
            ai_advice = ai_advice or "Đầu vào bị đánh dấu là nội dung troll hoặc không hợp lệ để phân tích."

        return risk, trigger_display, price, ai_advice

    def get_daily_usage(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise ScannerApiError(401, "Google sign-in is required.")
        base_url = BACKEND_URL.rstrip("/")
        firebase_id_token = self._refresh_firebase_id_token(
            base_url,
            refresh_token,
        )
        try:
            response = requests.get(
                f"{base_url}/api/v1/purchase-advice/usage",
                headers={"Authorization": f"Bearer {firebase_id_token}"},
                timeout=15,
            )
        except requests.RequestException as ex:
            Logger.warn(f"Purchase scanner usage request failed: {ex}")
            raise ScannerApiError(
                0,
                "Could not connect to the purchase scanner service.",
            ) from ex
        data = self._parse_response(response)
        if not isinstance(data.get("remaining"), int) or not isinstance(
            data.get("reset_at"), str
        ):
            raise ScannerApiError(502, "Scanner service returned invalid usage data.")
        return data

    @classmethod
    def _refresh_firebase_id_token(
        cls,
        base_url: str,
        refresh_token: str,
    ) -> str:
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
            Logger.warn(f"Google session refresh failed: {ex}")
            raise ScannerApiError(
                0,
                "Could not refresh the Google sign-in.",
            ) from ex
        token_data = cls._parse_response(response)
        firebase_id_token = token_data.get("access_token")
        if not firebase_id_token:
            raise ScannerApiError(
                502,
                "Authentication service returned no Firebase ID token.",
            )
        rotated_refresh_token = token_data.get("refresh_token")
        if rotated_refresh_token and not db.app_settings.update_google_refresh_token(
            rotated_refresh_token
        ):
            raise ScannerApiError(
                500,
                "Could not persist the refreshed Google sign-in.",
            )
        return firebase_id_token

    @staticmethod
    def _parse_response(response: requests.Response) -> dict:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not response.ok:
            detail = data.get("detail", "") if isinstance(data, dict) else ""
            raise ScannerApiError(
                response.status_code,
                detail or f"Scanner service returned HTTP {response.status_code}.",
            )
        if not isinstance(data, dict):
            raise ScannerApiError(502, "Scanner service returned an invalid response.")
        return data

    def save_scan_result(self, item_name: str, price: float, trigger: str, reason: str, thinking_time: str, risk_score: int | None, trigger_display: str, ai_advice: str) -> bool:
        if risk_score is None:
            return False
        return db.scanner_history.add_scan_result(self.current_user, item_name, price, trigger, reason, thinking_time, risk_score, trigger_display, ai_advice)

    def get_scan_history(self):
        return db.scanner_history.get_user_scan_history(self.current_user)

    def delete_scan_result(self, scan_id: int | None) -> bool:
        if scan_id is None:
            return False
        return db.scanner_history.delete_scan_result(self.current_user, scan_id)

    def clear_scan_history(self) -> bool:
        return db.scanner_history.clear_user_scan_history(self.current_user)
